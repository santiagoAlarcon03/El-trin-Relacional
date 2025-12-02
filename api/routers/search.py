"""
Router para endpoints de búsqueda vectorial
"""

from fastapi import APIRouter, HTTPException, File, UploadFile, Form
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import sys
import time
from typing import List, Optional
from PIL import Image
import io

# Agregar path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from api.models import SearchRequest, SearchResponse, SearchResult, ImageSearchRequest, ImageSearchResponse, TextToImageSearchRequest, TextToImageSearchResponse
from rag.embeddings import generar_embedding, generar_embedding_imagen, generar_embedding_texto_clip, similitud_coseno

# Cargar variables de entorno
load_dotenv()

# Conexión a MongoDB
client = MongoClient(os.getenv('MONGODB_URI'))
db = client['optica_db']

router = APIRouter(prefix="/search", tags=["Search"])


# Configuración de colecciones disponibles para búsqueda
COLECCIONES_DISPONIBLES = {
    'productos': ['nombre_producto', 'marca', 'descripcion', 'precio_venta'],
    'clientes': ['nombre', 'apellido', 'email'],
    'asesores': ['nombre', 'apellido', 'especialidad'],
    'especialistas': ['nombre', 'apellido', 'especialidad'],
    'proveedores': ['nombre', 'descripcion_servicios'],
    'laboratorios': ['nombre', 'especialidades'],
    'examenes': ['tipo_examen', 'diagnostico', 'observaciones'],
    'citas': ['motivo', 'estado', 'notas'],
    'ventas': ['estado', 'metodo_pago', 'total']
}


@router.post("/", response_model=SearchResponse)
async def search_documents(request: SearchRequest):
    """
    Búsqueda vectorial semántica en las colecciones de MongoDB
    
    - **query**: Texto de búsqueda
    - **limit**: Número de resultados (1-50)
    - **collection**: Colección específica o None para buscar en todas
    
    Retorna documentos ordenados por similitud coseno
    """
    start_time = time.time()
    
    try:
        # Generar embedding de la query
        query_embedding = generar_embedding(request.query)
        
        # Determinar colecciones a buscar
        if request.collection and request.collection != "all":
            if request.collection not in COLECCIONES_DISPONIBLES:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Colección '{request.collection}' no disponible. Usa: {list(COLECCIONES_DISPONIBLES.keys())}"
                )
            colecciones_buscar = [request.collection]
        else:
            colecciones_buscar = list(COLECCIONES_DISPONIBLES.keys())
        
        # Buscar en cada colección
        todos_resultados = []
        
        for col_name in colecciones_buscar:
            # Obtener documentos con embedding
            documentos = list(db[col_name].find({'embedding': {'$exists': True}}))
            
            campos_relevantes = COLECCIONES_DISPONIBLES[col_name]
            
            for doc in documentos:
                # Calcular similitud
                score = similitud_coseno(query_embedding, doc['embedding'])
                
                # Filtrar por score mínimo (0.2 = 20% similitud)
                if score < 0.2:
                    continue
                
                # Extraer solo campos relevantes
                content = {'_id': str(doc['_id'])}
                for campo in campos_relevantes:
                    if campo in doc:
                        content[campo] = doc[campo]
                
                todos_resultados.append(
                    SearchResult(
                        id=str(doc['_id']),
                        collection=col_name,
                        score=float(score),
                        content=content
                    )
                )
        
        # Ordenar por score y limitar
        todos_resultados.sort(key=lambda x: x.score, reverse=True)
        resultados_finales = todos_resultados[:request.limit]
        
        execution_time = (time.time() - start_time) * 1000  # ms
        
        return SearchResponse(
            query=request.query,
            total_results=len(resultados_finales),
            results=resultados_finales,
            execution_time_ms=round(execution_time, 2)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en búsqueda: {str(e)}")


@router.post("/image", response_model=ImageSearchResponse)
async def search_similar_images_by_file(
    image: UploadFile = File(...),
    limit: Optional[int] = Form(10),
    collection: Optional[str] = Form("productos")
):
    """
    Búsqueda de imágenes similares subiendo un archivo usando CLIP
    
    - **image**: Archivo de imagen (JPG, PNG, GIF)
    - **limit**: Número de resultados (1-50)
    - **collection**: Colección a buscar (por defecto 'productos')
    
    Retorna productos con imágenes similares ordenados por similitud visual
    """
    start_time = time.time()
    
    try:
        # Validar límite
        limit = min(max(1, limit), 50)
        
        # Leer el archivo de imagen
        contents = await image.read()
        
        # Convertir a PIL Image
        pil_image = Image.open(io.BytesIO(contents))
        
        # Generar embedding de la imagen con CLIP
        query_embedding = generar_embedding_imagen(pil_image)
        
        # Verificar que el embedding no sea nulo
        if not query_embedding or all(v == 0.0 for v in query_embedding):
            raise HTTPException(
                status_code=400,
                detail="No se pudo procesar la imagen. Verifica que sea un formato válido."
            )
        
        # Buscar productos con image_embedding
        documentos = list(db[collection].find({'image_embedding': {'$exists': True}}))
        
        if not documentos:
            return ImageSearchResponse(
                image_url=image.filename,
                total_results=0,
                results=[],
                execution_time_ms=round((time.time() - start_time) * 1000, 2),
                model_used="CLIP ViT-B/32"
            )
        
        # Calcular similitud con cada imagen de producto
        todos_resultados = []
        
        for doc in documentos:
            score = similitud_coseno(query_embedding, doc['image_embedding'])
            
            # Filtrar por score mínimo (0.15 para imágenes)
            if score < 0.15:
                continue
            
            # Extraer imagenes del documento
            imagenes = []
            if 'imagenes' in doc:
                import ast
                imgs = doc['imagenes']
                if isinstance(imgs, str):
                    try:
                        imagenes = ast.literal_eval(imgs)
                    except:
                        imagenes = []
                elif isinstance(imgs, list):
                    imagenes = imgs
            
            # Preparar contenido relevante
            content = {
                '_id': str(doc['_id']),
                'nombre_producto': doc.get('nombre_producto', 'Sin nombre'),
                'marca': doc.get('marca', 'Sin marca'),
                'precio_venta': doc.get('precio_venta', 0),
                'descripcion': doc.get('descripcion', ''),
                'imagenes': imagenes
            }
            
            todos_resultados.append(
                SearchResult(
                    id=str(doc['_id']),
                    collection=collection,
                    score=float(score),
                    content=content
                )
            )
        
        # Ordenar por score y limitar
        todos_resultados.sort(key=lambda x: x.score, reverse=True)
        resultados_finales = todos_resultados[:limit]
        
        execution_time = (time.time() - start_time) * 1000  # ms
        
        return ImageSearchResponse(
            image_url=image.filename,
            total_results=len(resultados_finales),
            results=resultados_finales,
            execution_time_ms=round(execution_time, 2),
            model_used="CLIP ViT-B/32"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en búsqueda de imágenes: {str(e)}")


@router.post("/image-url", response_model=ImageSearchResponse)
async def search_similar_images_by_url(request: ImageSearchRequest):
    """
    Búsqueda de imágenes similares usando URL con CLIP
    
    - **image_url**: URL de la imagen de consulta
    - **limit**: Número de resultados (1-50)
    - **collection**: Colección a buscar (por defecto 'productos')
    
    Retorna productos con imágenes similares ordenados por similitud visual
    """
    start_time = time.time()
    
    try:
        # Generar embedding de la imagen de consulta con CLIP
        query_embedding = generar_embedding_imagen(request.image_url)
        
        # Verificar que el embedding no sea nulo
        if not query_embedding or all(v == 0.0 for v in query_embedding):
            raise HTTPException(
                status_code=400,
                detail="No se pudo procesar la imagen. Verifica que la URL sea válida y accesible."
            )
        
        # Buscar productos con image_embedding
        documentos = list(db[request.collection].find({'image_embedding': {'$exists': True}}))
        
        if not documentos:
            return ImageSearchResponse(
                image_url=request.image_url,
                total_results=0,
                results=[],
                execution_time_ms=round((time.time() - start_time) * 1000, 2)
            )
        
        # Calcular similitud con cada imagen de producto
        todos_resultados = []
        
        for doc in documentos:
            score = similitud_coseno(query_embedding, doc['image_embedding'])
            
            # Filtrar por score mínimo (0.15 para imágenes)
            if score < 0.15:
                continue
            
            # Preparar contenido relevante
            content = {
                '_id': str(doc['_id']),
                'nombre_producto': doc.get('nombre_producto', 'Sin nombre'),
                'marca': doc.get('marca', 'Sin marca'),
                'precio_venta': doc.get('precio_venta', 0),
                'imagen_url': doc.get('imagen_url', ''),
                'imagen_url2': doc.get('imagen_url2', '')
            }
            
            todos_resultados.append(
                SearchResult(
                    id=str(doc['_id']),
                    collection=request.collection,
                    score=float(score),
                    content=content
                )
            )
        
        # Ordenar por score y limitar
        todos_resultados.sort(key=lambda x: x.score, reverse=True)
        resultados_finales = todos_resultados[:request.limit]
        
        execution_time = (time.time() - start_time) * 1000  # ms
        
        return ImageSearchResponse(
            image_url=request.image_url,
            total_results=len(resultados_finales),
            results=resultados_finales,
            execution_time_ms=round(execution_time, 2)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en búsqueda de imágenes: {str(e)}")


@router.post("/text-to-image", response_model=TextToImageSearchResponse)
async def search_images_by_text(request: TextToImageSearchRequest):
    """
    Búsqueda de imágenes mediante descripción de texto usando CLIP
    
    - **query**: Texto describiendo la imagen buscada (ej: "gafas de sol deportivas negras")
    - **limit**: Número de resultados (1-50)
    - **collection**: Colección a buscar (por defecto 'productos')
    
    Retorna productos cuyas imágenes coinciden con la descripción de texto
    """
    start_time = time.time()
    
    try:
        # Generar embedding del texto con CLIP
        query_embedding = generar_embedding_texto_clip(request.query)
        
        # Verificar que el embedding no sea nulo
        if not query_embedding or all(v == 0.0 for v in query_embedding):
            raise HTTPException(
                status_code=400,
                detail="No se pudo procesar el texto. CLIP no está disponible."
            )
        
        # Buscar productos con image_embedding
        documentos = list(db[request.collection].find({'image_embedding': {'$exists': True}}))
        
        if not documentos:
            return TextToImageSearchResponse(
                query=request.query,
                total_results=0,
                results=[],
                execution_time_ms=round((time.time() - start_time) * 1000, 2)
            )
        
        # Calcular similitud coseno entre texto y embeddings de imágenes
        todos_resultados = []
        
        for doc in documentos:
            score = similitud_coseno(query_embedding, doc['image_embedding'])
            
            # Filtrar por score mínimo (0.2 para texto→imagen)
            if score < 0.2:
                continue
            
            # Extraer imagenes del documento
            imagenes = []
            if 'imagenes' in doc:
                import ast
                imgs = doc['imagenes']
                if isinstance(imgs, str):
                    try:
                        imagenes = ast.literal_eval(imgs)
                    except:
                        imagenes = []
                elif isinstance(imgs, list):
                    imagenes = imgs
            
            # Preparar contenido relevante
            content = {
                '_id': str(doc['_id']),
                'nombre_producto': doc.get('nombre_producto', 'Sin nombre'),
                'marca': doc.get('marca', 'Sin marca'),
                'precio_venta': doc.get('precio_venta', 0),
                'descripcion': doc.get('descripcion', ''),
                'imagenes': imagenes
            }
            
            todos_resultados.append(
                SearchResult(
                    id=str(doc['_id']),
                    collection=request.collection,
                    score=float(score),
                    content=content
                )
            )
        
        # Ordenar por score y limitar
        todos_resultados.sort(key=lambda x: x.score, reverse=True)
        resultados_finales = todos_resultados[:request.limit]
        
        execution_time = (time.time() - start_time) * 1000  # ms
        
        return TextToImageSearchResponse(
            query=request.query,
            total_results=len(resultados_finales),
            results=resultados_finales,
            execution_time_ms=round(execution_time, 2)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en búsqueda texto→imagen: {str(e)}")


