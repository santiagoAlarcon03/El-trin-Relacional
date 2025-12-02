"""
Demo interactiva del buscador de imágenes
Prueba con diferentes URLs de gafas y ve los resultados
"""
import requests
import json

BASE_URL = "http://localhost:8000"

# URLs de prueba (diferentes tipos de gafas)
IMAGENES_PRUEBA = {
    "1": {
        "url": "https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=400",
        "descripcion": "Gafas de sol clásicas"
    },
    "2": {
        "url": "https://images.unsplash.com/photo-1556306535-0f09a537f0a3?w=400",
        "descripcion": "Monturas ópticas modernas"
    },
    "3": {
        "url": "https://images.unsplash.com/photo-1574258495973-f010dfbb5371?w=400",
        "descripcion": "Gafas formuladas elegantes"
    },
    "4": {
        "url": "https://images.unsplash.com/photo-1473496169904-658ba7c44d8a?w=400",
        "descripcion": "Gafas deportivas"
    },
    "5": {
        "url": "https://images.unsplash.com/photo-1509695507497-903c140c43b0?w=400",
        "descripcion": "Gafas aviador vintage"
    }
}

def buscar_imagen(url, limit=5):
    """Busca productos similares a una imagen"""
    print(f"\n{'=' * 80}")
    print(f"🔍 BUSCANDO PRODUCTOS SIMILARES")
    print(f"{'=' * 80}")
    print(f"\n📷 Imagen: {url}")
    print(f"⏳ Procesando con CLIP...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/search/image",
            json={
                "image_url": url,
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
            print(f"📊 Total resultados: {data['total_results']}")
            
            if data['total_results'] > 0:
                print(f"\n{'─' * 80}")
                print(f"🏆 TOP {min(limit, data['total_results'])} PRODUCTOS MÁS SIMILARES:")
                print(f"{'─' * 80}\n")
                
                for i, result in enumerate(data['results'], 1):
                    content = result['content']
                    score_pct = result['score'] * 100
                    
                    # Barra de progreso visual
                    bar_length = int(score_pct / 5)
                    bar = '█' * bar_length + '░' * (20 - bar_length)
                    
                    print(f"{i}. {content['nombre_producto']}")
                    print(f"   Marca: {content['marca']}")
                    print(f"   Precio: ${content['precio_venta']}")
                    print(f"   Similitud: {bar} {score_pct:.1f}%")
                    
                    if i < len(data['results']):
                        print()
            else:
                print("\n⚠️  No se encontraron productos similares")
                
        else:
            print(f"\n❌ Error {response.status_code}")
            print(json.dumps(response.json(), indent=2))
            
    except requests.exceptions.Timeout:
        print("\n❌ Timeout - La búsqueda tardó más de 30 segundos")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
    
    print(f"\n{'=' * 80}\n")


def menu_interactivo():
    """Menú para seleccionar imágenes de prueba"""
    print("\n" + "=" * 80)
    print("🖼️  DEMO BUSCADOR DE IMÁGENES - Óptica El-trin-Relacional")
    print("=" * 80)
    print("\nSelecciona una imagen de prueba:\n")
    
    for key, img in IMAGENES_PRUEBA.items():
        print(f"  [{key}] {img['descripcion']}")
        print(f"      {img['url'][:70]}...")
        print()
    
    print(f"  [0] Usar URL personalizada")
    print(f"  [Q] Salir\n")
    
    opcion = input("👉 Opción: ").strip().upper()
    
    if opcion == 'Q':
        print("\n👋 ¡Hasta luego!")
        return None
    elif opcion == '0':
        url = input("\n📷 Ingresa la URL de la imagen: ").strip()
        if url:
            return url
        else:
            print("❌ URL inválida")
            return menu_interactivo()
    elif opcion in IMAGENES_PRUEBA:
        img = IMAGENES_PRUEBA[opcion]
        print(f"\n✅ Seleccionado: {img['descripcion']}")
        return img['url']
    else:
        print("❌ Opción inválida")
        return menu_interactivo()


if __name__ == "__main__":
    while True:
        url = menu_interactivo()
        
        if url is None:
            break
        
        buscar_imagen(url, limit=5)
        
        continuar = input("¿Buscar otra imagen? (S/n): ").strip().upper()
        if continuar == 'N':
            print("\n👋 ¡Hasta luego!")
            break
