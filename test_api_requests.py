"""
Script de pruebas para los endpoints de la API
Ejecuta requests de ejemplo a todos los endpoints
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

print("=" * 80)
print("🧪 PRUEBAS DE API REST - SISTEMA RAG")
print("=" * 80)
print(f"\n🌐 Servidor: {BASE_URL}")
print(f"📚 Docs: {BASE_URL}/docs\n")

# ============================================================================
# TEST 1: Health Check
# ============================================================================
print("\n" + "=" * 80)
print("TEST 1: GET /health - Health Check")
print("=" * 80)

try:
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Estado: {data['status']}")
        print(f"✅ Versión: {data['version']}")
        print(f"✅ MongoDB: {'Conectada' if data['database_connected'] else 'Desconectada'}")
        print(f"✅ Embeddings: {'Cargados' if data['embeddings_model_loaded'] else 'No cargados'}")
    else:
        print(f"❌ Error: {response.text}")
except Exception as e:
    print(f"❌ Error: {e}")

# ============================================================================
# TEST 2: Listar Colecciones
# ============================================================================
print("\n" + "=" * 80)
print("TEST 2: GET /collections - Listar Colecciones")
print("=" * 80)

try:
    response = requests.get(f"{BASE_URL}/collections")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"\n📊 Total colecciones: {data['total_collections']}")
        print(f"📄 Total documentos: {data['total_documents']}\n")
        print("Colecciones disponibles:")
        for col in data['collections'][:5]:  # Mostrar solo las primeras 5
            print(f"  • {col['name']:20} → {col['documents_with_embeddings']:3}/{col['total_documents']:3} vectorizados ({col['vectorization_percentage']:.1f}%)")
    else:
        print(f"❌ Error: {response.text}")
except Exception as e:
    print(f"❌ Error: {e}")

# ============================================================================
# TEST 3: Búsqueda Vectorial
# ============================================================================
print("\n" + "=" * 80)
print("TEST 3: POST /search - Búsqueda Vectorial")
print("=" * 80)

queries = [
    {"query": "gafas deportivas", "limit": 3, "collection": "productos"},
    {"query": "María", "limit": 3, "collection": "clientes"},
    {"query": "examen de vista", "limit": 3, "collection": None}  # Buscar en todas
]

for i, query_data in enumerate(queries, 1):
    print(f"\n🔍 Query {i}: '{query_data['query']}' (colección: {query_data['collection'] or 'todas'})")
    print("-" * 80)
    
    try:
        response = requests.post(
            f"{BASE_URL}/search",
            json=query_data
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Encontrados: {data['total_results']} resultados")
            print(f"⚡ Tiempo: {data['execution_time_ms']:.2f}ms")
            
            for j, result in enumerate(data['results'], 1):
                print(f"\n  {j}. [Score: {result['score']:.4f}] {result['collection']}")
                content = result['content']
                
                # Mostrar campos relevantes según colección
                if result['collection'] == 'productos':
                    print(f"     {content.get('nombre_producto', 'N/A')} - {content.get('marca', 'N/A')}")
                    print(f"     Precio: ${content.get('precio_venta', 0):,.0f}")
                elif result['collection'] in ['clientes', 'asesores']:
                    print(f"     {content.get('nombre', '')} {content.get('apellido', '')}")
                    print(f"     Email: {content.get('email', 'N/A')}")
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
    
    except Exception as e:
        print(f"❌ Error: {e}")
    
    time.sleep(0.5)  # Pequeña pausa entre requests

# ============================================================================
# TEST 4: Sistema RAG Completo
# ============================================================================
print("\n\n" + "=" * 80)
print("TEST 4: POST /rag - Sistema RAG Completo")
print("=" * 80)

rag_queries = [
    {
        "query": "¿Qué gafas recomiendas para deportes?",
        "limit": 5,
        "temperature": 0.7
    },
    {
        "query": "¿Cuántos clientes se llaman María?",
        "limit": 5,
        "temperature": 0.5
    }
]

for i, rag_query in enumerate(rag_queries, 1):
    print(f"\n💬 Pregunta {i}: '{rag_query['query']}'")
    print("-" * 80)
    
    try:
        response = requests.post(
            f"{BASE_URL}/rag",
            json=rag_query
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Respuesta generada")
            print(f"⚡ Tiempo: {data['execution_time_ms']:.2f}ms")
            print(f"📚 Fuentes: {data['total_sources']} documentos")
            print(f"\n🤖 RESPUESTA DEL LLM:")
            print("-" * 80)
            print(data['answer'])
            print("-" * 80)
            
            print(f"\n📑 Fuentes utilizadas:")
            for j, source in enumerate(data['sources'][:3], 1):  # Mostrar top 3
                print(f"  {j}. [{source['collection']}] Score: {source['score']:.4f}")
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
    
    except Exception as e:
        print(f"❌ Error: {e}")
    
    time.sleep(1)  # Pausa entre requests RAG

# ============================================================================
# RESUMEN FINAL
# ============================================================================
print("\n\n" + "=" * 80)
print("✅ PRUEBAS COMPLETADAS")
print("=" * 80)
print("""
📊 ENDPOINTS PROBADOS:

✅ GET  /health       - Health check del sistema
✅ GET  /collections  - Lista de colecciones disponibles
✅ POST /search       - Búsqueda vectorial semántica
✅ POST /rag          - Sistema RAG completo (Retrieval + LLM)

🎯 PRÓXIMOS PASOS:

1. Prueba la interfaz interactiva: http://localhost:8000/docs
2. Experimenta con diferentes queries
3. Ajusta parámetros (limit, temperature, collection)
4. Integra la API en tu aplicación

📚 DOCUMENTACIÓN:
   • Swagger UI: http://localhost:8000/docs
   • ReDoc: http://localhost:8000/redoc
""")
print("=" * 80)
