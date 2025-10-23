"""
============================================================================
SCRIPT DE MIGRACIÓN AUTOMÁTICA: MySQL → MongoDB
Base de Datos: Optica
Fecha: Octubre 23, 2025
============================================================================

Este script conecta a MySQL, extrae los datos, los transforma aplicando
embedding y referencing según el diseño, y los carga en MongoDB Atlas.

Requisitos:
    pip install pymongo mysql-connector-python python-dotenv

Uso:
    python migracion_automatica.py
============================================================================
"""

import mysql.connector
from pymongo import MongoClient
from datetime import datetime
from bson.objectid import ObjectId
import os
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
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb+srv://admin_optica:password@optica-cluster.xxxxx.mongodb.net/')
MONGODB_DATABASE = 'Optica'

# ============================================================================
# CONEXIONES
# ============================================================================

def conectar_mysql():
    """Conectar a MySQL"""
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        print("✅ Conectado a MySQL")
        return conn
    except Exception as e:
        print(f"❌ Error conectando a MySQL: {e}")
        return None

def conectar_mongodb():
    """Conectar a MongoDB Atlas"""
    try:
        client = MongoClient(MONGODB_URI)
        db = client[MONGODB_DATABASE]
        # Verificar conexión
        client.admin.command('ping')
        print("✅ Conectado a MongoDB Atlas")
        return client, db
    except Exception as e:
        print(f"❌ Error conectando a MongoDB: {e}")
        return None, None

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

# ============================================================================
# FUNCIONES DE TRANSFORMACIÓN
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
    
    # Mapeo de IDs MySQL → ObjectId MongoDB
    id_map = {}
    clientes_mongo = []
    
    for cliente in clientes:
        # Generar ObjectId para MongoDB
        mongo_id = ObjectId()
        id_map[cliente['id_cliente']] = mongo_id
        
        # Filtrar direcciones del cliente
        dirs_cliente = [
            {
                'tipo': d.get('tipo_direccion', 'Principal'),
                'calle': d['calle'],
                'ciudad': d['ciudad'],
                'estado': d.get('estado', ''),
                'codigo_postal': d.get('codigo_postal', ''),
                'pais': d.get('pais', 'Colombia'),
                'es_principal': d.get('es_principal', False)
            }
            for d in direcciones if d['id_cliente'] == cliente['id_cliente']
        ]
        
        # Filtrar teléfonos del cliente
        tels_cliente = [
            {
                'numero': t['telefono'],
                'tipo': t.get('tipo_telefono', 'Móvil'),
                'es_principal': t.get('es_principal', False)
            }
            for t in telefonos if t['id_cliente'] == cliente['id_cliente']
        ]
        
        # Documento MongoDB
        doc_mongo = {
            '_id': mongo_id,
            'nombre': cliente['nombre'],
            'apellido': cliente['apellido'],
            'email': cliente['email'],
            'fecha_nacimiento': cliente.get('fecha_nacimiento'),
            'documento': {
                'tipo': cliente.get('tipo_documento', 'CC'),
                'numero': cliente.get('numero_documento', '')
            },
            'direcciones': dirs_cliente,
            'telefonos': tels_cliente,
            'activo': bool(cliente.get('activo', True)),
            'fecha_registro': cliente.get('fecha_registro', datetime.now())
        }
        
        clientes_mongo.append(doc_mongo)
    
    print(f"✅ {len(clientes_mongo)} clientes transformados")
    return clientes_mongo, id_map

def transformar_asesores(mysql_conn):
    """
    Transforma: Asesor + TelefonoAsesor + EmailAsesor
    En: asesores (con embedding)
    """
    print("\n🔄 Transformando asesores...")
    
    asesores = extraer_tabla(mysql_conn, 'Asesor')
    telefonos = extraer_tabla(mysql_conn, 'TelefonoAsesor')
    emails = extraer_tabla(mysql_conn, 'EmailAsesor')
    
    id_map = {}
    asesores_mongo = []
    
    for asesor in asesores:
        mongo_id = ObjectId()
        id_map[asesor['id_asesor']] = mongo_id
        
        tels = [
            {'numero': t['telefono'], 'tipo': t.get('tipo_telefono', 'Móvil')}
            for t in telefonos if t['id_asesor'] == asesor['id_asesor']
        ]
        
        mails = [
            {'email': e['email'], 'tipo': e.get('tipo_email', 'Corporativo')}
            for e in emails if e['id_asesor'] == asesor['id_asesor']
        ]
        
        doc_mongo = {
            '_id': mongo_id,
            'nombre': asesor['nombre'],
            'apellido': asesor['apellido'],
            'numero_documento': asesor['numero_documento'],
            'fecha_contratacion': asesor.get('fecha_contratacion'),
            'telefonos': tels,
            'emails': mails,
            'activo': bool(asesor.get('activo', True))
        }
        
        asesores_mongo.append(doc_mongo)
    
    print(f"✅ {len(asesores_mongo)} asesores transformados")
    return asesores_mongo, id_map

def transformar_especialistas(mysql_conn):
    """
    Transforma: Especialista + EspecialistaEspecialidad + contactos
    En: especialistas (con embedding)
    """
    print("\n🔄 Transformando especialistas...")
    
    especialistas = extraer_tabla(mysql_conn, 'Especialista')
    esp_especialidad = extraer_tabla(mysql_conn, 'EspecialistaEspecialidad')
    especialidades = extraer_tabla(mysql_conn, 'Especialidad')
    telefonos = extraer_tabla(mysql_conn, 'TelefonoEspecialista')
    emails = extraer_tabla(mysql_conn, 'EmailEspecialista')
    
    id_map = {}
    especialistas_mongo = []
    
    for esp in especialistas:
        mongo_id = ObjectId()
        id_map[esp['id_especialista']] = mongo_id
        
        # Obtener especialidades del especialista
        ids_esp = [
            ee['id_especialidad'] 
            for ee in esp_especialidad 
            if ee['id_especialista'] == esp['id_especialista']
        ]
        
        especialidades_doc = []
        for ee in esp_especialidad:
            if ee['id_especialista'] == esp['id_especialista']:
                esp_info = next((e for e in especialidades if e['id_especialidad'] == ee['id_especialidad']), None)
                if esp_info:
                    especialidades_doc.append({
                        'nombre': esp_info['nombre_especialidad'],
                        'descripcion': esp_info.get('descripcion', ''),
                        'fecha_certificacion': ee.get('fecha_certificacion')
                    })
        
        tels = [
            {'numero': t['telefono'], 'tipo': t.get('tipo_telefono', 'Móvil')}
            for t in telefonos if t['id_especialista'] == esp['id_especialista']
        ]
        
        mails = [
            {'email': e['email'], 'tipo': e.get('tipo_email', 'Profesional')}
            for e in emails if e['id_especialista'] == esp['id_especialista']
        ]
        
        doc_mongo = {
            '_id': mongo_id,
            'nombre': esp['nombre'],
            'apellido': esp['apellido'],
            'numero_licencia': esp.get('numero_licencia', ''),
            'numero_documento': esp['numero_documento'],
            'especialidades': especialidades_doc,
            'telefonos': tels,
            'emails': mails,
            'activo': bool(esp.get('activo', True))
        }
        
        especialistas_mongo.append(doc_mongo)
    
    print(f"✅ {len(especialistas_mongo)} especialistas transformados")
    return especialistas_mongo, id_map

def transformar_productos(mysql_conn, suministros_map):
    """
    Transforma: Producto + TipoProducto
    En: productos (con embedding de tipo)
    """
    print("\n🔄 Transformando productos...")
    
    productos = extraer_tabla(mysql_conn, 'Producto')
    tipos = extraer_tabla(mysql_conn, 'TipoProducto')
    
    id_map = {}
    productos_mongo = []
    
    for prod in productos:
        mongo_id = ObjectId()
        id_map[prod['id_producto']] = mongo_id
        
        # Buscar tipo
        tipo_info = next((t for t in tipos if t['id_tipo'] == prod['id_tipo']), None)
        
        doc_mongo = {
            '_id': mongo_id,
            'nombre': prod['nombre_producto'],
            'codigo_barras': prod.get('codigo_barras', ''),
            'tipo': {
                'nombre': tipo_info['nombre_tipo'] if tipo_info else '',
                'categoria': tipo_info.get('categoria', '') if tipo_info else ''
            },
            'marca': prod.get('marca', ''),
            'descripcion': prod.get('descripcion', ''),
            'precio_venta': float(prod['precio_venta']),
            'stock': {
                'actual': int(prod['stock']),
                'minimo': int(prod.get('stock_minimo', 5))
            },
            'suministro_ref': suministros_map.get(prod.get('id_suministro')) if prod.get('id_suministro') else None,
            'activo': bool(prod.get('activo', True)),
            'fecha_creacion': prod.get('fecha_creacion', datetime.now())
        }
        
        productos_mongo.append(doc_mongo)
    
    print(f"✅ {len(productos_mongo)} productos transformados")
    return productos_mongo, id_map

def transformar_ventas(mysql_conn, clientes_map, asesores_map, productos_map):
    """
    Transforma: Compra + DetalleCompra + Factura + MetodoPago
    En: ventas (con embedding de items y factura)
    """
    print("\n🔄 Transformando ventas...")
    
    compras = extraer_tabla(mysql_conn, 'Compra')
    detalles = extraer_tabla(mysql_conn, 'DetalleCompra')
    facturas = extraer_tabla(mysql_conn, 'Factura')
    metodos = extraer_tabla(mysql_conn, 'MetodoPago')
    productos = extraer_tabla(mysql_conn, 'Producto')
    
    ventas_mongo = []
    
    for compra in compras:
        mongo_id = ObjectId()
        
        # Buscar método de pago
        metodo = next((m for m in metodos if m['id_metodo'] == compra['id_metodo']), None)
        
        # Buscar factura
        factura = next((f for f in facturas if f['id_compra'] == compra['id_compra']), None)
        
        # Buscar items
        items_compra = [d for d in detalles if d['id_compra'] == compra['id_compra']]
        
        items_mongo = []
        for item in items_compra:
            prod = next((p for p in productos if p['id_producto'] == item['id_producto']), None)
            items_mongo.append({
                'producto_ref': productos_map.get(item['id_producto']),
                'producto_info': {
                    'nombre': prod['nombre_producto'] if prod else '',
                    'codigo_barras': prod.get('codigo_barras', '') if prod else ''
                },
                'cantidad': int(item['cantidad']),
                'precio_unitario': float(item['precio_unitario']),
                'subtotal': float(item['subtotal']),
                'descuento': float(item.get('descuento', 0)),
                'total': float(item['total'])
            })
        
        doc_mongo = {
            '_id': mongo_id,
            'numero_factura': factura['numero_factura'] if factura else f"F-{compra['id_compra']}",
            'fecha_compra': compra['fecha_compra'],
            'cliente_ref': clientes_map.get(compra['id_cliente']),
            'asesor_ref': asesores_map.get(compra['id_asesor']),
            'metodo_pago': {
                'nombre': metodo['nombre_metodo'] if metodo else '',
                'activo': bool(metodo.get('activo', True)) if metodo else True
            },
            'items': items_mongo,
            'subtotal': float(compra['subtotal']),
            'descuento': float(compra.get('descuento', 0)),
            'impuesto': float(compra.get('impuesto', 0)),
            'total': float(compra['total']),
            'estado': compra.get('estado', 'Completada'),
            'observaciones': compra.get('observaciones', '')
        }
        
        ventas_mongo.append(doc_mongo)
    
    print(f"✅ {len(ventas_mongo)} ventas transformadas")
    return ventas_mongo

# ============================================================================
# FUNCIÓN PRINCIPAL DE MIGRACIÓN
# ============================================================================

def migrar():
    """Función principal de migración"""
    
    print("=" * 80)
    print("INICIANDO MIGRACIÓN: MySQL → MongoDB Atlas")
    print("=" * 80)
    
    # Conectar a bases de datos
    mysql_conn = conectar_mysql()
    mongo_client, mongo_db = conectar_mongodb()
    
    if not mysql_conn or not mongo_db:
        print("❌ Error en las conexiones. Abortando migración.")
        return
    
    try:
        # Limpiar colecciones existentes (opcional)
        print("\n🗑️  Limpiando colecciones existentes...")
        for coleccion in ['clientes', 'asesores', 'especialistas', 'productos', 'ventas']:
            mongo_db[coleccion].delete_many({})
        print("✅ Colecciones limpiadas")
        
        # 1. Migrar Clientes
        clientes, clientes_map = transformar_clientes(mysql_conn)
        if clientes:
            mongo_db.clientes.insert_many(clientes)
            print(f"✅ {len(clientes)} clientes insertados en MongoDB")
        
        # 2. Migrar Asesores
        asesores, asesores_map = transformar_asesores(mysql_conn)
        if asesores:
            mongo_db.asesores.insert_many(asesores)
            print(f"✅ {len(asesores)} asesores insertados en MongoDB")
        
        # 3. Migrar Especialistas
        especialistas, especialistas_map = transformar_especialistas(mysql_conn)
        if especialistas:
            mongo_db.especialistas.insert_many(especialistas)
            print(f"✅ {len(especialistas)} especialistas insertados en MongoDB")
        
        # 4. Migrar Suministros (necesario para productos)
        # Nota: Implementar similar a las funciones anteriores
        suministros_map = {}  # Placeholder
        
        # 5. Migrar Productos
        productos, productos_map = transformar_productos(mysql_conn, suministros_map)
        if productos:
            mongo_db.productos.insert_many(productos)
            print(f"✅ {len(productos)} productos insertados en MongoDB")
        
        # 6. Migrar Ventas
        ventas = transformar_ventas(mysql_conn, clientes_map, asesores_map, productos_map)
        if ventas:
            mongo_db.ventas.insert_many(ventas)
            print(f"✅ {len(ventas)} ventas insertadas en MongoDB")
        
        print("\n" + "=" * 80)
        print("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
        print("=" * 80)
        
        # Resumen
        print("\n📊 RESUMEN:")
        print(f"   Clientes: {mongo_db.clientes.count_documents({})}")
        print(f"   Asesores: {mongo_db.asesores.count_documents({})}")
        print(f"   Especialistas: {mongo_db.especialistas.count_documents({})}")
        print(f"   Productos: {mongo_db.productos.count_documents({})}")
        print(f"   Ventas: {mongo_db.ventas.count_documents({})}")
        
    except Exception as e:
        print(f"\n❌ Error durante la migración: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cerrar conexiones
        if mysql_conn:
            mysql_conn.close()
            print("\n✅ Conexión MySQL cerrada")
        if mongo_client:
            mongo_client.close()
            print("✅ Conexión MongoDB cerrada")

# ============================================================================
# EJECUTAR MIGRACIÓN
# ============================================================================

if __name__ == "__main__":
    migrar()
