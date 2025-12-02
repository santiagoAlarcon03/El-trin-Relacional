"""
Módulo de Embeddings Reales usando Sentence Transformers y CLIP
Reemplaza los embeddings falsos (hash-based) con modelos de ML reales
"""

from sentence_transformers import SentenceTransformer
from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import torch
import numpy as np
from typing import List, Union
import logging
import requests
from io import BytesIO

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmbeddingGenerator:
    """
    Generador de embeddings usando modelos de ML reales
    - Texto: all-MiniLM-L6-v2 (384 dimensiones)
    - Imágenes: CLIP ViT-B/32 (512 dimensiones)
    """
    
    def __init__(self):
        logger.info("🔄 Cargando modelos de embeddings...")
        
        # Verificar si hay GPU disponible
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        logger.info(f"📱 Dispositivo: {self.device}")
        
        # Modelo para texto (recomendado por el proyecto)
        self.text_model = SentenceTransformer('all-MiniLM-L6-v2')
        logger.info("✅ Modelo de texto cargado: all-MiniLM-L6-v2 (384 dims)")
        
        if self.device == 'cuda':
            self.text_model = self.text_model.to(self.device)
        
        # Modelo CLIP para imágenes
        try:
            logger.info("🔄 Cargando CLIP para embeddings de imágenes...")
            self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
            self.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
            
            if self.device == 'cuda':
                self.clip_model = self.clip_model.to(self.device)
            
            self.clip_model.eval()  # Modo evaluación
            logger.info("✅ CLIP cargado: clip-vit-base-patch32 (512 dims)")
        except Exception as e:
            logger.error(f"❌ Error cargando CLIP: {e}")
            self.clip_model = None
            self.clip_processor = None
    
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
    
    def generar_embedding_texto_clip(self, texto: str) -> List[float]:
        """
        Genera embedding de texto usando CLIP (para búsqueda texto→imagen)
        
        Args:
            texto: Texto descriptivo (ej: "gafas de sol deportivas negras")
            
        Returns:
            Lista de 512 floats (embedding CLIP normalizado)
        """
        if self.clip_model is None or self.clip_processor is None:
            logger.error("❌ CLIP no está disponible")
            return [0.0] * 512
        
        if not texto or not texto.strip():
            logger.warning("⚠️ Texto vacío")
            return [0.0] * 512
        
        try:
            # Procesar texto con CLIP
            inputs = self.clip_processor(text=[texto], return_tensors="pt", padding=True)
            
            if self.device == 'cuda':
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Generar embedding con CLIP
            with torch.no_grad():
                text_features = self.clip_model.get_text_features(**inputs)
                
                # Normalizar L2
                text_features = text_features / text_features.norm(dim=-1, keepdim=True)
            
            # Convertir a lista
            embedding = text_features.cpu().numpy()[0].tolist()
            
            logger.info(f"✅ Embedding de texto CLIP generado: {len(embedding)} dims")
            return embedding
            
        except Exception as e:
            logger.error(f"❌ Error generando embedding de texto CLIP: {e}")
            return [0.0] * 512
    
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
    
    def generar_embedding_imagen(self, imagen_source: Union[str, Image.Image]) -> List[float]:
        """
        Genera embedding para imagen usando CLIP
        
        Args:
            imagen_source: Puede ser:
                - URL de la imagen (str empezando con http:// o https://)
                - Ruta local al archivo (str)
                - Objeto PIL.Image
            
        Returns:
            Lista de 512 floats (embedding normalizado CLIP)
        """
        if self.clip_model is None or self.clip_processor is None:
            logger.error("❌ CLIP no está disponible")
            return [0.0] * 512
        
        try:
            # Cargar imagen según el tipo de fuente
            if isinstance(imagen_source, str):
                if imagen_source.startswith(('http://', 'https://')):
                    # Descargar desde URL
                    logger.info(f"🔽 Descargando imagen desde URL: {imagen_source[:50]}...")
                    response = requests.get(imagen_source, timeout=10)
                    response.raise_for_status()
                    image = Image.open(BytesIO(response.content)).convert('RGB')
                else:
                    # Cargar desde archivo local
                    logger.info(f"📂 Cargando imagen local: {imagen_source}")
                    image = Image.open(imagen_source).convert('RGB')
            elif isinstance(imagen_source, Image.Image):
                image = imagen_source.convert('RGB')
            else:
                raise ValueError(f"Tipo de imagen no soportado: {type(imagen_source)}")
            
            # Procesar imagen con CLIP
            inputs = self.clip_processor(images=image, return_tensors="pt")
            
            if self.device == 'cuda':
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Generar embedding con CLIP
            with torch.no_grad():
                image_features = self.clip_model.get_image_features(**inputs)
                
                # Normalizar L2
                image_features = image_features / image_features.norm(dim=-1, keepdim=True)
            
            # Convertir a lista
            embedding = image_features.cpu().numpy()[0].tolist()
            
            logger.info(f"✅ Embedding de imagen generado: {len(embedding)} dims")
            return embedding
            
        except requests.RequestException as e:
            logger.error(f"❌ Error descargando imagen: {e}")
            return [0.0] * 512
        except Exception as e:
            logger.error(f"❌ Error generando embedding de imagen: {e}")
            return [0.0] * 512
    
    def generar_embeddings_imagenes_batch(self, imagenes: List[Union[str, Image.Image]], batch_size: int = 8) -> List[List[float]]:
        """
        Genera embeddings para múltiples imágenes (más eficiente)
        
        Args:
            imagenes: Lista de URLs, rutas o imágenes PIL
            batch_size: Tamaño del lote (menor que texto por memoria)
            
        Returns:
            Lista de embeddings CLIP
        """
        if self.clip_model is None or self.clip_processor is None:
            logger.error("❌ CLIP no está disponible")
            return [[0.0] * 512] * len(imagenes)
        
        if not imagenes:
            return []
        
        embeddings_resultado = []
        
        try:
            logger.info(f"🔄 Procesando {len(imagenes)} imágenes en lotes de {batch_size}...")
            
            # Procesar en lotes
            for i in range(0, len(imagenes), batch_size):
                batch = imagenes[i:i + batch_size]
                batch_images = []
                
                # Cargar imágenes del lote
                for img_source in batch:
                    try:
                        if isinstance(img_source, str):
                            if img_source.startswith(('http://', 'https://')):
                                response = requests.get(img_source, timeout=10)
                                response.raise_for_status()
                                img = Image.open(BytesIO(response.content)).convert('RGB')
                            else:
                                img = Image.open(img_source).convert('RGB')
                        elif isinstance(img_source, Image.Image):
                            img = img_source.convert('RGB')
                        else:
                            logger.warning(f"⚠️ Tipo no soportado, usando vector cero")
                            embeddings_resultado.append([0.0] * 512)
                            continue
                        
                        batch_images.append(img)
                        
                    except Exception as e:
                        logger.warning(f"⚠️ Error cargando imagen: {e}")
                        embeddings_resultado.append([0.0] * 512)
                
                if not batch_images:
                    continue
                
                # Procesar lote con CLIP
                inputs = self.clip_processor(images=batch_images, return_tensors="pt", padding=True)
                
                if self.device == 'cuda':
                    inputs = {k: v.to(self.device) for k, v in inputs.items()}
                
                with torch.no_grad():
                    image_features = self.clip_model.get_image_features(**inputs)
                    image_features = image_features / image_features.norm(dim=-1, keepdim=True)
                
                # Convertir a lista
                batch_embeddings = image_features.cpu().numpy().tolist()
                embeddings_resultado.extend(batch_embeddings)
                
                logger.info(f"   Procesado lote {i//batch_size + 1}/{(len(imagenes)-1)//batch_size + 1}")
            
            return embeddings_resultado
            
        except Exception as e:
            logger.error(f"❌ Error en batch de imágenes: {e}")
            return [[0.0] * 512] * len(imagenes)

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


def generar_embedding_imagen(imagen_source: Union[str, Image.Image]) -> List[float]:
    """Función simple para generar un embedding de imagen"""
    generator = get_embedding_generator()
    return generator.generar_embedding_imagen(imagen_source)


def generar_embedding_texto_clip(texto: str) -> List[float]:
    """Función simple para generar un embedding de texto con CLIP (para búsqueda texto→imagen)"""
    generator = get_embedding_generator()
    return generator.generar_embedding_texto_clip(texto)


def generar_embeddings_batch(textos: List[str], batch_size: int = 32) -> List[List[float]]:
    """Función simple para generar embeddings de texto en lote"""
    generator = get_embedding_generator()
    return generator.generar_embeddings_batch(textos, batch_size)


def generar_embeddings_imagenes_batch(imagenes: List[Union[str, Image.Image]], batch_size: int = 8) -> List[List[float]]:
    """Función simple para generar embeddings de imágenes en lote"""
    generator = get_embedding_generator()
    return generator.generar_embeddings_imagenes_batch(imagenes, batch_size)


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
    
    # Prueba 1: Embedding de texto simple
    print("\n1️⃣ Prueba de embedding de texto:")
    texto = "gafas de sol deportivas"
    embedding = generar_embedding(texto)
    print(f"   Texto: '{texto}'")
    print(f"   Dimensiones: {len(embedding)}")
    print(f"   Primeros 5 valores: {embedding[:5]}")
    print(f"   Norma L2: {np.linalg.norm(embedding):.6f} (debe ser ~1.0)")
    
    # Prueba 2: Similitud semántica de texto
    print("\n2️⃣ Prueba de similitud semántica (texto):")
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
    
    # Prueba 3: Embedding de imagen
    print("\n3️⃣ Prueba de embedding de imagen (CLIP):")
    try:
        # Usar una imagen de prueba de internet
        imagen_url = "https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=400"
        embedding_img = generar_embedding_imagen(imagen_url)
        print(f"   URL: {imagen_url[:50]}...")
        print(f"   Dimensiones: {len(embedding_img)}")
        print(f"   Primeros 5 valores: {embedding_img[:5]}")
        print(f"   Norma L2: {np.linalg.norm(embedding_img):.6f} (debe ser ~1.0)")
    except Exception as e:
        print(f"   ⚠️ No se pudo probar CLIP: {e}")
    
    # Prueba 4: Performance
    print("\n4️⃣ Prueba de performance:")
    import time
    
    start = time.time()
    _ = generar_embedding("prueba de velocidad")
    tiempo_single = time.time() - start
    print(f"   Embedding texto individual: {tiempo_single*1000:.2f}ms")
    
    textos_batch = ["texto de prueba"] * 100
    start = time.time()
    _ = generar_embeddings_batch(textos_batch)
    tiempo_batch = time.time() - start
    print(f"   Batch de 100 embeddings texto: {tiempo_batch*1000:.2f}ms")
    print(f"   Promedio por embedding: {tiempo_batch*10:.2f}ms")
    
    print("\n" + "=" * 80)
    print("✅ MÓDULO DE EMBEDDINGS LISTO (Texto + Imágenes)")
    print("=" * 80)
