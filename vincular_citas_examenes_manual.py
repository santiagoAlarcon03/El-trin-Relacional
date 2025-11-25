"""
Script auxiliar para vincular manualmente Citas y Exámenes
==========================================================

Este script muestra las citas y exámenes sin vincular para que puedas
establecer las relaciones manualmente basándote en el contexto del negocio.

Ejecución: python vincular_citas_examenes_manual.py
"""

from pymongo import MongoClient
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta

# Cargar variables de entorno
load_dotenv()

# Configuración
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb+srv://CamaroSS:Chevrolet@clusterbases.8qang0c.mongodb.net/?appName=ClusterBases')
MONGODB_DATABASE = 'optica_db'

print("=" * 80)
print("🔍 ANÁLISIS DE CITAS Y EXÁMENES SIN VINCULAR")
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

# Obtener citas sin examen
citas_sin_examen = list(db.citas.find({"examen_ref": {"$exists": False}}).sort("fecha_cita", -1))
print(f"📅 Citas sin examen asociado: {len(citas_sin_examen)}")
print()

# Obtener exámenes sin cita
examenes_sin_cita = list(db.examenes.find({"cita_ref": {"$exists": False}}).sort("fecha_examen", -1))
print(f"🔬 Exámenes sin cita asociada: {len(examenes_sin_cita)}")
print()

# Mostrar detalles de citas sin examen
if citas_sin_examen:
    print("=" * 80)
    print("📋 CITAS SIN EXAMEN ASOCIADO")
    print("=" * 80)
    print()
    
    for i, cita in enumerate(citas_sin_examen, 1):
        cliente = db.clientes.find_one({"_id": cita.get('cliente_ref')})
        especialista = db.especialistas.find_one({"_id": cita.get('especialista_ref')})
        
        print(f"{i}. Cita ID: {cita['_id']}")
        print(f"   Fecha: {cita.get('fecha_cita', 'N/A')}")
        print(f"   Estado: {cita.get('estado', 'N/A')}")
        print(f"   Cliente: {cliente.get('nombre', 'N/A') if cliente else 'N/A'} {cliente.get('apellido', '') if cliente else ''}")
        print(f"   Especialista: {especialista.get('nombre', 'N/A') if especialista else 'N/A'} {especialista.get('apellido', '') if especialista else ''}")
        print(f"   Motivo: {cita.get('motivo', {}).get('descripcion', 'N/A')}")
        print()

# Mostrar detalles de exámenes sin cita
if examenes_sin_cita:
    print("=" * 80)
    print("📋 EXÁMENES SIN CITA ASOCIADA")
    print("=" * 80)
    print()
    
    for i, examen in enumerate(examenes_sin_cita, 1):
        cliente = db.clientes.find_one({"_id": examen.get('cliente_ref')})
        especialista = db.especialistas.find_one({"_id": examen.get('especialista_ref')})
        
        print(f"{i}. Examen ID: {examen['_id']}")
        print(f"   Fecha: {examen.get('fecha_examen', 'N/A')}")
        print(f"   Cliente: {cliente.get('nombre', 'N/A') if cliente else 'N/A'} {cliente.get('apellido', '') if cliente else ''}")
        print(f"   Especialista: {especialista.get('nombre', 'N/A') if especialista else 'N/A'} {especialista.get('apellido', '') if especialista else ''}")
        
        diagnostico = examen.get('diagnostico', {})
        print(f"   Diagnóstico: {diagnostico.get('tipo', {}).get('nombre', 'N/A')}")
        print()

# Buscar coincidencias potenciales (ampliado a ±30 días)
print("=" * 80)
print("🔎 COINCIDENCIAS POTENCIALES (rango ampliado: ±30 días)")
print("=" * 80)
print()

coincidencias = 0
for examen in examenes_sin_cita:
    cliente_ref = examen.get('cliente_ref')
    especialista_ref = examen.get('especialista_ref')
    fecha_examen = examen.get('fecha_examen')
    
    if cliente_ref and especialista_ref and fecha_examen:
        # Buscar en rango de ±30 días
        fecha_inicio = fecha_examen - timedelta(days=30)
        fecha_fin = fecha_examen + timedelta(days=30)
        
        citas_potenciales = list(db.citas.find({
            "cliente_ref": cliente_ref,
            "especialista_ref": especialista_ref,
            "fecha_cita": {"$gte": fecha_inicio, "$lte": fecha_fin},
            "examen_ref": {"$exists": False}
        }).sort("fecha_cita", 1))
        
        if citas_potenciales:
            coincidencias += 1
            cliente = db.clientes.find_one({"_id": cliente_ref})
            especialista = db.especialistas.find_one({"_id": especialista_ref})
            
            print(f"Posible coincidencia #{coincidencias}:")
            print(f"   🔬 Examen ID: {examen['_id']}")
            print(f"      Fecha examen: {fecha_examen.date()}")
            print(f"      Cliente: {cliente.get('nombre', 'N/A')} {cliente.get('apellido', '')}")
            print(f"      Especialista: {especialista.get('nombre', 'N/A')} {especialista.get('apellido', '')}")
            print()
            print(f"   📅 Citas candidatas:")
            for j, cita in enumerate(citas_potenciales, 1):
                diferencia_dias = abs((cita['fecha_cita'].date() - fecha_examen.date()).days)
                print(f"      {j}. Cita ID: {cita['_id']}")
                print(f"         Fecha: {cita['fecha_cita'].date()} (Δ {diferencia_dias} días)")
                print(f"         Estado: {cita.get('estado', 'N/A')}")
                print(f"         Motivo: {cita.get('motivo', {}).get('descripcion', 'N/A')}")
            print()
            print("   " + "-" * 70)
            print()

if coincidencias == 0:
    print("   ⚠️  No se encontraron coincidencias potenciales en rango de ±30 días")
    print()

# Función para vincular manualmente
print("=" * 80)
print("🛠️  VINCULAR MANUALMENTE")
print("=" * 80)
print()
print("Para vincular una cita con un examen, ejecuta en tu código:")
print()
print("from pymongo import MongoClient")
print("from bson import ObjectId")
print("client = MongoClient('tu_uri')")
print("db = client['optica_db']")
print()
print("# Vincular cita con examen")
print("cita_id = ObjectId('ID_DE_LA_CITA')")
print("examen_id = ObjectId('ID_DEL_EXAMEN')")
print()
print("db.citas.update_one({'_id': cita_id}, {'$set': {'examen_ref': examen_id}})")
print("db.examenes.update_one({'_id': examen_id}, {'$set': {'cita_ref': cita_id}})")
print()
print("print('✅ Vinculación exitosa')")
print()

# Cerrar conexión
client.close()
print("=" * 80)
print("🔌 Conexión cerrada")
print("=" * 80)
