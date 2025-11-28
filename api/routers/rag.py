"""
Router para sistema RAG (Retrieval-Augmented Generation)
"""

from fastapi import APIRouter, HTTPException
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import sys
import time

# Agregar path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from api.models import RAGRequest, RAGResponse, SearchResult
from rag.embeddings import generar_embedding, similitud_coseno
from llm.groq_client import get_groq_client

# Cargar variables de entorno
load_dotenv()

# Conexión a MongoDB
client = MongoClient(os.getenv('MONGODB_URI'))
db = client['optica_db']

router = APIRouter(prefix="/rag", tags=["RAG"])


# Configuración de colecciones
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


@router.post("/", response_model=RAGResponse)
async def rag_query(request: RAGRequest):
    """
    Sistema RAG completo: Retrieval + Generation
    
    1. Recupera documentos relevantes (búsqueda vectorial)
    2. Construye contexto con los documentos
    3. Envía pregunta + contexto a LLM (Groq + Llama 3.1)
    4. Retorna respuesta generada + fuentes
    
    - **query**: Pregunta del usuario
    - **limit**: Documentos a recuperar para contexto (1-20)
    - **collection**: Colección específica o None para todas
    - **temperature**: Creatividad del LLM (0.0-2.0)
    """
    start_time = time.time()
    
    try:
        # PASO 1: RETRIEVAL - Búsqueda vectorial
        query_embedding = generar_embedding(request.query)
        
        # Determinar colecciones
        if request.collection and request.collection != "all":
            if request.collection not in COLECCIONES_DISPONIBLES:
                raise HTTPException(
                    status_code=400,
                    detail=f"Colección '{request.collection}' no disponible"
                )
            colecciones_buscar = [request.collection]
        else:
            colecciones_buscar = list(COLECCIONES_DISPONIBLES.keys())
        
        # Recuperar documentos relevantes
        documentos_recuperados = []
        
        for col_name in colecciones_buscar:
            documentos = list(db[col_name].find({'embedding': {'$exists': True}}))
            campos_relevantes = COLECCIONES_DISPONIBLES[col_name]
            
            for doc in documentos:
                score = similitud_coseno(query_embedding, doc['embedding'])
                
                if score < 0.2:  # Filtro mínimo
                    continue
                
                # Extraer contenido relevante
                content = {'_id': str(doc['_id'])}
                for campo in campos_relevantes:
                    if campo in doc:
                        content[campo] = doc[campo]
                
                documentos_recuperados.append({
                    'id': str(doc['_id']),
                    'collection': col_name,
                    'score': float(score),
                    'content': content
                })
        
        # Ordenar por relevancia y limitar
        documentos_recuperados.sort(key=lambda x: x['score'], reverse=True)
        top_documentos = documentos_recuperados[:request.limit]
        
        if not top_documentos:
            raise HTTPException(
                status_code=404,
                detail="No se encontraron documentos relevantes para tu consulta"
            )
        
        # PASO 2: GENERATION - Generar respuesta con LLM
        groq_client = get_groq_client()
        
        respuesta_llm = groq_client.generar_respuesta(
            pregunta=request.query,
            contexto=top_documentos,
            temperature=request.temperature
        )
        
        # PASO 3: Formatear response
        sources = [
            SearchResult(
                id=doc['id'],
                collection=doc['collection'],
                score=doc['score'],
                content=doc['content']
            )
            for doc in top_documentos
        ]
        
        execution_time = (time.time() - start_time) * 1000  # ms
        
        return RAGResponse(
            query=request.query,
            answer=respuesta_llm,
            sources=sources,
            total_sources=len(sources),
            execution_time_ms=round(execution_time, 2)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en RAG: {str(e)}")
