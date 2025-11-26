"""
Script para vectorizar TODAS las colecciones con embeddings reales
Reemplaza los embeddings falsos con vectores generados por Sentence-BERT
"""

from pymongo import MongoClient
from dotenv import load_dotenv
import os
import sys
from datetime import datetime

# Agregar directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag.embeddings import generar_embedding, generar_embeddings_batch

# Configuración
load_dotenv()
MONGODB_URI = os.getenv('MONGODB_URI')

print("=" * 80)
print("🚀 VECTORIZACIÓN COMPLETA CON EMBEDDINGS REALES")
print("=" * 80)
print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# Conectar a MongoDB
client = MongoClient(MONGODB_URI)
db = client['optica_db']

# Configuración de colecciones a vectorizar
COLECCIONES_CONFIG = {
    'productos': {
        'campos_texto': ['nombre_producto', 'descripcion', 'marca', 'categoria'],
        'formato': lambda doc: f"{doc.get('nombre_producto', '')} {doc.get('marca', '')} {doc.get('categoria', '')} {doc.get('descripcion', '')}",
        'prioridad': 1
    },
    'clientes': {
        'campos_texto': ['nombre', 'apellido', 'email'],
        'formato': lambda doc: f"{doc.get('nombre', '')} {doc.get('apellido', '')} {doc.get('email', '')}",
        'prioridad': 2
    },
    'asesores': {
        'campos_texto': ['nombre', 'apellido', 'especialidad'],
        'formato': lambda doc: f"{doc.get('nombre', '')} {doc.get('apellido', '')} {doc.get('especialidad', '')}",
        'prioridad': 2
    },
    'especialistas': {
        'campos_texto': ['nombre', 'apellido', 'especialidad'],
        'formato': lambda doc: f"{doc.get('nombre', '')} {doc.get('apellido', '')} {doc.get('especialidad', '')}",
        'prioridad': 2
    },
    'proveedores': {
        'campos_texto': ['nombre', 'descripcion_servicios'],
        'formato': lambda doc: f"{doc.get('nombre', '')} {doc.get('descripcion_servicios', '')}",
        'prioridad': 3
    },
    'laboratorios': {
        'campos_texto': ['nombre', 'especialidades'],
        'formato': lambda doc: f"{doc.get('nombre', '')} {' '.join(doc.get('especialidades', []))}",
        'prioridad': 3
    },
    'examenes': {
        'campos_texto': ['tipo_examen', 'diagnostico', 'observaciones'],
        'formato': lambda doc: f"{doc.get('tipo_examen', '')} {doc.get('diagnostico', '')} {doc.get('observaciones', '')}",
        'prioridad': 4
    },
    'citas': {
        'campos_texto': ['motivo', 'estado', 'notas'],
        'formato': lambda doc: f"{doc.get('motivo', '')} {doc.get('estado', '')} {doc.get('notas', '')}",
        'prioridad': 4
    },
    'ventas': {
        'campos_texto': ['estado', 'metodo_pago'],
        'formato': lambda doc: f"Venta {doc.get('estado', '')} método {doc.get('metodo_pago', '')}",
        'prioridad': 5
    }
}


def vectorizar_coleccion(nombre_coleccion, config):
    """Vectoriza una colección completa con embeddings reales"""
    
    print(f"\n{'=' * 80}")
    print(f"📊 Colección: {nombre_coleccion.upper()}")
    print(f"{'=' * 80}")
    
    col = db[nombre_coleccion]
    
    # Obtener documentos
    documentos = list(col.find({}))
    total = len(documentos)
    
    if total == 0:
        print(f"   ⚠️ Sin documentos, saltando...")
        return 0
    
    print(f"   📄 Total documentos: {total}")
    
    # Preparar textos para vectorización
    textos = []
    doc_ids = []
    
    for doc in documentos:
        texto = config['formato'](doc)
        textos.append(texto.strip())
        doc_ids.append(doc['_id'])
    
    # Generar embeddings en batch (mucho más rápido)
    print(f"   🔄 Generando embeddings...")
    embeddings = generar_embeddings_batch(textos, batch_size=32)
    
    # Actualizar documentos
    print(f"   💾 Actualizando base de datos...")
    actualizados = 0
    
    for doc_id, embedding in zip(doc_ids, embeddings):
        try:
            result = col.update_one(
                {'_id': doc_id},
                {
                    '$set': {
                        'embedding': embedding,
                        'embedding_metadata': {
                            'model': 'all-MiniLM-L6-v2',
                            'dimensions': 384,
                            'generado': datetime.now(),
                            'tipo': 'sentence-bert'
                        }
                    }
                }
            )
            if result.modified_count > 0:
                actualizados += 1
        except Exception as e:
            print(f"   ❌ Error actualizando {doc_id}: {e}")
    
    print(f"   ✅ Actualizados: {actualizados}/{total}")
    
    # Verificar algunos embeddings
    muestra = col.find_one({'embedding': {'$exists': True}})
    if muestra and 'embedding' in muestra:
        emb = muestra['embedding']
        import numpy as np
        norma = np.linalg.norm(emb)
        print(f"   📊 Verificación - Dimensiones: {len(emb)}, Norma L2: {norma:.6f}")
    
    return actualizados


def main():
    """Ejecuta la vectorización completa"""
    
    print("\n🎯 INICIO DE VECTORIZACIÓN")
    print("-" * 80)
    
    resultados = {}
    
    # Ordenar por prioridad
    colecciones_ordenadas = sorted(
        COLECCIONES_CONFIG.items(),
        key=lambda x: x[1]['prioridad']
    )
    
    for nombre, config in colecciones_ordenadas:
        try:
            actualizados = vectorizar_coleccion(nombre, config)
            resultados[nombre] = actualizados
        except Exception as e:
            print(f"\n❌ ERROR en {nombre}: {e}")
            resultados[nombre] = 0
    
    # Resumen final
    print("\n\n" + "=" * 80)
    print("📊 RESUMEN DE VECTORIZACIÓN")
    print("=" * 80)
    
    total_vectorizados = 0
    for coleccion, count in resultados.items():
        total_vectorizados += count
        status = "✅" if count > 0 else "⚠️"
        print(f"{status} {coleccion:20} → {count:3} documentos vectorizados")
    
    print("-" * 80)
    print(f"🎯 TOTAL: {total_vectorizados} documentos con embeddings reales")
    
    # Verificación final
    print("\n🔍 VERIFICACIÓN FINAL:")
    for nombre in resultados.keys():
        count_con_embedding = db[nombre].count_documents({'embedding': {'$exists': True}})
        count_total = db[nombre].count_documents({})
        porcentaje = (count_con_embedding / count_total * 100) if count_total > 0 else 0
        print(f"   {nombre}: {count_con_embedding}/{count_total} ({porcentaje:.1f}%)")
    
    print("\n" + "=" * 80)
    print("✅ VECTORIZACIÓN COMPLETADA")
    print("=" * 80)
    print("\n💡 Próximos pasos:")
    print("   1. Probar búsqueda semántica con: python buscar.py")
    print("   2. Comparar resultados con embeddings anteriores")
    print("   3. Continuar con Fase 2: REST API")
    
    client.close()


if __name__ == "__main__":
    main()
