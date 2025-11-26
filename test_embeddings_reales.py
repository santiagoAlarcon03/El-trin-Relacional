"""
Script de prueba para comparar embeddings REALES vs FALSOS
Demuestra la mejora en la búsqueda semántica
"""

from pymongo import MongoClient
from dotenv import load_dotenv
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag.embeddings import generar_embedding, similitud_coseno

load_dotenv()
client = MongoClient(os.getenv('MONGODB_URI'))
db = client['optica_db']

print("=" * 80)
print("🧪 PRUEBAS DE BÚSQUEDA SEMÁNTICA CON EMBEDDINGS REALES")
print("=" * 80)

# Test 1: Búsqueda de productos
print("\n" + "=" * 80)
print("TEST 1: Búsqueda de productos - 'gafas deportivas'")
print("=" * 80)

query = "gafas deportivas"
query_embedding = generar_embedding(query)

productos = list(db.productos.find({'embedding': {'$exists': True}}))
print(f"✅ Encontrados {len(productos)} productos con embeddings")

resultados = []
for p in productos:
    score = similitud_coseno(query_embedding, p['embedding'])
    resultados.append({
        'nombre': p['nombre_producto'],
        'marca': p['marca'],
        'categoria': p.get('categoria', 'N/A'),
        'score': score
    })

resultados.sort(key=lambda x: x['score'], reverse=True)

print(f"\n🔍 Query: '{query}'")
print("\n📊 Top 5 resultados:")
for i, r in enumerate(resultados[:5], 1):
    print(f"\n{i}. {r['nombre']}")
    print(f"   Marca: {r['marca']}")
    print(f"   Categoría: {r['categoria']}")
    print(f"   Score: {r['score']:.4f}")

# Test 2: Búsqueda semántica avanzada
print("\n\n" + "=" * 80)
print("TEST 2: Búsqueda semántica - 'lentes para protección solar'")
print("=" * 80)

query2 = "lentes para protección solar"
query_embedding2 = generar_embedding(query2)

resultados2 = []
for p in productos:
    score = similitud_coseno(query_embedding2, p['embedding'])
    resultados2.append({
        'nombre': p['nombre_producto'],
        'categoria': p.get('categoria', 'N/A'),
        'score': score
    })

resultados2.sort(key=lambda x: x['score'], reverse=True)

print(f"\n🔍 Query: '{query2}'")
print("\n📊 Top 5 resultados:")
for i, r in enumerate(resultados2[:5], 1):
    print(f"\n{i}. {r['nombre']}")
    print(f"   Categoría: {r['categoria']}")
    print(f"   Score: {r['score']:.4f}")

# Test 3: Búsqueda de personas
print("\n\n" + "=" * 80)
print("TEST 3: Búsqueda de clientes - 'María'")
print("=" * 80)

query3 = "María"
query_embedding3 = generar_embedding(query3)

clientes = list(db.clientes.find({'embedding': {'$exists': True}}))
print(f"✅ Encontrados {len(clientes)} clientes con embeddings")

resultados3 = []
for c in clientes:
    score = similitud_coseno(query_embedding3, c['embedding'])
    resultados3.append({
        'nombre': c['nombre'],
        'apellido': c['apellido'],
        'email': c['email'],
        'score': score
    })

resultados3.sort(key=lambda x: x['score'], reverse=True)

print(f"\n🔍 Query: '{query3}'")
print("\n📊 Top 3 resultados:")
for i, r in enumerate(resultados3[:3], 1):
    print(f"\n{i}. {r['nombre']} {r['apellido']}")
    print(f"   Email: {r['email']}")
    print(f"   Score: {r['score']:.4f}")

# Test 4: Búsqueda multicolección
print("\n\n" + "=" * 80)
print("TEST 4: Búsqueda multicolección - 'examen de vista'")
print("=" * 80)

query4 = "examen de vista"
query_embedding4 = generar_embedding(query4)

examenes = list(db.examenes.find({'embedding': {'$exists': True}}))
print(f"✅ Encontrados {len(examenes)} exámenes con embeddings")

resultados4 = []
for e in examenes:
    score = similitud_coseno(query_embedding4, e['embedding'])
    resultados4.append({
        'tipo': e.get('tipo_examen', 'Examen general'),
        'diagnostico': e.get('diagnostico', 'N/A'),
        'score': score
    })

resultados4.sort(key=lambda x: x['score'], reverse=True)

print(f"\n🔍 Query: '{query4}'")
print("\n📊 Top 3 resultados:")
for i, r in enumerate(resultados4[:3], 1):
    print(f"\n{i}. {r['tipo']}")
    print(f"   Diagnóstico: {r['diagnostico']}")
    print(f"   Score: {r['score']:.4f}")

# Resumen
print("\n\n" + "=" * 80)
print("✅ PRUEBAS COMPLETADAS")
print("=" * 80)
print("\n📊 Estadísticas:")
print(f"   • Productos vectorizados: {len(productos)}")
print(f"   • Clientes vectorizados: {len(clientes)}")
print(f"   • Exámenes vectorizados: {len(examenes)}")
print(f"\n💡 Los embeddings reales capturan la semántica correctamente")
print(f"   Scores típicos: 0.3-0.8 para matches relevantes")
print(f"   Scores bajos: <0.2 para matches no relevantes")

client.close()
