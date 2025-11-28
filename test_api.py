"""
Script de prueba para la API REST
Valida que todos los componentes estén funcionando
"""

import os
from dotenv import load_dotenv

print("=" * 80)
print("🧪 VALIDACIÓN PRE-INICIO DE API")
print("=" * 80)

load_dotenv()

# Test 1: Variables de entorno
print("\n1️⃣ Verificando variables de entorno...")
mongodb_uri = os.getenv('MONGODB_URI')
groq_key = os.getenv('GROQ_API_KEY')

if mongodb_uri:
    print("   ✅ MONGODB_URI configurada")
else:
    print("   ❌ MONGODB_URI NO encontrada")

if groq_key and groq_key != "tu_api_key_aqui":
    print("   ✅ GROQ_API_KEY configurada")
else:
    print("   ⚠️ GROQ_API_KEY NO configurada (necesaria para /rag)")
    print("      Configúrala en .env antes de usar el endpoint RAG")

# Test 2: Conexión a MongoDB
print("\n2️⃣ Probando conexión a MongoDB...")
try:
    from pymongo import MongoClient
    client = MongoClient(mongodb_uri)
    db = client['optica_db']
    db.command('ping')
    print("   ✅ Conexión a MongoDB exitosa")
    
    # Contar documentos con embeddings
    count = 0
    for col_name in ['productos', 'clientes', 'examenes']:
        count += db[col_name].count_documents({'embedding': {'$exists': True}})
    print(f"   ✅ Encontrados {count} documentos vectorizados")
    client.close()
except Exception as e:
    print(f"   ❌ Error en MongoDB: {e}")

# Test 3: Modelo de embeddings
print("\n3️⃣ Cargando modelo de embeddings...")
try:
    from rag.embeddings import generar_embedding
    test_embedding = generar_embedding("prueba")
    print(f"   ✅ Modelo cargado (dimensión: {len(test_embedding)})")
except Exception as e:
    print(f"   ❌ Error cargando modelo: {e}")

# Test 4: Cliente Groq (opcional)
print("\n4️⃣ Validando cliente Groq...")
if groq_key and groq_key != "tu_api_key_aqui":
    try:
        from llm.groq_client import get_groq_client
        client = get_groq_client()
        print("   ✅ Cliente Groq inicializado")
    except Exception as e:
        print(f"   ❌ Error con Groq: {e}")
else:
    print("   ⚠️ Saltando (API key no configurada)")

# Test 5: Importar routers
print("\n5️⃣ Verificando routers de FastAPI...")
try:
    from api.routers import search, rag
    print("   ✅ Routers importados correctamente")
except Exception as e:
    print(f"   ❌ Error importando routers: {e}")

# Resumen
print("\n" + "=" * 80)
print("📊 RESUMEN DE VALIDACIÓN")
print("=" * 80)
print("""
✅ Componentes listos para:
   • GET  /health        - Health check
   • GET  /collections   - Lista de colecciones
   • POST /search        - Búsqueda vectorial

⚠️  Para usar POST /rag necesitas:
   • Configurar GROQ_API_KEY en .env
   • Obtener key gratis en: https://console.groq.com/keys

🚀 Para iniciar el servidor:
   python -m uvicorn api.main:app --reload --port 8000

📚 Documentación interactiva:
   http://localhost:8000/docs
""")
print("=" * 80)
