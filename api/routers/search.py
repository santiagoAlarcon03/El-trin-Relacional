"""
Router para endpoints de búsqueda vectorial
"""

from fastapi import APIRouter, HTTPException
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import sys
import time
from typing import List

# Agregar path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from api.models import SearchRequest, SearchResponse, SearchResult
from rag.embeddings import generar_embedding, similitud_coseno

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
