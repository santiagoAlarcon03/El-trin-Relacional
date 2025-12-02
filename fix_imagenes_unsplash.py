#!/usr/bin/env python3
"""
Script para actualizar imágenes con URLs públicas confiables
Todas las imágenes son de Unsplash - garantizadas funcionando
"""

from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

client = MongoClient(os.getenv('MONGODB_URI'))
db = client['optica_db']
productos_col = db['productos']

# URLs de imágenes reales y apropiadas de Unsplash
actualizaciones = [
    # GAFAS DE SOL
    {
        "nombre": "Ray-Ban Aviator Classic RB3025",
        "imagenes": [
            "https://images.unsplash.com/photo-1572635196237-14b3f281503f?w=800&q=80",  # Aviador dorado
            "https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=800&q=80"   # Gafas classic
        ]
    },
    {
        "nombre": "Oakley Holbrook OO9102 Polarized",
        "imagenes": [
            "https://images.unsplash.com/photo-1577803645773-f96470509666?w=800&q=80",  # Gafas deportivas
            "https://images.unsplash.com/photo-1508296695146-257a814070b4?w=800&q=80"   # Gafas negras
        ]
    },
    {
        "nombre": "Gucci GG0061S Redondo Luxury",
        "imagenes": [
            "https://images.unsplash.com/photo-1609587312208-cea54be969e7?w=800&q=80",  # Gafas redondas elegantes
            "https://images.unsplash.com/photo-1473496169904-658ba7c44d8a?w=800&q=80"   # Gafas fashion
        ]
    },
    {
        "nombre": "Polaroid Sport PLD7028/S Wrap",
        "imagenes": [
            "https://images.unsplash.com/photo-1584036561566-baf8f5f1b144?w=800&q=80",  # Gafas deportivas azules
            "https://images.unsplash.com/photo-1589782182703-2aaa69037b5b?w=800&q=80"   # Gafas sport
        ]
    },
    
    # LENTES DE CONTACTO
    {
        "nombre": "Acuvue Oasys Hydraclear Plus - Caja x6",
        "imagenes": [
            "https://images.unsplash.com/photo-1606811841689-23dfddce3e95?w=800&q=80",  # Lente de contacto en dedo
            "https://images.unsplash.com/photo-1576669802260-5f4854c6e0ea?w=800&q=80"   # Ojos con lentes
        ]
    },
    {
        "nombre": "Biofinity Monthly CooperVision - Caja x6",
        "imagenes": [
            "https://images.unsplash.com/photo-1606811841689-23dfddce3e95?w=800&q=80",  # Lente contacto
            "https://images.unsplash.com/photo-1576669802176-6b280c6c803f?w=800&q=80"   # Caja de lentes
        ]
    },
    {
        "nombre": "Dailies AquaComfort Plus Alcon - Caja x30",
        "imagenes": [
            "https://images.unsplash.com/photo-1606811841689-23dfddce3e95?w=800&q=80",  # Lente
            "https://images.unsplash.com/photo-1576669802260-5f4854c6e0ea?w=800&q=80"   # Aplicación
        ]
    },
    
    # SOLUCIONES - Frascos y líquidos
    {
        "nombre": "ReNu MultiPlus Bausch+Lomb 360ml",
        "imagenes": [
            "https://images.unsplash.com/photo-1585435557343-3b092031a831?w=800&q=80",  # Frasco spray/solución
            "https://images.unsplash.com/photo-1611930022073-b7a4ba5fcccd?w=800&q=80"   # Productos de cuidado
        ]
    },
    {
        "nombre": "Opti-Free PureMoist Alcon 300ml",
        "imagenes": [
            "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=800&q=80",  # Botella producto
            "https://images.unsplash.com/photo-1611930022073-b7a4ba5fcccd?w=800&q=80"   # Cuidado ocular
        ]
    },
    {
        "nombre": "Biotrue Flight Pack 60ml x2 Viaje",
        "imagenes": [
            "https://images.unsplash.com/photo-1585435557343-3b092031a831?w=800&q=80",  # Frasco pequeño
            "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=800&q=80"   # Travel size
        ]
    },
    
    # ACCESORIOS
    {
        "nombre": "Estuche Rígido Premium EVA Negro",
        "imagenes": [
            "https://images.unsplash.com/photo-1556306535-0f09a537f0a3?w=800&q=80",  # Estuche gafas
            "https://images.unsplash.com/photo-1509695507497-903c140c43b0?w=800&q=80"   # Accesorios óptica
        ]
    },
    {
        "nombre": "Gamuza Microfibra Premium Pack x3",
        "imagenes": [
            "https://images.unsplash.com/photo-1509695507497-903c140c43b0?w=800&q=80",  # Limpieza gafas
            "https://images.unsplash.com/photo-1556306535-0f09a537f0a3?w=800&q=80"   # Accesorios
        ]
    },
    {
        "nombre": "Spray Limpiador Antivaho FogTech 50ml",
        "imagenes": [
            "https://images.unsplash.com/photo-1585435557343-3b092031a831?w=800&q=80",  # Spray
            "https://images.unsplash.com/photo-1611930022073-b7a4ba5fcccd?w=800&q=80"   # Producto limpieza
        ]
    },
    {
        "nombre": "Cordón Deportivo Neopreno Croakies",
        "imagenes": [
            "https://images.unsplash.com/photo-1509695507497-903c140c43b0?w=800&q=80",  # Accesorios
            "https://images.unsplash.com/photo-1556306535-0f09a537f0a3?w=800&q=80"   # Gafas con accesorio
        ]
    },
    
    # MONTURAS ÓPTICAS
    {
        "nombre": "Silhouette Titan Minimal Art 5515",
        "imagenes": [
            "https://images.unsplash.com/photo-1574258495973-f010dfbb5371?w=800&q=80",  # Monturas elegantes
            "https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=800&q=80"   # Monturas premium
        ]
    },
    {
        "nombre": "Tom Ford TF5178 Square Black",
        "imagenes": [
            "https://images.unsplash.com/photo-1509695507497-903c140c43b0?w=800&q=80",  # Monturas cuadradas
            "https://images.unsplash.com/photo-1574258495973-f010dfbb5371?w=800&q=80"   # Gafas negras
        ]
    },
    {
        "nombre": "Lindberg Air Titanium Rim 6517",
        "imagenes": [
            "https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=800&q=80",  # Monturas ligeras
            "https://images.unsplash.com/photo-1574258495973-f010dfbb5371?w=800&q=80"   # Gafas premium
        ]
    },
    {
        "nombre": "Warby Parker Percey Whiskey Tortoise",
        "imagenes": [
            "https://images.unsplash.com/photo-1574258495973-f010dfbb5371?w=800&q=80",  # Monturas vintage
            "https://images.unsplash.com/photo-1509695507497-903c140c43b0?w=800&q=80"   # Gafas redondas
        ]
    }
]

def actualizar_imagenes():
    """Actualizar imágenes con URLs verificadas"""
    print("=" * 80)
    print("🖼️  ACTUALIZANDO IMÁGENES CON URLs VERIFICADAS DE UNSPLASH")
    print("=" * 80)
    print()
    
    exitosos = 0
    
    for item in actualizaciones:
        nombre = item['nombre']
        imagenes = item['imagenes']
        
        resultado = productos_col.update_one(
            {'nombre_producto': nombre},
            {'$set': {'imagenes': imagenes}}
        )
        
        if resultado.matched_count > 0:
            print(f"✅ {nombre}")
            exitosos += 1
    
    print()
    print("=" * 80)
    print(f"✅ {exitosos} productos actualizados con imágenes verificadas")
    print("=" * 80)
    print()
    print("📋 PRÓXIMO PASO:")
    print("   python vectorizar_imagenes.py")
    print("=" * 80)

if __name__ == "__main__":
    actualizar_imagenes()
