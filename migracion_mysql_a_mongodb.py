"""
============================================================================
SCRIPT DE MIGRACIÓN AUTOMÁTICA: MySQL → MongoDB Atlas
Base de Datos: optica_db
Fecha: Octubre 28, 2025
============================================================================

Este script extrae datos de MySQL, los transforma aplicando patrones
de embedding y referencing, y los carga en MongoDB Atlas.

Requisitos:
    pip install pymongo mysql-connector-python python-dotenv

Uso:
    1. Configurar las credenciales en el archivo .env
    2. Ejecutar: python migracion_mysql_a_mongodb.py

============================================================================
"""

import os
import sys
import mysql.connector
from pymongo import MongoClient
from datetime import datetime
from bson.objectid import ObjectId
from collections import defaultdict
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

# MySQL Configuration
MYSQL_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', ''),
    'database': os.getenv('MYSQL_DATABASE', 'Optica')
}

# MongoDB Atlas Configuration
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb+srv://usuario:password@cluster.mongodb.net/')
MONGODB_DATABASE = 'optica_db'

# ============================================================================
# UTILIDADES
# ============================================================================

def convertir_fecha(fecha):
    """Convertir datetime.date a datetime.datetime para MongoDB"""
    if fecha is None:
        return None
    if isinstance(fecha, datetime):
        return fecha
    # Si es date, convertir a datetime
    return datetime.combine(fecha, datetime.min.time())

# ============================================================================
# CONEXIONES
# ============================================================================

def conectar_mysql():
    """Conectar a MySQL"""
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        print(f"✅ Conectado a MySQL: {MYSQL_CONFIG['database']}")
        return conn
    except Exception as e:
        print(f"❌ Error conectando a MySQL: {e}")
        sys.exit(1)

def conectar_mongodb():
    """Conectar a MongoDB Atlas"""
    try:
        client = MongoClient(MONGODB_URI)
        db = client[MONGODB_DATABASE]
        # Test conexión
        client.admin.command('ping')
        print(f"✅ Conectado a MongoDB Atlas: {MONGODB_DATABASE}")
        return db
    except Exception as e:
        print(f"❌ Error conectando a MongoDB: {e}")
        sys.exit(1)

# ============================================================================
# FUNCIONES DE EXTRACCIÓN (MySQL)
# ============================================================================

def extraer_tabla(mysql_conn, tabla):
    """Extrae todos los datos de una tabla MySQL"""
    cursor = mysql_conn.cursor(dictionary=True)
    cursor.execute(f"SELECT * FROM {tabla}")
    datos = cursor.fetchall()
    cursor.close()
    return datos

def extraer_con_join(mysql_conn, query):
    """Ejecuta una query personalizada con JOIN"""
    cursor = mysql_conn.cursor(dictionary=True)
    cursor.execute(query)
    datos = cursor.fetchall()
    cursor.close()
    return datos

# ============================================================================
# TRANSFORMACIÓN: CATÁLOGOS (Documento único)
# ============================================================================

def transformar_catalogos(mysql_conn):
    """
    Transforma todos los catálogos en un único documento
    """
    print("\n🔄 Transformando catálogos...")
    
    especialidades = extraer_tabla(mysql_conn, 'Especialidad')
    motivos = extraer_tabla(mysql_conn, 'Motivo')
    tipos_diagnostico = extraer_tabla(mysql_conn, 'TipoDiagnostico')
    metodos_pago = extraer_tabla(mysql_conn, 'MetodoPago')
    tipos_suministro = extraer_tabla(mysql_conn, 'TipoSuministro')
    tipos_producto = extraer_tabla(mysql_conn, 'TipoProducto')
    
    catalogos_doc = {
        '_id': 'catalogos_optica',
        'especialidades': [
            {
                'nombre': e['nombre_especialidad'],
                'descripcion': e['descripcion']
            } for e in especialidades
        ],
        'motivos': [
            {'descripcion': m['descripcion']} for m in motivos
        ],
        'tipos_diagnostico': [
            {
                'nombre': td['nombre_diagnostico'],
                'descripcion': td['descripcion']
            } for td in tipos_diagnostico
        ],
        'metodos_pago': [
            {
                'nombre': mp['nombre_metodo'],
                'activo': bool(mp['activo'])
            } for mp in metodos_pago
        ],
        'tipos_suministro': [
            {
                'nombre': ts['nombre_tipo'],
                'descripcion': ts['descripcion']
            } for ts in tipos_suministro
        ],
        'tipos_producto': [
            {
                'nombre': tp['nombre_tipo'],
                'categoria': tp['categoria']
            } for tp in tipos_producto
        ]
    }
    
    print(f"✅ Catálogos transformados (1 documento)")
    return catalogos_doc

# ============================================================================
# TRANSFORMACIÓN: CLIENTES (Embedding de direcciones y teléfonos)
# ============================================================================

def transformar_clientes(mysql_conn):
    """
    Transforma: Cliente + DireccionCliente + TelefonoCliente
    En: clientes (con embedding)
    """
    print("\n🔄 Transformando clientes...")
    
    clientes = extraer_tabla(mysql_conn, 'Cliente')
    direcciones = extraer_tabla(mysql_conn, 'DireccionCliente')
    telefonos = extraer_tabla(mysql_conn, 'TelefonoCliente')
    
    # Agrupar direcciones y teléfonos por cliente
    dir_por_cliente = defaultdict(list)
    for d in direcciones:
        dir_por_cliente[d['id_cliente']].append(d)
    
    tel_por_cliente = defaultdict(list)
    for t in telefonos:
        tel_por_cliente[t['id_cliente']].append(t)
    
    # Mapeo de IDs MySQL → ObjectId MongoDB
    id_map = {}
    clientes_mongo = []
    
    for cliente in clientes:
        id_mysql = cliente['id_cliente']
        id_mongo = ObjectId()
        id_map[id_mysql] = id_mongo
        
        doc = {
            '_id': id_mongo,
            'nombre': cliente['nombre'],
            'apellido': cliente['apellido'],
            'email': cliente['email'],
            'fecha_nacimiento': datetime.combine(cliente['fecha_nacimiento'], datetime.min.time()) if cliente['fecha_nacimiento'] else None,
            'activo': bool(cliente['activo']),
            'fecha_registro': cliente['fecha_registro']
        }
        
        # Documento embebido
        if cliente['numero_documento']:
            doc['documento'] = {
                'tipo': cliente['tipo_documento'],
                'numero': cliente['numero_documento']
            }
        
        # Direcciones embebidas
        doc['direcciones'] = [
            {
                'tipo': d['tipo_direccion'],
                'calle': d['calle'],
                'ciudad': d['ciudad'],
                'estado': d['estado'],
                'codigo_postal': d['codigo_postal'],
                'pais': d['pais'],
                'es_principal': bool(d['es_principal'])
            }
            for d in dir_por_cliente.get(id_mysql, [])
        ]
        
        # Teléfonos embebidos
        doc['telefonos'] = [
            {
                'numero': t['telefono'],
                'tipo': t['tipo_telefono'],
                'es_principal': bool(t['es_principal'])
            }
            for t in tel_por_cliente.get(id_mysql, [])
        ]
        
        clientes_mongo.append(doc)
    
    print(f"✅ {len(clientes_mongo)} clientes transformados")
    return clientes_mongo, id_map

# ============================================================================
# TRANSFORMACIÓN: ASESORES (Embedding de contactos)
# ============================================================================

def transformar_asesores(mysql_conn):
    """
    Transforma: Asesor + TelefonoAsesor + EmailAsesor
    En: asesores (con embedding)
    """
    print("\n🔄 Transformando asesores...")
    
    asesores = extraer_tabla(mysql_conn, 'Asesor')
    telefonos = extraer_tabla(mysql_conn, 'TelefonoAsesor')
    emails = extraer_tabla(mysql_conn, 'EmailAsesor')
    
    tel_por_asesor = defaultdict(list)
    for t in telefonos:
        tel_por_asesor[t['id_asesor']].append(t)
    
    email_por_asesor = defaultdict(list)
    for e in emails:
        email_por_asesor[e['id_asesor']].append(e)
    
    id_map = {}
    asesores_mongo = []
    
    for asesor in asesores:
        id_mysql = asesor['id_asesor']
        id_mongo = ObjectId()
        id_map[id_mysql] = id_mongo
        
        doc = {
            '_id': id_mongo,
            'nombre': asesor['nombre'],
            'apellido': asesor['apellido'],
            'numero_documento': asesor['numero_documento'],
            'fecha_contratacion': convertir_fecha(asesor['fecha_contratacion']),
            'activo': bool(asesor['activo']),
            'telefonos': [
                {
                    'numero': t['telefono'],
                    'tipo': t['tipo_telefono']
                }
                for t in tel_por_asesor.get(id_mysql, [])
            ],
            'emails': [
                {
                    'email': e['email'],
                    'tipo': e['tipo_email']
                }
                for e in email_por_asesor.get(id_mysql, [])
            ]
        }
        
        asesores_mongo.append(doc)
    
    print(f"✅ {len(asesores_mongo)} asesores transformados")
    return asesores_mongo, id_map

# ============================================================================
# TRANSFORMACIÓN: ESPECIALISTAS (Embedding de especialidades y contactos)
# ============================================================================

def transformar_especialistas(mysql_conn):
    """
    Transforma: Especialista + EspecialistaEspecialidad + contactos
    En: especialistas (con embedding)
    """
    print("\n🔄 Transformando especialistas...")
    
    especialistas = extraer_tabla(mysql_conn, 'Especialista')
    esp_especialidad = extraer_tabla(mysql_conn, 'EspecialistaEspecialidad')
    especialidades = {e['id_especialidad']: e for e in extraer_tabla(mysql_conn, 'Especialidad')}
    telefonos = extraer_tabla(mysql_conn, 'TelefonoEspecialista')
    emails = extraer_tabla(mysql_conn, 'EmailEspecialista')
    
    # Agrupar relaciones
    esp_por_especialista = defaultdict(list)
    for ee in esp_especialidad:
        esp_por_especialista[ee['id_especialista']].append(ee)
    
    tel_por_especialista = defaultdict(list)
    for t in telefonos:
        tel_por_especialista[t['id_especialista']].append(t)
    
    email_por_especialista = defaultdict(list)
    for e in emails:
        email_por_especialista[e['id_especialista']].append(e)
    
    id_map = {}
    especialistas_mongo = []
    
    for especialista in especialistas:
        id_mysql = especialista['id_especialista']
        id_mongo = ObjectId()
        id_map[id_mysql] = id_mongo
        
        doc = {
            '_id': id_mongo,
            'nombre': especialista['nombre'],
            'apellido': especialista['apellido'],
            'numero_licencia': especialista['numero_licencia'],
            'numero_documento': especialista['numero_documento'],
            'activo': bool(especialista['activo']),
            'especialidades': [
                {
                    'nombre': especialidades[ee['id_especialidad']]['nombre_especialidad'],
                    'descripcion': especialidades[ee['id_especialidad']]['descripcion'],
                    'fecha_certificacion': convertir_fecha(ee['fecha_certificacion'])
                }
                for ee in esp_por_especialista.get(id_mysql, [])
            ],
            'telefonos': [
                {
                    'numero': t['telefono'],
                    'tipo': t['tipo_telefono']
                }
                for t in tel_por_especialista.get(id_mysql, [])
            ],
            'emails': [
                {
                    'email': e['email'],
                    'tipo': e['tipo_email']
                }
                for e in email_por_especialista.get(id_mysql, [])
            ]
        }
        
        especialistas_mongo.append(doc)
    
    print(f"✅ {len(especialistas_mongo)} especialistas transformados")
    return especialistas_mongo, id_map

# ============================================================================
# TRANSFORMACIÓN: PROVEEDORES (Embedding de contactos)
# ============================================================================

def transformar_proveedores(mysql_conn):
    """
    Transforma: Proveedor + direcciones + teléfonos + emails
    En: proveedores (con embedding)
    """
    print("\n🔄 Transformando proveedores...")
    
    proveedores = extraer_tabla(mysql_conn, 'Proveedor')
    direcciones = extraer_tabla(mysql_conn, 'DireccionProveedor')
    telefonos = extraer_tabla(mysql_conn, 'TelefonoProveedor')
    emails = extraer_tabla(mysql_conn, 'EmailProveedor')
    
    dir_por_proveedor = defaultdict(list)
    for d in direcciones:
        dir_por_proveedor[d['id_proveedor']].append(d)
    
    tel_por_proveedor = defaultdict(list)
    for t in telefonos:
        tel_por_proveedor[t['id_proveedor']].append(t)
    
    email_por_proveedor = defaultdict(list)
    for e in emails:
        email_por_proveedor[e['id_proveedor']].append(e)
    
    id_map = {}
    proveedores_mongo = []
    
    for proveedor in proveedores:
        id_mysql = proveedor['id_proveedor']
        id_mongo = ObjectId()
        id_map[id_mysql] = id_mongo
        
        doc = {
            '_id': id_mongo,
            'nombre': proveedor['nombre_proveedor'],
            'contacto_principal': proveedor['contacto_principal'],
            'activo': bool(proveedor['activo']),
            'direcciones': [
                {
                    'calle': d['calle'],
                    'ciudad': d['ciudad'],
                    'estado': d['estado'],
                    'codigo_postal': d['codigo_postal'],
                    'pais': d['pais']
                }
                for d in dir_por_proveedor.get(id_mysql, [])
            ],
            'telefonos': [
                {
                    'numero': t['telefono'],
                    'extension': t.get('extension')
                }
                for t in tel_por_proveedor.get(id_mysql, [])
            ],
            'emails': [
                {
                    'email': e['email'],
                    'tipo': e['tipo_email']
                }
                for e in email_por_proveedor.get(id_mysql, [])
            ]
        }
        
        proveedores_mongo.append(doc)
    
    print(f"✅ {len(proveedores_mongo)} proveedores transformados")
    return proveedores_mongo, id_map

# ============================================================================
# TRANSFORMACIÓN: LABORATORIOS (Embedding de contactos)
# ============================================================================

def transformar_laboratorios(mysql_conn):
    """
    Transforma: Laboratorio + direcciones + teléfonos
    En: laboratorios (con embedding)
    """
    print("\n🔄 Transformando laboratorios...")
    
    laboratorios = extraer_tabla(mysql_conn, 'Laboratorio')
    direcciones = extraer_tabla(mysql_conn, 'DireccionLaboratorio')
    telefonos = extraer_tabla(mysql_conn, 'TelefonoLaboratorio')
    
    dir_por_lab = defaultdict(list)
    for d in direcciones:
        dir_por_lab[d['id_laboratorio']].append(d)
    
    tel_por_lab = defaultdict(list)
    for t in telefonos:
        tel_por_lab[t['id_laboratorio']].append(t)
    
    id_map = {}
    laboratorios_mongo = []
    
    for laboratorio in laboratorios:
        id_mysql = laboratorio['id_laboratorio']
        id_mongo = ObjectId()
        id_map[id_mysql] = id_mongo
        
        doc = {
            '_id': id_mongo,
            'nombre': laboratorio['nombre_laboratorio'],
            'contacto_principal': laboratorio['contacto_principal'],
            'activo': bool(laboratorio['activo']),
            'direcciones': [
                {
                    'calle': d['calle'],
                    'ciudad': d['ciudad'],
                    'estado': d['estado'],
                    'codigo_postal': d['codigo_postal'],
                    'pais': d['pais']
                }
                for d in dir_por_lab.get(id_mysql, [])
            ],
            'telefonos': [
                {
                    'numero': t['telefono'],
                    'extension': t.get('extension')
                }
                for t in tel_por_lab.get(id_mysql, [])
            ]
        }
        
        laboratorios_mongo.append(doc)
    
    print(f"✅ {len(laboratorios_mongo)} laboratorios transformados")
    return laboratorios_mongo, id_map

# ============================================================================
# TRANSFORMACIÓN: SUMINISTROS (Referencing)
# ============================================================================

def transformar_suministros(mysql_conn, proveedores_map, laboratorios_map):
    """
    Transforma: Suministro con referencias a proveedor y laboratorio
    """
    print("\n🔄 Transformando suministros...")
    
    suministros = extraer_tabla(mysql_conn, 'Suministro')
    tipos_suministro = {t['id_tipo']: t for t in extraer_tabla(mysql_conn, 'TipoSuministro')}
    
    id_map = {}
    suministros_mongo = []
    
    for suministro in suministros:
        id_mysql = suministro['id_suministro']
        id_mongo = ObjectId()
        id_map[id_mysql] = id_mongo
        
        tipo = tipos_suministro[suministro['id_tipo']]
        
        doc = {
            '_id': id_mongo,
            'tipo': {
                'nombre': tipo['nombre_tipo'],
                'descripcion': tipo['descripcion']
            },
            'cantidad': suministro['cantidad'],
            'precio_unitario': float(suministro['precio_unitario']),
            'fecha_ingreso': convertir_fecha(suministro['fecha_ingreso']),
            'numero_lote': suministro['numero_lote'],
            'fecha_vencimiento': convertir_fecha(suministro['fecha_vencimiento']),
            'proveedor_ref': proveedores_map[suministro['id_proveedor']],
            'observaciones': suministro['observaciones'] or ''
        }
        
        # Referencia opcional al laboratorio
        if suministro['id_laboratorio']:
            doc['laboratorio_ref'] = laboratorios_map[suministro['id_laboratorio']]
        
        suministros_mongo.append(doc)
    
    print(f"✅ {len(suministros_mongo)} suministros transformados")
    return suministros_mongo, id_map

# ============================================================================
# TRANSFORMACIÓN: PRODUCTOS (Embedding tipo, Referencing suministro)
# ============================================================================

def transformar_productos(mysql_conn, suministros_map):
    """
    Transforma: Producto con tipo embebido y referencia a suministro
    """
    print("\n🔄 Transformando productos...")
    
    productos = extraer_tabla(mysql_conn, 'Producto')
    tipos_producto = {t['id_tipo']: t for t in extraer_tabla(mysql_conn, 'TipoProducto')}
    
    id_map = {}
    productos_mongo = []
    
    for producto in productos:
        id_mysql = producto['id_producto']
        id_mongo = ObjectId()
        id_map[id_mysql] = id_mongo
        
        tipo = tipos_producto[producto['id_tipo']]
        
        doc = {
            '_id': id_mongo,
            'nombre': producto['nombre_producto'],
            'codigo_barras': producto['codigo_barras'],
            'tipo': {
                'nombre': tipo['nombre_tipo'],
                'categoria': tipo['categoria']
            },
            'marca': producto['marca'],
            'descripcion': producto['descripcion'],
            'precio_venta': float(producto['precio_venta']),
            'stock': {
                'actual': producto['stock'],
                'minimo': producto['stock_minimo']
            },
            'activo': bool(producto['activo']),
            'fecha_creacion': producto['fecha_creacion']
        }
        
        # Referencia opcional al suministro
        if producto['id_suministro'] and producto['id_suministro'] in suministros_map:
            doc['suministro_ref'] = suministros_map[producto['id_suministro']]
        
        productos_mongo.append(doc)
    
    print(f"✅ {len(productos_mongo)} productos transformados")
    return productos_mongo, id_map

# ============================================================================
# TRANSFORMACIÓN: CITAS (Embedding motivo, Referencing)
# ============================================================================

def transformar_citas(mysql_conn, clientes_map, asesores_map, especialistas_map):
    """
    Transforma: Cita con motivo embebido y referencias
    """
    print("\n🔄 Transformando citas...")
    
    citas = extraer_tabla(mysql_conn, 'Cita')
    motivos = {m['id_motivo']: m for m in extraer_tabla(mysql_conn, 'Motivo')}
    
    id_map = {}
    citas_mongo = []
    
    for cita in citas:
        id_mysql = cita['id_cita']
        id_mongo = ObjectId()
        id_map[id_mysql] = id_mongo
        
        motivo = motivos[cita['id_motivo']]
        
        doc = {
            '_id': id_mongo,
            'fecha_cita': convertir_fecha(cita['fecha_cita']),
            'hora_cita': str(cita['hora_cita']),
            'motivo': {
                'descripcion': motivo['descripcion']
            },
            'cliente_ref': clientes_map[cita['id_cliente']],
            'estado': cita['estado'],
            'observaciones': cita['observaciones'] or '',
            'fecha_creacion': cita['fecha_creacion']
        }
        
        # Referencias opcionales
        if cita['id_asesor']:
            doc['asesor_ref'] = asesores_map[cita['id_asesor']]
        
        if cita['id_especialista']:
            doc['especialista_ref'] = especialistas_map[cita['id_especialista']]
        
        citas_mongo.append(doc)
    
    print(f"✅ {len(citas_mongo)} citas transformadas")
    return citas_mongo, id_map

# ============================================================================
# TRANSFORMACIÓN: EXÁMENES (Embedding completo)
# ============================================================================

def transformar_examenes(mysql_conn, clientes_map, especialistas_map, citas_map):
    """
    Transforma: ExamenVista + Diagnostico + FormulaMedica en un documento
    """
    print("\n🔄 Transformando exámenes...")
    
    examenes = extraer_tabla(mysql_conn, 'ExamenVista')
    diagnosticos = extraer_tabla(mysql_conn, 'Diagnostico')
    formulas = extraer_tabla(mysql_conn, 'FormulaMedica')
    tipos_diagnostico = {t['id_tipo_diagnostico']: t for t in extraer_tabla(mysql_conn, 'TipoDiagnostico')}
    
    # Agrupar por examen
    diag_por_examen = {d['id_examen']: d for d in diagnosticos if d['id_examen']}
    formula_por_diag = {f['id_diagnostico']: f for f in formulas if f['id_diagnostico']}
    
    examenes_mongo = []
    
    for examen in examenes:
        id_mongo = ObjectId()
        
        doc = {
            '_id': id_mongo,
            'fecha_examen': examen['fecha_examen'],
            'cliente_ref': clientes_map[examen['id_cliente']],
            'especialista_ref': especialistas_map[examen['id_especialista']],
            'examen': {
                'ojo_derecho': {
                    'agudeza_visual': examen['agudeza_visual_od'],
                    'esfera': float(examen['esfera_od']) if examen['esfera_od'] else None,
                    'cilindro': float(examen['cilindro_od']) if examen['cilindro_od'] else None,
                    'eje': examen['eje_od'],
                    'presion_intraocular': float(examen['presion_intraocular_od']) if examen['presion_intraocular_od'] else None
                },
                'ojo_izquierdo': {
                    'agudeza_visual': examen['agudeza_visual_oi'],
                    'esfera': float(examen['esfera_oi']) if examen['esfera_oi'] else None,
                    'cilindro': float(examen['cilindro_oi']) if examen['cilindro_oi'] else None,
                    'eje': examen['eje_oi'],
                    'presion_intraocular': float(examen['presion_intraocular_oi']) if examen['presion_intraocular_oi'] else None
                },
                'adicion': float(examen['adicion']) if examen['adicion'] else None,
                'distancia_pupilar': float(examen['distancia_pupilar']) if examen['distancia_pupilar'] else None,
                'observaciones': examen['observaciones'] or ''
            }
        }
        
        # Referencia opcional a cita
        if examen['id_cita'] and examen['id_cita'] in citas_map:
            doc['cita_ref'] = citas_map[examen['id_cita']]
        
        # Diagnóstico embebido
        diagnostico = diag_por_examen.get(examen['id_examen'])
        if diagnostico:
            tipo_diag = tipos_diagnostico[diagnostico['id_tipo_diagnostico']]
            doc['diagnostico'] = {
                'tipo': {
                    'nombre': tipo_diag['nombre_diagnostico'],
                    'descripcion': tipo_diag['descripcion']
                },
                'descripcion': diagnostico['descripcion'],
                'fecha': convertir_fecha(diagnostico['fecha_diagnostico'])
            }
            
            # Fórmula embebida
            formula = formula_por_diag.get(diagnostico['id_diagnostico'])
            if formula:
                doc['formula'] = {
                    'descripcion': formula['descripcion_formula'],
                    'fecha_emision': convertir_fecha(formula['fecha_emision']),
                    'fecha_vencimiento': convertir_fecha(formula['fecha_vencimiento']),
                    'activa': bool(formula['activa'])
                }
        
        examenes_mongo.append(doc)
    
    print(f"✅ {len(examenes_mongo)} exámenes transformados")
    return examenes_mongo

# ============================================================================
# TRANSFORMACIÓN: VENTAS (Embedding completo de items y factura)
# ============================================================================

def transformar_ventas(mysql_conn, clientes_map, asesores_map, productos_map):
    """
    Transforma: Compra + DetalleCompra + Factura en un documento
    """
    print("\n🔄 Transformando ventas...")
    
    compras = extraer_tabla(mysql_conn, 'Compra')
    detalles = extraer_tabla(mysql_conn, 'DetalleCompra')
    facturas = extraer_tabla(mysql_conn, 'Factura')
    metodos_pago = {m['id_metodo']: m for m in extraer_tabla(mysql_conn, 'MetodoPago')}
    productos = {p['id_producto']: p for p in extraer_tabla(mysql_conn, 'Producto')}
    
    # Agrupar detalles por compra
    detalles_por_compra = defaultdict(list)
    for d in detalles:
        detalles_por_compra[d['id_compra']].append(d)
    
    # Mapear facturas por compra
    factura_por_compra = {f['id_compra']: f for f in facturas}
    
    ventas_mongo = []
    
    for compra in compras:
        id_mongo = ObjectId()
        
        metodo = metodos_pago[compra['id_metodo']]
        factura = factura_por_compra.get(compra['id_compra'])
        
        doc = {
            '_id': id_mongo,
            'fecha_compra': compra['fecha_compra'],
            'cliente_ref': clientes_map[compra['id_cliente']],
            'asesor_ref': asesores_map[compra['id_asesor']],
            'metodo_pago': {
                'nombre': metodo['nombre_metodo'],
                'activo': bool(metodo['activo'])
            },
            'items': [],
            'subtotal': float(compra['subtotal']),
            'descuento': float(compra['descuento']),
            'impuesto': float(compra['impuesto']),
            'total': float(compra['total']),
            'estado': compra['estado'],
            'observaciones': compra['observaciones'] or ''
        }
        
        # Items embebidos
        for detalle in detalles_por_compra.get(compra['id_compra'], []):
            producto = productos[detalle['id_producto']]
            doc['items'].append({
                'producto_ref': productos_map[detalle['id_producto']],
                'producto_info': {
                    'nombre': producto['nombre_producto'],
                    'codigo_barras': producto['codigo_barras']
                },
                'cantidad': detalle['cantidad'],
                'precio_unitario': float(detalle['precio_unitario']),
                'subtotal': float(detalle['subtotal']),
                'descuento': float(detalle['descuento']),
                'total': float(detalle['total'])
            })
        
        # Factura embebida (como campos del documento)
        if factura:
            doc['numero_factura'] = factura['numero_factura']
        
        ventas_mongo.append(doc)
    
    print(f"✅ {len(ventas_mongo)} ventas transformadas")
    return ventas_mongo

# ============================================================================
# TRANSFORMACIÓN: DEVOLUCIONES (Referencing)
# ============================================================================

def transformar_devoluciones(mysql_conn, ventas_ids, asesores_map):
    """
    Transforma: Devolucion con referencia a venta
    """
    print("\n🔄 Transformando devoluciones...")
    
    devoluciones = extraer_tabla(mysql_conn, 'Devolucion')
    
    # Como no tenemos el mapeo directo de id_compra a ObjectId de ventas,
    # necesitamos crearlo durante la transformación de ventas
    # Por simplicidad, usaremos un mapeo temporal
    
    devoluciones_mongo = []
    
    for devolucion in devoluciones:
        id_mongo = ObjectId()
        
        # Nota: Necesitarías el mapeo de id_compra a ObjectId
        # Lo dejamos como None por ahora
        doc = {
            '_id': id_mongo,
            'venta_ref': None,  # Requiere mapeo
            'item_index': devolucion['id_detalle'],
            'fecha_devolucion': convertir_fecha(devolucion['fecha_devolucion']),
            'cantidad_devuelta': devolucion['cantidad_devuelta'],
            'motivo': devolucion['motivo'],
            'estado': devolucion['estado'],
            'monto_reembolso': float(devolucion['monto_reembolso'])
        }
        
        if devolucion['id_asesor']:
            doc['asesor_ref'] = asesores_map[devolucion['id_asesor']]
        
        devoluciones_mongo.append(doc)
    
    print(f"✅ {len(devoluciones_mongo)} devoluciones transformadas")
    return devoluciones_mongo

# ============================================================================
# FUNCIÓN PRINCIPAL DE MIGRACIÓN
# ============================================================================

def migrar():
    """
    Ejecuta la migración completa de MySQL a MongoDB
    """
    print("=" * 80)
    print("MIGRACIÓN: MySQL → MongoDB Atlas")
    print("Base de datos destino: optica_db")
    print("=" * 80)
    
    # Conectar a bases de datos
    mysql_conn = conectar_mysql()
    mongo_db = conectar_mongodb()
    
    # LIMPIEZA: Eliminar datos existentes
    print("\n🧹 Limpiando colecciones existentes...")
    colecciones = ['catalogos', 'clientes', 'asesores', 'especialistas', 
                   'proveedores', 'laboratorios', 'suministros', 'productos', 
                   'citas', 'examenes', 'ventas']
    for col in colecciones:
        result = mongo_db[col].delete_many({})
        print(f"  ✓ {col}: {result.deleted_count} documentos eliminados")
    
    try:
        # 1. CATÁLOGOS (documento único)
        catalogos_doc = transformar_catalogos(mysql_conn)
        mongo_db.catalogos.insert_one(catalogos_doc)
        print("💾 Catálogos guardados en MongoDB")
        
        # 2. CLIENTES
        clientes, clientes_map = transformar_clientes(mysql_conn)
        if clientes:
            mongo_db.clientes.insert_many(clientes)
            print("💾 Clientes guardados en MongoDB")
        
        # 3. ASESORES
        asesores, asesores_map = transformar_asesores(mysql_conn)
        if asesores:
            mongo_db.asesores.insert_many(asesores)
            print("💾 Asesores guardados en MongoDB")
        
        # 4. ESPECIALISTAS
        especialistas, especialistas_map = transformar_especialistas(mysql_conn)
        if especialistas:
            mongo_db.especialistas.insert_many(especialistas)
            print("💾 Especialistas guardados en MongoDB")
        
        # 5. PROVEEDORES
        proveedores, proveedores_map = transformar_proveedores(mysql_conn)
        if proveedores:
            mongo_db.proveedores.insert_many(proveedores)
            print("💾 Proveedores guardados en MongoDB")
        
        # 6. LABORATORIOS
        laboratorios, laboratorios_map = transformar_laboratorios(mysql_conn)
        if laboratorios:
            mongo_db.laboratorios.insert_many(laboratorios)
            print("💾 Laboratorios guardados en MongoDB")
        
        # 7. SUMINISTROS
        suministros, suministros_map = transformar_suministros(mysql_conn, proveedores_map, laboratorios_map)
        if suministros:
            mongo_db.suministros.insert_many(suministros)
            print("💾 Suministros guardados en MongoDB")
        
        # 8. PRODUCTOS
        productos, productos_map = transformar_productos(mysql_conn, suministros_map)
        if productos:
            mongo_db.productos.insert_many(productos)
            print("💾 Productos guardados en MongoDB")
        
        # 9. CITAS
        citas, citas_map = transformar_citas(mysql_conn, clientes_map, asesores_map, especialistas_map)
        if citas:
            mongo_db.citas.insert_many(citas)
            print("💾 Citas guardadas en MongoDB")
        
        # 10. EXÁMENES (con diagnósticos y fórmulas embebidos)
        examenes = transformar_examenes(mysql_conn, clientes_map, especialistas_map, citas_map)
        if examenes:
            mongo_db.examenes.insert_many(examenes)
            print("💾 Exámenes guardados en MongoDB")
        
        # 11. VENTAS (con items y factura embebidos)
        ventas = transformar_ventas(mysql_conn, clientes_map, asesores_map, productos_map)
        if ventas:
            mongo_db.ventas.insert_many(ventas)
            print("💾 Ventas guardadas en MongoDB")
        
        # 12. DEVOLUCIONES
        # devoluciones = transformar_devoluciones(mysql_conn, None, asesores_map)
        # if devoluciones:
        #     mongo_db.devoluciones.insert_many(devoluciones)
        #     print("💾 Devoluciones guardadas en MongoDB")
        
        # VALIDACIÓN FINAL
        print("\n" + "=" * 80)
        print("📊 VALIDACIÓN DE DATOS MIGRADOS:")
        print("=" * 80)
        print(f"Catálogos:      {mongo_db.catalogos.count_documents({})}")
        print(f"Clientes:       {mongo_db.clientes.count_documents({})}")
        print(f"Asesores:       {mongo_db.asesores.count_documents({})}")
        print(f"Especialistas:  {mongo_db.especialistas.count_documents({})}")
        print(f"Proveedores:    {mongo_db.proveedores.count_documents({})}")
        print(f"Laboratorios:   {mongo_db.laboratorios.count_documents({})}")
        print(f"Suministros:    {mongo_db.suministros.count_documents({})}")
        print(f"Productos:      {mongo_db.productos.count_documents({})}")
        print(f"Citas:          {mongo_db.citas.count_documents({})}")
        print(f"Exámenes:       {mongo_db.examenes.count_documents({})}")
        print(f"Ventas:         {mongo_db.ventas.count_documents({})}")
        # print(f"Devoluciones:   {mongo_db.devoluciones.count_documents({})}")
        
        print("\n✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
        
    except Exception as e:
        print(f"\n❌ Error durante la migración: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        mysql_conn.close()
        print("\n🔒 Conexiones cerradas")

# ============================================================================
# EJECUTAR MIGRACIÓN
# ============================================================================

if __name__ == "__main__":
    migrar()
