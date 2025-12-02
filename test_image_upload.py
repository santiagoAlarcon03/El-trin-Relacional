#!/usr/bin/env python3
"""
Test rápido para búsqueda imagen→imagen con archivo
"""

import requests
from pathlib import Path

API_BASE = "http://localhost:8000"

def test_image_search():
    """Probar búsqueda por imagen subiendo archivo"""
    
    # Crear una imagen de prueba simple si no existe
    test_image_path = Path("test_imagen.jpg")
    
    if not test_image_path.exists():
        print("⚠️  No hay imagen de prueba. Usa una imagen existente.")
        print("   Ej: test_image_search('ruta/a/tu/imagen.jpg')")
        return
    
    print(f"📸 Probando búsqueda con imagen: {test_image_path}")
    
    # Preparar request
    with open(test_image_path, 'rb') as f:
        files = {'image': f}
        data = {
            'limit': 5,
            'collection': 'productos'
        }
        
        response = requests.post(
            f"{API_BASE}/search/image",
            files=files,
            data=data
        )
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ Búsqueda exitosa!")
        print(f"   Total resultados: {data['total_results']}")
        print(f"   Tiempo: {data['execution_time_ms']}ms")
        print(f"   Modelo: {data['model_used']}")
        print(f"\n📋 Resultados:")
        
        for i, result in enumerate(data['results'], 1):
            content = result['content']
            print(f"   {i}. {content['nombre_producto']}")
            print(f"      Marca: {content['marca']}")
            print(f"      Similitud: {result['score']*100:.1f}%")
            print()
    else:
        print(f"\n❌ Error {response.status_code}")
        print(f"   {response.text}")

if __name__ == "__main__":
    test_image_search()
