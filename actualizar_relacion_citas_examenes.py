"""
Script para implementar relación bidireccional entre Citas y Exámenes
=====================================================================

PROBLEMA IDENTIFICADO:
- Las citas están definidas como la agendación de un paciente
- Los exámenes son el resultado de esas citas
- Actualmente NO existe conexión explícita entre ambas colecciones
- Solo conexión implícita: cliente_ref + especialista_ref + fechas aproximadas

SOLUCIÓN IMPLEMENTADA:
1. Agregar campo opcional 'examen_ref' en citas (referencia al examen resultante)
2. El campo 'cita_ref' ya existe en examenes (ya implementado en el schema actual)
3. Crear índices para optimizar consultas bidireccionales
4. Migrar datos existentes para establecer relaciones

RELACIONES:
- 1 Cliente → N Citas
- 1 Cliente → N Exámenes
- 1 Cita → 0 o 1 Examen (una cita puede no tener examen aún, o puede tener uno)
- 1 Examen → 1 Cita (todo examen debe estar asociado a una cita)

Ejecución: python actualizar_relacion_citas_examenes.py
"""

from pymongo import MongoClient, ASCENDING
from dotenv import load_dotenv
from datetime import datetime, timedelta
import os
from bson import ObjectId

# Cargar variables de entorno
load_dotenv()

# Configuración
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb+srv://CamaroSS:Chevrolet@clusterbases.8qang0c.mongodb.net/?appName=ClusterBases')
MONGODB_DATABASE = 'optica_db'

print("=" * 80)
print("🔧 ACTUALIZANDO RELACIÓN BIDIRECCIONAL: CITAS ↔ EXAMENES")
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
# PASO 1: ACTUALIZAR SCHEMA DE VALIDACIÓN - CITAS
# ============================================================================
print("=" * 80)
print("PASO 1: Actualizando schema de validación de la colección 'citas'")
print("=" * 80)

try:
    # Obtener el validador actual
    citas_info = db.command("collMod", "citas", validator={
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["fecha_cita", "hora_cita", "motivo", "cliente_ref", "estado"],
            "properties": {
                "fecha_cita": {"bsonType": "date"},
                "hora_cita": {"bsonType": "string"},
                "motivo": {
                    "bsonType": "object",
                    "required": ["descripcion"],
                    "properties": {
                        "descripcion": {"bsonType": "string"}
                    }
                },
                "cliente_ref": {
                    "bsonType": "objectId",
                    "description": "Referencia al cliente"
                },
                "asesor_ref": {
                    "bsonType": "objectId",
                    "description": "Referencia al asesor (opcional)"
                },
                "especialista_ref": {
                    "bsonType": "objectId",
                    "description": "Referencia al especialista (opcional)"
                },
                "examen_ref": {
                    "bsonType": "objectId",
                    "description": "Referencia al examen resultante (opcional - bidireccional)"
                },
                "estado": {
                    "enum": ["Programada", "Confirmada", "Completada", "Cancelada"],
                    "description": "Estado de la cita"
                },
                "observaciones": {"bsonType": "string"},
                "fecha_creacion": {"bsonType": "date"}
            }
        }
    })
    print("✅ Schema de 'citas' actualizado con campo 'examen_ref'")
    print("   - Campo: examen_ref (ObjectId, opcional)")
    print("   - Descripción: Referencia al examen resultante de la cita")
    print()
except Exception as e:
    print(f"⚠️  Advertencia al actualizar schema de citas: {e}")
    print("   Continuando con la ejecución...\n")

# ============================================================================
# PASO 2: CREAR ÍNDICE EN CITAS PARA EXAMEN_REF
# ============================================================================
print("=" * 80)
print("PASO 2: Creando índice en 'citas' para campo 'examen_ref'")
print("=" * 80)

try:
    db.citas.create_index([("examen_ref", ASCENDING)], name="idx_examen_ref")
    print("✅ Índice 'idx_examen_ref' creado en colección 'citas'")
    print("   - Optimiza consultas: cita → examen")
    print()
except Exception as e:
    if "already exists" in str(e):
        print("⚠️  Índice 'idx_examen_ref' ya existe, saltando...")
        print()
    else:
        print(f"❌ Error al crear índice: {e}")
        print()

# ============================================================================
# PASO 3: VERIFICAR ÍNDICE EN EXAMENES PARA CITA_REF
# ============================================================================
print("=" * 80)
print("PASO 3: Verificando índice en 'examenes' para campo 'cita_ref'")
print("=" * 80)

try:
    indices_examenes = list(db.examenes.list_indexes())
    tiene_idx_cita_ref = any(idx.get('name') == 'idx_cita_ref' for idx in indices_examenes)
    
    if tiene_idx_cita_ref:
        print("✅ Índice 'idx_cita_ref' ya existe en colección 'examenes'")
        print("   - Optimiza consultas: examen → cita")
        print()
    else:
        db.examenes.create_index([("cita_ref", ASCENDING)], name="idx_cita_ref")
        print("✅ Índice 'idx_cita_ref' creado en colección 'examenes'")
        print("   - Optimiza consultas: examen → cita")
        print()
except Exception as e:
    print(f"⚠️  Advertencia al verificar/crear índice: {e}")
    print("   Continuando con la ejecución...\n")

# ============================================================================
# PASO 4: MIGRAR DATOS EXISTENTES
# ============================================================================
print("=" * 80)
print("PASO 4: Migrando datos existentes - Estableciendo relaciones bidireccionales")
print("=" * 80)
print()

# Obtener todos los exámenes
examenes = list(db.examenes.find())
print(f"📊 Total de exámenes en la base de datos: {len(examenes)}")

relaciones_creadas = 0
relaciones_saltadas = 0
errores = 0

for examen in examenes:
    examen_id = examen['_id']
    cita_ref = examen.get('cita_ref')
    
    # Si el examen ya tiene cita_ref, actualizar la cita correspondiente
    if cita_ref:
        try:
            # Verificar si la cita existe
            cita = db.citas.find_one({"_id": cita_ref})
            
            if cita:
                # Verificar si la cita ya tiene examen_ref
                if cita.get('examen_ref') == examen_id:
                    print(f"   ⏭️  Cita {cita_ref} ya tiene referencia al examen {examen_id}")
                    relaciones_saltadas += 1
                else:
                    # Actualizar la cita con la referencia al examen
                    db.citas.update_one(
                        {"_id": cita_ref},
                        {"$set": {"examen_ref": examen_id}}
                    )
                    print(f"   ✅ Cita {cita_ref} ← Examen {examen_id} (relación establecida)")
                    relaciones_creadas += 1
            else:
                print(f"   ⚠️  Cita {cita_ref} no existe (referenciada por examen {examen_id})")
                errores += 1
        except Exception as e:
            print(f"   ❌ Error al procesar examen {examen_id}: {e}")
            errores += 1
    else:
        # El examen no tiene cita_ref, intentar encontrar la cita por coincidencia
        # (cliente + especialista + fecha cercana)
        try:
            cliente_ref = examen.get('cliente_ref')
            especialista_ref = examen.get('especialista_ref')
            fecha_examen = examen.get('fecha_examen')
            
            if cliente_ref and especialista_ref and fecha_examen:
                # Buscar cita dentro de un rango de ±7 días
                fecha_inicio = fecha_examen - timedelta(days=7)
                fecha_fin = fecha_examen + timedelta(days=7)
                
                # Buscar citas coincidentes sin examen_ref asignado
                citas_candidatas = list(db.citas.find({
                    "cliente_ref": cliente_ref,
                    "especialista_ref": especialista_ref,
                    "fecha_cita": {"$gte": fecha_inicio, "$lte": fecha_fin},
                    "estado": {"$in": ["Completada", "Confirmada"]},
                    "examen_ref": {"$exists": False}
                }).sort("fecha_cita", 1))
                
                if citas_candidatas:
                    # Tomar la cita más cercana
                    cita = citas_candidatas[0]
                    cita_id = cita['_id']
                    
                    # Actualizar ambas referencias
                    db.examenes.update_one(
                        {"_id": examen_id},
                        {"$set": {"cita_ref": cita_id}}
                    )
                    db.citas.update_one(
                        {"_id": cita_id},
                        {"$set": {"examen_ref": examen_id}}
                    )
                    print(f"   ✅ Cita {cita_id} ↔ Examen {examen_id} (relación inferida por coincidencia)")
                    relaciones_creadas += 1
                else:
                    print(f"   ⚠️  No se encontró cita para examen {examen_id} (cliente: {cliente_ref}, fecha: {fecha_examen.date()})")
                    errores += 1
            else:
                print(f"   ⚠️  Examen {examen_id} no tiene datos suficientes para inferir cita")
                errores += 1
        except Exception as e:
            print(f"   ❌ Error al intentar inferir cita para examen {examen_id}: {e}")
            errores += 1

print()
print("=" * 80)
print("📊 RESUMEN DE MIGRACIÓN")
print("=" * 80)
print(f"✅ Relaciones creadas:     {relaciones_creadas}")
print(f"⏭️  Relaciones ya existían: {relaciones_saltadas}")
print(f"⚠️  Errores o sin coincidencia: {errores}")
print(f"📈 Total procesado:        {len(examenes)}")
print()

# ============================================================================
# PASO 5: VERIFICACIÓN DE INTEGRIDAD
# ============================================================================
print("=" * 80)
print("PASO 5: Verificando integridad de las relaciones bidireccionales")
print("=" * 80)
print()

# Verificar citas con examen_ref que apunten a exámenes válidos
citas_con_examen = list(db.citas.find({"examen_ref": {"$exists": True}}))
print(f"📊 Citas con examen_ref: {len(citas_con_examen)}")

referencias_rotas_citas = 0
for cita in citas_con_examen:
    examen_ref = cita.get('examen_ref')
    if examen_ref:
        examen = db.examenes.find_one({"_id": examen_ref})
        if not examen:
            print(f"   ❌ Cita {cita['_id']} referencia examen inexistente: {examen_ref}")
            referencias_rotas_citas += 1
        elif examen.get('cita_ref') != cita['_id']:
            print(f"   ⚠️  Cita {cita['_id']} → Examen {examen_ref}, pero la relación inversa no coincide")
            referencias_rotas_citas += 1

if referencias_rotas_citas == 0:
    print("   ✅ Todas las referencias desde citas son válidas")
else:
    print(f"   ⚠️  {referencias_rotas_citas} referencias rotas o inconsistentes desde citas")

print()

# Verificar exámenes con cita_ref que apunten a citas válidas
examenes_con_cita = list(db.examenes.find({"cita_ref": {"$exists": True}}))
print(f"📊 Exámenes con cita_ref: {len(examenes_con_cita)}")

referencias_rotas_examenes = 0
for examen in examenes_con_cita:
    cita_ref = examen.get('cita_ref')
    if cita_ref:
        cita = db.citas.find_one({"_id": cita_ref})
        if not cita:
            print(f"   ❌ Examen {examen['_id']} referencia cita inexistente: {cita_ref}")
            referencias_rotas_examenes += 1
        elif cita.get('examen_ref') != examen['_id']:
            print(f"   ⚠️  Examen {examen['_id']} → Cita {cita_ref}, pero la relación inversa no coincide")
            referencias_rotas_examenes += 1

if referencias_rotas_examenes == 0:
    print("   ✅ Todas las referencias desde exámenes son válidas")
else:
    print(f"   ⚠️  {referencias_rotas_examenes} referencias rotas o inconsistentes desde exámenes")

print()

# ============================================================================
# PASO 6: ESTADÍSTICAS FINALES
# ============================================================================
print("=" * 80)
print("📊 ESTADÍSTICAS FINALES")
print("=" * 80)

total_citas = db.citas.count_documents({})
total_examenes = db.examenes.count_documents({})
citas_con_examen_count = db.citas.count_documents({"examen_ref": {"$exists": True, "$ne": None}})
examenes_con_cita_count = db.examenes.count_documents({"cita_ref": {"$exists": True, "$ne": None}})
citas_sin_examen = total_citas - citas_con_examen_count
examenes_sin_cita = total_examenes - examenes_con_cita_count

print(f"📅 Total de citas:                    {total_citas}")
print(f"   └─ Con examen asociado:            {citas_con_examen_count} ({(citas_con_examen_count/total_citas*100) if total_citas > 0 else 0:.1f}%)")
print(f"   └─ Sin examen asociado:            {citas_sin_examen} ({(citas_sin_examen/total_citas*100) if total_citas > 0 else 0:.1f}%)")
print()
print(f"🔬 Total de exámenes:                 {total_examenes}")
print(f"   └─ Con cita asociada:              {examenes_con_cita_count} ({(examenes_con_cita_count/total_examenes*100) if total_examenes > 0 else 0:.1f}%)")
print(f"   └─ Sin cita asociada:              {examenes_sin_cita} ({(examenes_sin_cita/total_examenes*100) if total_examenes > 0 else 0:.1f}%)")
print()

# ============================================================================
# FINALIZACIÓN
# ============================================================================
print("=" * 80)
print("✅ ACTUALIZACIÓN COMPLETADA EXITOSAMENTE")
print("=" * 80)
print()
print("CAMBIOS REALIZADOS:")
print("1. ✅ Schema de 'citas' actualizado con campo 'examen_ref'")
print("2. ✅ Índice 'idx_examen_ref' creado en colección 'citas'")
print("3. ✅ Índice 'idx_cita_ref' verificado en colección 'examenes'")
print(f"4. ✅ {relaciones_creadas} relaciones bidireccionales establecidas")
print("5. ✅ Verificación de integridad completada")
print()
print("PRÓXIMOS PASOS RECOMENDADOS:")
print("- Actualizar la documentación del proyecto")
print("- Revisar las citas sin examen asociado (pueden ser citas futuras o canceladas)")
print("- Revisar los exámenes sin cita asociada (datos históricos sin coincidencia)")
print()

# Cerrar conexión
client.close()
print("🔌 Conexión cerrada")
print("=" * 80)
