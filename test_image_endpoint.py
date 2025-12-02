"""
Prueba rápida del endpoint de búsqueda de imágenes
"""
import requests
import json

BASE_URL = "http://localhost:8000"

print("=" * 80)
print("🧪 PRUEBA RÁPIDA: Endpoint /search/image")
print("=" * 80)

# Imagen de prueba (gafas de sol de Unsplash)
test_image_url = "https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=400"

print(f"\n📷 Imagen de prueba: {test_image_url}")
print("🔄 Enviando request...")

try:
    response = requests.post(
        f"{BASE_URL}/search/image",
        json={
            "image_url": test_image_url,
            "limit": 5,
            "collection": "productos"
        },
        timeout=30
    )
    
    print(f"✅ Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        
        print(f"\n📊 Resultados:")
        print(f"   Total: {data['total_results']}")
        print(f"   Modelo: {data.get('model_used', 'N/A')}")
        print(f"   Tiempo: {data['execution_time_ms']:.2f}ms")
        
        print(f"\n🏆 Top resultados:")
        for i, result in enumerate(data['results'][:3], 1):
            print(f"   {i}. {result['content']['nombre_producto']} - {result['content']['marca']}")
            print(f"      Score: {result['score']:.4f}")
            
        print("\n✅ Endpoint funcionando correctamente!")
    else:
        print(f"\n❌ Error {response.status_code}")
        print(json.dumps(response.json(), indent=2))
        
except Exception as e:
    print(f"\n❌ Error: {str(e)}")

print("\n" + "=" * 80)
