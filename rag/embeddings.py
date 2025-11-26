"""
Módulo de Embeddings Reales usando Sentence Transformers y CLIP
Reemplaza los embeddings falsos (hash-based) con modelos de ML reales
"""

from sentence_transformers import SentenceTransformer
import torch
import numpy as np
from typing import List, Union
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmbeddingGenerator:
    """
    Generador de embeddings usando modelos de ML reales
    - Texto: all-MiniLM-L6-v2 (384 dimensiones)
    - Imágenes: CLIP (próximamente)
    """
    
    def __init__(self):
        logger.info("🔄 Cargando modelo de embeddings...")
        
        # Modelo para texto (recomendado por el proyecto)
        self.text_model = SentenceTransformer('all-MiniLM-L6-v2')
        logger.info("✅ Modelo de texto cargado: all-MiniLM-L6-v2 (384 dims)")
        
        # Verificar si hay GPU disponible
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        logger.info(f"📱 Dispositivo: {self.device}")
        
        if self.device == 'cuda':
            self.text_model = self.text_model.to(self.device)
    
    def generar_embedding_texto(self, texto: str) -> List[float]:
        """
        Genera embedding real para texto usando Sentence-BERT
        
        Args:
            texto: Texto a vectorizar
            
        Returns:
            Lista de 384 floats (embedding normalizado)
        """
        if not texto or not texto.strip():
            logger.warning("⚠️ Texto vacío, retornando vector cero")
            return [0.0] * 384
        
        try:
            # Generar embedding con modelo real
            embedding = self.text_model.encode(
                texto,
                convert_to_tensor=True,
                normalize_embeddings=True  # Normalización L2
            )
            
            # Convertir a lista
            return embedding.cpu().tolist()
            
        except Exception as e:
            logger.error(f"❌ Error generando embedding: {e}")
            return [0.0] * 384
    
    def generar_embeddings_batch(self, textos: List[str], batch_size: int = 32) -> List[List[float]]:
        """
        Genera embeddings para múltiples textos (más eficiente)
        
        Args:
            textos: Lista de textos a vectorizar
            batch_size: Tamaño del lote para procesamiento
            
        Returns:
            Lista de embeddings
        """
        if not textos:
            return []
        
        try:
            logger.info(f"🔄 Generando {len(textos)} embeddings en lotes de {batch_size}...")
            
            embeddings = self.text_model.encode(
                textos,
                batch_size=batch_size,
                convert_to_tensor=True,
                normalize_embeddings=True,
                show_progress_bar=True
            )
            
            # Convertir a lista de listas
            return embeddings.cpu().tolist()
            
        except Exception as e:
            logger.error(f"❌ Error en batch: {e}")
            return [[0.0] * 384] * len(textos)
    
    def similitud_coseno(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calcula similitud coseno entre dos embeddings
        
        Returns:
            Score de similitud [0.0, 1.0]
        """
        # Como los embeddings ya están normalizados, el producto punto es la similitud
        return float(np.dot(embedding1, embedding2))


# Instancia global del generador (singleton)
_generator = None

def get_embedding_generator() -> EmbeddingGenerator:
    """Obtiene instancia única del generador (lazy loading)"""
    global _generator
    if _generator is None:
        _generator = EmbeddingGenerator()
    return _generator


# Funciones de conveniencia
def generar_embedding(texto: str) -> List[float]:
    """Función simple para generar un embedding de texto"""
    generator = get_embedding_generator()
    return generator.generar_embedding_texto(texto)


def generar_embeddings_batch(textos: List[str], batch_size: int = 32) -> List[List[float]]:
    """Función simple para generar embeddings en lote"""
    generator = get_embedding_generator()
    return generator.generar_embeddings_batch(textos, batch_size)


def similitud_coseno(embedding1: List[float], embedding2: List[float]) -> float:
    """Calcula similitud coseno"""
    generator = get_embedding_generator()
    return generator.similitud_coseno(embedding1, embedding2)


# Para compatibilidad con código anterior
def generar_embedding_simple(texto: str) -> List[float]:
    """
    Alias para compatibilidad con código anterior
    DEPRECADO: Usa generar_embedding() en su lugar
    """
    logger.warning("⚠️ generar_embedding_simple() está deprecado, usa generar_embedding()")
    return generar_embedding(texto)


if __name__ == "__main__":
    # Pruebas del módulo
    print("=" * 80)
    print("🧪 PRUEBAS DE EMBEDDINGS REALES")
    print("=" * 80)
    
    # Prueba 1: Embedding simple
    print("\n1️⃣ Prueba de embedding simple:")
    texto = "gafas de sol deportivas"
    embedding = generar_embedding(texto)
    print(f"   Texto: '{texto}'")
    print(f"   Dimensiones: {len(embedding)}")
    print(f"   Primeros 5 valores: {embedding[:5]}")
    print(f"   Norma L2: {np.linalg.norm(embedding):.6f} (debe ser ~1.0)")
    
    # Prueba 2: Similitud semántica
    print("\n2️⃣ Prueba de similitud semántica:")
    textos_prueba = [
        "gafas de sol deportivas",
        "lentes deportivos para correr",
        "zapatos de fútbol",
        "anteojos oscuros"
    ]
    
    embeddings_prueba = generar_embeddings_batch(textos_prueba)
    base_embedding = embeddings_prueba[0]
    
    print(f"   Texto base: '{textos_prueba[0]}'")
    for i, texto in enumerate(textos_prueba[1:], 1):
        sim = similitud_coseno(base_embedding, embeddings_prueba[i])
        print(f"   vs '{texto}': {sim:.4f}")
    
    # Prueba 3: Performance
    print("\n3️⃣ Prueba de performance:")
    import time
    
    start = time.time()
    _ = generar_embedding("prueba de velocidad")
    tiempo_single = time.time() - start
    print(f"   Embedding individual: {tiempo_single*1000:.2f}ms")
    
    textos_batch = ["texto de prueba"] * 100
    start = time.time()
    _ = generar_embeddings_batch(textos_batch)
    tiempo_batch = time.time() - start
    print(f"   Batch de 100 embeddings: {tiempo_batch*1000:.2f}ms")
    print(f"   Promedio por embedding: {tiempo_batch*10:.2f}ms")
    
    print("\n" + "=" * 80)
    print("✅ MÓDULO DE EMBEDDINGS LISTO")
    print("=" * 80)
