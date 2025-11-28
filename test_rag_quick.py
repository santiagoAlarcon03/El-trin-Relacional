"""
Prueba rápida del endpoint RAG con el nuevo modelo
"""

import requests
import json

BASE_URL = "http://localhost:8000"

print("=" * 80)
print("🧪 PRUEBA RÁPIDA - ENDPOINT RAG")
print("=" * 80)

# Pregunta de prueba
rag_query = {
    "query": "¿Qué gafas tienes disponibles y cuáles recomiendas?",
    "limit": 5,
    "temperature": 0.7
}

print(f"\n💬 Pregunta: '{rag_query['query']}'")
print("-" * 80)

try:
    response = requests.post(
        f"{BASE_URL}/rag",
        json=rag_query,
        timeout=30
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Status: {response.status_code}")
        print(f"⚡ Tiempo: {data['execution_time_ms']:.2f}ms")
        print(f"📚 Fuentes: {data['total_sources']} documentos")
        print(f"🤖 Modelo: {data['model_used']}")
        
        print(f"\n{'=' * 80}")
        print("💬 RESPUESTA DEL LLM:")
        print(f"{'=' * 80}")
        print(data['answer'])
        print(f"{'=' * 80}")
        
        print(f"\n📑 Fuentes principales (Top 3):")
        for i, source in enumerate(data['sources'][:3], 1):
            print(f"\n  {i}. [{source['collection']}] - Score: {source['score']:.4f}")
            content = source['content']
            if source['collection'] == 'productos':
                print(f"     Producto: {content.get('nombre_producto', 'N/A')}")
                print(f"     Marca: {content.get('marca', 'N/A')}")
                print(f"     Precio: ${content.get('precio_venta', 0):,.0f}")
        
        print(f"\n{'=' * 80}")
        print("✅ ENDPOINT RAG FUNCIONANDO CORRECTAMENTE")
        print(f"{'=' * 80}")
    else:
        print(f"❌ Error {response.status_code}")
        print(response.text)

except Exception as e:
    print(f"❌ Error: {e}")
