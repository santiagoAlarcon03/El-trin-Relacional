"""
API REST - Sistema RAG para Óptica El-trin-Relacional
FastAPI + MongoDB + Sentence-BERT + Groq (Llama 3.1)
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import sys
from datetime import datetime

# Agregar path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.models import HealthResponse, CollectionsResponse
from api.routers import search, rag

# Cargar variables de entorno
load_dotenv()

# Crear aplicación FastAPI
app = FastAPI(
    title="RAG System API - Óptica El-trin-Relacional",
    description="""
    Sistema de Recuperación Aumentada por Generación (RAG) para gestión de óptica.
    
    ## Características
    
    * **Búsqueda Vectorial Semántica** - Usando Sentence-BERT (all-MiniLM-L6-v2)
    * **Sistema RAG Completo** - Retrieval + LLM (Groq + Llama 3.1)
    * **Multimodal** - Búsqueda en 9 colecciones diferentes
    * **Alta Precisión** - Embeddings reales con ~90% precisión
    
    ## Endpoints Principales
    
    * `POST /search` - Búsqueda vectorial pura
    * `POST /rag` - Sistema RAG completo (pregunta → respuesta)
    * `GET /health` - Estado del sistema
    * `GET /collections` - Información de colecciones
    """,
    version="1.0.0",
    contact={
        "name": "El-trin-Relacional",
        "url": "https://github.com/santiagoAlarcon03/El-trin-Relacional"
    }
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(search.router)
app.include_router(rag.router)

# Conexión a MongoDB
client = MongoClient(os.getenv('MONGODB_URI'))
db = client['optica_db']


@app.get("/", tags=["Root"])
async def root():
    """Endpoint raíz - Información de la API"""
    return {
        "message": "API RAG System - Óptica El-trin-Relacional",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "docs": "/docs",
            "search": "/search",
            "rag": "/rag",
            "health": "/health",
            "collections": "/collections"
        }
    }


@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """
    Health check - Verifica estado del sistema
    
    Comprueba:
    - Conexión a base de datos
    - Modelo de embeddings cargado
    - Estado general de la API
    """
    try:
        # Verificar conexión a MongoDB
        db.command('ping')
        db_connected = True
    except:
        db_connected = False
    
    try:
        # Verificar modelo de embeddings
        from rag.embeddings import get_embedding_generator
        _ = get_embedding_generator()
        embeddings_loaded = True
    except:
        embeddings_loaded = False
    
    status = "healthy" if (db_connected and embeddings_loaded) else "degraded"
    
    return HealthResponse(
        status=status,
        version="1.0.0",
        timestamp=datetime.now(),
        database_connected=db_connected,
        embeddings_model_loaded=embeddings_loaded
    )


@app.get("/collections", response_model=CollectionsResponse, tags=["System"])
async def get_collections():
    """
    Lista todas las colecciones disponibles con estadísticas
    
    Retorna:
    - Nombre de colección
    - Número de documentos
    - Documentos con embeddings
    - Porcentaje vectorizado
    """
    try:
        colecciones_info = []
        total_docs = 0
        
        for col_name in db.list_collection_names():
            if col_name.startswith('system'):
                continue
            
            count_total = db[col_name].count_documents({})
            count_embeddings = db[col_name].count_documents({'embedding': {'$exists': True}})
            
            porcentaje = (count_embeddings / count_total * 100) if count_total > 0 else 0
            
            colecciones_info.append({
                'name': col_name,
                'total_documents': count_total,
                'documents_with_embeddings': count_embeddings,
                'vectorization_percentage': round(porcentaje, 1)
            })
            
            total_docs += count_total
        
        # Ordenar por nombre
        colecciones_info.sort(key=lambda x: x['name'])
        
        return CollectionsResponse(
            collections=colecciones_info,
            total_collections=len(colecciones_info),
            total_documents=total_docs
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo colecciones: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    
    print("=" * 80)
    print("🚀 INICIANDO API REST - SISTEMA RAG")
    print("=" * 80)
    print(f"\n📍 URL: http://localhost:8000")
    print(f"📚 Documentación: http://localhost:8000/docs")
    print(f"🔧 ReDoc: http://localhost:8000/redoc")
    print("\n" + "=" * 80)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
