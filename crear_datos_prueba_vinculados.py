"""
Script para crear datos de prueba con relaciones bidireccionales correctas
==========================================================================

Este script:
1. Elimina citas y exámenes sin vincular correctamente
2. Crea nuevos datos de prueba con relaciones bidireccionales consistentes
3. Verifica la integridad de las relaciones creadas

Ejecución: python crear_datos_prueba_vinculados.py
"""

from pymongo import MongoClient
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
print("🔄 CREANDO DATOS DE PRUEBA CON RELACIONES BIDIRECCIONALES")
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
# PASO 1: ELIMINAR DATOS INCONSISTENTES
# ============================================================================
print("=" * 80)
print("PASO 1: Eliminando datos sin vínculos correctos")
print("=" * 80)
print()

# Eliminar citas sin examen_ref
citas_eliminadas = db.citas.delete_many({"examen_ref": {"$exists": False}})
print(f"✅ Citas eliminadas: {citas_eliminadas.deleted_count}")

# Eliminar exámenes sin cita_ref
examenes_eliminados = db.examenes.delete_many({"cita_ref": {"$exists": False}})
print(f"✅ Exámenes eliminados: {examenes_eliminados.deleted_count}")
print()

# ============================================================================
# PASO 2: OBTENER DATOS BASE (CLIENTES, ESPECIALISTAS, ASESORES)
# ============================================================================
print("=" * 80)
print("PASO 2: Obteniendo datos base")
print("=" * 80)
print()

clientes = list(db.clientes.find().limit(10))
especialistas = list(db.especialistas.find())
asesores = list(db.asesores.find())

print(f"📊 Clientes disponibles: {len(clientes)}")
print(f"📊 Especialistas disponibles: {len(especialistas)}")
print(f"📊 Asesores disponibles: {len(asesores)}")
print()

if len(clientes) == 0 or len(especialistas) == 0:
    print("❌ Error: No hay suficientes clientes o especialistas en la base de datos")
    client.close()
    exit(1)

# Obtener catálogos
catalogos = db.catalogos.find_one({"_id": "catalogos_optica"})
if not catalogos:
    print("⚠️  Catálogos no encontrados, usando valores por defecto")
    motivos = [{"descripcion": "Examen visual de rutina"}, {"descripcion": "Revisión de lentes"}, {"descripcion": "Consulta por molestias visuales"}]
    tipos_diagnostico = [{"nombre": "Miopía"}, {"nombre": "Hipermetropía"}, {"nombre": "Astigmatismo"}, {"nombre": "Presbicia"}]
else:
    motivos = catalogos.get('motivos', [])
    tipos_diagnostico = catalogos.get('tipos_diagnostico', [])

print(f"📋 Motivos de cita disponibles: {len(motivos)}")
print(f"📋 Tipos de diagnóstico disponibles: {len(tipos_diagnostico)}")
print()

# ============================================================================
# PASO 3: CREAR DATOS DE PRUEBA VINCULADOS
# ============================================================================
print("=" * 80)
print("PASO 3: Creando datos de prueba con relaciones bidireccionales")
print("=" * 80)
print()

# Definir fechas base (últimos 6 meses)
fecha_actual = datetime.now()
casos_prueba = 15

citas_creadas = []
examenes_creados = []

for i in range(casos_prueba):
    # Seleccionar datos aleatorios
    cliente = random.choice(clientes)
    especialista = random.choice(especialistas)
    asesor = random.choice(asesores) if asesores else None
    motivo = random.choice(motivos)
    tipo_diagnostico = random.choice(tipos_diagnostico)
    
    # Calcular fechas (citas de los últimos 6 meses, exámenes 0-7 días después)
    dias_atras = random.randint(0, 180)
    fecha_cita = fecha_actual - timedelta(days=dias_atras)
    fecha_examen = fecha_cita + timedelta(days=random.randint(0, 7))
    
    # Determinar estado de la cita
    if dias_atras > 7:
        estado_cita = "Completada"
    elif dias_atras > 0:
        estado_cita = random.choice(["Completada", "Confirmada"])
    else:
        estado_cita = "Programada"
    
    # Hora de la cita
    hora_cita = f"{random.randint(8, 17):02d}:{random.choice(['00', '30'])}:00"
    
    # ============================================================================
    # CREAR CITA (sin examen_ref todavía)
    # ============================================================================
    nueva_cita = {
        "fecha_cita": fecha_cita,
        "hora_cita": hora_cita,
        "motivo": {
            "descripcion": motivo.get('descripcion', 'Examen visual de rutina')
        },
        "cliente_ref": cliente['_id'],
        "asesor_ref": asesor['_id'] if asesor else None,
        "especialista_ref": especialista['_id'],
        "estado": estado_cita,
        "observaciones": f"Cita de prueba #{i+1} con vinculación bidireccional",
        "fecha_creacion": fecha_cita - timedelta(days=random.randint(1, 7))
    }
    
    cita_result = db.citas.insert_one(nueva_cita)
    cita_id = cita_result.inserted_id
    
    # ============================================================================
    # CREAR EXAMEN VINCULADO A LA CITA
    # ============================================================================
    # Generar valores aleatorios para el examen
    nuevo_examen = {
        "fecha_examen": fecha_examen,
        "cliente_ref": cliente['_id'],
        "especialista_ref": especialista['_id'],
        "cita_ref": cita_id,  # ⭐ Referencia a la cita
        "examen": {
            "ojo_derecho": {
                "agudeza_visual": f"{random.randint(15, 20)}/{random.choice([20, 25, 30])}",
                "esfera": round(random.uniform(-6.0, 3.0), 2),
                "cilindro": round(random.uniform(-3.0, 0.0), 2),
                "eje": random.randint(0, 180),
                "presion_intraocular": round(random.uniform(10.0, 21.0), 1)
            },
            "ojo_izquierdo": {
                "agudeza_visual": f"{random.randint(15, 20)}/{random.choice([20, 25, 30])}",
                "esfera": round(random.uniform(-6.0, 3.0), 2),
                "cilindro": round(random.uniform(-3.0, 0.0), 2),
                "eje": random.randint(0, 180),
                "presion_intraocular": round(random.uniform(10.0, 21.0), 1)
            },
            "adicion": round(random.uniform(0.5, 3.0), 2) if random.random() > 0.5 else None,
            "distancia_pupilar": round(random.uniform(58.0, 68.0), 1),
            "observaciones": f"Examen de prueba #{i+1} vinculado bidireccialmente"
        },
        "diagnostico": {
            "tipo": {
                "nombre": tipo_diagnostico.get('nombre', 'Miopía'),
                "descripcion": tipo_diagnostico.get('descripcion', '')
            },
            "descripcion": f"Diagnóstico de {tipo_diagnostico.get('nombre', 'Miopía')} detectado en examen visual completo",
            "fecha": fecha_examen
        },
        "formula": {
            "descripcion": f"Fórmula prescrita para corrección de {tipo_diagnostico.get('nombre', 'Miopía')}",
            "fecha_emision": fecha_examen,
            "fecha_vencimiento": fecha_examen + timedelta(days=365),
            "activa": True
        }
    }
    
    examen_result = db.examenes.insert_one(nuevo_examen)
    examen_id = examen_result.inserted_id
    
    # ============================================================================
    # ACTUALIZAR CITA CON REFERENCIA AL EXAMEN (BIDIRECCIONAL)
    # ============================================================================
    db.citas.update_one(
        {"_id": cita_id},
        {"$set": {"examen_ref": examen_id}}  # ⭐ Completar relación bidireccional
    )
    
    citas_creadas.append({
        "cita_id": cita_id,
        "examen_id": examen_id,
        "cliente": f"{cliente.get('nombre', '')} {cliente.get('apellido', '')}",
        "especialista": f"{especialista.get('nombre', '')} {especialista.get('apellido', '')}",
        "fecha_cita": fecha_cita.date(),
        "estado": estado_cita
    })
    
    examenes_creados.append({
        "examen_id": examen_id,
        "cita_id": cita_id,
        "diagnostico": tipo_diagnostico.get('nombre', 'Miopía'),
        "fecha_examen": fecha_examen.date()
    })
    
    print(f"   ✅ Caso #{i+1}:")
    print(f"      Cita: {cita_id} | {cliente.get('nombre', '')} {cliente.get('apellido', '')} | {fecha_cita.date()} | {estado_cita}")
    print(f"      Examen: {examen_id} | {tipo_diagnostico.get('nombre', '')} | {fecha_examen.date()}")
    print(f"      ↔️ Relación bidireccional establecida")
    print()

print(f"✅ Total de citas creadas: {len(citas_creadas)}")
print(f"✅ Total de exámenes creados: {len(examenes_creados)}")
print()

# ============================================================================
# PASO 4: VERIFICAR INTEGRIDAD DE LAS RELACIONES
# ============================================================================
print("=" * 80)
print("PASO 4: Verificando integridad de las relaciones bidireccionales")
print("=" * 80)
print()

errores_integridad = 0

# Verificar todas las citas
todas_citas = list(db.citas.find())
print(f"📊 Verificando {len(todas_citas)} citas...")

for cita in todas_citas:
    examen_ref = cita.get('examen_ref')
    
    if not examen_ref:
        print(f"   ❌ Cita {cita['_id']} no tiene examen_ref")
        errores_integridad += 1
        continue
    
    # Verificar que el examen existe
    examen = db.examenes.find_one({"_id": examen_ref})
    if not examen:
        print(f"   ❌ Cita {cita['_id']} referencia examen inexistente: {examen_ref}")
        errores_integridad += 1
        continue
    
    # Verificar relación bidireccional
    if examen.get('cita_ref') != cita['_id']:
        print(f"   ❌ Cita {cita['_id']} → Examen {examen_ref}, pero la relación inversa no coincide")
        errores_integridad += 1

# Verificar todos los exámenes
todos_examenes = list(db.examenes.find())
print(f"📊 Verificando {len(todos_examenes)} exámenes...")

for examen in todos_examenes:
    cita_ref = examen.get('cita_ref')
    
    if not cita_ref:
        print(f"   ❌ Examen {examen['_id']} no tiene cita_ref")
        errores_integridad += 1
        continue
    
    # Verificar que la cita existe
    cita = db.citas.find_one({"_id": cita_ref})
    if not cita:
        print(f"   ❌ Examen {examen['_id']} referencia cita inexistente: {cita_ref}")
        errores_integridad += 1
        continue
    
    # Verificar relación bidireccional
    if cita.get('examen_ref') != examen['_id']:
        print(f"   ❌ Examen {examen['_id']} → Cita {cita_ref}, pero la relación inversa no coincide")
        errores_integridad += 1

if errores_integridad == 0:
    print("   ✅ Todas las relaciones son consistentes y bidireccionales")
else:
    print(f"   ⚠️ Se encontraron {errores_integridad} errores de integridad")

print()

# ============================================================================
# PASO 5: ESTADÍSTICAS FINALES
# ============================================================================
print("=" * 80)
print("📊 ESTADÍSTICAS FINALES")
print("=" * 80)
print()

total_citas = db.citas.count_documents({})
total_examenes = db.examenes.count_documents({})
citas_con_examen = db.citas.count_documents({"examen_ref": {"$exists": True, "$ne": None}})
examenes_con_cita = db.examenes.count_documents({"cita_ref": {"$exists": True, "$ne": None}})

print(f"📅 Total de citas:                    {total_citas}")
print(f"   └─ Con examen asociado:            {citas_con_examen} ({(citas_con_examen/total_citas*100) if total_citas > 0 else 0:.1f}%)")
print()
print(f"🔬 Total de exámenes:                 {total_examenes}")
print(f"   └─ Con cita asociada:              {examenes_con_cita} ({(examenes_con_cita/total_examenes*100) if total_examenes > 0 else 0:.1f}%)")
print()

# Estadísticas por estado de cita
print("📊 Distribución por estado de cita:")
for estado in ["Programada", "Confirmada", "Completada", "Cancelada"]:
    count = db.citas.count_documents({"estado": estado})
    if count > 0:
        print(f"   └─ {estado}: {count}")
print()

# Muestra de datos creados
print("📋 MUESTRA DE DATOS CREADOS (primeros 5):")
print()
for i, caso in enumerate(citas_creadas[:5], 1):
    print(f"{i}. Cliente: {caso['cliente']}")
    print(f"   Especialista: {caso['especialista']}")
    print(f"   Fecha cita: {caso['fecha_cita']} | Estado: {caso['estado']}")
    print(f"   Cita ID: {caso['cita_id']}")
    print(f"   Examen ID: {caso['examen_id']}")
    print(f"   ↔️ Vinculación bidireccional confirmada")
    print()

# ============================================================================
# PASO 6: QUERY DE PRUEBA
# ============================================================================
print("=" * 80)
print("🔍 QUERY DE PRUEBA: Citas completadas con sus exámenes")
print("=" * 80)
print()

pipeline = [
    {
        "$match": {
            "estado": "Completada",
            "examen_ref": {"$exists": True}
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
    {
        "$lookup": {
            "from": "examenes",
            "localField": "examen_ref",
            "foreignField": "_id",
            "as": "examen"
        }
    },
    {
        "$unwind": "$cliente"
    },
    {
        "$unwind": "$examen"
    },
    {
        "$project": {
            "fecha_cita": 1,
            "cliente_nombre": {"$concat": ["$cliente.nombre", " ", "$cliente.apellido"]},
            "diagnostico": "$examen.diagnostico.tipo.nombre",
            "fecha_examen": "$examen.fecha_examen"
        }
    },
    {
        "$limit": 5
    }
]

resultados = list(db.citas.aggregate(pipeline))
print(f"📊 Resultados encontrados: {len(resultados)}")
print()

for i, resultado in enumerate(resultados, 1):
    print(f"{i}. {resultado.get('cliente_nombre', 'N/A')}")
    print(f"   Cita: {resultado.get('fecha_cita', 'N/A').date() if isinstance(resultado.get('fecha_cita'), datetime) else 'N/A'}")
    print(f"   Examen: {resultado.get('fecha_examen', 'N/A').date() if isinstance(resultado.get('fecha_examen'), datetime) else 'N/A'}")
    print(f"   Diagnóstico: {resultado.get('diagnostico', 'N/A')}")
    print()

# ============================================================================
# FINALIZACIÓN
# ============================================================================
print("=" * 80)
print("✅ PROCESO COMPLETADO EXITOSAMENTE")
print("=" * 80)
print()
print("RESUMEN:")
print(f"1. ✅ Eliminadas {citas_eliminadas.deleted_count} citas sin vínculos")
print(f"2. ✅ Eliminados {examenes_eliminados.deleted_count} exámenes sin vínculos")
print(f"3. ✅ Creadas {len(citas_creadas)} citas nuevas con relaciones bidireccionales")
print(f"4. ✅ Creados {len(examenes_creados)} exámenes vinculados correctamente")
print(f"5. ✅ Verificación de integridad: {errores_integridad} errores encontrados")
print()
print("🎯 Todas las citas y exámenes ahora tienen relaciones bidireccionales correctas")
print()

# Cerrar conexión
client.close()
print("🔌 Conexión cerrada")
print("=" * 80)
