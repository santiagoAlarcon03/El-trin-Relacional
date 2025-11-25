"""
Sistema de Gestión de Órdenes de Compra a Proveedores
======================================================

Este script implementa el sistema completo de órdenes de compra/pedidos
que la óptica hace a sus proveedores, estableciendo la trazabilidad completa
desde la solicitud hasta la recepción de suministros.

FLUJO COMPLETO:
1. Detectar necesidad (stock bajo)
2. Crear orden de compra al proveedor
3. Seguimiento de estado (Solicitado → En proceso → En tránsito → Recibido)
4. Recepción y registro como suministro
5. Actualización de inventario

RELACIONES:
- 1 Orden de Compra → 1 Proveedor
- 1 Orden de Compra → N Items (productos solicitados)
- 1 Orden de Compra → N Suministros (productos recibidos)
- 1 Suministro → 1 Orden de Compra (bidireccional)

Ejecución: python implementar_ordenes_compra.py
"""

from pymongo import MongoClient, ASCENDING, DESCENDING
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
from bson import ObjectId
import random

# Cargar variables de entorno
load_dotenv()

# Configuración
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb+srv://CamaroSS:Chevrolet@clusterbases.8qang0c.mongodb.net/?appName=ClusterBases')
MONGODB_DATABASE = 'optica_db'

print("=" * 80)
print("🛒 IMPLEMENTANDO SISTEMA DE ÓRDENES DE COMPRA A PROVEEDORES")
print("=" * 80)
print()

# Conectar a MongoDB
try:
    client = MongoClient(MONGODB_URI)
    db = client[MONGODB_DATABASE]
    print(f"✅ Conectado a MongoDB Atlas: {MONGODB_DATABASE}\n")
except Exception as e:
    print(f"❌ Error al conectar a MongoDB: {e}")
    exit(1)

# ============================================================================
# PASO 1: CREAR COLECCIÓN ORDENES_COMPRA CON SCHEMA DE VALIDACIÓN
# ============================================================================
print("=" * 80)
print("PASO 1: Creando colección 'ordenes_compra' con schema de validación")
print("=" * 80)
print()

try:
    # Eliminar colección si existe (para desarrollo)
    if "ordenes_compra" in db.list_collection_names():
        db.ordenes_compra.drop()
        print("⚠️  Colección 'ordenes_compra' existente eliminada para recrear")
    
    # Crear colección con validación
    db.create_collection("ordenes_compra", validator={
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["numero_orden", "fecha_solicitud", "proveedor_ref", "items", "estado", "total"],
            "properties": {
                "numero_orden": {
                    "bsonType": "string",
                    "description": "Número único de orden (ej: OC-2025-001)"
                },
                "fecha_solicitud": {
                    "bsonType": "date",
                    "description": "Fecha en que se generó la orden"
                },
                "fecha_estimada_entrega": {
                    "bsonType": "date",
                    "description": "Fecha estimada de entrega"
                },
                "fecha_entrega_real": {
                    "bsonType": "date",
                    "description": "Fecha real de recepción"
                },
                "proveedor_ref": {
                    "bsonType": "objectId",
                    "description": "Referencia al proveedor"
                },
                "proveedor_snapshot": {
                    "bsonType": "object",
                    "description": "Snapshot de datos del proveedor",
                    "properties": {
                        "nombre": {"bsonType": "string"},
                        "contacto_principal": {"bsonType": "string"},
                        "email": {"bsonType": "string"},
                        "telefono": {"bsonType": "string"}
                    }
                },
                "items": {
                    "bsonType": "array",
                    "minItems": 1,
                    "description": "Lista de productos solicitados",
                    "items": {
                        "bsonType": "object",
                        "required": ["tipo_suministro", "cantidad_solicitada", "precio_unitario_estimado", "subtotal"],
                        "properties": {
                            "tipo_suministro": {
                                "bsonType": "object",
                                "required": ["nombre"],
                                "properties": {
                                    "nombre": {"bsonType": "string"},
                                    "descripcion": {"bsonType": "string"}
                                }
                            },
                            "cantidad_solicitada": {
                                "bsonType": "int",
                                "minimum": 1
                            },
                            "cantidad_recibida": {
                                "bsonType": "int",
                                "minimum": 0,
                                "description": "Cantidad efectivamente recibida"
                            },
                            "precio_unitario_estimado": {
                                "bsonType": "double",
                                "minimum": 0
                            },
                            "precio_unitario_real": {
                                "bsonType": "double",
                                "minimum": 0
                            },
                            "subtotal": {
                                "bsonType": "double",
                                "minimum": 0
                            },
                            "suministro_ref": {
                                "bsonType": "objectId",
                                "description": "Referencia al suministro recibido (se crea al recibir)"
                            },
                            "observaciones": {"bsonType": "string"}
                        }
                    }
                },
                "estado": {
                    "enum": ["Solicitado", "Confirmado", "En proceso", "En tránsito", "Recibido", "Recibido parcial", "Cancelado"],
                    "description": "Estado actual de la orden"
                },
                "subtotal": {
                    "bsonType": "double",
                    "minimum": 0
                },
                "impuesto": {
                    "bsonType": "double",
                    "minimum": 0
                },
                "descuento": {
                    "bsonType": "double",
                    "minimum": 0
                },
                "total": {
                    "bsonType": "double",
                    "minimum": 0
                },
                "solicitado_por": {
                    "bsonType": "string",
                    "description": "Nombre de quien solicitó la orden"
                },
                "recibido_por": {
                    "bsonType": "string",
                    "description": "Nombre de quien recibió el pedido"
                },
                "observaciones": {
                    "bsonType": "string"
                },
                "historial_estados": {
                    "bsonType": "array",
                    "description": "Historial de cambios de estado",
                    "items": {
                        "bsonType": "object",
                        "properties": {
                            "estado": {"bsonType": "string"},
                            "fecha": {"bsonType": "date"},
                            "observacion": {"bsonType": "string"}
                        }
                    }
                }
            }
        }
    })
    
    print("✅ Colección 'ordenes_compra' creada con schema de validación")
    print()
    
except Exception as e:
    print(f"⚠️  Advertencia al crear colección: {e}")
    print("   Continuando con la ejecución...\n")

# ============================================================================
# PASO 2: CREAR ÍNDICES PARA ORDENES_COMPRA
# ============================================================================
print("=" * 80)
print("PASO 2: Creando índices para colección 'ordenes_compra'")
print("=" * 80)
print()

indices_creados = 0

try:
    db.ordenes_compra.create_index([("numero_orden", ASCENDING)], unique=True, name="idx_numero_orden_unique")
    print("✅ Índice único 'idx_numero_orden_unique' creado")
    indices_creados += 1
except Exception as e:
    print(f"⚠️  {e}")

try:
    db.ordenes_compra.create_index([("proveedor_ref", ASCENDING), ("fecha_solicitud", DESCENDING)], name="idx_proveedor_fecha")
    print("✅ Índice compuesto 'idx_proveedor_fecha' creado")
    indices_creados += 1
except Exception as e:
    print(f"⚠️  {e}")

try:
    db.ordenes_compra.create_index([("estado", ASCENDING)], name="idx_estado")
    print("✅ Índice 'idx_estado' creado")
    indices_creados += 1
except Exception as e:
    print(f"⚠️  {e}")

try:
    db.ordenes_compra.create_index([("fecha_solicitud", DESCENDING)], name="idx_fecha_solicitud")
    print("✅ Índice 'idx_fecha_solicitud' creado")
    indices_creados += 1
except Exception as e:
    print(f"⚠️  {e}")

try:
    db.ordenes_compra.create_index([("fecha_estimada_entrega", ASCENDING)], name="idx_fecha_estimada")
    print("✅ Índice 'idx_fecha_estimada' creado")
    indices_creados += 1
except Exception as e:
    print(f"⚠️  {e}")

try:
    db.ordenes_compra.create_index([("items.suministro_ref", ASCENDING)], name="idx_items_suministro")
    print("✅ Índice 'idx_items_suministro' creado (para relación bidireccional)")
    indices_creados += 1
except Exception as e:
    print(f"⚠️  {e}")

print(f"\n📊 Total de índices creados: {indices_creados}")
print()

# ============================================================================
# PASO 3: ACTUALIZAR SCHEMA DE SUMINISTROS (AGREGAR ORDEN_COMPRA_REF)
# ============================================================================
print("=" * 80)
print("PASO 3: Actualizando schema de 'suministros' con campo 'orden_compra_ref'")
print("=" * 80)
print()

try:
    db.command("collMod", "suministros", validator={
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["tipo", "cantidad", "precio_unitario", "fecha_ingreso", "proveedor_ref"],
            "properties": {
                "tipo": {
                    "bsonType": "object",
                    "required": ["nombre"],
                    "properties": {
                        "nombre": {"bsonType": "string"},
                        "descripcion": {"bsonType": "string"}
                    }
                },
                "cantidad": {
                    "bsonType": "int",
                    "minimum": 1
                },
                "precio_unitario": {
                    "bsonType": "double",
                    "minimum": 0
                },
                "fecha_ingreso": {"bsonType": "date"},
                "numero_lote": {"bsonType": "string"},
                "fecha_vencimiento": {"bsonType": "date"},
                "proveedor_ref": {
                    "bsonType": "objectId",
                    "description": "Referencia al proveedor"
                },
                "laboratorio_ref": {
                    "bsonType": "objectId",
                    "description": "Referencia al laboratorio (opcional)"
                },
                "orden_compra_ref": {
                    "bsonType": "objectId",
                    "description": "Referencia a la orden de compra que originó este suministro (bidireccional)"
                },
                "observaciones": {"bsonType": "string"}
            }
        }
    })
    print("✅ Schema de 'suministros' actualizado con campo 'orden_compra_ref'")
    print()
except Exception as e:
    print(f"⚠️  Advertencia: {e}")
    print("   Continuando con la ejecución...\n")

# ============================================================================
# PASO 4: CREAR ÍNDICE EN SUMINISTROS PARA ORDEN_COMPRA_REF
# ============================================================================
print("=" * 80)
print("PASO 4: Creando índice en 'suministros' para 'orden_compra_ref'")
print("=" * 80)
print()

try:
    db.suministros.create_index([("orden_compra_ref", ASCENDING)], name="idx_orden_compra_ref")
    print("✅ Índice 'idx_orden_compra_ref' creado en colección 'suministros'")
    print("   - Optimiza consultas: suministro → orden de compra (bidireccional)")
    print()
except Exception as e:
    if "already exists" in str(e):
        print("⚠️  Índice 'idx_orden_compra_ref' ya existe, saltando...")
        print()
    else:
        print(f"❌ Error: {e}\n")

# ============================================================================
# PASO 5: OBTENER DATOS BASE
# ============================================================================
print("=" * 80)
print("PASO 5: Obteniendo datos base (proveedores, laboratorios, catálogos)")
print("=" * 80)
print()

proveedores = list(db.proveedores.find({"activo": True}))
laboratorios = list(db.laboratorios.find({"activo": True}))
catalogos = db.catalogos.find_one({"_id": "catalogos_optica"})

print(f"📊 Proveedores disponibles: {len(proveedores)}")
print(f"📊 Laboratorios disponibles: {len(laboratorios)}")

if len(proveedores) == 0:
    print("❌ Error: No hay proveedores en la base de datos")
    client.close()
    exit(1)

# Tipos de suministro
if catalogos and 'tipos_suministro' in catalogos:
    tipos_suministro = catalogos['tipos_suministro']
else:
    tipos_suministro = [
        {"nombre": "Lentes oftálmicos", "descripcion": "Suministro para óptica"},
        {"nombre": "Lentes de contacto", "descripcion": "Suministro para óptica"},
        {"nombre": "Monturas", "descripcion": "Suministro para óptica"},
        {"nombre": "Accesorios", "descripcion": "Suministro para óptica"}
    ]

print(f"📋 Tipos de suministro disponibles: {len(tipos_suministro)}")
print()

# ============================================================================
# PASO 6: CREAR ÓRDENES DE COMPRA CON DATOS DE PRUEBA
# ============================================================================
print("=" * 80)
print("PASO 6: Creando órdenes de compra con datos de prueba")
print("=" * 80)
print()

ordenes_creadas = []
suministros_creados = []
fecha_actual = datetime.now()

# Crear 10 órdenes de compra
for i in range(1, 11):
    # Seleccionar proveedor aleatorio
    proveedor = random.choice(proveedores)
    
    # Calcular fechas (órdenes de los últimos 3 meses)
    dias_atras = random.randint(0, 90)
    fecha_solicitud = fecha_actual - timedelta(days=dias_atras)
    fecha_estimada = fecha_solicitud + timedelta(days=random.randint(7, 21))
    
    # Determinar estado según antigüedad
    if dias_atras <= 5:
        estado = random.choice(["Solicitado", "Confirmado"])
        fecha_entrega_real = None
    elif dias_atras <= 15:
        estado = random.choice(["En proceso", "En tránsito"])
        fecha_entrega_real = None
    else:
        estado = random.choice(["Recibido", "Recibido parcial"])
        fecha_entrega_real = fecha_solicitud + timedelta(days=random.randint(7, 20))
    
    # Crear items (2-4 tipos de suministros por orden)
    num_items = random.randint(2, 4)
    items = []
    subtotal = 0
    
    for j in range(num_items):
        tipo = random.choice(tipos_suministro)
        cantidad_solicitada = random.randint(50, 500)
        precio_unitario = round(random.uniform(20000, 150000), 2)
        item_subtotal = round(cantidad_solicitada * precio_unitario, 2)
        subtotal += item_subtotal
        
        # Si está recibido, agregar datos de recepción
        if estado in ["Recibido", "Recibido parcial"]:
            if estado == "Recibido parcial":
                cantidad_recibida = random.randint(int(cantidad_solicitada * 0.5), cantidad_solicitada)
            else:
                cantidad_recibida = cantidad_solicitada
            
            precio_real = round(precio_unitario * random.uniform(0.95, 1.05), 2)  # Variación ±5%
        else:
            cantidad_recibida = None
            precio_real = None
        
        item = {
            "tipo_suministro": tipo,
            "cantidad_solicitada": cantidad_solicitada,
            "cantidad_recibida": cantidad_recibida,
            "precio_unitario_estimado": precio_unitario,
            "precio_unitario_real": precio_real,
            "subtotal": item_subtotal,
            "observaciones": ""
        }
        
        # Agregar laboratorio_ref solo si existe
        if laboratorios and random.random() > 0.5:
            item["laboratorio_ref"] = random.choice(laboratorios)['_id']
        items.append(item)
    
    # Calcular totales
    descuento = round(subtotal * random.uniform(0, 0.10), 2)  # 0-10% descuento
    impuesto = round((subtotal - descuento) * 0.19, 2)  # IVA 19%
    total = round(subtotal - descuento + impuesto, 2)
    
    # Snapshot del proveedor
    proveedor_snapshot = {
        "nombre": proveedor.get('nombre', ''),
        "contacto_principal": proveedor.get('contacto_principal', ''),
        "email": proveedor.get('emails', [{}])[0].get('email', '') if proveedor.get('emails') else '',
        "telefono": proveedor.get('telefonos', [{}])[0].get('numero', '') if proveedor.get('telefonos') else ''
    }
    
    # Historial de estados
    historial = [
        {
            "estado": "Solicitado",
            "fecha": fecha_solicitud,
            "observacion": "Orden generada automáticamente por sistema"
        }
    ]
    
    if estado != "Solicitado":
        historial.append({
            "estado": "Confirmado",
            "fecha": fecha_solicitud + timedelta(hours=random.randint(2, 24)),
            "observacion": "Confirmado por proveedor"
        })
    
    if estado in ["En proceso", "En tránsito", "Recibido", "Recibido parcial"]:
        historial.append({
            "estado": "En proceso",
            "fecha": fecha_solicitud + timedelta(days=random.randint(1, 3)),
            "observacion": "Proveedor procesando orden"
        })
    
    if estado in ["En tránsito", "Recibido", "Recibido parcial"]:
        historial.append({
            "estado": "En tránsito",
            "fecha": fecha_solicitud + timedelta(days=random.randint(5, 10)),
            "observacion": "Pedido en camino"
        })
    
    if estado in ["Recibido", "Recibido parcial"]:
        historial.append({
            "estado": estado,
            "fecha": fecha_entrega_real,
            "observacion": "Pedido recibido en bodega" if estado == "Recibido" else "Recepción parcial por faltantes"
        })
    
    # Crear orden de compra
    nueva_orden = {
        "numero_orden": f"OC-2025-{i:04d}",
        "fecha_solicitud": fecha_solicitud,
        "fecha_estimada_entrega": fecha_estimada,
        "fecha_entrega_real": fecha_entrega_real,
        "proveedor_ref": proveedor['_id'],
        "proveedor_snapshot": proveedor_snapshot,
        "items": items,
        "estado": estado,
        "subtotal": subtotal,
        "impuesto": impuesto,
        "descuento": descuento,
        "total": total,
        "solicitado_por": random.choice(["Carlos Ruiz", "Laura Martínez", "Admin Sistema"]),
        "recibido_por": random.choice(["Carlos Ruiz", "Laura Martínez"]) if estado in ["Recibido", "Recibido parcial"] else None,
        "observaciones": f"Orden de compra #{i} para reposición de inventario",
        "historial_estados": historial
    }
    
    orden_result = db.ordenes_compra.insert_one(nueva_orden)
    orden_id = orden_result.inserted_id
    
    print(f"   ✅ Orden #{i}: {nueva_orden['numero_orden']}")
    print(f"      Proveedor: {proveedor_snapshot['nombre']}")
    print(f"      Fecha: {fecha_solicitud.date()} | Estado: {estado}")
    print(f"      Items: {len(items)} | Total: ${total:,.2f}")
    
    # Si está recibido, crear suministros y vincular bidireccional
    if estado in ["Recibido", "Recibido parcial"]:
        print(f"      📦 Creando suministros vinculados...")
        
        for idx, item in enumerate(items):
            if item['cantidad_recibida'] and item['cantidad_recibida'] > 0:
                # Crear suministro
                nuevo_suministro = {
                    "tipo": item['tipo_suministro'],
                    "cantidad": item['cantidad_recibida'],
                    "precio_unitario": item['precio_unitario_real'],
                    "fecha_ingreso": fecha_entrega_real,
                    "numero_lote": f"LOTE-2025-{len(suministros_creados) + 1000:04d}",
                    "fecha_vencimiento": fecha_entrega_real + timedelta(days=random.randint(365, 1095)),
                    "proveedor_ref": proveedor['_id'],
                    "orden_compra_ref": orden_id,  # ⭐ Referencia bidireccional
                    "observaciones": f"Recibido de orden {nueva_orden['numero_orden']}"
                }
                
                # Agregar laboratorio_ref solo si existe en el item
                if 'laboratorio_ref' in item and item['laboratorio_ref']:
                    nuevo_suministro["laboratorio_ref"] = item['laboratorio_ref']
                
                suministro_result = db.suministros.insert_one(nuevo_suministro)
                suministro_id = suministro_result.inserted_id
                
                # Actualizar item de la orden con referencia al suministro (bidireccional)
                db.ordenes_compra.update_one(
                    {"_id": orden_id},
                    {"$set": {f"items.{idx}.suministro_ref": suministro_id}}
                )
                
                suministros_creados.append(suministro_id)
                print(f"         ↔️ Suministro: {item['tipo_suministro']['nombre']} x{item['cantidad_recibida']} (ID: {suministro_id})")
    
    ordenes_creadas.append({
        "orden_id": orden_id,
        "numero_orden": nueva_orden['numero_orden'],
        "proveedor": proveedor_snapshot['nombre'],
        "estado": estado,
        "total": total
    })
    print()

print(f"✅ Total de órdenes creadas: {len(ordenes_creadas)}")
print(f"✅ Total de suministros creados: {len(suministros_creados)}")
print()

# ============================================================================
# PASO 7: VERIFICAR INTEGRIDAD DE RELACIONES BIDIRECCIONALES
# ============================================================================
print("=" * 80)
print("PASO 7: Verificando integridad de relaciones bidireccionales")
print("=" * 80)
print()

errores = 0

# Verificar órdenes → suministros
ordenes_recibidas = list(db.ordenes_compra.find({"estado": {"$in": ["Recibido", "Recibido parcial"]}}))
print(f"📊 Verificando {len(ordenes_recibidas)} órdenes recibidas...")

for orden in ordenes_recibidas:
    for item in orden.get('items', []):
        suministro_ref = item.get('suministro_ref')
        if suministro_ref:
            suministro = db.suministros.find_one({"_id": suministro_ref})
            if not suministro:
                print(f"   ❌ Orden {orden['numero_orden']} referencia suministro inexistente: {suministro_ref}")
                errores += 1
            elif suministro.get('orden_compra_ref') != orden['_id']:
                print(f"   ⚠️  Orden {orden['numero_orden']} → Suministro {suministro_ref}, pero la relación inversa no coincide")
                errores += 1

# Verificar suministros → órdenes
suministros_con_orden = list(db.suministros.find({"orden_compra_ref": {"$exists": True}}))
print(f"📊 Verificando {len(suministros_con_orden)} suministros con orden...")

for suministro in suministros_con_orden:
    orden_ref = suministro.get('orden_compra_ref')
    if orden_ref:
        orden = db.ordenes_compra.find_one({"_id": orden_ref})
        if not orden:
            print(f"   ❌ Suministro {suministro['_id']} referencia orden inexistente: {orden_ref}")
            errores += 1

if errores == 0:
    print("   ✅ Todas las relaciones bidireccionales son consistentes")
else:
    print(f"   ⚠️ Se encontraron {errores} errores de integridad")

print()

# ============================================================================
# PASO 8: ESTADÍSTICAS FINALES
# ============================================================================
print("=" * 80)
print("📊 ESTADÍSTICAS FINALES")
print("=" * 80)
print()

total_ordenes = db.ordenes_compra.count_documents({})
print(f"🛒 Total de órdenes de compra:        {total_ordenes}")

for estado in ["Solicitado", "Confirmado", "En proceso", "En tránsito", "Recibido", "Recibido parcial", "Cancelado"]:
    count = db.ordenes_compra.count_documents({"estado": estado})
    if count > 0:
        print(f"   └─ {estado}: {count}")

print()

total_suministros = db.suministros.count_documents({})
suministros_con_orden_count = db.suministros.count_documents({"orden_compra_ref": {"$exists": True, "$ne": None}})
suministros_sin_orden = total_suministros - suministros_con_orden_count

print(f"📦 Total de suministros:              {total_suministros}")
print(f"   └─ Con orden asociada:             {suministros_con_orden_count} ({(suministros_con_orden_count/total_suministros*100) if total_suministros > 0 else 0:.1f}%)")
print(f"   └─ Sin orden asociada:             {suministros_sin_orden} ({(suministros_sin_orden/total_suministros*100) if total_suministros > 0 else 0:.1f}%)")
print()

# Muestra de órdenes creadas
print("📋 MUESTRA DE ÓRDENES CREADAS (primeros 5):")
print()
for i, orden in enumerate(ordenes_creadas[:5], 1):
    print(f"{i}. {orden['numero_orden']}")
    print(f"   Proveedor: {orden['proveedor']}")
    print(f"   Estado: {orden['estado']}")
    print(f"   Total: ${orden['total']:,.2f}")
    print(f"   ID: {orden['orden_id']}")
    print()

# ============================================================================
# PASO 9: QUERY DE PRUEBA
# ============================================================================
print("=" * 80)
print("🔍 QUERY DE PRUEBA: Órdenes recibidas con sus suministros")
print("=" * 80)
print()

pipeline = [
    {
        "$match": {
            "estado": {"$in": ["Recibido", "Recibido parcial"]}
        }
    },
    {
        "$lookup": {
            "from": "proveedores",
            "localField": "proveedor_ref",
            "foreignField": "_id",
            "as": "proveedor"
        }
    },
    {
        "$unwind": "$proveedor"
    },
    {
        "$project": {
            "numero_orden": 1,
            "fecha_solicitud": 1,
            "fecha_entrega_real": 1,
            "proveedor_nombre": "$proveedor.nombre",
            "estado": 1,
            "total": 1,
            "num_items": {"$size": "$items"}
        }
    },
    {
        "$sort": {"fecha_entrega_real": -1}
    },
    {
        "$limit": 5
    }
]

resultados = list(db.ordenes_compra.aggregate(pipeline))
print(f"📊 Resultados encontrados: {len(resultados)}")
print()

for i, resultado in enumerate(resultados, 1):
    print(f"{i}. {resultado.get('numero_orden', 'N/A')}")
    print(f"   Proveedor: {resultado.get('proveedor_nombre', 'N/A')}")
    print(f"   Solicitada: {resultado.get('fecha_solicitud', 'N/A').date() if isinstance(resultado.get('fecha_solicitud'), datetime) else 'N/A'}")
    print(f"   Recibida: {resultado.get('fecha_entrega_real', 'N/A').date() if isinstance(resultado.get('fecha_entrega_real'), datetime) else 'N/A'}")
    print(f"   Items: {resultado.get('num_items', 0)} | Total: ${resultado.get('total', 0):,.2f}")
    print()

# ============================================================================
# FINALIZACIÓN
# ============================================================================
print("=" * 80)
print("✅ IMPLEMENTACIÓN COMPLETADA EXITOSAMENTE")
print("=" * 80)
print()
print("RESUMEN:")
print(f"1. ✅ Colección 'ordenes_compra' creada con schema de validación")
print(f"2. ✅ {indices_creados} índices creados en 'ordenes_compra'")
print(f"3. ✅ Schema de 'suministros' actualizado con 'orden_compra_ref'")
print(f"4. ✅ Índice bidireccional creado en 'suministros'")
print(f"5. ✅ {len(ordenes_creadas)} órdenes de compra creadas")
print(f"6. ✅ {len(suministros_creados)} suministros vinculados")
print(f"7. ✅ Verificación de integridad: {errores} errores encontrados")
print()
print("🎯 Sistema completo de órdenes de compra implementado con relaciones bidireccionales")
print()
print("FLUJO COMPLETO AHORA DISPONIBLE:")
print("┌──────────────┐   solicita   ┌──────────────┐   genera   ┌──────────────┐")
print("│    Óptica    │ ──────────→  │Orden Compra  │ ──────────→│  Suministro  │")
print("└──────────────┘              └──────────────┘             └──────────────┘")
print("                                     ↕                            ↕")
print("                              (bidireccional)             (bidireccional)")
print("                                     ↕                            ↕")
print("                              ┌──────────────┐             ┌──────────────┐")
print("                              │  Proveedor   │             │  Producto    │")
print("                              └──────────────┘             └──────────────┘")
print()

# Cerrar conexión
client.close()
print("🔌 Conexión cerrada")
print("=" * 80)
