#!/usr/bin/env python3
"""
Script para agregar productos variados con imágenes reales
Incluye: gafas de sol, lentes de contacto, soluciones, estuches, accesorios
"""

from pymongo import MongoClient
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

# Conectar a MongoDB
client = MongoClient(os.getenv('MONGODB_URI'))
db = client['optica_db']
productos_col = db['productos']

# Productos variados siguiendo el esquema de MongoDB
nuevos_productos = [
    # ============ GAFAS DE SOL ============
    {
        "nombre_producto": "Ray-Ban Aviator Classic RB3025",
        "marca": "Ray-Ban",
        "tipo": {
            "categoria": "Gafas de sol",
            "estilo": "Aviador clásico",
            "material_montura": "Metal dorado",
            "material_lentes": "Cristal G-15",
            "color": "Dorado/Verde",
            "genero": "Unisex"
        },
        "descripcion": "Las icónicas gafas aviador Ray-Ban con lentes verdes clásicas. Estilo atemporal con protección UV400. Incluye: Lentes de cristal verde G-15, Protección UV400, Montura de metal dorado resistente, Puente doble característico, Almohadillas nasales ajustables para máximo confort.",
        "precio_venta": 520000.00,
        "stock": 15,
        "stock_minimo": 5,
        "activo": True,
        "codigo_barras": "8056597378277",
        "imagenes": [
            "https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=800",
            "https://images.unsplash.com/photo-1572635196237-14b3f281503f?w=800"
        ]
    },
    {
        "nombre_producto": "Oakley Holbrook OO9102 Polarized",
        "marca": "Oakley",
        "tipo": {
            "categoria": "Gafas de sol",
            "estilo": "Deportivo rectangular",
            "material_montura": "O-Matter",
            "material_lentes": "Plutonite polarizado",
            "color": "Negro mate/Gris Prizm",
            "genero": "Unisex",
            "tecnologia": "Prizm HDO"
        },
        "descripcion": "Gafas deportivas con tecnología de lentes polarizadas Prizm para máxima claridad y contraste. Montura O-Matter resistente y ligera, Protección UV400 total, Diseño envolvente para protección lateral, Tecnología HDO (High Definition Optics).",
        "precio_venta": 680000.00,
        "stock": 12,
        "stock_minimo": 4,
        "activo": True,
        "codigo_barras": "888392461483",
        "imagenes": [
            "https://images.unsplash.com/photo-1508296695146-257a814070b4?w=800",
            "https://images.unsplash.com/photo-1577803645773-f96470509666?w=800"
        ]
    },
    {
        "nombre_producto": "Gucci GG0061S Redondo Luxury",
        "marca": "Gucci",
        "tipo": {
            "categoria": "Gafas de sol",
            "estilo": "Fashion redondo",
            "material_montura": "Acetato italiano premium",
            "material_lentes": "CR-39 degradado",
            "color": "Negro/Dorado",
            "genero": "Mujer",
            "coleccion": "Luxury"
        },
        "descripcion": "Gafas de sol redondas de lujo con detalles dorados GG. Elegancia italiana en cada detalle. Incluye: Acetato Mazzucchelli de alta calidad, Logo GG grabado en las varillas, Lentes degradadas premium, Protección UV400, Estuche de terciopelo y certificado de autenticidad.",
        "precio_venta": 1250000.00,
        "stock": 8,
        "stock_minimo": 3,
        "activo": True,
        "codigo_barras": "889652082561",
        "imagenes": [
            "https://images.unsplash.com/photo-1473496169904-658ba7c44d8a?w=800",
            "https://images.unsplash.com/photo-1609587312208-cea54be969e7?w=800"
        ]
    },
    {
        "nombre_producto": "Polaroid Sport PLD7028/S Wrap",
        "marca": "Polaroid",
        "tipo": {
            "categoria": "Gafas de sol",
            "estilo": "Deportivo envolvente",
            "material_montura": "Policarbonato TR90",
            "material_lentes": "Policarbonato polarizado",
            "color": "Negro/Azul espejo",
            "genero": "Unisex",
            "uso": "Deporte outdoor"
        },
        "descripcion": "Gafas deportivas con diseño envolvente y lentes polarizadas UltraSight. Perfectas para ciclismo, running y deportes acuáticos. Características: Lentes polarizadas anti-reflejos, Diseño envolvente deportivo, Protección lateral completa, Almohadillas de goma antideslizantes, Ventilación integrada.",
        "precio_venta": 320000.00,
        "stock": 20,
        "stock_minimo": 8,
        "activo": True,
        "codigo_barras": "716736242378",
        "imagenes": [
            "https://images.unsplash.com/photo-1584036561566-baf8f5f1b144?w=800",
            "https://images.unsplash.com/photo-1589782182703-2aaa69037b5b?w=800"
        ]
    },
    
    # ============ LENTES DE CONTACTO ============
    {
        "nombre_producto": "Acuvue Oasys Hydraclear Plus - Caja x6",
        "marca": "Johnson & Johnson",
        "tipo": {
            "categoria": "Lentes de contacto",
            "tipo_lente": "Blandos quincenales",
            "material": "Senofilcon A",
            "contenido_agua": "38%",
            "permeabilidad": "147 Dk/t",
            "duracion": "2 semanas"
        },
        "descripcion": "Lentes de contacto blandos con tecnología Hydraclear Plus para máxima humectación durante todo el día. Ideal para usuarios con ojos sensibles o secos. Incluye: Uso quincenal (2 semanas), Hidratación prolongada todo el día, Protección UV clase 1, Material altamente transpirable, Caja con 6 lentes estériles.",
        "precio_venta": 85000.00,
        "stock": 50,
        "stock_minimo": 20,
        "activo": True,
        "codigo_barras": "733905567643",
        "imagenes": [
            "https://images.unsplash.com/photo-1614452892306-45e9f36a4f9f?w=800",
            "https://images.unsplash.com/photo-1606811841689-23dfddce3e95?w=800"
        ]
    },
    {
        "nombre_producto": "Biofinity Monthly CooperVision - Caja x6",
        "marca": "CooperVision",
        "tipo": {
            "categoria": "Lentes de contacto",
            "tipo_lente": "Blandos mensuales",
            "material": "Comfilcon A",
            "contenido_agua": "48%",
            "permeabilidad": "160 Dk/t",
            "duracion": "1 mes"
        },
        "descripcion": "Lentes mensuales de silicona hidrogel de tercera generación con tecnología Aquaform para máximo confort sin necesidad de soluciones humectantes adicionales. Características: Uso mensual de reemplazo, Alta transmisibilidad de oxígeno 160 Dk/t, Retención natural de humedad con Aquaform, No requiere humectantes adicionales, Material ultra suave y flexible.",
        "precio_venta": 95000.00,
        "stock": 45,
        "stock_minimo": 18,
        "activo": True,
        "codigo_barras": "619382831738",
        "imagenes": [
            "https://images.unsplash.com/photo-1606811841689-23dfddce3e95?w=800",
            "https://images.unsplash.com/photo-1614452892306-45e9f36a4f9f?w=800"
        ]
    },
    {
        "nombre_producto": "Dailies AquaComfort Plus Alcon - Caja x30",
        "marca": "Alcon",
        "tipo": {
            "categoria": "Lentes de contacto",
            "tipo_lente": "Desechables diarios",
            "material": "Nelfilcon A",
            "contenido_agua": "69%",
            "permeabilidad": "26 Dk/t",
            "duracion": "1 día"
        },
        "descripcion": "Lentes de contacto diarios con triple acción hidratante. Máxima higiene y frescura cada día sin necesidad de limpieza. Beneficios: Uso diario desechable (máxima higiene), Triple acción hidratante patentada, Liberación de humedad en cada parpadeo, Sin necesidad de limpieza ni mantenimiento, Ideal para uso ocasional o viajes.",
        "precio_venta": 110000.00,
        "stock": 60,
        "stock_minimo": 25,
        "activo": True,
        "codigo_barras": "300650355704",
        "imagenes": [
            "https://images.unsplash.com/photo-1614452892306-45e9f36a4f9f?w=800",
            "https://images.unsplash.com/photo-1606811841689-23dfddce3e95?w=800"
        ]
    },
    
    # ============ SOLUCIONES Y LIMPIEZA ============
    {
        "nombre_producto": "ReNu MultiPlus Bausch+Lomb 360ml",
        "marca": "Bausch + Lomb",
        "tipo": {
            "categoria": "Soluciones",
            "tipo_solucion": "Multipropósito",
            "funciones": "Limpia, desinfecta, almacena",
            "volumen": "360ml",
            "compatible": "Lentes blandos"
        },
        "descripcion": "Solución multipropósito para limpieza, desinfección y almacenamiento de lentes de contacto blandos. Fórmula avanzada que elimina proteínas y depósitos. Características: Limpia y desinfecta en un solo paso, Elimina proteínas y depósitos lipídicos, Hidratación prolongada hasta 20 horas, Sin frotar requerido (opcional), Compatible con todos los lentes blandos.",
        "precio_venta": 35000.00,
        "stock": 80,
        "stock_minimo": 30,
        "activo": True,
        "codigo_barras": "324208631904",
        "imagenes": [
            "https://images.unsplash.com/photo-1585435557343-3b092031a831?w=800",
            "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=800"
        ]
    },
    {
        "nombre_producto": "Opti-Free PureMoist Alcon 300ml",
        "marca": "Alcon",
        "tipo": {
            "categoria": "Soluciones",
            "tipo_solucion": "Multipropósito premium",
            "funciones": "Limpia, desinfecta, humecta",
            "volumen": "300ml",
            "tecnologia": "HydraGlyde"
        },
        "descripcion": "Solución premium con tecnología HydraGlyde que crea un escudo humectante de larga duración en la superficie del lente. Ideal para lentes de silicona hidrogel. Beneficios: Tecnología HydraGlyde Moisture Matrix exclusiva, Humectación hasta 16 horas comprobada, Desinfección efectiva contra microorganismos, Elimina depósitos de lípidos y proteínas, Sensación de frescura todo el día.",
        "precio_venta": 42000.00,
        "stock": 70,
        "stock_minimo": 28,
        "activo": True,
        "codigo_barras": "300650355810",
        "imagenes": [
            "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=800",
            "https://images.unsplash.com/photo-1585435557343-3b092031a831?w=800"
        ]
    },
    {
        "nombre_producto": "Biotrue Flight Pack 60ml x2 Viaje",
        "marca": "Bausch + Lomb",
        "tipo": {
            "categoria": "Soluciones",
            "tipo_solucion": "Multipropósito viaje",
            "funciones": "Limpia, desinfecta, almacena",
            "volumen": "60ml x 2 unidades",
            "formato": "Travel size"
        },
        "descripcion": "Pack de viaje con 2 frascos de 60ml. Perfecto para llevar en equipaje de mano y cumple con regulaciones de vuelos internacionales. Características: 2 frascos de 60ml (120ml total), Aprobado para vuelos (menos de 100ml), pH balanceado como lágrimas naturales (7.5), Formato conveniente para viajes, Fórmula bio-inspirada con ácido hialurónico.",
        "precio_venta": 18000.00,
        "stock": 100,
        "stock_minimo": 40,
        "activo": True,
        "codigo_barras": "324208631973",
        "imagenes": [
            "https://images.unsplash.com/photo-1585435557343-3b092031a831?w=800",
            "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=800"
        ]
    },
    
    # ============ ESTUCHES Y ACCESORIOS ============
    {
        "nombre_producto": "Estuche Rígido Premium EVA Negro",
        "marca": "OptiCase",
        "tipo": {
            "categoria": "Accesorios",
            "tipo_accesorio": "Estuche protector",
            "material": "EVA rígido",
            "color": "Negro mate",
            "tamaño": "Universal"
        },
        "descripcion": "Estuche rígido de alta protección para gafas con interior acolchado y cierre de cremallera resistente. Protección total contra golpes e impactos. Características: Material EVA resistente a impactos, Interior acolchado de microfibra premium, Cierre de cremallera YKK duradero, Tamaño universal (16x7x5cm), Diseño compacto y ligero.",
        "precio_venta": 25000.00,
        "stock": 150,
        "stock_minimo": 50,
        "activo": True,
        "codigo_barras": "7891234567890",
        "imagenes": [
            "https://images.unsplash.com/photo-1556306535-0f09a537f0a3?w=800",
            "https://images.unsplash.com/photo-1509695507497-903c140c43b0?w=800"
        ]
    },
    {
        "nombre_producto": "Gamuza Microfibra Premium Pack x3",
        "marca": "OptiClean Pro",
        "tipo": {
            "categoria": "Accesorios",
            "tipo_accesorio": "Limpieza",
            "material": "Microfibra ultra-suave",
            "cantidad": "3 unidades",
            "colores": "Gris, Azul, Negro"
        },
        "descripcion": "Pack de 3 gamuzas de microfibra premium para limpieza de lentes sin rayones ni pelusas. Lavables y reutilizables. Beneficios: Pack de 3 unidades en colores variados, Microfibra de 200 GSM alta densidad, No deja pelusas ni rayones, Lavables hasta 500 veces, Tamaño generoso 15x18cm.",
        "precio_venta": 15000.00,
        "stock": 200,
        "stock_minimo": 80,
        "activo": True,
        "codigo_barras": "7891234567906",
        "imagenes": [
            "https://images.unsplash.com/photo-1509695507497-903c140c43b0?w=800",
            "https://images.unsplash.com/photo-1556306535-0f09a537f0a3?w=800"
        ]
    },
    {
        "nombre_producto": "Spray Limpiador Antivaho FogTech 50ml",
        "marca": "FogTech",
        "tipo": {
            "categoria": "Accesorios",
            "tipo_accesorio": "Limpiador spray",
            "volumen": "50ml",
            "funcion": "Antivaho + Limpieza",
            "duracion": "24 horas"
        },
        "descripcion": "Spray limpiador con fórmula antivaho de larga duración. Ideal para uso con mascarilla o en ambientes húmedos. Evita empañamiento hasta 24 horas. Características: Fórmula antivaho avanzada de larga duración, Protección hasta 24 horas comprobada, No deja residuos ni manchas, Compatible con tratamientos antirreflejantes, Frasco spray conveniente de 50ml.",
        "precio_venta": 28000.00,
        "stock": 120,
        "stock_minimo": 45,
        "activo": True,
        "codigo_barras": "850006759019",
        "imagenes": [
            "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=800",
            "https://images.unsplash.com/photo-1585435557343-3b092031a831?w=800"
        ]
    },
    {
        "nombre_producto": "Cordón Deportivo Neopreno Croakies",
        "marca": "Croakies",
        "tipo": {
            "categoria": "Accesorios",
            "tipo_accesorio": "Sujetador deportivo",
            "material": "Neopreno flotante",
            "color": "Negro",
            "ajuste": "Universal"
        },
        "descripcion": "Cordón deportivo de neopreno para sujetar gafas durante actividades físicas intensas. Material flotante ideal para deportes acuáticos. Características: Material de neopreno flotante premium, Ajuste universal para cualquier gafa, Resistente al agua y secado rápido, Sistema de ajuste rápido sin nudos, Ideal para deportes acuáticos y outdoor.",
        "precio_venta": 22000.00,
        "stock": 100,
        "stock_minimo": 35,
        "activo": True,
        "codigo_barras": "019522390030",
        "imagenes": [
            "https://images.unsplash.com/photo-1509695507497-903c140c43b0?w=800",
            "https://images.unsplash.com/photo-1556306535-0f09a537f0a3?w=800"
        ]
    },
    
    # ============ MONTURAS ÓPTICAS ============
    {
        "nombre_producto": "Silhouette Titan Minimal Art 5515",
        "marca": "Silhouette",
        "tipo": {
            "categoria": "Monturas oftálmicas",
            "estilo": "Sin aro minimalista",
            "material": "Titanio puro",
            "color": "Plateado mate",
            "genero": "Unisex",
            "peso": "1.8 gramos"
        },
        "descripcion": "Monturas sin aro de titanio ultra-ligero. Diseño minimalista austríaco que apenas se siente en el rostro (solo 1.8 gramos). Características: Peso pluma récord de 1.8 gramos, Titanio hipoalergénico 100% puro, Sin tornillos ni soldaduras (patentado), Flexibilidad controlada sin deformación, Diseño minimalista austríaco premiado.",
        "precio_venta": 850000.00,
        "stock": 10,
        "stock_minimo": 3,
        "activo": True,
        "codigo_barras": "9001638285157",
        "imagenes": [
            "https://images.unsplash.com/photo-1574258495973-f010dfbb5371?w=800",
            "https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=800"
        ]
    },
    {
        "nombre_producto": "Tom Ford TF5178 Square Black",
        "marca": "Tom Ford",
        "tipo": {
            "categoria": "Monturas oftálmicas",
            "estilo": "Cuadrado clásico",
            "material": "Acetato italiano Mazzucchelli",
            "color": "Negro brillante",
            "genero": "Hombre",
            "coleccion": "Classic"
        },
        "descripcion": "Monturas cuadradas de acetato premium con el icónico logo T dorado en las varillas. Elegancia masculina con calidad excepcional. Incluye: Acetato Mazzucchelli italiano premium, Logo T metálico grabado exclusivo, Bisagras de 5 pernos ultra resistentes, Puente keyhole distintivo, Estuche de lujo y certificado de autenticidad.",
        "precio_venta": 980000.00,
        "stock": 12,
        "stock_minimo": 4,
        "activo": True,
        "codigo_barras": "664689493456",
        "imagenes": [
            "https://images.unsplash.com/photo-1509695507497-903c140c43b0?w=800",
            "https://images.unsplash.com/photo-1574258495973-f010dfbb5371?w=800"
        ]
    },
    {
        "nombre_producto": "Lindberg Air Titanium Rim 6517",
        "marca": "Lindberg",
        "tipo": {
            "categoria": "Monturas oftálmicas",
            "estilo": "Medio aro moderno",
            "material": "Titanio escandinavo",
            "color": "Azul mate",
            "genero": "Unisex",
            "tecnologia": "Sin tornillos"
        },
        "descripcion": "Diseño danés de vanguardia. Monturas de titanio con sistema patentado sin tornillos que nunca se aflojan. Tecnología aeroespacial en óptica. Características: Sistema sin tornillos patentado único, Titanio de grado aeroespacial, Peso ultra-ligero y resistencia extrema, Personalización de colores disponible, Garantía de por vida del fabricante.",
        "precio_venta": 1200000.00,
        "stock": 6,
        "stock_minimo": 2,
        "activo": True,
        "codigo_barras": "5708151265173",
        "imagenes": [
            "https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=800",
            "https://images.unsplash.com/photo-1574258495973-f010dfbb5371?w=800"
        ]
    },
    {
        "nombre_producto": "Warby Parker Percey Whiskey Tortoise",
        "marca": "Warby Parker",
        "tipo": {
            "categoria": "Monturas oftálmicas",
            "estilo": "Redondo vintage",
            "material": "Acetato celulosa reciclado",
            "color": "Whiskey Tortoise",
            "genero": "Unisex",
            "programa": "Buy a Pair Give a Pair"
        },
        "descripcion": "Monturas redondas vintage con compromiso sostenible. Por cada compra, se dona una montura a personas necesitadas. Moda con propósito social. Beneficios: Acetato de celulosa 100% reciclado, Programa Buy a Pair Give a Pair (dona 1 por cada compra), Bisagras con resorte de 5 pernos, Tratamiento anti-reflejo incluido en el precio, Garantía de ajuste perfecto o devolución.",
        "precio_venta": 380000.00,
        "stock": 25,
        "stock_minimo": 10,
        "activo": True,
        "codigo_barras": "848675084287",
        "imagenes": [
            "https://images.unsplash.com/photo-1574258495973-f010dfbb5371?w=800",
            "https://images.unsplash.com/photo-1509695507497-903c140c43b0?w=800"
        ]
    }
]

def agregar_productos():
    """Agregar productos variados a la base de datos"""
    print("=" * 80)
    print("📦 AGREGANDO PRODUCTOS VARIADOS CON IMÁGENES REALES")
    print("=" * 80)
    print()
    
    # Agregar timestamps
    for producto in nuevos_productos:
        producto['fecha_creacion'] = datetime.now()
    
    # Insertar productos
    try:
        resultado = productos_col.insert_many(nuevos_productos)
        
        print(f"✅ {len(resultado.inserted_ids)} productos agregados exitosamente")
        print()
        
        # Resumen por categoría
        categorias = {}
        for prod in nuevos_productos:
            cat = prod['tipo']['categoria']
            categorias[cat] = categorias.get(cat, 0) + 1
        
        print("📊 Resumen por categoría:")
        for cat, count in sorted(categorias.items()):
            print(f"   • {cat}: {count} productos")
        
        print()
        print("💰 Rango de precios:")
        precios = [p['precio_venta'] for p in nuevos_productos]
        print(f"   • Mínimo: ${min(precios):,.0f}")
        print(f"   • Máximo: ${max(precios):,.0f}")
        print(f"   • Promedio: ${sum(precios)/len(precios):,.0f}")
        
        print()
        print("=" * 80)
        print(f"🎉 Total productos en DB: {productos_col.count_documents({})}")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ Error al insertar productos: {e}")
        return False
    
    return True

if __name__ == "__main__":
    agregar_productos()
