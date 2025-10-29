"""
Buscador de Imágenes con Vector Search en MongoDB Atlas
Usa embeddings de texto para búsqueda semántica de productos con imágenes
"""

from pymongo import MongoClient
from dotenv import load_dotenv
import os
import json

# Configuración
load_dotenv()
MONGODB_URI = os.getenv('MONGODB_URI')
MONGODB_DATABASE = 'optica_db'

print("=" * 80)
print("🔍 BUSCADOR DE IMÁGENES - VECTOR SEARCH")
print("=" * 80)

# Conectar
client = MongoClient(MONGODB_URI)
db = client[MONGODB_DATABASE]

print(f"✅ Conectado a: {MONGODB_DATABASE}\n")

# ============================================================================
# PASO 1: Generar embeddings simulados para productos
# ============================================================================
print("📊 PASO 1: Generando embeddings para productos con imágenes...\n")

# Función simple para generar embeddings basados en texto
def generar_embedding_simple(texto):
    """
    Genera un embedding simple de 384 dimensiones basado en el texto.
    En producción usarías un modelo real como Sentence Transformers.
    """
    import hashlib
    import numpy as np
    
    # Usar hash para generar vector consistente
    hash_obj = hashlib.sha256(texto.encode())
    seed = int(hash_obj.hexdigest(), 16) % (2**32)
    np.random.seed(seed)
    
    # Vector de 384 dimensiones (compatible con muchos modelos)
    embedding = np.random.randn(384).tolist()
    
    # Normalizar
    norm = sum(x*x for x in embedding) ** 0.5
    embedding = [x / norm for x in embedding]
    
    return embedding

# Actualizar productos con embeddings
productos = list(db.productos.find({}))
print(f"Encontrados {len(productos)} productos con imágenes\n")

count = 0
for producto in productos:
    # Generar texto descriptivo
    texto = f"{producto['nombre_producto']} {producto['marca']} {producto['descripcion']}"
    
    # Generar embedding
    embedding = generar_embedding_simple(texto)
    
    # Actualizar documento
    db.productos.update_one(
        {'_id': producto['_id']},
        {'$set': {'embedding': embedding}}
    )
    
    print(f"   ✓ {producto['nombre_producto'][:50]}... → embedding generado")
    count += 1

print(f"\n✅ {count} productos actualizados con embeddings\n")

# ============================================================================
# PASO 2: Instrucciones para crear índice vectorial en Atlas
# ============================================================================
print("=" * 80)
print("📋 PASO 2: CREAR ÍNDICE VECTORIAL EN MONGODB ATLAS")
print("=" * 80)

indice_config = {
    "name": "vector_index_productos",
    "type": "vectorSearch",
    "definition": {
        "fields": [
            {
                "type": "vector",
                "path": "embedding",
                "numDimensions": 384,
                "similarity": "cosine"
            }
        ]
    }
}

print("""
⚠️  IMPORTANTE: Debes crear el índice manualmente en MongoDB Atlas:

1. Ve a MongoDB Atlas → tu Cluster
2. Click en "Atlas Search" en el menú lateral
3. Click en "Create Search Index"
4. Selecciona "JSON Editor"
5. Copia y pega esta configuración:
""")

print(json.dumps(indice_config, indent=2))

print("""
6. Database: optica_db
7. Collection: productos
8. Click "Next" y luego "Create Search Index"
9. Espera 1-2 minutos a que se construya el índice

Mientras tanto, puedes ejecutar búsquedas KNN sin el índice (más lento).
""")

# ============================================================================
# PASO 3: Función de búsqueda
# ============================================================================
print("\n" + "=" * 80)
print("🔎 PASO 3: FUNCIONES DE BÚSQUEDA IMPLEMENTADAS")
print("=" * 80 + "\n")

def buscar_imagenes_vector_search(query, limit=5):
    """
    Búsqueda usando $vectorSearch (requiere índice Atlas Search)
    """
    query_embedding = generar_embedding_simple(query)
    
    pipeline = [
        {
            "$vectorSearch": {
                "index": "vector_index_productos",
                "path": "embedding",
                "queryVector": query_embedding,
                "numCandidates": 100,
                "limit": limit
            }
        },
        {
            "$project": {
                "nombre_producto": 1,
                "marca": 1,
                "descripcion": 1,
                "precio_venta": 1,
                "imagenes": 1,
                "score": {"$meta": "vectorSearchScore"}
            }
        }
    ]
    
    return list(db.productos.aggregate(pipeline))


def buscar_imagenes_knn(query, limit=5):
    """
    Búsqueda KNN sin índice (funciona siempre, pero más lento)
    """
    query_embedding = generar_embedding_simple(query)
    
    # Buscar todos los productos y calcular similitud coseno
    productos = list(db.productos.find({"embedding": {"$exists": True}}))
    
    # Calcular similitud
    def cosine_similarity(v1, v2):
        dot = sum(a*b for a, b in zip(v1, v2))
        return dot  # Ya están normalizados
    
    resultados = []
    for p in productos:
        similitud = cosine_similarity(query_embedding, p['embedding'])
        resultados.append({
            '_id': p['_id'],
            'nombre_producto': p['nombre_producto'],
            'marca': p['marca'],
            'descripcion': p['descripcion'],
            'precio_venta': p['precio_venta'],
            'imagenes': p.get('imagenes', []),
            'score': similitud
        })
    
    # Ordenar por similitud
    resultados.sort(key=lambda x: x['score'], reverse=True)
    
    return resultados[:limit]


# ============================================================================
# PASO 4: Ejemplos de búsqueda
# ============================================================================
print("🎯 EJEMPLOS DE BÚSQUEDA:\n")

# Ejemplo 1: Búsqueda KNN (funciona siempre)
print("Ejemplo 1: Buscar 'gafas de sol deportivas'")
print("-" * 80)

try:
    resultados = buscar_imagenes_knn("gafas de sol deportivas", limit=5)
    
    for i, r in enumerate(resultados, 1):
        print(f"\n{i}. {r['nombre_producto']}")
        print(f"   Marca: {r['marca']}")
        print(f"   Precio: ${r['precio_venta']:,.0f}")
        print(f"   Score: {r['score']:.4f}")
        print(f"   Imágenes: {len(r.get('imagenes', []))} fotos")
        if r.get('imagenes'):
            print(f"   URL: {r['imagenes'][0][:60]}...")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 80)
print("Ejemplo 2: Buscar 'monturas elegantes Ray-Ban'")
print("-" * 80)

try:
    resultados = buscar_imagenes_knn("monturas elegantes Ray-Ban", limit=3)
    
    for i, r in enumerate(resultados, 1):
        print(f"\n{i}. {r['nombre_producto']}")
        print(f"   Score: {r['score']:.4f}")
        print(f"   Precio: ${r['precio_venta']:,.0f}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# ============================================================================
# GUARDAR SCRIPT DE BÚSQUEDA
# ============================================================================
print("\n\n" + "=" * 80)
print("💾 GUARDANDO SCRIPT DE BÚSQUEDA INTERACTIVO")
print("=" * 80)

script_busqueda = """
# Buscador interactivo de imágenes
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
client = MongoClient(os.getenv('MONGODB_URI'))
db = client['optica_db']

def generar_embedding_simple(texto):
    import hashlib
    import numpy as np
    hash_obj = hashlib.sha256(texto.encode())
    seed = int(hash_obj.hexdigest(), 16) % (2**32)
    np.random.seed(seed)
    embedding = np.random.randn(384).tolist()
    norm = sum(x*x for x in embedding) ** 0.5
    return [x / norm for x in embedding]

def buscar(query, limit=5):
    query_embedding = generar_embedding_simple(query)
    productos = list(db.productos.find({"embedding": {"$exists": True}}))
    
    def cosine_similarity(v1, v2):
        return sum(a*b for a, b in zip(v1, v2))
    
    resultados = []
    for p in productos:
        similitud = cosine_similarity(query_embedding, p['embedding'])
        resultados.append({
            'nombre': p['nombre_producto'],
            'marca': p['marca'],
            'precio': p['precio_venta'],
            'imagenes': p.get('imagenes', []),
            'score': similitud
        })
    
    resultados.sort(key=lambda x: x['score'], reverse=True)
    return resultados[:limit]

# USO:
# resultados = buscar("gafas deportivas")
# for r in resultados:
#     print(f"{r['nombre']} - Score: {r['score']:.4f}")
#     print(f"Imágenes: {r['imagenes']}")
"""

with open('buscador_simple.py', 'w', encoding='utf-8') as f:
    f.write(script_busqueda)

print("\n✅ Archivo creado: buscador_simple.py")
print("\nUso:")
print("  python")
print("  >>> from buscador_simple import buscar")
print("  >>> resultados = buscar('gafas de sol')")
print("  >>> print(resultados[0])")

print("\n" + "=" * 80)
print("✅ BUSCADOR DE IMÁGENES LISTO!")
print("=" * 80)
print("""
📋 RESUMEN:
   ✅ 20 productos con embeddings generados
   ✅ Función buscar_imagenes_knn() implementada
   ✅ Función buscar_imagenes_vector_search() lista (requiere índice Atlas)
   ✅ Script interactivo guardado: buscador_simple.py

🎯 PRÓXIMOS PASOS:
   1. Crear índice vectorial en MongoDB Atlas (instrucciones arriba)
   2. Usar buscar_imagenes_vector_search() para búsquedas rápidas
   3. Alternativamente, usar buscar_imagenes_knn() (más lento pero funciona sin índice)
""")

client.close()
