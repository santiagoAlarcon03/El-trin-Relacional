"""
Modelos Pydantic para validación de requests y responses
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class SearchRequest(BaseModel):
    """Request para búsqueda vectorial"""
    query: str = Field(..., description="Texto de búsqueda", min_length=1)
    limit: int = Field(5, description="Número máximo de resultados", ge=1, le=50)
    collection: Optional[str] = Field(None, description="Colección específica o 'all' para todas")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "query": "gafas de sol deportivas",
                    "limit": 5,
                    "collection": "productos"
                }
            ]
        }
    }


class SearchResult(BaseModel):
    """Resultado individual de búsqueda"""
    id: str = Field(..., description="ID del documento")
    collection: str = Field(..., description="Colección de origen")
    score: float = Field(..., description="Score de similitud [0.0-1.0]")
    content: Dict[str, Any] = Field(..., description="Contenido del documento")


class SearchResponse(BaseModel):
    """Response de búsqueda vectorial"""
    query: str
    total_results: int
    results: List[SearchResult]
    execution_time_ms: float
    model_used: str = "all-MiniLM-L6-v2"


class ImageSearchRequest(BaseModel):
    """Request para búsqueda de imágenes similares"""
    image_url: str = Field(..., description="URL de la imagen de consulta", min_length=1)
    limit: int = Field(5, description="Número máximo de resultados", ge=1, le=50)
    collection: str = Field("productos", description="Colección a buscar (solo productos con imágenes)")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "image_url": "https://ejemplo.com/gafas.jpg",
                    "limit": 5,
                    "collection": "productos"
                }
            ]
        }
    }


class ImageSearchResponse(BaseModel):
    """Response de búsqueda de imágenes"""
    image_url: str
    total_results: int
    results: List[SearchResult]
    execution_time_ms: float
    model_used: str = "CLIP-ViT-B/32"


class TextToImageSearchRequest(BaseModel):
    """Request para búsqueda texto → imagen con CLIP"""
    query: str = Field(..., description="Texto describiendo la imagen buscada", min_length=1)
    limit: int = Field(5, description="Número máximo de resultados", ge=1, le=50)
    collection: str = Field("productos", description="Colección a buscar")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "query": "gafas de sol deportivas negras",
                    "limit": 5,
                    "collection": "productos"
                }
            ]
        }
    }


class TextToImageSearchResponse(BaseModel):
    """Response de búsqueda texto → imagen"""
    query: str
    total_results: int
    results: List[SearchResult]
    execution_time_ms: float
    model_used: str = "CLIP-ViT-B/32"


class RAGRequest(BaseModel):
    """Request para sistema RAG completo"""
    query: str = Field(..., description="Pregunta del usuario", min_length=1)
    limit: int = Field(5, description="Documentos a recuperar para contexto", ge=1, le=20)
    collection: Optional[str] = Field(None, description="Colección específica o None para todas")
    temperature: float = Field(0.7, description="Temperatura del LLM", ge=0.0, le=2.0)
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "query": "¿Qué lentes recomiendas para deportes acuáticos?",
                    "limit": 5,
                    "temperature": 0.7
                }
            ]
        }
    }


class RAGResponse(BaseModel):
    """Response de sistema RAG"""
    query: str
    answer: str = Field(..., description="Respuesta generada por el LLM")
    sources: List[SearchResult] = Field(..., description="Documentos usados como contexto")
    total_sources: int
    execution_time_ms: float
    model_used: str = "llama-3.3-70b-versatile"


class HealthResponse(BaseModel):
    """Response de health check"""
    status: str
    version: str
    timestamp: datetime
    database_connected: bool
    embeddings_model_loaded: bool


class CollectionsResponse(BaseModel):
    """Response con lista de colecciones disponibles"""
    collections: List[Dict[str, Any]]
    total_collections: int
    total_documents: int
