"""
Implementación del sistema de PEDIDOS AL LABORATORIO
Flujo: Examen → Pedido Laboratorio → Producto Personalizado → Venta

Este script:
1. Crea la colección pedidos_laboratorio con schema validation
2. Crea índices para optimización
3. Actualiza schemas de examenes, productos y ventas
4. Genera datos de prueba vinculados
5. Verifica integridad referencial
"""

from pymongo import MongoClient, ASCENDING, DESCENDING
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
from bson import ObjectId
import random
from typing import List, Dict, Any

load_dotenv()

# Conexión a MongoDB
client = MongoClient(os.getenv('MONGODB_URI'))
db = client['optica_db']

print("=" * 80)
print("IMPLEMENTACIÓN: SISTEMA DE PEDIDOS AL LABORATORIO")
print("=" * 80)

# ============================================================================
# 1. CREAR COLECCIÓN pedidos_laboratorio CON SCHEMA VALIDATION
# ============================================================================

print("\n1. Creando colección 'pedidos_laboratorio' con schema validation...")

# Eliminar colección si existe (para pruebas)
if 'pedidos_laboratorio' in db.list_collection_names():
    db.pedidos_laboratorio.drop()
    print("   ⚠️  Colección existente eliminada")

# Schema validation para pedidos_laboratorio
pedidos_laboratorio_schema = {
    "bsonType": "object",
    "required": [
        "numero_pedido",
        "fecha_solicitud",
        "cliente_ref",
        "examen_ref",
        "laboratorio_ref",
        "formula_snapshot",
        "especificaciones",
        "estado",
        "costo_fabricacion"
    ],
    "properties": {
        "numero_pedido": {
            "bsonType": "string",
            "description": "Número único del pedido al laboratorio"
        },
        "fecha_solicitud": {
            "bsonType": "date",
            "description": "Fecha en que se solicitó el pedido"
        },
        "fecha_estimada_entrega": {
            "bsonType": ["date", "null"],
            "description": "Fecha estimada de entrega"
        },
        "fecha_entrega_real": {
            "bsonType": ["date", "null"],
            "description": "Fecha real de entrega del pedido"
        },
        "cliente_ref": {
            "bsonType": "objectId",
            "description": "Referencia al cliente"
        },
        "cliente_snapshot": {
            "bsonType": "object",
            "description": "Snapshot de datos del cliente",
            "properties": {
                "nombre": {"bsonType": "string"},
                "apellido": {"bsonType": "string"},
                "email": {"bsonType": "string"}
            }
        },
        "examen_ref": {
            "bsonType": "objectId",
            "description": "Referencia al examen que originó este pedido"
        },
        "laboratorio_ref": {
            "bsonType": "objectId",
            "description": "Referencia al laboratorio que fabricará"
        },
        "laboratorio_snapshot": {
            "bsonType": "object",
            "description": "Snapshot del laboratorio al momento del pedido",
            "properties": {
                "nombre": {"bsonType": "string"},
                "contacto": {"bsonType": "string"}
            }
        },
        "asesor_ref": {
            "bsonType": ["objectId", "null"],
            "description": "Asesor que gestionó el pedido"
        },
        "formula_snapshot": {
            "bsonType": "object",
            "required": ["ojo_derecho", "ojo_izquierdo", "distancia_pupilar"],
            "description": "Copia de la fórmula del examen para histórico",
            "properties": {
                "ojo_derecho": {
                    "bsonType": "object",
                    "properties": {
                        "esfera": {"bsonType": ["double", "null"]},
                        "cilindro": {"bsonType": ["double", "null"]},
                        "eje": {"bsonType": ["int", "null"]},
                        "adicion": {"bsonType": ["double", "null"]}
                    }
                },
                "ojo_izquierdo": {
                    "bsonType": "object",
                    "properties": {
                        "esfera": {"bsonType": ["double", "null"]},
                        "cilindro": {"bsonType": ["double", "null"]},
                        "eje": {"bsonType": ["int", "null"]},
                        "adicion": {"bsonType": ["double", "null"]}
                    }
                },
                "distancia_pupilar": {"bsonType": ["double", "null"]},
                "observaciones": {"bsonType": ["string", "null"]}
            }
        },
        "especificaciones": {
            "bsonType": "object",
            "required": ["tipo_lente", "material"],
            "description": "Especificaciones técnicas del pedido",
            "properties": {
                "tipo_lente": {
                    "bsonType": "string",
                    "enum": ["Monofocal", "Bifocal", "Progresivo", "Ocupacional", "Para lectura"],
                    "description": "Tipo de lente solicitado"
                },
                "material": {
                    "bsonType": "string",
                    "enum": ["CR-39", "Policarbonato", "Trivex", "Alto índice 1.67", "Alto índice 1.74"],
                    "description": "Material del lente"
                },
                "tratamientos": {
                    "bsonType": "array",
                    "items": {
                        "bsonType": "string",
                        "enum": ["Anti-reflejo", "Fotocromático", "Blue light", "UV400", "Anti-rayas", "Hidrofóbico"]
                    },
                    "description": "Tratamientos aplicados al lente"
                },
                "color_tinte": {
                    "bsonType": ["string", "null"],
                    "description": "Color del tinte si aplica"
                },
                "tipo_montaje": {
                    "bsonType": ["string", "null"],
                    "description": "Tipo de montaje en montura"
                }
            }
        },
        "costo_fabricacion": {
            "bsonType": "double",
            "minimum": 0,
            "description": "Costo de fabricación del laboratorio"
        },
        "precio_venta_estimado": {
            "bsonType": ["double", "null"],
            "minimum": 0,
            "description": "Precio estimado de venta al cliente"
        },
        "estado": {
            "bsonType": "string",
            "enum": ["Solicitado", "Confirmado", "En fabricación", "Control de calidad", "Completado", "Entregado", "Cancelado"],
            "description": "Estado actual del pedido"
        },
        "historial_estados": {
            "bsonType": "array",
            "items": {
                "bsonType": "object",
                "required": ["estado", "fecha", "usuario"],
                "properties": {
                    "estado": {"bsonType": "string"},
                    "fecha": {"bsonType": "date"},
                    "usuario": {"bsonType": "string"},
                    "observaciones": {"bsonType": ["string", "null"]}
                }
            },
            "description": "Historial de cambios de estado"
        },
        "producto_ref": {
            "bsonType": ["objectId", "null"],
            "description": "Referencia al producto creado cuando se recibe el pedido"
        },
        "observaciones": {
            "bsonType": ["string", "null"],
            "description": "Observaciones generales del pedido"
        }
    }
}

# Crear colección con validación
db.create_collection(
    "pedidos_laboratorio",
    validator={"$jsonSchema": pedidos_laboratorio_schema}
)

print("   ✅ Colección 'pedidos_laboratorio' creada con schema validation")

# ============================================================================
# 2. CREAR ÍNDICES PARA pedidos_laboratorio
# ============================================================================

print("\n2. Creando índices para 'pedidos_laboratorio'...")

indices_creados = 0

# Índice único para número de pedido
db.pedidos_laboratorio.create_index(
    [("numero_pedido", ASCENDING)],
    unique=True,
    name="idx_numero_pedido_unique"
)
indices_creados += 1

# Índice compuesto: laboratorio + fecha solicitud
db.pedidos_laboratorio.create_index(
    [("laboratorio_ref", ASCENDING), ("fecha_solicitud", DESCENDING)],
    name="idx_laboratorio_fecha"
)
indices_creados += 1

# Índice para estado
db.pedidos_laboratorio.create_index(
    [("estado", ASCENDING)],
    name="idx_estado"
)
indices_creados += 1

# Índice para cliente
db.pedidos_laboratorio.create_index(
    [("cliente_ref", ASCENDING), ("fecha_solicitud", DESCENDING)],
    name="idx_cliente_fecha"
)
indices_creados += 1

# Índice para examen (bidireccional)
db.pedidos_laboratorio.create_index(
    [("examen_ref", ASCENDING)],
    name="idx_examen_ref"
)
indices_creados += 1

# Índice para fecha de entrega estimada
db.pedidos_laboratorio.create_index(
    [("fecha_estimada_entrega", ASCENDING)],
    name="idx_fecha_estimada",
    sparse=True
)
indices_creados += 1

# Índice para producto resultante (bidireccional)
db.pedidos_laboratorio.create_index(
    [("producto_ref", ASCENDING)],
    name="idx_producto_ref",
    sparse=True
)
indices_creados += 1

print(f"   ✅ {indices_creados} índices creados")

# ============================================================================
# 3. ACTUALIZAR SCHEMAS DE COLECCIONES RELACIONADAS
# ============================================================================

print("\n3. Actualizando schemas de colecciones relacionadas...")

# 3.1 Actualizar schema de EXAMENES (agregar pedido_laboratorio_ref)
print("   📋 Actualizando schema de 'examenes'...")
db.command({
    "collMod": "examenes",
    "validator": {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["fecha_examen", "cliente_ref", "especialista_ref", "examen"],
            "properties": {
                "fecha_examen": {"bsonType": "date"},
                "cliente_ref": {"bsonType": "objectId"},
                "especialista_ref": {"bsonType": "objectId"},
                "cita_ref": {"bsonType": ["objectId", "null"]},
                "pedido_laboratorio_ref": {
                    "bsonType": ["objectId", "null"],
                    "description": "Referencia al pedido de laboratorio generado (bidireccional)"
                },
                "examen": {"bsonType": "object"},
                "diagnostico": {"bsonType": "object"},
                "formula": {"bsonType": "object"}
            }
        }
    }
})
print("   ✅ Schema de 'examenes' actualizado (+ pedido_laboratorio_ref)")

# Crear índice para pedido_laboratorio_ref en examenes
db.examenes.create_index(
    [("pedido_laboratorio_ref", ASCENDING)],
    name="idx_pedido_laboratorio_ref",
    sparse=True
)

# 3.2 Actualizar schema de PRODUCTOS (agregar pedido_laboratorio_ref)
print("   📦 Actualizando schema de 'productos'...")
db.command({
    "collMod": "productos",
    "validator": {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["nombre_producto", "tipo", "precio_venta", "stock"],
            "properties": {
                "nombre_producto": {"bsonType": "string"},
                "tipo": {"bsonType": "object"},
                "marca": {"bsonType": ["string", "null"]},
                "descripcion": {"bsonType": ["string", "null"]},
                "precio_venta": {"bsonType": "double", "minimum": 0},
                "stock": {"bsonType": "int", "minimum": 0},
                "stock_minimo": {"bsonType": ["int", "null"]},
                "codigo_barras": {"bsonType": ["string", "null"]},
                "suministro_ref": {"bsonType": ["objectId", "null"]},
                "pedido_laboratorio_ref": {
                    "bsonType": ["objectId", "null"],
                    "description": "Referencia al pedido de laboratorio que originó este producto (bidireccional)"
                },
                "activo": {"bsonType": "bool"},
                "fecha_creacion": {"bsonType": "date"},
                "imagenes": {"bsonType": ["array", "null"]},
                "embedding": {"bsonType": ["array", "null"]}
            }
        }
    }
})
print("   ✅ Schema de 'productos' actualizado (+ pedido_laboratorio_ref)")

# Crear índice para pedido_laboratorio_ref en productos
db.productos.create_index(
    [("pedido_laboratorio_ref", ASCENDING)],
    name="idx_pedido_laboratorio_ref",
    sparse=True
)

# 3.3 Actualizar schema de VENTAS (agregar examen_ref)
print("   🛒 Actualizando schema de 'ventas'...")
db.command({
    "collMod": "ventas",
    "validator": {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["numero_factura", "fecha_compra", "cliente_ref", "items", "total"],
            "properties": {
                "numero_factura": {"bsonType": "string"},
                "fecha_compra": {"bsonType": "date"},
                "metodo_pago": {"bsonType": "object"},
                "cliente_ref": {"bsonType": "objectId"},
                "asesor_ref": {"bsonType": ["objectId", "null"]},
                "examen_ref": {
                    "bsonType": ["objectId", "null"],
                    "description": "Referencia al examen que originó esta venta (opcional)"
                },
                "items": {
                    "bsonType": "array",
                    "minItems": 1
                },
                "subtotal": {"bsonType": "double"},
                "descuento": {"bsonType": "double"},
                "impuesto": {"bsonType": "double"},
                "total": {"bsonType": "double"},
                "estado": {"bsonType": "string"},
                "observaciones": {"bsonType": ["string", "null"]}
            }
        }
    }
})
print("   ✅ Schema de 'ventas' actualizado (+ examen_ref)")

# Crear índice para examen_ref en ventas
db.ventas.create_index(
    [("examen_ref", ASCENDING)],
    name="idx_examen_ref",
    sparse=True
)

# ============================================================================
# 4. GENERAR DATOS DE PRUEBA
# ============================================================================

print("\n4. Generando datos de prueba para pedidos_laboratorio...")

# Obtener datos necesarios
examenes = list(db.examenes.find())
clientes = list(db.clientes.find())
laboratorios = list(db.laboratorios.find())
asesores = list(db.asesores.find())

if not examenes or not laboratorios:
    print("   ⚠️  No hay examenes o laboratorios disponibles")
    client.close()
    exit(1)

# Tipos de lentes y materiales
tipos_lente = ["Monofocal", "Bifocal", "Progresivo", "Ocupacional", "Para lectura"]
materiales = ["CR-39", "Policarbonato", "Trivex", "Alto índice 1.67", "Alto índice 1.74"]
tratamientos_disponibles = ["Anti-reflejo", "Fotocromático", "Blue light", "UV400", "Anti-rayas", "Hidrofóbico"]
estados_posibles = ["Solicitado", "Confirmado", "En fabricación", "Control de calidad", "Completado", "Entregado"]

pedidos_creados = []
productos_creados = []

# Seleccionar 10 examenes para crear pedidos
examenes_para_pedidos = random.sample(examenes, min(10, len(examenes)))

for i, examen in enumerate(examenes_para_pedidos, 1):
    # Buscar datos del cliente
    cliente = db.clientes.find_one({"_id": examen["cliente_ref"]})
    if not cliente:
        continue
    
    # Seleccionar laboratorio aleatorio
    laboratorio = random.choice(laboratorios)
    
    # Seleccionar asesor aleatorio
    asesor = random.choice(asesores) if asesores else None
    
    # Fecha de solicitud (después del examen)
    fecha_examen = examen["fecha_examen"]
    fecha_solicitud = fecha_examen + timedelta(days=random.randint(1, 7))
    fecha_estimada = fecha_solicitud + timedelta(days=random.randint(7, 21))
    
    # Determinar estado y fecha entrega
    estado = random.choice(estados_posibles)
    fecha_entrega_real = None
    
    if estado in ["Completado", "Entregado"]:
        fecha_entrega_real = fecha_solicitud + timedelta(days=random.randint(10, 25))
    
    # Extraer fórmula del examen
    formula_snapshot = {
        "ojo_derecho": {
            "esfera": examen["examen"]["ojo_derecho"].get("esfera"),
            "cilindro": examen["examen"]["ojo_derecho"].get("cilindro"),
            "eje": examen["examen"]["ojo_derecho"].get("eje"),
            "adicion": examen["examen"].get("adicion")
        },
        "ojo_izquierdo": {
            "esfera": examen["examen"]["ojo_izquierdo"].get("esfera"),
            "cilindro": examen["examen"]["ojo_izquierdo"].get("cilindro"),
            "eje": examen["examen"]["ojo_izquierdo"].get("eje"),
            "adicion": examen["examen"].get("adicion")
        },
        "distancia_pupilar": examen["examen"].get("distancia_pupilar"),
        "observaciones": examen["examen"].get("observaciones", "")
    }
    
    # Especificaciones técnicas
    tipo_lente = random.choice(tipos_lente)
    material = random.choice(materiales)
    num_tratamientos = random.randint(1, 4)
    tratamientos = random.sample(tratamientos_disponibles, num_tratamientos)
    
    # Costos
    costo_base = random.uniform(80000, 300000)
    costo_fabricacion = round(costo_base, 2)
    precio_venta_estimado = round(costo_fabricacion * random.uniform(1.8, 2.5), 2)
    
    # Crear pedido
    pedido = {
        "numero_pedido": f"PL-2025-{1000 + i}",
        "fecha_solicitud": fecha_solicitud,
        "fecha_estimada_entrega": fecha_estimada,
        "fecha_entrega_real": fecha_entrega_real,
        "cliente_ref": cliente["_id"],
        "cliente_snapshot": {
            "nombre": cliente["nombre"],
            "apellido": cliente["apellido"],
            "email": cliente["email"]
        },
        "examen_ref": examen["_id"],
        "laboratorio_ref": laboratorio["_id"],
        "laboratorio_snapshot": {
            "nombre": laboratorio["nombre_laboratorio"],
            "contacto": laboratorio.get("contacto_principal", "")
        },
        "asesor_ref": asesor["_id"] if asesor else None,
        "formula_snapshot": formula_snapshot,
        "especificaciones": {
            "tipo_lente": tipo_lente,
            "material": material,
            "tratamientos": tratamientos,
            "color_tinte": random.choice([None, "Gris", "Marrón", "Verde"]) if random.random() > 0.7 else None,
            "tipo_montaje": random.choice([None, "Ranurado", "Taladrado", "Completo"])
        },
        "costo_fabricacion": costo_fabricacion,
        "precio_venta_estimado": precio_venta_estimado,
        "estado": estado,
        "historial_estados": [
            {
                "estado": "Solicitado",
                "fecha": fecha_solicitud,
                "usuario": "Sistema",
                "observaciones": "Pedido creado automáticamente"
            }
        ],
        "producto_ref": None,  # Se llenará si el estado es Completado/Entregado
        "observaciones": f"Pedido personalizado basado en fórmula del examen {examen['_id']}"
    }
    
    # Agregar más estados al historial según el estado actual
    fecha_hist = fecha_solicitud
    for est in ["Confirmado", "En fabricación", "Control de calidad", "Completado", "Entregado"]:
        if estados_posibles.index(estado) >= estados_posibles.index(est):
            fecha_hist = fecha_hist + timedelta(days=random.randint(2, 5))
            pedido["historial_estados"].append({
                "estado": est,
                "fecha": fecha_hist,
                "usuario": f"Usuario_{random.randint(1, 3)}",
                "observaciones": None
            })
        else:
            break
    
    # Si el pedido está completado, crear el producto
    if estado in ["Completado", "Entregado"]:
        # Crear producto personalizado
        producto = {
            "nombre_producto": f"Lentes {tipo_lente} personalizados - {cliente['nombre']} {cliente['apellido']}",
            "tipo": {
                "nombre": f"Lentes {tipo_lente}",
                "categoria": "Lente"
            },
            "marca": laboratorio["nombre_laboratorio"],
            "descripcion": f"Lentes {tipo_lente} en {material} con tratamientos: {', '.join(tratamientos)}. Fabricado según fórmula específica del cliente.",
            "precio_venta": precio_venta_estimado,
            "stock": 1,  # Producto personalizado, stock = 1
            "stock_minimo": 0,
            "codigo_barras": f"CUSTOM-{i:04d}",  # Código único para productos personalizados
            "suministro_ref": None,  # No viene de suministro genérico
            "pedido_laboratorio_ref": None,  # Se llenará después de insertar el pedido
            "activo": True,
            "fecha_creacion": fecha_entrega_real or datetime.utcnow(),
            "imagenes": [],
            "embedding": None
        }
        
        productos_creados.append((producto, i - 1))  # Guardar índice del pedido
    
    pedidos_creados.append(pedido)

# Insertar pedidos
if pedidos_creados:
    result_pedidos = db.pedidos_laboratorio.insert_many(pedidos_creados)
    print(f"   ✅ {len(result_pedidos.inserted_ids)} pedidos de laboratorio creados")
    
    # Actualizar productos con pedido_laboratorio_ref
    for producto_data, pedido_idx in productos_creados:
        pedido_id = result_pedidos.inserted_ids[pedido_idx]
        producto_data["pedido_laboratorio_ref"] = pedido_id
        
        # Insertar producto
        result_prod = db.productos.insert_one(producto_data)
        
        # Actualizar pedido con producto_ref (bidireccional)
        db.pedidos_laboratorio.update_one(
            {"_id": pedido_id},
            {"$set": {"producto_ref": result_prod.inserted_id}}
        )
    
    print(f"   ✅ {len(productos_creados)} productos personalizados creados y vinculados")
    
    # Actualizar examenes con pedido_laboratorio_ref (bidireccional)
    for pedido, pedido_id in zip(pedidos_creados, result_pedidos.inserted_ids):
        db.examenes.update_one(
            {"_id": pedido["examen_ref"]},
            {"$set": {"pedido_laboratorio_ref": pedido_id}}
        )
    
    print(f"   ✅ {len(result_pedidos.inserted_ids)} examenes actualizados con pedido_laboratorio_ref")
    
    # Crear algunas ventas vinculadas a examenes
    print("\n5. Creando ventas vinculadas a examenes...")
    
    # Seleccionar pedidos entregados
    pedidos_entregados = [p for p, pid in zip(pedidos_creados, result_pedidos.inserted_ids) 
                          if p["estado"] == "Entregado" and p["producto_ref"]]
    
    ventas_creadas = 0
    for pedido in pedidos_entregados[:5]:  # Crear 5 ventas de ejemplo
        # Buscar el producto
        producto = db.productos.find_one({"_id": pedido["producto_ref"]})
        if not producto:
            continue
        
        # Crear venta
        venta = {
            "numero_factura": f"F-2025-{2000 + ventas_creadas}",
            "fecha_compra": pedido["fecha_entrega_real"] + timedelta(hours=random.randint(1, 48)),
            "metodo_pago": {"nombre": random.choice(["Efectivo", "Tarjeta crédito", "Transferencia"])},
            "cliente_ref": pedido["cliente_ref"],
            "asesor_ref": pedido["asesor_ref"],
            "examen_ref": pedido["examen_ref"],  # ⭐ NUEVA RELACIÓN
            "items": [{
                "producto_ref": producto["_id"],
                "nombre": producto["nombre_producto"],
                "cantidad": 1,
                "precio_unitario": producto["precio_venta"],
                "subtotal": producto["precio_venta"],
                "descuento": 0,
                "total": producto["precio_venta"]
            }],
            "subtotal": producto["precio_venta"],
            "descuento": 0,
            "impuesto": round(producto["precio_venta"] * 0.19, 2),
            "total": round(producto["precio_venta"] * 1.19, 2),
            "estado": "Completada",
            "observaciones": f"Venta de lentes personalizados - Pedido {pedido['numero_pedido']}"
        }
        
        db.ventas.insert_one(venta)
        ventas_creadas += 1
        
        # Actualizar stock del producto
        db.productos.update_one(
            {"_id": producto["_id"]},
            {"$inc": {"stock": -1}}
        )
    
    print(f"   ✅ {ventas_creadas} ventas creadas vinculadas a examenes")

else:
    print("   ⚠️  No se pudieron crear pedidos de prueba")

# ============================================================================
# 6. VERIFICAR INTEGRIDAD REFERENCIAL
# ============================================================================

print("\n6. Verificando integridad referencial...")

# Verificar pedidos con todas sus referencias
pedidos = list(db.pedidos_laboratorio.find())
errores = []

for pedido in pedidos:
    # Verificar cliente
    cliente = db.clientes.find_one({"_id": pedido["cliente_ref"]})
    if not cliente:
        errores.append(f"Pedido {pedido['numero_pedido']}: cliente_ref inválido")
    
    # Verificar examen
    examen = db.examenes.find_one({"_id": pedido["examen_ref"]})
    if not examen:
        errores.append(f"Pedido {pedido['numero_pedido']}: examen_ref inválido")
    elif examen.get("pedido_laboratorio_ref") != pedido["_id"]:
        errores.append(f"Pedido {pedido['numero_pedido']}: relación bidireccional con examen no establecida")
    
    # Verificar laboratorio
    laboratorio = db.laboratorios.find_one({"_id": pedido["laboratorio_ref"]})
    if not laboratorio:
        errores.append(f"Pedido {pedido['numero_pedido']}: laboratorio_ref inválido")
    
    # Verificar producto si existe
    if pedido.get("producto_ref"):
        producto = db.productos.find_one({"_id": pedido["producto_ref"]})
        if not producto:
            errores.append(f"Pedido {pedido['numero_pedido']}: producto_ref inválido")
        elif producto.get("pedido_laboratorio_ref") != pedido["_id"]:
            errores.append(f"Pedido {pedido['numero_pedido']}: relación bidireccional con producto no establecida")

if errores:
    print(f"   ⚠️  {len(errores)} errores de integridad encontrados:")
    for error in errores[:10]:
        print(f"      - {error}")
else:
    print("   ✅ Integridad referencial verificada correctamente")

# ============================================================================
# 7. RESUMEN Y ESTADÍSTICAS
# ============================================================================

print("\n" + "=" * 80)
print("RESUMEN DE IMPLEMENTACIÓN")
print("=" * 80)

total_pedidos = db.pedidos_laboratorio.count_documents({})
pedidos_por_estado = {}
for estado in estados_posibles:
    count = db.pedidos_laboratorio.count_documents({"estado": estado})
    if count > 0:
        pedidos_por_estado[estado] = count

productos_personalizados = db.productos.count_documents({"pedido_laboratorio_ref": {"$exists": True, "$ne": None}})
examenes_con_pedido = db.examenes.count_documents({"pedido_laboratorio_ref": {"$exists": True, "$ne": None}})
ventas_con_examen = db.ventas.count_documents({"examen_ref": {"$exists": True, "$ne": None}})

print(f"\n📊 Estadísticas:")
print(f"   • Total pedidos laboratorio: {total_pedidos}")
print(f"\n   Pedidos por estado:")
for estado, count in pedidos_por_estado.items():
    print(f"      - {estado}: {count}")
print(f"\n   • Productos personalizados creados: {productos_personalizados}")
print(f"   • Examenes con pedido asociado: {examenes_con_pedido}")
print(f"   • Ventas vinculadas a examenes: {ventas_con_examen}")

# Consulta de prueba: Flujo completo
print("\n🔍 Consulta de prueba - Flujo completo:")
print("   Examen → Pedido Laboratorio → Producto → Venta\n")

pipeline = [
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
    {
        "$unwind": "$examen"
    },
    {
        "$lookup": {
            "from": "pedidos_laboratorio",
            "localField": "examen_ref",
            "foreignField": "examen_ref",
            "as": "pedido"
        }
    },
    {
        "$unwind": "$pedido"
    },
    {
        "$lookup": {
            "from": "productos",
            "localField": "pedido.producto_ref",
            "foreignField": "_id",
            "as": "producto"
        }
    },
    {
        "$unwind": "$producto"
    },
    {
        "$lookup": {
            "from": "clientes",
            "localField": "cliente_ref",
            "foreignField": "_id",
            "as": "cliente"
        }
    },
    {
        "$unwind": "$cliente"
    },
    {
        "$project": {
            "numero_factura": 1,
            "fecha_compra": 1,
            "total": 1,
            "cliente_nombre": {"$concat": ["$cliente.nombre", " ", "$cliente.apellido"]},
            "examen_fecha": "$examen.fecha_examen",
            "pedido_numero": "$pedido.numero_pedido",
            "pedido_laboratorio": "$pedido.laboratorio_snapshot.nombre",
            "pedido_tipo_lente": "$pedido.especificaciones.tipo_lente",
            "producto_nombre": "$producto.nombre_producto"
        }
    },
    {
        "$limit": 3
    }
]

resultados = list(db.ventas.aggregate(pipeline))
for i, resultado in enumerate(resultados, 1):
    print(f"   Venta #{i}:")
    print(f"      Factura: {resultado['numero_factura']}")
    print(f"      Cliente: {resultado['cliente_nombre']}")
    print(f"      Fecha examen: {resultado['examen_fecha'].strftime('%Y-%m-%d')}")
    print(f"      Pedido: {resultado['pedido_numero']} ({resultado['pedido_laboratorio']})")
    print(f"      Tipo lente: {resultado['pedido_tipo_lente']}")
    print(f"      Producto: {resultado['producto_nombre']}")
    print(f"      Total: ${resultado['total']:,.2f}")
    print()

print("=" * 80)
print("✅ IMPLEMENTACIÓN COMPLETADA EXITOSAMENTE")
print("=" * 80)
print("\nAhora tienes trazabilidad completa:")
print("   Cliente → Cita → Examen → Pedido Laboratorio → Producto → Venta")
print("\nColecciones actualizadas:")
print("   • pedidos_laboratorio (NUEVA)")
print("   • examenes (+pedido_laboratorio_ref)")
print("   • productos (+pedido_laboratorio_ref)")
print("   • ventas (+examen_ref)")

client.close()
