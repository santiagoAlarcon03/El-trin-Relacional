"""
Análisis de relación entre Laboratorio, Producto, Examen y Ventas
Detectar si falta la trazabilidad: Examen → Pedido Laboratorio → Producto
"""
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from bson import json_util
import json

load_dotenv()

client = MongoClient(os.getenv('MONGODB_URI'))
db = client['optica_db']

print("=" * 80)
print("ANÁLISIS DE RELACIÓN: LABORATORIO - PRODUCTO - EXAMEN")
print("=" * 80)

# 1. VERIFICAR ESTRUCTURA ACTUAL
print("\n1. ESTRUCTURA ACTUAL DE COLECCIONES")
print("-" * 80)

print("\n📊 EXAMENES - Campos disponibles:")
exam_sample = db.examenes.find_one()
if exam_sample:
    print(json.dumps(list(exam_sample.keys()), indent=2, ensure_ascii=False))

print("\n📦 PRODUCTOS - Campos disponibles:")
prod_sample = db.productos.find_one()
if prod_sample:
    print(json.dumps(list(prod_sample.keys()), indent=2, ensure_ascii=False))
    print(f"\n¿Tiene laboratorio_ref? {bool(prod_sample.get('laboratorio_ref'))}")
    print(f"¿Tiene examen_ref? {bool(prod_sample.get('examen_ref'))}")
    print(f"¿Tiene suministro_ref? {bool(prod_sample.get('suministro_ref'))}")

print("\n🛒 VENTAS - Campos disponibles:")
venta_sample = db.ventas.find_one()
if venta_sample:
    print(json.dumps(list(venta_sample.keys()), indent=2, ensure_ascii=False))
    print(f"\n¿Tiene examen_ref? {bool(venta_sample.get('examen_ref'))}")
    
print("\n🔬 SUMINISTROS - Campos disponibles:")
suministro_sample = db.suministros.find_one()
if suministro_sample:
    print(json.dumps(list(suministro_sample.keys()), indent=2, ensure_ascii=False))
    print(f"\n¿Tiene laboratorio_ref? {bool(suministro_sample.get('laboratorio_ref'))}")

# 2. VERIFICAR RELACIONES EXISTENTES
print("\n\n2. RELACIONES EXISTENTES")
print("-" * 80)

print("\n🔍 Productos con laboratorio_ref:")
prod_with_lab = db.productos.count_documents({'laboratorio_ref': {'$exists': True}})
print(f"   Total: {prod_with_lab} / {db.productos.count_documents({})}")

print("\n🔍 Productos con examen_ref:")
prod_with_exam = db.productos.count_documents({'examen_ref': {'$exists': True}})
print(f"   Total: {prod_with_exam} / {db.productos.count_documents({})}")

print("\n🔍 Ventas con examen_ref:")
venta_with_exam = db.ventas.count_documents({'examen_ref': {'$exists': True}})
print(f"   Total: {venta_with_exam} / {db.ventas.count_documents({})}")

print("\n🔍 Suministros con laboratorio_ref:")
sum_with_lab = db.suministros.count_documents({'laboratorio_ref': {'$exists': True}})
print(f"   Total: {sum_with_lab} / {db.suministros.count_documents({})}")

# 3. MOSTRAR FLUJO ACTUAL
print("\n\n3. FLUJO ACTUAL DE DATOS")
print("-" * 80)

print("\n📋 Flujo detectado:")
print("""
   1. EXAMEN (examenes)
      ├── cliente_ref
      ├── especialista_ref
      ├── cita_ref (bidireccional)
      └── formula (embebida) ⚠️ NO se conecta con producto/laboratorio
   
   2. SUMINISTRO (suministros)
      ├── proveedor_ref
      ├── laboratorio_ref (opcional)
      └── orden_compra_ref (opcional)
   
   3. PRODUCTO (productos)
      └── suministro_ref → Suministro
                           └── laboratorio_ref (opcional)
   
   4. VENTA (ventas)
      ├── cliente_ref
      ├── asesor_ref
      └── items[] (con producto_ref)
          └── producto_ref → Producto
                             └── suministro_ref → Suministro
""")

# 4. ANÁLISIS DEL PROBLEMA
print("\n4. PROBLEMA DETECTADO ⚠️")
print("-" * 80)

print("""
🚨 FALTA TRAZABILIDAD: EXAMEN → LABORATORIO → PRODUCTO

El flujo de negocio real debería ser:

   1. Cliente hace CITA
   2. Especialista realiza EXAMEN y genera FÓRMULA
   3. Cliente aprueba hacer los lentes formulados
   4. Óptica envía PEDIDO AL LABORATORIO con la fórmula del examen
   5. Laboratorio fabrica y entrega el PRODUCTO personalizado
   6. Óptica registra VENTA del producto al cliente

ACTUALMENTE NO EXISTE:
   ❌ Relación: examenes.formula → laboratorio (pedido personalizado)
   ❌ Relación: productos → examen_ref (producto hecho para examen específico)
   ❌ Relación: ventas → examen_ref (venta originada por un examen)
   ❌ Colección: pedidos_laboratorio (ordenes de fabricación personalizadas)

LO QUE SÍ EXISTE:
   ✅ ordenes_compra → Pedidos de inventario genérico (no personalizado)
   ✅ suministros → Inventario genérico recibido
   ✅ productos → Productos en stock (no necesariamente personalizados)
""")

# 5. PROPUESTA DE SOLUCIÓN
print("\n\n5. PROPUESTA DE SOLUCIÓN 💡")
print("-" * 80)

print("""
CREAR NUEVA COLECCIÓN: pedidos_laboratorio

Esquema propuesto:
{
  _id: ObjectId,
  numero_pedido: String (único),
  fecha_solicitud: Date,
  fecha_estimada_entrega: Date,
  fecha_entrega_real: Date (opcional),
  
  // Referencias
  cliente_ref: ObjectId → clientes,
  examen_ref: ObjectId → examenes,
  laboratorio_ref: ObjectId → laboratorios,
  asesor_ref: ObjectId → asesores,
  
  // Snapshot del examen (histórico)
  formula_snapshot: {
    ojo_derecho: { esfera, cilindro, eje, adicion },
    ojo_izquierdo: { esfera, cilindro, eje, adicion },
    distancia_pupilar: Number,
    observaciones: String
  },
  
  // Detalle del pedido
  tipo_lente: String, // "Monofocal", "Bifocal", "Progresivo", etc.
  material: String,    // "CR-39", "Policarbonato", "Alto índice", etc.
  tratamientos: [],    // ["Anti-reflejo", "Fotocromático", "Blue light"]
  
  // Precios y costos
  costo_fabricacion: Number,
  precio_venta_estimado: Number,
  
  // Estado
  estado: String, // "Solicitado", "En fabricación", "Completado", "Entregado", "Cancelado"
  historial_estados: [{
    estado: String,
    fecha: Date,
    usuario: String,
    observaciones: String
  }],
  
  // Producto resultante (cuando llega)
  producto_ref: ObjectId → productos (opcional, cuando se recibe),
  
  observaciones: String
}

RELACIONES BIDIRECCIONALES NUEVAS:
   • examenes ← pedidos_laboratorio → productos
   • laboratorios ← pedidos_laboratorio
   • ventas → examen_ref (opcional, si la venta viene de un examen)
""")

# 6. ESTADÍSTICAS ACTUALES
print("\n\n6. ESTADÍSTICAS ACTUALES")
print("-" * 80)

total_examenes = db.examenes.count_documents({})
total_productos = db.productos.count_documents({})
total_ventas = db.ventas.count_documents({})
total_labs = db.laboratorios.count_documents({})

print(f"\n📊 Total examenes: {total_examenes}")
print(f"📦 Total productos: {total_productos}")
print(f"🛒 Total ventas: {total_ventas}")
print(f"🔬 Total laboratorios: {total_labs}")
print(f"📋 Total suministros: {db.suministros.count_documents({})}")
print(f"🛒 Total órdenes de compra: {db.ordenes_compra.count_documents({})}")

# Verificar si hay fórmulas activas que podrían requerir productos
formulas_activas = db.examenes.count_documents({'formula.activa': True})
print(f"\n✨ Fórmulas activas (sin pedido asociado): {formulas_activas}")

print("\n" + "=" * 80)
print("CONCLUSIÓN:")
print("=" * 80)
print("""
Se necesita implementar el sistema de PEDIDOS AL LABORATORIO para trazabilidad
completa del flujo: Examen → Pedido Laboratorio → Producto Personalizado → Venta

¿Deseas implementar esta funcionalidad?
""")

client.close()
