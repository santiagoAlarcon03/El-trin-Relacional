#!/usr/bin/env python3
"""
Script para actualizar imágenes de productos con URLs apropiadas
"""

from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

client = MongoClient(os.getenv('MONGODB_URI'))
db = client['optica_db']
productos_col = db['productos']

# Actualizaciones de imágenes por producto
actualizaciones = [
    # GAFAS DE SOL - Imágenes de gafas reales
    {
        "nombre": "Ray-Ban Aviator Classic RB3025",
        "imagenes": [
            "https://images.ray-ban.com/is/image/RayBan/8056597378277__STD__shad__qt.png",
            "https://m.media-amazon.com/images/I/61ZnKpHt2eL._AC_UX679_.jpg"
        ]
    },
    {
        "nombre": "Oakley Holbrook OO9102 Polarized",
        "imagenes": [
            "https://www.oakley.com/cdn-cgi/image/width=1200,quality=75,format=auto/medias/888392461483.png",
            "https://m.media-amazon.com/images/I/71hWJPKY0BL._AC_UX679_.jpg"
        ]
    },
    {
        "nombre": "Gucci GG0061S Redondo Luxury",
        "imagenes": [
            "https://www.gucci.com/content/dam/gucci/catwalk/main/2024/women/collection-all/GG0061S/001/GG0061S_001_1.jpg",
            "https://m.media-amazon.com/images/I/61Y9xKQKZqL._AC_UX679_.jpg"
        ]
    },
    {
        "nombre": "Polaroid Sport PLD7028/S Wrap",
        "imagenes": [
            "https://www.polaroid-eyewear.com/media/catalog/product/cache/1/image/1000x/17f82f742ffe127f42dca9de82fb58b1/p/l/pld7028s_003m9.png",
            "https://m.media-amazon.com/images/I/61+9qg+YHDL._AC_UX679_.jpg"
        ]
    },
    
    # LENTES DE CONTACTO - Imágenes de cajas de lentes
    {
        "nombre": "Acuvue Oasys Hydraclear Plus - Caja x6",
        "imagenes": [
            "https://www.acuvue.com/sites/acuvue_us/files/product_images/oasys_6pk_box.png",
            "https://m.media-amazon.com/images/I/71ZNqGPJYVL._SX522_.jpg"
        ]
    },
    {
        "nombre": "Biofinity Monthly CooperVision - Caja x6",
        "imagenes": [
            "https://coopervision.com.co/sites/coopervision_co/files/styles/product_detail_image/public/product-packshot/biofinity-6pk.png",
            "https://m.media-amazon.com/images/I/71wXz7ZQESL._SX522_.jpg"
        ]
    },
    {
        "nombre": "Dailies AquaComfort Plus Alcon - Caja x30",
        "imagenes": [
            "https://www.alcon.com/sites/g/files/rbvwei3636/files/styles/tile_image_default/public/2022-04/dailies-aquacomfort-plus-30-pack.png",
            "https://m.media-amazon.com/images/I/61lrN0YdLyL._SX522_.jpg"
        ]
    },
    
    # SOLUCIONES - Imágenes de frascos de solución
    {
        "nombre": "ReNu MultiPlus Bausch+Lomb 360ml",
        "imagenes": [
            "https://www.bausch.com.co/globalassets/bausch-consumer-health-products-v2/renu-multiplus-360ml-front.png",
            "https://m.media-amazon.com/images/I/61eJ5xIy8HL._SX522_.jpg"
        ]
    },
    {
        "nombre": "Opti-Free PureMoist Alcon 300ml",
        "imagenes": [
            "https://www.alcon.com/sites/g/files/rbvwei3636/files/styles/tile_image_default/public/2022-04/opti-free-puremoist-300ml.png",
            "https://m.media-amazon.com/images/I/61kJcRXZ+PL._SX522_.jpg"
        ]
    },
    {
        "nombre": "Biotrue Flight Pack 60ml x2 Viaje",
        "imagenes": [
            "https://www.bausch.com.co/globalassets/bausch-consumer-health-products-v2/biotrue-60ml-twin-pack.png",
            "https://m.media-amazon.com/images/I/71vLr3J7uZL._SX522_.jpg"
        ]
    },
    
    # ACCESORIOS - Imágenes reales de accesorios
    {
        "nombre": "Estuche Rígido Premium EVA Negro",
        "imagenes": [
            "https://m.media-amazon.com/images/I/71XQJ5oVhpL._AC_SX679_.jpg",
            "https://m.media-amazon.com/images/I/81b2qLq9dAL._AC_SX679_.jpg"
        ]
    },
    {
        "nombre": "Gamuza Microfibra Premium Pack x3",
        "imagenes": [
            "https://m.media-amazon.com/images/I/81vVXyHC7HL._AC_SX679_.jpg",
            "https://m.media-amazon.com/images/I/71kJHzVoiJL._AC_SX679_.jpg"
        ]
    },
    {
        "nombre": "Spray Limpiador Antivaho FogTech 50ml",
        "imagenes": [
            "https://m.media-amazon.com/images/I/61xQqZnCU4L._AC_SX679_.jpg",
            "https://m.media-amazon.com/images/I/71QLYG0gm3L._AC_SX679_.jpg"
        ]
    },
    {
        "nombre": "Cordón Deportivo Neopreno Croakies",
        "imagenes": [
            "https://m.media-amazon.com/images/I/71m7Y9ZqLWL._AC_SX679_.jpg",
            "https://m.media-amazon.com/images/I/81CQYQhVk2L._AC_SX679_.jpg"
        ]
    },
    
    # MONTURAS ÓPTICAS - Imágenes de monturas reales
    {
        "nombre": "Silhouette Titan Minimal Art 5515",
        "imagenes": [
            "https://www.silhouette.com/media/catalog/product/cache/1/image/1000x/17f82f742ffe127f42dca9de82fb58b1/5/5/5515_6560_1.jpg",
            "https://m.media-amazon.com/images/I/61XQm7fQpvL._AC_UX679_.jpg"
        ]
    },
    {
        "nombre": "Tom Ford TF5178 Square Black",
        "imagenes": [
            "https://www.tomford.com/dw/image/v2/AAQM_PRD/on/demandware.static/-/Sites-tomford-master/default/dw5f7f0c3e/images/TF5178/001/TF5178_001_A.jpg",
            "https://m.media-amazon.com/images/I/61YqXZGXfYL._AC_UX679_.jpg"
        ]
    },
    {
        "nombre": "Lindberg Air Titanium Rim 6517",
        "imagenes": [
            "https://www.lindberg.com/media/catalog/product/cache/1/image/1000x/17f82f742ffe127f42dca9de82fb58b1/6/5/6517_u14.jpg",
            "https://m.media-amazon.com/images/I/51XqGYZGHtL._AC_UX679_.jpg"
        ]
    },
    {
        "nombre": "Warby Parker Percey Whiskey Tortoise",
        "imagenes": [
            "https://cdn.warbyparker.com/l/eyeglasses/percey-whiskey-tortoise-front.jpg",
            "https://m.media-amazon.com/images/I/61kLJdYoJ3L._AC_UX679_.jpg"
        ]
    }
]

def actualizar_imagenes():
    """Actualizar imágenes de productos"""
    print("=" * 80)
    print("🖼️  ACTUALIZANDO IMÁGENES DE PRODUCTOS")
    print("=" * 80)
    print()
    
    exitosos = 0
    errores = 0
    
    for item in actualizaciones:
        nombre = item['nombre']
        imagenes = item['imagenes']
        
        resultado = productos_col.update_one(
            {'nombre_producto': nombre},
            {'$set': {'imagenes': imagenes}}
        )
        
        if resultado.matched_count > 0:
            print(f"✅ {nombre}")
            print(f"   📸 {len(imagenes)} imágenes actualizadas")
            exitosos += 1
        else:
            print(f"❌ {nombre} - No encontrado")
            errores += 1
    
    print()
    print("=" * 80)
    print(f"✅ Exitosos: {exitosos}")
    print(f"❌ Errores: {errores}")
    print("=" * 80)
    print()
    print("⚠️  IMPORTANTE: Ahora debes re-vectorizar las imágenes con:")
    print("   python vectorizar_imagenes.py")
    print("=" * 80)

if __name__ == "__main__":
    actualizar_imagenes()
