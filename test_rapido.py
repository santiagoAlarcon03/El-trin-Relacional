"""
Test rápido del endpoint texto→imagen
Muestra progreso mientras carga
"""
import requests
import time

print("=" * 80)
print("🧪 TEST RÁPIDO: Búsqueda Texto → Imagen")
print("=" * 80)

# Verificar servidor
print("\n1️⃣ Verificando servidor...")
try:
    response = requests.get("http://localhost:8000/health", timeout=5)
    print(f"   ✅ Servidor activo (Status: {response.status_code})")
except:
    print("   ❌ Servidor no responde")
    print("   💡 Ejecuta en otra terminal: python main.py")
    exit(1)

# Buscar con texto
query = "gafas de sol deportivas"
print(f"\n2️⃣ Buscando: '{query}'")
print("   ⏳ Cargando CLIP... (puede tardar 60-90s la primera vez)")

start = time.time()

try:
    response = requests.post(
        "http://localhost:8000/search/text-to-image",
        json={"query": query, "limit": 3},
        timeout=120  # 2 minutos
    )
    
    elapsed = time.time() - start
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Completado en {elapsed:.1f}s")
        print(f"\n📊 Resultados: {data['total_results']} productos")
        print(f"⚡ Latencia API: {data['execution_time_ms']:.0f}ms")
        print(f"🤖 Modelo: {data['model_used']}")
        
        print(f"\n🏆 Top 3:")
        for i, r in enumerate(data['results'], 1):
            c = r['content']
            print(f"   {i}. {c['nombre_producto']} ({r['score']*100:.1f}%)")
    else:
        print(f"   ❌ Error {response.status_code}")
        print(f"   {response.text}")
        
except requests.Timeout:
    print(f"   ⏱️ Timeout después de 120s")
    print("   💡 CLIP está cargando, intenta de nuevo")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 80)
