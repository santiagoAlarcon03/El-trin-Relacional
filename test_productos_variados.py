#!/usr/bin/env python3
"""
Demo rápida del buscador con productos variados
"""

import requests
import sys

# Configurar encoding UTF-8
sys.stdout.reconfigure(encoding='utf-8')

API_URL = "http://localhost:8000/search/text-to-image"

# Consultas de prueba para diferentes categorías
consultas = [
    "gafas de sol estilo aviador doradas",
    "lentes de contacto para ojos secos",
    "solución de limpieza para lentes",
    "estuche rígido protector",
    "monturas de titanio ultra ligeras",
    "spray antivaho"
]

print("=" * 80)
print("🔍 PRUEBA DEL BUSCADOR CON PRODUCTOS VARIADOS")
print("=" * 80)
print()

for i, query in enumerate(consultas, 1):
    print(f"[{i}/{len(consultas)}] 🔎 Buscando: '{query}'")
    
    try:
        response = requests.post(
            API_URL,
            json={"query": query, "limit": 3},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ {data['total_results']} resultados en {data['execution_time_ms']:.0f}ms")
            
            if data['results']:
                top = data['results'][0]
                # Manejar tanto estructura nueva (tipo.categoria) como vieja (categoria)
                content = top.get('content', top)
                if isinstance(content.get('tipo'), dict):
                    categoria = content['tipo'].get('categoria', 'N/A')
                else:
                    categoria = content.get('categoria', 'N/A')
                similitud = top.get('score', 0) * 100
                nombre = content.get('nombre_producto', content.get('nombre', 'N/A'))
                print(f"   🏆 Top: {nombre}")
                print(f"   📦 Categoría: {categoria}")
                print(f"   📊 Similitud: {similitud:.1f}%")
            print()
        else:
            print(f"   ❌ Error {response.status_code}")
            print()
    
    except Exception as e:
        print(f"   ❌ Error: {e}")
        print()

print("=" * 80)
print("✅ Prueba completada")
print("🌐 Abre http://localhost:8000/buscador para probar interactivamente")
print("=" * 80)
