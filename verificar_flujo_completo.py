"""
Verificación del flujo completo: Examen → Pedido Laboratorio → Producto → Venta
Muestra la trazabilidad end-to-end de productos personalizados
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
print("VERIFICACIÓN: FLUJO COMPLETO DE PRODUCTOS PERSONALIZADOS")
print("=" * 80)

# Estadísticas generales
print("\n📊 ESTADÍSTICAS GENERALES")
print("-" * 80)

total_examenes = db.examenes.count_documents({})
examenes_con_pedido = db.examenes.count_documents({"pedido_laboratorio_ref": {"$exists": True, "$ne": None}})
total_pedidos = db.pedidos_laboratorio.count_documents({})
productos_personalizados = db.productos.count_documents({"pedido_laboratorio_ref": {"$exists": True, "$ne": None}})
ventas_con_examen = db.ventas.count_documents({"examen_ref": {"$exists": True, "$ne": None}})

print(f"\n✅ Total examenes: {total_examenes}")
print(f"✅ Examenes con pedido laboratorio: {examenes_con_pedido} ({examenes_con_pedido/total_examenes*100:.1f}%)")
print(f"✅ Total pedidos laboratorio: {total_pedidos}")
print(f"✅ Productos personalizados: {productos_personalizados}")
print(f"✅ Ventas vinculadas a examen: {ventas_con_examen}")

# Pedidos por estado
print("\n📋 PEDIDOS LABORATORIO POR ESTADO")
print("-" * 80)

pipeline_estados = [
    {
        "$group": {
            "_id": "$estado",
            "count": {"$sum": 1}
        }
    },
    {
        "$sort": {"count": -1}
    }
]

for resultado in db.pedidos_laboratorio.aggregate(pipeline_estados):
    print(f"   {resultado['_id']}: {resultado['count']}")

# Flujo completo de ejemplo
print("\n\n🔍 EJEMPLOS DE FLUJO COMPLETO")
print("=" * 80)

# Consulta: Ventas con trazabilidad completa
pipeline_flujo = [
    {
        "$match": {
            "examen_ref": {"$exists": True},
            "estado": "Completada"
        }
    },
    {
        "$lookup": {
            "from": "examenes",
            "localField": "examen_ref",
            "foreignField": "_id",
            "as": "examen"
        }
    },
    {"$unwind": "$examen"},
    {
        "$lookup": {
            "from": "pedidos_laboratorio",
            "localField": "examen_ref",
            "foreignField": "examen_ref",
            "as": "pedido_lab"
        }
    },
    {"$unwind": "$pedido_lab"},
    {
        "$lookup": {
            "from": "productos",
            "localField": "pedido_lab.producto_ref",
            "foreignField": "_id",
            "as": "producto"
        }
    },
    {"$unwind": "$producto"},
    {
        "$lookup": {
            "from": "clientes",
            "localField": "cliente_ref",
            "foreignField": "_id",
            "as": "cliente"
        }
    },
    {"$unwind": "$cliente"},
    {
        "$project": {
            "numero_factura": 1,
            "fecha_compra": 1,
            "total": 1,
            "cliente_nombre": {"$concat": ["$cliente.nombre", " ", "$cliente.apellido"]},
            "examen_fecha": "$examen.fecha_examen",
            "diagnostico": "$examen.diagnostico.tipo.nombre",
            "pedido_numero": "$pedido_lab.numero_pedido",
            "pedido_laboratorio": "$pedido_lab.laboratorio_snapshot.nombre",
            "tipo_lente": "$pedido_lab.especificaciones.tipo_lente",
            "material": "$pedido_lab.especificaciones.material",
            "tratamientos": "$pedido_lab.especificaciones.tratamientos",
            "fecha_fabricacion": "$pedido_lab.fecha_solicitud",
            "fecha_entrega": "$pedido_lab.fecha_entrega_real",
            "producto_nombre": "$producto.nombre_producto",
            "producto_precio": "$producto.precio_venta"
        }
    },
    {"$limit": 3}
]

resultados = list(db.ventas.aggregate(pipeline_flujo))

if resultados:
    for i, venta in enumerate(resultados, 1):
        print(f"\n{'─' * 80}")
        print(f"CASO #{i}: VENTA CON TRAZABILIDAD COMPLETA")
        print(f"{'─' * 80}")
        
        print(f"\n1️⃣ VENTA")
        print(f"   Factura: {venta['numero_factura']}")
        print(f"   Fecha: {venta['fecha_compra'].strftime('%Y-%m-%d')}")
        print(f"   Cliente: {venta['cliente_nombre']}")
        print(f"   Total: ${venta['total']:,.2f}")
        
        print(f"\n2️⃣ EXAMEN ASOCIADO")
        print(f"   Fecha examen: {venta['examen_fecha'].strftime('%Y-%m-%d')}")
        print(f"   Diagnóstico: {venta['diagnostico']}")
        
        print(f"\n3️⃣ PEDIDO LABORATORIO")
        print(f"   Número: {venta['pedido_numero']}")
        print(f"   Laboratorio: {venta['pedido_laboratorio']}")
        print(f"   Tipo de lente: {venta['tipo_lente']}")
        print(f"   Material: {venta['material']}")
        print(f"   Tratamientos: {', '.join(venta['tratamientos'])}")
        print(f"   Solicitado: {venta['fecha_fabricacion'].strftime('%Y-%m-%d')}")
        if venta.get('fecha_entrega'):
            dias = (venta['fecha_entrega'] - venta['fecha_fabricacion']).days
            print(f"   Entregado: {venta['fecha_entrega'].strftime('%Y-%m-%d')} ({dias} días)")
        
        print(f"\n4️⃣ PRODUCTO PERSONALIZADO")
        print(f"   Nombre: {venta['producto_nombre']}")
        print(f"   Precio: ${venta['producto_precio']:,.2f}")
        
        print(f"\n🔗 FLUJO COMPLETO:")
        print(f"   Cliente → Cita → Examen ({venta['examen_fecha'].strftime('%Y-%m-%d')})")
        print(f"   → Pedido Lab ({venta['pedido_numero']})")
        print(f"   → Fabricación ({venta['pedido_laboratorio']})")
        print(f"   → Producto personalizado")
        print(f"   → Venta ({venta['numero_factura']}) - ${venta['total']:,.2f}")
else:
    print("\n⚠️  No hay ventas con flujo completo aún")

# Pedidos en proceso
print(f"\n\n{'=' * 80}")
print("📋 PEDIDOS EN PROCESO (PENDIENTES DE COMPLETAR)")
print("=" * 80)

pipeline_pendientes = [
    {
        "$match": {
            "estado": {"$in": ["Solicitado", "Confirmado", "En fabricación", "Control de calidad"]}
        }
    },
    {
        "$lookup": {
            "from": "clientes",
            "localField": "cliente_ref",
            "foreignField": "_id",
            "as": "cliente"
        }
    },
    {"$unwind": "$cliente"},
    {
        "$lookup": {
            "from": "examenes",
            "localField": "examen_ref",
            "foreignField": "_id",
            "as": "examen"
        }
    },
    {"$unwind": "$examen"},
    {
        "$project": {
            "numero_pedido": 1,
            "estado": 1,
            "fecha_solicitud": 1,
            "fecha_estimada_entrega": 1,
            "cliente_nombre": {"$concat": ["$cliente.nombre", " ", "$cliente.apellido"]},
            "laboratorio": "$laboratorio_snapshot.nombre",
            "tipo_lente": "$especificaciones.tipo_lente",
            "dias_transcurridos": {
                "$dateDiff": {
                    "startDate": "$fecha_solicitud",
                    "endDate": "$$NOW",
                    "unit": "day"
                }
            }
        }
    },
    {"$sort": {"fecha_solicitud": 1}}
]

pendientes = list(db.pedidos_laboratorio.aggregate(pipeline_pendientes))

if pendientes:
    for pedido in pendientes:
        print(f"\n📌 Pedido: {pedido['numero_pedido']}")
        print(f"   Estado: {pedido['estado']}")
        print(f"   Cliente: {pedido['cliente_nombre']}")
        print(f"   Laboratorio: {pedido['laboratorio']}")
        print(f"   Tipo lente: {pedido['tipo_lente']}")
        print(f"   Solicitado hace: {pedido['dias_transcurridos']} días")
        if pedido.get('fecha_estimada_entrega'):
            print(f"   Entrega estimada: {pedido['fecha_estimada_entrega'].strftime('%Y-%m-%d')}")
else:
    print("\n✅ No hay pedidos pendientes")

# Estadísticas de rendimiento
print(f"\n\n{'=' * 80}")
print("📈 ESTADÍSTICAS DE RENDIMIENTO")
print("=" * 80)

pipeline_stats = [
    {
        "$match": {
            "fecha_entrega_real": {"$exists": True}
        }
    },
    {
        "$addFields": {
            "dias_fabricacion": {
                "$dateDiff": {
                    "startDate": "$fecha_solicitud",
                    "endDate": "$fecha_entrega_real",
                    "unit": "day"
                }
            }
        }
    },
    {
        "$group": {
            "_id": {
                "laboratorio": "$laboratorio_snapshot.nombre",
                "tipo_lente": "$especificaciones.tipo_lente"
            },
            "total_pedidos": {"$sum": 1},
            "dias_promedio": {"$avg": "$dias_fabricacion"},
            "dias_minimo": {"$min": "$dias_fabricacion"},
            "dias_maximo": {"$max": "$dias_fabricacion"},
            "costo_promedio": {"$avg": "$costo_fabricacion"},
            "precio_venta_promedio": {"$avg": "$precio_venta_estimado"}
        }
    },
    {
        "$project": {
            "laboratorio": "$_id.laboratorio",
            "tipo_lente": "$_id.tipo_lente",
            "total_pedidos": 1,
            "dias_promedio": {"$round": ["$dias_promedio", 1]},
            "dias_minimo": 1,
            "dias_maximo": 1,
            "costo_promedio": {"$round": ["$costo_promedio", 2]},
            "precio_venta_promedio": {"$round": ["$precio_venta_promedio", 2]}
        }
    },
    {"$sort": {"total_pedidos": -1}}
]

stats = list(db.pedidos_laboratorio.aggregate(pipeline_stats))

if stats:
    print("\nPor Laboratorio y Tipo de Lente:")
    print("-" * 80)
    for stat in stats:
        print(f"\n🔬 {stat['laboratorio']} - {stat['tipo_lente']}")
        print(f"   Pedidos: {stat['total_pedidos']}")
        print(f"   Tiempo fabricación: {stat['dias_promedio']} días (min: {stat['dias_minimo']}, max: {stat['dias_maximo']})")
        print(f"   Costo promedio: ${stat['costo_promedio']:,.2f}")
        print(f"   Precio venta promedio: ${stat['precio_venta_promedio']:,.2f}")
        margen = ((stat['precio_venta_promedio'] - stat['costo_promedio']) / stat['costo_promedio']) * 100
        print(f"   Margen: {margen:.1f}%")
else:
    print("\n⚠️  No hay suficientes datos para estadísticas")

# Verificación de integridad
print(f"\n\n{'=' * 80}")
print("🔍 VERIFICACIÓN DE INTEGRIDAD REFERENCIAL")
print("=" * 80)

errores = []

# Verificar pedidos_laboratorio
pedidos = list(db.pedidos_laboratorio.find())
for pedido in pedidos:
    # Verificar examen bidireccional
    examen = db.examenes.find_one({"_id": pedido["examen_ref"]})
    if not examen:
        errores.append(f"Pedido {pedido['numero_pedido']}: examen_ref inválido")
    elif examen.get("pedido_laboratorio_ref") != pedido["_id"]:
        errores.append(f"Pedido {pedido['numero_pedido']}: relación bidireccional con examen rota")
    
    # Verificar producto bidireccional si existe
    if pedido.get("producto_ref"):
        producto = db.productos.find_one({"_id": pedido["producto_ref"]})
        if not producto:
            errores.append(f"Pedido {pedido['numero_pedido']}: producto_ref inválido")
        elif producto.get("pedido_laboratorio_ref") != pedido["_id"]:
            errores.append(f"Pedido {pedido['numero_pedido']}: relación bidireccional con producto rota")

# Verificar ventas con examen_ref
ventas_examen = list(db.ventas.find({"examen_ref": {"$exists": True, "$ne": None}}))
for venta in ventas_examen:
    examen = db.examenes.find_one({"_id": venta["examen_ref"]})
    if not examen:
        errores.append(f"Venta {venta['numero_factura']}: examen_ref inválido")

if errores:
    print(f"\n⚠️  {len(errores)} errores de integridad encontrados:")
    for error in errores[:10]:
        print(f"   ❌ {error}")
else:
    print("\n✅ Integridad referencial verificada correctamente")
    print("   • Todas las relaciones bidireccionales están correctas")
    print("   • No hay referencias huérfanas")

print("\n" + "=" * 80)
print("✅ VERIFICACIÓN COMPLETADA")
print("=" * 80)

print("\n📌 RESUMEN:")
print(f"   • Sistema operativo con {total_pedidos} pedidos laboratorio")
print(f"   • {productos_personalizados} productos personalizados creados")
print(f"   • {ventas_con_examen} ventas con trazabilidad completa")
print(f"   • {len(pendientes)} pedidos en proceso")
print(f"   • Integridad: {'✅ OK' if not errores else f'⚠️  {len(errores)} errores'}")

client.close()
