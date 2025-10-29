"""
Script para crear índices en MongoDB Atlas - optica_db
Ejecución rápida: python crear_indices.py
"""

from pymongo import MongoClient, ASCENDING, DESCENDING, TEXT
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

# Configuración
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb+srv://CamaroSS:Chevrolet@clusterbases.8qang0c.mongodb.net/?appName=ClusterBases')
MONGODB_DATABASE = 'optica_db'

print("=" * 80)
print("🔧 CREANDO ÍNDICES EN MONGODB ATLAS")
print("=" * 80)

# Conectar a MongoDB
client = MongoClient(MONGODB_URI)
db = client[MONGODB_DATABASE]

print(f"✅ Conectado a MongoDB Atlas: {MONGODB_DATABASE}\n")

def crear_indice_seguro(collection, keys, **kwargs):
    """Crear índice manejando errores de duplicados"""
    try:
        collection.create_index(keys, **kwargs)
        return True
    except Exception as e:
        if "already exists" in str(e) or "11000" in str(e):
            print(f"      ⚠️  {kwargs.get('name', 'índice')} ya existe, saltando...")
            return False
        else:
            print(f"      ❌ Error: {str(e)[:80]}")
            return False

total_indices = 0

# ============================================================================
# 2. CLIENTES
# ============================================================================
print("2. Creando índices para clientes...")
crear_indice_seguro(db.clientes, [("email", ASCENDING)], unique=True, name="idx_email_unique")
crear_indice_seguro(db.clientes, [("documento.numero", ASCENDING)], unique=True, sparse=True, name="idx_documento_numero")
crear_indice_seguro(db.clientes, [("nombre", ASCENDING), ("apellido", ASCENDING)], name="idx_nombre_completo")
crear_indice_seguro(db.clientes, [("activo", ASCENDING)], name="idx_activo")
crear_indice_seguro(db.clientes, [("direcciones.ciudad", ASCENDING)], name="idx_ciudad")
print("   ✅ 5 índices procesados")
total_indices += 5

# ============================================================================
# 3. ASESORES
# ============================================================================
print("3. Creando índices para asesores...")
db.asesores.create_index([("numero_documento", ASCENDING)], unique=True, name="idx_documento")
db.asesores.create_index([("nombre", ASCENDING), ("apellido", ASCENDING)], name="idx_nombre_completo")
db.asesores.create_index([("activo", ASCENDING)], name="idx_activo")
db.asesores.create_index([("emails.email", ASCENDING)], name="idx_email")
print("   ✅ 4 índices creados")
total_indices += 4

# ============================================================================
# 4. ESPECIALISTAS
# ============================================================================
print("4. Creando índices para especialistas...")
db.especialistas.create_index([("numero_documento", ASCENDING)], unique=True, name="idx_documento")
db.especialistas.create_index([("numero_licencia", ASCENDING)], unique=True, sparse=True, name="idx_licencia")
db.especialistas.create_index([("nombre", ASCENDING), ("apellido", ASCENDING)], name="idx_nombre_completo")
db.especialistas.create_index([("activo", ASCENDING)], name="idx_activo")
db.especialistas.create_index([("especialidades.nombre", ASCENDING)], name="idx_especialidad")
print("   ✅ 5 índices creados")
total_indices += 5

# ============================================================================
# 5. PROVEEDORES
# ============================================================================
print("5. Creando índices para proveedores...")
try:
    db.proveedores.create_index([("nombre_proveedor", ASCENDING)], unique=True, sparse=True, name="idx_nombre")
except Exception as e:
    print(f"   ⚠️  idx_nombre ya existe o error: {str(e)[:50]}")
db.proveedores.create_index([("activo", ASCENDING)], name="idx_activo")
db.proveedores.create_index([("direcciones.ciudad", ASCENDING)], name="idx_ciudad")
db.proveedores.create_index([("emails.email", ASCENDING)], name="idx_email")
print("   ✅ 4 índices creados")
total_indices += 4

# ============================================================================
# 6. LABORATORIOS
# ============================================================================
print("6. Creando índices para laboratorios...")
db.laboratorios.create_index([("nombre_laboratorio", ASCENDING)], unique=True, name="idx_nombre")
db.laboratorios.create_index([("activo", ASCENDING)], name="idx_activo")
db.laboratorios.create_index([("direcciones.ciudad", ASCENDING)], name="idx_ciudad")
print("   ✅ 3 índices creados")
total_indices += 3

# ============================================================================
# 7. SUMINISTROS
# ============================================================================
print("7. Creando índices para suministros...")
db.suministros.create_index([("fecha_ingreso", DESCENDING)], name="idx_fecha_ingreso")
db.suministros.create_index([("fecha_vencimiento", ASCENDING)], name="idx_fecha_vencimiento")
db.suministros.create_index([("proveedor_ref", ASCENDING)], name="idx_proveedor_ref")
db.suministros.create_index([("laboratorio_ref", ASCENDING)], name="idx_laboratorio_ref")
db.suministros.create_index([("numero_lote", ASCENDING)], name="idx_numero_lote")
db.suministros.create_index([("tipo.nombre", ASCENDING), ("proveedor_ref", ASCENDING)], name="idx_tipo_proveedor")
print("   ✅ 6 índices creados")
total_indices += 6

# ============================================================================
# 8. PRODUCTOS
# ============================================================================
print("8. Creando índices para productos...")
db.productos.create_index([("codigo_barras", ASCENDING)], unique=True, sparse=True, name="idx_codigo_barras")
db.productos.create_index([("nombre_producto", ASCENDING)], name="idx_nombre_producto")
db.productos.create_index([("tipo.nombre", ASCENDING)], name="idx_tipo")
db.productos.create_index([("marca", ASCENDING)], name="idx_marca")
db.productos.create_index([("activo", ASCENDING)], name="idx_activo")
db.productos.create_index([("stock", ASCENDING)], name="idx_stock")
db.productos.create_index([("suministro_ref", ASCENDING)], name="idx_suministro_ref")
db.productos.create_index([("activo", ASCENDING), ("stock", ASCENDING)], name="idx_activo_stock")
db.productos.create_index([("nombre_producto", TEXT), ("descripcion", TEXT)], name="idx_text_search", default_language="spanish")
print("   ✅ 9 índices creados")
total_indices += 9

# ============================================================================
# 9. CITAS
# ============================================================================
print("9. Creando índices para citas...")
db.citas.create_index([("fecha_cita", ASCENDING)], name="idx_fecha_cita")
db.citas.create_index([("cliente_ref", ASCENDING)], name="idx_cliente_ref")
db.citas.create_index([("especialista_ref", ASCENDING)], name="idx_especialista_ref")
db.citas.create_index([("asesor_ref", ASCENDING)], name="idx_asesor_ref")
db.citas.create_index([("estado", ASCENDING)], name="idx_estado")
db.citas.create_index([("especialista_ref", ASCENDING), ("fecha_cita", ASCENDING)], name="idx_especialista_fecha")
db.citas.create_index([("estado", ASCENDING), ("fecha_cita", ASCENDING)], name="idx_estado_fecha")
db.citas.create_index([("fecha_cita", ASCENDING), ("hora_cita", ASCENDING)], name="idx_fecha_hora")
print("   ✅ 8 índices creados")
total_indices += 8

# ============================================================================
# 10. EXAMENES
# ============================================================================
print("10. Creando índices para examenes...")
db.examenes.create_index([("fecha_examen", DESCENDING)], name="idx_fecha_examen")
db.examenes.create_index([("cliente_ref", ASCENDING)], name="idx_cliente_ref")
db.examenes.create_index([("especialista_ref", ASCENDING)], name="idx_especialista_ref")
db.examenes.create_index([("cita_ref", ASCENDING)], name="idx_cita_ref")
db.examenes.create_index([("cliente_ref", ASCENDING), ("fecha_examen", DESCENDING)], name="idx_cliente_fecha")
db.examenes.create_index([("diagnostico.tipo.nombre", ASCENDING)], name="idx_tipo_diagnostico")
db.examenes.create_index([("formula.activa", ASCENDING)], name="idx_formula_activa")
print("   ✅ 7 índices creados")
total_indices += 7

# ============================================================================
# 11. VENTAS
# ============================================================================
print("11. Creando índices para ventas...")
db.ventas.create_index([("fecha_compra", DESCENDING)], name="idx_fecha_compra")
db.ventas.create_index([("cliente_ref", ASCENDING)], name="idx_cliente_ref")
db.ventas.create_index([("asesor_ref", ASCENDING)], name="idx_asesor_ref")
db.ventas.create_index([("estado", ASCENDING)], name="idx_estado")
db.ventas.create_index([("numero_factura", ASCENDING)], unique=True, name="idx_numero_factura")
db.ventas.create_index([("cliente_ref", ASCENDING), ("fecha_compra", DESCENDING)], name="idx_cliente_fecha")
db.ventas.create_index([("asesor_ref", ASCENDING), ("fecha_compra", DESCENDING)], name="idx_asesor_fecha")
db.ventas.create_index([("items.producto_ref", ASCENDING)], name="idx_items_producto")
db.ventas.create_index([("estado", ASCENDING), ("fecha_compra", DESCENDING)], name="idx_estado_fecha")
db.ventas.create_index([("metodo_pago.nombre", ASCENDING)], name="idx_metodo_pago")
print("   ✅ 10 índices creados")
total_indices += 10

# ============================================================================
# RESUMEN
# ============================================================================
print("\n" + "=" * 80)
print("📊 RESUMEN DE ÍNDICES")
print("=" * 80)
print("\n1. catalogos:      0 índices (documento único)")
print("2. clientes:       5 índices")
print("3. asesores:       4 índices")
print("4. especialistas:  5 índices")
print("5. proveedores:    4 índices")
print("6. laboratorios:   3 índices")
print("7. suministros:    6 índices")
print("8. productos:      9 índices")
print("9. citas:          8 índices")
print("10. examenes:      7 índices")
print("11. ventas:        10 índices")
print("\n" + "=" * 80)
print(f"✅ TOTAL: {total_indices} índices creados exitosamente")
print("=" * 80)

# Verificar
print("\n🔍 Verificando índices creados:\n")
for col in ["clientes", "asesores", "especialistas", "proveedores", "laboratorios", 
            "suministros", "productos", "citas", "examenes", "ventas"]:
    indices = db[col].list_indexes()
    count = len(list(indices))
    print(f"   {col}: {count} índices")

client.close()
print("\n✅ Proceso completado! 🎉")
