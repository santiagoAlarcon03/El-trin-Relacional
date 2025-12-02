"""
Demo del buscador texto→imagen
Muestra resultados con visualización de URLs de imágenes
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def buscar_por_texto(query, limit=5):
    """Busca imágenes mediante descripción de texto"""
    print("=" * 80)
    print(f"🔍 BÚSQUEDA TEXTO → IMAGEN")
    print("=" * 80)
    print(f"\n📝 Consulta: '{query}'")
    print("⏳ Procesando con CLIP...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/search/text-to-image",
            json={
                "query": query,
                "limit": limit,
                "collection": "productos"
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"\n✅ Búsqueda completada")
            print(f"⚡ Tiempo: {data['execution_time_ms']:.2f}ms")
            print(f"🤖 Modelo: {data['model_used']}")
            print(f"📊 Total: {data['total_results']} productos")
            
            if data['total_results'] > 0:
                print(f"\n{'─' * 80}")
                print(f"🏆 TOP {min(limit, data['total_results'])} PRODUCTOS:")
                print(f"{'─' * 80}\n")
                
                for i, result in enumerate(data['results'], 1):
                    content = result['content']
                    score = result['score'] * 100
                    
                    # Barra visual
                    bar_length = int(score / 5)
                    bar = '█' * bar_length + '░' * (20 - bar_length)
                    
                    print(f"{i}. {content['nombre_producto']}")
                    print(f"   Marca: {content['marca']}")
                    print(f"   Precio: ${content['precio_venta']}")
                    print(f"   Similitud: {bar} {score:.1f}%")
                    
                    # Mostrar URLs de imágenes
                    imagenes = content.get('imagenes', [])
                    if imagenes:
                        print(f"   🖼️  Imágenes ({len(imagenes)}):")
                        for j, img_url in enumerate(imagenes[:2], 1):
                            print(f"      {j}. {img_url}")
                    print()
            else:
                print("\n⚠️  No se encontraron productos similares")
                
        else:
            print(f"\n❌ Error {response.status_code}")
            print(json.dumps(response.json(), indent=2))
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
    
    print("=" * 80 + "\n")


if __name__ == "__main__":
    # Consultas de prueba
    queries = [
        "gafas de sol deportivas negras",
        "monturas elegantes para oficina",
        "lentes aviador clásicos",
    ]
    
    print("\n" + "=" * 80)
    print("🖼️  DEMO BUSCADOR TEXTO → IMAGEN")
    print("=" * 80)
    print("\nBuscando productos mediante descripciones de texto...\n")
    
    for query in queries:
        buscar_por_texto(query, limit=3)
        input("Presiona Enter para continuar...")
