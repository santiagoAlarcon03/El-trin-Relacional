"""
Script para verificar índices creados en MongoDB Atlas
"""

from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Configuración
load_dotenv()
MONGODB_URI = os.getenv('MONGODB_URI')
MONGODB_DATABASE = 'optica_db'

print("=" * 80)
print("🔍 VERIFICANDO ÍNDICES EN MONGODB ATLAS")
print("=" * 80)

# Conectar
client = MongoClient(MONGODB_URI)
db = client[MONGODB_DATABASE]

colecciones = ['catalogos', 'clientes', 'asesores', 'especialistas', 'proveedores', 
               'laboratorios', 'suministros', 'productos', 'citas', 'examenes', 'ventas']

print(f"✅ Conectado a: {MONGODB_DATABASE}\n")

total_indices = 0

for coleccion in colecciones:
    print(f"📋 Colección: {coleccion}")
    indices = list(db[coleccion].list_indexes())
    
    if len(indices) == 0:
        print(f"   ❌ Sin índices")
    else:
        for idx in indices:
            nombre = idx.get('name', 'N/A')
            keys = idx.get('key', {})
            unique = '🔑 UNIQUE' if idx.get('unique', False) else ''
            sparse = '⚡ SPARSE' if idx.get('sparse', False) else ''
            
            # Formato de las keys
            keys_str = ', '.join([f"{k}: {v}" for k, v in keys.items()])
            
            print(f"   ✓ {nombre:<25} | {keys_str:<40} {unique} {sparse}")
            total_indices += 1
    
    print()

print("=" * 80)
print(f"✅ TOTAL ÍNDICES ENCONTRADOS: {total_indices}")
print("=" * 80)

# Comparar con lo esperado
esperados = {
    'catalogos': 1,  # solo _id
    'clientes': 6,
    'asesores': 5,
    'especialistas': 6,
    'proveedores': 5,
    'laboratorios': 4,
    'suministros': 7,
    'productos': 10,
    'citas': 9,
    'examenes': 8,
    'ventas': 11
}

print("\n📊 COMPARACIÓN CON ÍNDICES ESPERADOS:\n")
for col in colecciones:
    indices = list(db[col].list_indexes())
    actual = len(indices)
    esperado = esperados[col]
    estado = "✅" if actual == esperado else "⚠️"
    
    print(f"   {estado} {col:<20} | Actual: {actual:2d} | Esperado: {esperado:2d}")

client.close()
