"""
Script para generar dataset completo para optica_db
- 100+ documentos de texto
- 50+ imágenes asociadas
- Formato JSON válido
"""

from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime, timedelta
import random
from dotenv import load_dotenv
import os

# Cargar configuración
load_dotenv()
MONGODB_URI = os.getenv('MONGODB_URI')
MONGODB_DATABASE = 'optica_db'

print("=" * 80)
print("📦 GENERANDO DATASET COMPLETO PARA OPTICA_DB")
print("=" * 80)

# Conectar
client = MongoClient(MONGODB_URI)
db = client[MONGODB_DATABASE]

print(f"✅ Conectado a: {MONGODB_DATABASE}\n")

# Limpiar datos existentes (excepto catálogos)
print("🧹 Limpiando datos previos...")
for col in ['clientes', 'asesores', 'especialistas', 'proveedores', 
            'laboratorios', 'suministros', 'productos', 'citas', 'examenes', 'ventas']:
    result = db[col].delete_many({})
    print(f"   ✓ {col}: {result.deleted_count} eliminados")

# ============================================================================
# DATOS BASE
# ============================================================================

# Nombres y apellidos colombianos
nombres_m = ["Juan", "Carlos", "Miguel", "Luis", "José", "David", "Andrés", "Santiago", "Daniel", "Felipe",
             "Sebastián", "Alejandro", "Manuel", "Ricardo", "Fernando", "Diego", "Pablo", "Javier", "Camilo", "Mateo"]
nombres_f = ["María", "Ana", "Laura", "Sofía", "Carolina", "Valentina", "Camila", "Isabella", "Daniela", "Natalia",
             "Juliana", "Andrea", "Paula", "Catalina", "Alejandra", "Diana", "Gabriela", "Mariana", "Claudia", "Patricia"]
apellidos = ["García", "Rodríguez", "Martínez", "López", "González", "Pérez", "Sánchez", "Ramírez", "Torres", "Flores",
             "Rivera", "Gómez", "Díaz", "Hernández", "Ruiz", "Moreno", "Jiménez", "Álvarez", "Romero", "Vargas",
             "Castro", "Ortiz", "Silva", "Rojas", "Mendoza", "Morales", "Guerrero", "Medina", "Ramos", "Vega"]

ciudades = ["Bogotá", "Medellín", "Cali", "Barranquilla", "Cartagena", "Bucaramanga", "Pereira", "Manizales", "Cúcuta", "Armenia"]

# URLs de imágenes (Unsplash - gratuitas)
imagenes_productos = [
    "https://images.unsplash.com/photo-1574258495973-f010dfbb5371",  # Gafas elegantes
    "https://images.unsplash.com/photo-1511499767150-a48a237f0083",  # Gafas aviador
    "https://images.unsplash.com/photo-1509695507497-903c140c43b0",  # Gafas modernas
    "https://images.unsplash.com/photo-1577803645773-f96470509666",  # Monturas
    "https://images.unsplash.com/photo-1473496169904-658ba7c44d8a",  # Gafas sol
    "https://images.unsplash.com/photo-1508296695146-257a814070b4",  # Gafas deportivas
    "https://images.unsplash.com/photo-1556306535-0f09a537f0a3",  # Óptica tienda
    "https://images.unsplash.com/photo-1622519407650-3df9883f76a5",  # Lentes contacto
    "https://images.unsplash.com/photo-1601513445506-2ab0d4fb4229",  # Gafas lectura
    "https://images.unsplash.com/photo-1584036561566-baf8f5f1b144",  # Gafas vintage
]

imagenes_personas = [
    "https://i.pravatar.cc/300?img={}".format(i) for i in range(1, 71)  # 70 avatares
]

total_docs = 0
total_imagenes = 0

# ============================================================================
# 1. CLIENTES (30 documentos con fotos)
# ============================================================================
print("\n1. Generando CLIENTES...")
clientes_ids = []
for i in range(30):
    genero = random.choice(['M', 'F'])
    nombre = random.choice(nombres_m if genero == 'M' else nombres_f)
    apellido = random.choice(apellidos)
    
    cliente = {
        '_id': ObjectId(),
        'nombre': nombre,
        'apellido': apellido,
        'email': f"{nombre.lower()}.{apellido.lower()}{i}@mail.com",
        'fecha_nacimiento': datetime(random.randint(1960, 2005), random.randint(1, 12), random.randint(1, 28)),
        'activo': random.choice([True, True, True, False]),
        'fecha_registro': datetime.now() - timedelta(days=random.randint(1, 1000)),
        'foto_perfil': random.choice(imagenes_personas),  # IMAGEN
        'documento': {
            'tipo': random.choice(['CC', 'CE', 'TI']),
            'numero': str(1000000000 + random.randint(0, 999999999))
        },
        'direcciones': [
            {
                'tipo': 'Principal',
                'calle': f"Calle {random.randint(1, 200)} #{random.randint(1, 99)}-{random.randint(1, 99)}",
                'ciudad': random.choice(ciudades),
                'estado': 'Cundinamarca',
                'codigo_postal': str(110000 + random.randint(0, 999)),
                'pais': 'Colombia',
                'es_principal': True
            }
        ],
        'telefonos': [
            {
                'numero': f"3{random.randint(100000000, 199999999)}",
                'tipo': 'Móvil',
                'es_principal': True
            }
        ]
    }
    clientes_ids.append(cliente['_id'])
    db.clientes.insert_one(cliente)
    total_imagenes += 1

total_docs += 30
print(f"   ✅ 30 clientes creados (30 fotos)")

# ============================================================================
# 2. ASESORES (8 documentos con fotos)
# ============================================================================
print("2. Generando ASESORES...")
asesores_ids = []
for i in range(8):
    genero = random.choice(['M', 'F'])
    nombre = random.choice(nombres_m if genero == 'M' else nombres_f)
    apellido = random.choice(apellidos)
    
    asesor = {
        '_id': ObjectId(),
        'nombre': nombre,
        'apellido': apellido,
        'numero_documento': str(1000000000 + random.randint(0, 999999999)),
        'fecha_contratacion': datetime(2020 + random.randint(0, 5), random.randint(1, 12), random.randint(1, 28)),
        'activo': True,
        'foto_perfil': random.choice(imagenes_personas),  # IMAGEN
        'telefonos': [
            {'numero': f"3{random.randint(100000000, 199999999)}", 'tipo': 'Móvil'}
        ],
        'emails': [
            {'email': f"{nombre.lower()}.{apellido.lower()}@optica.com", 'tipo': 'Corporativo'}
        ]
    }
    asesores_ids.append(asesor['_id'])
    db.asesores.insert_one(asesor)
    total_imagenes += 1

total_docs += 8
print(f"   ✅ 8 asesores creados (8 fotos)")

# ============================================================================
# 3. ESPECIALISTAS (6 documentos con fotos)
# ============================================================================
print("3. Generando ESPECIALISTAS...")
especialidades_nombres = ["Optometría", "Oftalmología", "Contactología"]
especialistas_ids = []

for i in range(6):
    genero = random.choice(['M', 'F'])
    nombre = random.choice(nombres_m if genero == 'M' else nombres_f)
    apellido = random.choice(apellidos)
    
    especialista = {
        '_id': ObjectId(),
        'nombre': nombre,
        'apellido': apellido,
        'numero_licencia': f"{'OPT' if i < 3 else 'OFT'}-{10000 + random.randint(0, 89999)}",
        'numero_documento': str(1000000000 + random.randint(0, 999999999)),
        'activo': True,
        'foto_perfil': random.choice(imagenes_personas),  # IMAGEN
        'especialidades': [
            {
                'nombre': random.choice(especialidades_nombres),
                'descripcion': 'Especialidad en salud visual',
                'fecha_certificacion': datetime(2010 + random.randint(0, 13), random.randint(1, 12), 1)
            }
        ],
        'telefonos': [
            {'numero': f"3{random.randint(100000000, 199999999)}", 'tipo': 'Móvil'}
        ],
        'emails': [
            {'email': f"dr.{nombre.lower()}.{apellido.lower()}@optica.com", 'tipo': 'Profesional'}
        ]
    }
    especialistas_ids.append(especialista['_id'])
    db.especialistas.insert_one(especialista)
    total_imagenes += 1

total_docs += 6
print(f"   ✅ 6 especialistas creados (6 fotos)")

# ============================================================================
# 4. PROVEEDORES (5 documentos con logos)
# ============================================================================
print("4. Generando PROVEEDORES...")
proveedores_nombres = ["LentesPro Internacional", "Monturas Premium", "VisualTech SA", "Óptica Mayorista", "GlobalVision"]
proveedores_ids = []

logos_proveedores = [
    "https://via.placeholder.com/200x80/0066cc/ffffff?text=LentesPro",
    "https://via.placeholder.com/200x80/cc0000/ffffff?text=MonturasPremium",
    "https://via.placeholder.com/200x80/00cc66/ffffff?text=VisualTech",
    "https://via.placeholder.com/200x80/ff9900/ffffff?text=OpticaMayorista",
    "https://via.placeholder.com/200x80/9900cc/ffffff?text=GlobalVision"
]

for i in range(5):
    proveedor = {
        '_id': ObjectId(),
        'nombre_proveedor': proveedores_nombres[i],
        'contacto_principal': f"{random.choice(nombres_m)} {random.choice(apellidos)}",
        'activo': True,
        'logo': logos_proveedores[i],  # IMAGEN
        'direcciones': [
            {
                'calle': f"Carrera {random.randint(1, 100)} #{random.randint(1, 99)}-{random.randint(1, 99)}",
                'ciudad': random.choice(ciudades),
                'estado': 'Cundinamarca',
                'codigo_postal': str(110000 + random.randint(0, 999)),
                'pais': 'Colombia'
            }
        ],
        'telefonos': [
            {'telefono': f"6{random.randint(10000000, 19999999)}", 'extension': str(random.randint(100, 999))}
        ],
        'emails': [
            {'email': f"ventas@{proveedores_nombres[i].lower().replace(' ', '')}.com", 'tipo': 'Ventas'}
        ]
    }
    proveedores_ids.append(proveedor['_id'])
    db.proveedores.insert_one(proveedor)
    total_imagenes += 1

total_docs += 5
print(f"   ✅ 5 proveedores creados (5 logos)")

# ============================================================================
# 5. LABORATORIOS (3 documentos con logos)
# ============================================================================
print("5. Generando LABORATORIOS...")
laboratorios_nombres = ["LabVisión Colombia", "CristalLab", "LenteFino Labs"]
laboratorios_ids = []

for i in range(3):
    lab = {
        '_id': ObjectId(),
        'nombre_laboratorio': laboratorios_nombres[i],
        'contacto_principal': f"{random.choice(nombres_m)} {random.choice(apellidos)}",
        'activo': True,
        'logo': f"https://via.placeholder.com/200x80/003366/ffffff?text={laboratorios_nombres[i].replace(' ', '')}",  # IMAGEN
        'direcciones': [
            {
                'calle': f"Avenida {random.randint(1, 50)} #{random.randint(1, 99)}-{random.randint(1, 99)}",
                'ciudad': random.choice(ciudades),
                'estado': 'Cundinamarca',
                'codigo_postal': str(110000 + random.randint(0, 999)),
                'pais': 'Colombia'
            }
        ],
        'telefonos': [
            {'telefono': f"6{random.randint(10000000, 19999999)}", 'extension': str(random.randint(100, 999))}
        ]
    }
    laboratorios_ids.append(lab['_id'])
    db.laboratorios.insert_one(lab)
    total_imagenes += 1

total_docs += 3
print(f"   ✅ 3 laboratorios creados (3 logos)")

# ============================================================================
# 6. SUMINISTROS (10 documentos)
# ============================================================================
print("6. Generando SUMINISTROS...")
tipos_suministro = ["Lentes oftálmicos", "Lentes de contacto", "Monturas", "Accesorios"]
suministros_ids = []

for i in range(10):
    suministro = {
        '_id': ObjectId(),
        'tipo': {
            'nombre': random.choice(tipos_suministro),
            'descripcion': 'Suministro para óptica'
        },
        'cantidad': random.randint(50, 500),
        'precio_unitario': round(random.uniform(20000, 150000), 2),
        'fecha_ingreso': datetime.now() - timedelta(days=random.randint(1, 365)),
        'numero_lote': f"LOTE-2025-{1000 + i}",
        'fecha_vencimiento': datetime.now() + timedelta(days=random.randint(365, 1095)),
        'proveedor_ref': random.choice(proveedores_ids),
        'laboratorio_ref': random.choice(laboratorios_ids) if random.choice([True, False]) else None,
        'observaciones': ''
    }
    suministros_ids.append(suministro['_id'])
    db.suministros.insert_one(suministro)

total_docs += 10
print(f"   ✅ 10 suministros creados")

# ============================================================================
# 7. PRODUCTOS (20 documentos con imágenes)
# ============================================================================
print("7. Generando PRODUCTOS...")
marcas = ["Ray-Ban", "Oakley", "Prada", "Gucci", "Carrera", "Vogue", "Dolce&Gabbana", "Arnette", "Persol", "Police"]
tipos_productos = ["Gafas formuladas", "Gafas de sol", "Lentes de contacto", "Monturas oftálmicas"]
productos_ids = []

for i in range(20):
    tipo = random.choice(tipos_productos)
    marca = random.choice(marcas)
    
    producto = {
        '_id': ObjectId(),
        'nombre_producto': f"{marca} {tipo} Modelo-{i+1}",
        'tipo': {
            'nombre': tipo,
            'categoria': 'Lente' if 'Lentes' in tipo or 'Gafas' in tipo else 'Montura'
        },
        'marca': marca,
        'descripcion': f"{tipo} de alta calidad marca {marca}",
        'precio_venta': round(random.uniform(100000, 800000), 2),
        'stock': random.randint(5, 100),
        'stock_minimo': 5,
        'codigo_barras': f"789012345600{i}",
        'suministro_ref': random.choice(suministros_ids),
        'activo': True,
        'fecha_creacion': datetime.now() - timedelta(days=random.randint(1, 365)),
        'imagenes': [  # IMÁGENES DE PRODUCTO
            random.choice(imagenes_productos),
            random.choice(imagenes_productos)
        ]
    }
    productos_ids.append(producto['_id'])
    db.productos.insert_one(producto)
    total_imagenes += 2  # 2 imágenes por producto

total_docs += 20
print(f"   ✅ 20 productos creados (40 imágenes)")

# ============================================================================
# 8. CITAS (15 documentos)
# ============================================================================
print("8. Generando CITAS...")
motivos = ["Examen visual de rutina", "Revisión de lentes", "Ajuste de monturas", "Consulta por molestias visuales"]
estados = ["Programada", "Confirmada", "Completada", "Cancelada"]

for i in range(15):
    cita = {
        '_id': ObjectId(),
        'fecha_cita': datetime.now() + timedelta(days=random.randint(-30, 60)),
        'hora_cita': f"{random.randint(8, 18)}:{random.choice(['00', '30'])}:00",
        'motivo': {
            'descripcion': random.choice(motivos)
        },
        'cliente_ref': random.choice(clientes_ids),
        'asesor_ref': random.choice(asesores_ids),
        'especialista_ref': random.choice(especialistas_ids),
        'estado': random.choice(estados),
        'observaciones': '',
        'fecha_creacion': datetime.now() - timedelta(days=random.randint(1, 30))
    }
    db.citas.insert_one(cita)

total_docs += 15
print(f"   ✅ 15 citas creadas")

# ============================================================================
# 9. EXAMENES (12 documentos)
# ============================================================================
print("9. Generando EXAMENES...")
tipos_diagnostico = ["Miopía", "Hipermetropía", "Astigmatismo", "Presbicia"]

for i in range(12):
    examen = {
        '_id': ObjectId(),
        'fecha_examen': datetime.now() - timedelta(days=random.randint(1, 180)),
        'agudeza_visual_od': f"20/{random.choice([20, 25, 30, 40, 50])}",
        'agudeza_visual_oi': f"20/{random.choice([20, 25, 30, 40, 50])}",
        'esfera_od': round(random.uniform(-6.0, 3.0), 2),
        'esfera_oi': round(random.uniform(-6.0, 3.0), 2),
        'cilindro_od': round(random.uniform(-3.0, 0.0), 2),
        'cilindro_oi': round(random.uniform(-3.0, 0.0), 2),
        'eje_od': random.randint(0, 180),
        'eje_oi': random.randint(0, 180),
        'distancia_pupilar': round(random.uniform(58.0, 68.0), 1),
        'observaciones': 'Examen visual completo realizado',
        'cliente_ref': random.choice(clientes_ids),
        'especialista_ref': random.choice(especialistas_ids),
        'diagnostico': {
            'tipo': {
                'nombre': random.choice(tipos_diagnostico),
                'descripcion': 'Diagnóstico visual'
            },
            'descripcion': f"{random.choice(tipos_diagnostico)} leve bilateral",
            'fecha': datetime.now() - timedelta(days=random.randint(1, 180))
        },
        'formula': {
            'descripcion': f"OD: {round(random.uniform(-6.0, 3.0), 2)} {round(random.uniform(-3.0, 0.0), 2)} x {random.randint(0, 180)}",
            'fecha_emision': datetime.now() - timedelta(days=random.randint(1, 180)),
            'fecha_vencimiento': datetime.now() + timedelta(days=365),
            'activa': True
        }
    }
    db.examenes.insert_one(examen)

total_docs += 12
print(f"   ✅ 12 exámenes creados")

# ============================================================================
# 10. VENTAS (18 documentos)
# ============================================================================
print("10. Generando VENTAS...")
metodos_pago = ["Efectivo", "Tarjeta de Crédito", "Tarjeta de Débito", "Transferencia Bancaria"]

for i in range(18):
    num_items = random.randint(1, 4)
    items = []
    subtotal = 0
    
    for j in range(num_items):
        producto_id = random.choice(productos_ids)
        producto = db.productos.find_one({'_id': producto_id})
        cantidad = random.randint(1, 3)
        precio = producto['precio_venta']
        total_item = cantidad * precio
        subtotal += total_item
        
        items.append({
            'producto_ref': producto_id,
            'nombre': producto['nombre_producto'],
            'cantidad': cantidad,
            'precio_unitario': precio,
            'subtotal': total_item,
            'descuento': 0,
            'total': total_item
        })
    
    descuento = round(subtotal * random.uniform(0, 0.15), 2)
    impuesto = round((subtotal - descuento) * 0.19, 2)
    total = subtotal - descuento + impuesto
    
    venta = {
        '_id': ObjectId(),
        'numero_factura': f"F-2025-{1000 + i}",
        'fecha_compra': datetime.now() - timedelta(days=random.randint(1, 180)),
        'metodo_pago': {
            'nombre': random.choice(metodos_pago)
        },
        'cliente_ref': random.choice(clientes_ids),
        'asesor_ref': random.choice(asesores_ids),
        'items': items,
        'subtotal': subtotal,
        'descuento': descuento,
        'impuesto': impuesto,
        'total': total,
        'estado': random.choice(['Completada', 'Completada', 'Completada', 'Pendiente']),
        'observaciones': ''
    }
    db.ventas.insert_one(venta)

total_docs += 18
print(f"   ✅ 18 ventas creadas")

# ============================================================================
# RESUMEN FINAL
# ============================================================================
print("\n" + "=" * 80)
print("📊 RESUMEN DEL DATASET GENERADO")
print("=" * 80)
print(f"\n1. Clientes:       30 documentos (30 fotos perfil)")
print(f"2. Asesores:       8 documentos (8 fotos perfil)")
print(f"3. Especialistas:  6 documentos (6 fotos perfil)")
print(f"4. Proveedores:    5 documentos (5 logos)")
print(f"5. Laboratorios:   3 documentos (3 logos)")
print(f"6. Suministros:    10 documentos")
print(f"7. Productos:      20 documentos (40 imágenes)")
print(f"8. Citas:          15 documentos")
print(f"9. Exámenes:       12 documentos")
print(f"10. Ventas:        18 documentos")
print(f"\n{'='*80}")
print(f"✅ TOTAL DOCUMENTOS: {total_docs} (Requerido: 100)")
print(f"✅ TOTAL IMÁGENES: {total_imagenes} (Requerido: 50)")
print(f"{'='*80}")

# Verificar conteos
print("\n🔍 Verificando en MongoDB Atlas:\n")
for col in ['clientes', 'asesores', 'especialistas', 'proveedores', 'laboratorios',
            'suministros', 'productos', 'citas', 'examenes', 'ventas']:
    count = db[col].count_documents({})
    print(f"   {col}: {count} documentos")

client.close()
print("\n✅ Dataset generado exitosamente! 🎉")
print("💾 Datos listos para exportar a JSON si es necesario")
