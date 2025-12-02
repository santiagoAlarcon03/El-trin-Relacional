#!/usr/bin/env python3
"""
Actualizar TODOS los productos (viejos y nuevos) con imágenes apropiadas
"""

from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

client = MongoClient(os.getenv('MONGODB_URI'))
db = client['optica_db']
productos_col = db['productos']

# Actualizaciones para TODOS los productos
actualizaciones_completas = [
    # PRODUCTOS VIEJOS - Actualizar con imágenes apropiadas
    {
        "nombre": "Arnette Monturas oftálmicas Modelo-1",
        "imagenes": [
            "https://images.unsplash.com/photo-1574258495973-f010dfbb5371?w=800&q=80",  # Monturas
            "https://images.unsplash.com/photo-1509695507497-903c140c43b0?w=800&q=80"   # Gafas
        ]
    },
    {
        "nombre": "Prada Gafas formuladas Modelo-2",
        "imagenes": [
            "https://images.unsplash.com/photo-1574258495973-f010dfbb5371?w=800&q=80",
            "https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=800&q=80"
        ]
    },
    {
        "nombre": "Persol Lentes de contacto Modelo-3",
        "imagenes": [
            "https://images.unsplash.com/photo-1606811841689-23dfddce3e95?w=800&q=80",
            "https://images.unsplash.com/photo-1576669802260-5f4854c6e0ea?w=800&q=80"
        ]
    },
    {
        "nombre": "Prada Lentes de contacto Modelo-4",
        "imagenes": [
            "https://images.unsplash.com/photo-1606811841689-23dfddce3e95?w=800&q=80",
            "https://images.unsplash.com/photo-1576669802176-6b280c6c803f?w=800&q=80"
        ]
    },
    {
        "nombre": "Oakley Monturas oftálmicas Modelo-5",
        "imagenes": [
            "https://images.unsplash.com/photo-1574258495973-f010dfbb5371?w=800&q=80",
            "https://images.unsplash.com/photo-1509695507497-903c140c43b0?w=800&q=80"
        ]
    },
    {
        "nombre": "Vogue Monturas oftálmicas Modelo-6",
        "imagenes": [
            "https://images.unsplash.com/photo-1574258495973-f010dfbb5371?w=800&q=80",
            "https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=800&q=80"
        ]
    },
    {
        "nombre": "Prada Monturas oftálmicas Modelo-7",
        "imagenes": [
            "https://images.unsplash.com/photo-1574258495973-f010dfbb5371?w=800&q=80",
            "https://images.unsplash.com/photo-1509695507497-903c140c43b0?w=800&q=80"
        ]
    },
    {
        "nombre": "Ray-Ban Lentes de contacto Modelo-8",
        "imagenes": [
            "https://images.unsplash.com/photo-1606811841689-23dfddce3e95?w=800&q=80",
            "https://images.unsplash.com/photo-1576669802260-5f4854c6e0ea?w=800&q=80"
        ]
    },
    {
        "nombre": "Police Monturas oftálmicas Modelo-9",
        "imagenes": [
            "https://images.unsplash.com/photo-1574258495973-f010dfbb5371?w=800&q=80",
            "https://images.unsplash.com/photo-1509695507497-903c140c43b0?w=800&q=80"
        ]
    },
    {
        "nombre": "Prada Lentes de contacto Modelo-10",
        "imagenes": [
            "https://images.unsplash.com/photo-1606811841689-23dfddce3e95?w=800&q=80",
            "https://images.unsplash.com/photo-1576669802176-6b280c6c803f?w=800&q=80"
        ]
    },
    {
        "nombre": "Carrera Lentes de contacto Modelo-11",
        "imagenes": [
            "https://images.unsplash.com/photo-1606811841689-23dfddce3e95?w=800&q=80",
            "https://images.unsplash.com/photo-1576669802260-5f4854c6e0ea?w=800&q=80"
        ]
    },
    {
        "nombre": "Vogue Gafas formuladas Modelo-12",
        "imagenes": [
            "https://images.unsplash.com/photo-1574258495973-f010dfbb5371?w=800&q=80",
            "https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=800&q=80"
        ]
    },
    {
        "nombre": "Persol Monturas oftálmicas Modelo-13",
        "imagenes": [
            "https://images.unsplash.com/photo-1574258495973-f010dfbb5371?w=800&q=80",
            "https://images.unsplash.com/photo-1509695507497-903c140c43b0?w=800&q=80"
        ]
    },
    {
        "nombre": "Carrera Lentes de contacto Modelo-14",
        "imagenes": [
            "https://images.unsplash.com/photo-1606811841689-23dfddce3e95?w=800&q=80",
            "https://images.unsplash.com/photo-1576669802260-5f4854c6e0ea?w=800&q=80"
        ]
    },
    {
        "nombre": "Oakley Gafas formuladas Modelo-15",
        "imagenes": [
            "https://images.unsplash.com/photo-1574258495973-f010dfbb5371?w=800&q=80",
            "https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=800&q=80"
        ]
    },
    {
        "nombre": "Gucci Gafas de sol Modelo-16",
        "imagenes": [
            "https://images.unsplash.com/photo-1572635196237-14b3f281503f?w=800&q=80",
            "https://images.unsplash.com/photo-1609587312208-cea54be969e7?w=800&q=80"
        ]
    },
    {
        "nombre": "Ray-Ban Lentes de contacto Modelo-17",
        "imagenes": [
            "https://images.unsplash.com/photo-1606811841689-23dfddce3e95?w=800&q=80",
            "https://images.unsplash.com/photo-1576669802176-6b280c6c803f?w=800&q=80"
        ]
    },
    {
        "nombre": "Persol Gafas formuladas Modelo-18",
        "imagenes": [
            "https://images.unsplash.com/photo-1574258495973-f010dfbb5371?w=800&q=80",
            "https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=800&q=80"
        ]
    },
    {
        "nombre": "Oakley Monturas oftálmicas Modelo-19",
        "imagenes": [
            "https://images.unsplash.com/photo-1577803645773-f96470509666?w=800&q=80",
            "https://images.unsplash.com/photo-1508296695146-257a814070b4?w=800&q=80"
        ]
    },
    {
        "nombre": "Prada Lentes de contacto Modelo-20",
        "imagenes": [
            "https://images.unsplash.com/photo-1606811841689-23dfddce3e95?w=800&q=80",
            "https://images.unsplash.com/photo-1576669802260-5f4854c6e0ea?w=800&q=80"
        ]
    },
    
    # PRODUCTOS NUEVOS (ya los tienes actualizados, pero por completitud)
    {
        "nombre": "Ray-Ban Aviator Classic RB3025",
        "imagenes": [
            "https://images.unsplash.com/photo-1572635196237-14b3f281503f?w=800&q=80",
            "https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=800&q=80"
        ]
    },
    {
        "nombre": "Oakley Holbrook OO9102 Polarized",
        "imagenes": [
            "https://images.unsplash.com/photo-1577803645773-f96470509666?w=800&q=80",
            "https://images.unsplash.com/photo-1508296695146-257a814070b4?w=800&q=80"
        ]
    },
    {
        "nombre": "Gucci GG0061S Redondo Luxury",
        "imagenes": [
            "https://images.unsplash.com/photo-1609587312208-cea54be969e7?w=800&q=80",
            "https://images.unsplash.com/photo-1473496169904-658ba7c44d8a?w=800&q=80"
        ]
    },
    {
        "nombre": "Polaroid Sport PLD7028/S Wrap",
        "imagenes": [
            "https://images.unsplash.com/photo-1584036561566-baf8f5f1b144?w=800&q=80",
            "https://images.unsplash.com/photo-1589782182703-2aaa69037b5b?w=800&q=80"
        ]
    },
    {
        "nombre": "Acuvue Oasys Hydraclear Plus - Caja x6",
        "imagenes": [
            "https://images.unsplash.com/photo-1606811841689-23dfddce3e95?w=800&q=80",
            "https://images.unsplash.com/photo-1576669802260-5f4854c6e0ea?w=800&q=80"
        ]
    },
    {
        "nombre": "Biofinity Monthly CooperVision - Caja x6",
        "imagenes": [
            "https://images.unsplash.com/photo-1606811841689-23dfddce3e95?w=800&q=80",
            "https://images.unsplash.com/photo-1576669802176-6b280c6c803f?w=800&q=80"
        ]
    },
    {
        "nombre": "Dailies AquaComfort Plus Alcon - Caja x30",
        "imagenes": [
            "https://images.unsplash.com/photo-1606811841689-23dfddce3e95?w=800&q=80",
            "https://images.unsplash.com/photo-1576669802260-5f4854c6e0ea?w=800&q=80"
        ]
    },
    {
        "nombre": "ReNu MultiPlus Bausch+Lomb 360ml",
        "imagenes": [
            "https://images.unsplash.com/photo-1585435557343-3b092031a831?w=800&q=80",
            "https://images.unsplash.com/photo-1611930022073-b7a4ba5fcccd?w=800&q=80"
        ]
    },
    {
        "nombre": "Opti-Free PureMoist Alcon 300ml",
        "imagenes": [
            "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=800&q=80",
            "https://images.unsplash.com/photo-1611930022073-b7a4ba5fcccd?w=800&q=80"
        ]
    },
    {
        "nombre": "Biotrue Flight Pack 60ml x2 Viaje",
        "imagenes": [
            "https://images.unsplash.com/photo-1585435557343-3b092031a831?w=800&q=80",
            "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=800&q=80"
        ]
    },
    {
        "nombre": "Estuche Rígido Premium EVA Negro",
        "imagenes": [
            "https://images.unsplash.com/photo-1556306535-0f09a537f0a3?w=800&q=80",
            "https://images.unsplash.com/photo-1509695507497-903c140c43b0?w=800&q=80"
        ]
    },
    {
        "nombre": "Gamuza Microfibra Premium Pack x3",
        "imagenes": [
            "https://images.unsplash.com/photo-1509695507497-903c140c43b0?w=800&q=80",
            "https://images.unsplash.com/photo-1556306535-0f09a537f0a3?w=800&q=80"
        ]
    },
    {
        "nombre": "Spray Limpiador Antivaho FogTech 50ml",
        "imagenes": [
            "https://images.unsplash.com/photo-1585435557343-3b092031a831?w=800&q=80",
            "https://images.unsplash.com/photo-1611930022073-b7a4ba5fcccd?w=800&q=80"
        ]
    },
    {
        "nombre": "Cordón Deportivo Neopreno Croakies",
        "imagenes": [
            "https://images.unsplash.com/photo-1509695507497-903c140c43b0?w=800&q=80",
            "https://images.unsplash.com/photo-1556306535-0f09a537f0a3?w=800&q=80"
        ]
    },
    {
        "nombre": "Silhouette Titan Minimal Art 5515",
        "imagenes": [
            "https://images.unsplash.com/photo-1574258495973-f010dfbb5371?w=800&q=80",
            "https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=800&q=80"
        ]
    },
    {
        "nombre": "Tom Ford TF5178 Square Black",
        "imagenes": [
            "https://images.unsplash.com/photo-1509695507497-903c140c43b0?w=800&q=80",
            "https://images.unsplash.com/photo-1574258495973-f010dfbb5371?w=800&q=80"
        ]
    },
    {
        "nombre": "Lindberg Air Titanium Rim 6517",
        "imagenes": [
            "https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=800&q=80",
            "https://images.unsplash.com/photo-1574258495973-f010dfbb5371?w=800&q=80"
        ]
    },
    {
        "nombre": "Warby Parker Percey Whiskey Tortoise",
        "imagenes": [
            "https://images.unsplash.com/photo-1574258495973-f010dfbb5371?w=800&q=80",
            "https://images.unsplash.com/photo-1509695507497-903c140c43b0?w=800&q=80"
        ]
    }
]

def actualizar_todos():
    """Actualizar TODOS los productos"""
    print("=" * 80)
    print("🔄 ACTUALIZANDO TODOS LOS PRODUCTOS CON IMÁGENES APROPIADAS")
    print("=" * 80)
    print()
    
    exitosos = 0
    no_encontrados = 0
    
    for item in actualizaciones_completas:
        nombre = item['nombre']
        imagenes = item['imagenes']
        
        resultado = productos_col.update_one(
            {'nombre_producto': nombre},
            {'$set': {'imagenes': imagenes}}
        )
        
        if resultado.matched_count > 0:
            print(f"✅ {nombre}")
            exitosos += 1
        else:
            print(f"⚠️  {nombre} - No encontrado")
            no_encontrados += 1
    
    print()
    print("=" * 80)
    print(f"✅ Actualizados: {exitosos}")
    print(f"⚠️  No encontrados: {no_encontrados}")
    print("=" * 80)
    print()
    print("📋 SIGUIENTE PASO:")
    print("   python vectorizar_imagenes.py")
    print()
    print("   Esto actualizará el campo 'image_embedding_source' automáticamente")
    print("=" * 80)

if __name__ == "__main__":
    actualizar_todos()
