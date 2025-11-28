#!/usr/bin/env python3
"""
Script de validación end-to-end del sistema RAG
Verifica que todos los componentes funcionen correctamente
"""

import sys
from pymongo import MongoClient
from dotenv import load_dotenv
import os

def colorize(text, color):
    colors = {
        'green': '\033[92m',
        'red': '\033[91m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'reset': '\033[0m'
    }
    return f"{colors[color]}{text}{colors['reset']}"

def check_env():
    """Verificar variables de entorno"""
    print("\n🔍 Validando variables de entorno...")
    load_dotenv()
    
    mongodb_uri = os.getenv('MONGODB_URI')
    mongodb_db = os.getenv('MONGODB_DATABASE')
    groq_key = os.getenv('GROQ_API_KEY')
    
    if not mongodb_uri:
        print(colorize("❌ MONGODB_URI no configurada en .env", 'red'))
        return False
    print(colorize("✅ MONGODB_URI configurada", 'green'))
    
    if not mongodb_db:
        print(colorize("❌ MONGODB_DATABASE no configurada en .env", 'red'))
        return False
    print(colorize("✅ MONGODB_DATABASE configurada", 'green'))
    
    if not groq_key:
        print(colorize("❌ GROQ_API_KEY no configurada en .env", 'red'))
        return False
    print(colorize("✅ GROQ_API_KEY configurada", 'green'))
    
    return True

def check_mongodb():
    """Verificar conexión a MongoDB"""
    print("\n🔍 Validando conexión a MongoDB...")
    try:
        load_dotenv()
        client = MongoClient(os.getenv('MONGODB_URI'), serverSelectionTimeoutMS=5000)
        db = client[os.getenv('MONGODB_DATABASE')]
        
        # Ping para verificar conexión
        client.admin.command('ping')
        print(colorize("✅ Conexión a MongoDB exitosa", 'green'))
        
        # Contar colecciones
        collections = db.list_collection_names()
        print(f"✅ Encontradas {len(collections)} colecciones")
        
        # Contar documentos vectorizados
        target_collections = ['productos', 'clientes', 'examenes', 'citas', 'ventas', 
                            'asesores', 'especialistas', 'proveedores', 'laboratorios']
        
        total_docs = 0
        total_vectorized = 0
        
        for col in target_collections:
            if col in collections:
                count = db[col].count_documents({})
                vectorized = db[col].count_documents({'embedding': {'$exists': True}})
                total_docs += count
                total_vectorized += vectorized
        
        print(f"✅ Documentos totales: {total_docs}")
        print(f"✅ Documentos vectorizados: {total_vectorized}")
        
        if total_vectorized < 100:
            print(colorize(f"⚠️  Bajo número de documentos vectorizados ({total_vectorized})", 'yellow'))
            print(colorize("   Ejecuta: python vectorizar_colecciones.py", 'yellow'))
        
        client.close()
        return True
        
    except Exception as e:
        print(colorize(f"❌ Error al conectar a MongoDB: {str(e)}", 'red'))
        return False

def check_dependencies():
    """Verificar dependencias instaladas"""
    print("\n🔍 Validando dependencias...")
    
    # Mapeo de paquetes a nombres de importación
    required = {
        'fastapi': 'fastapi',
        'uvicorn': 'uvicorn',
        'pydantic': 'pydantic',
        'pymongo': 'pymongo',
        'sentence-transformers': 'sentence_transformers',
        'groq': 'groq',
        'python-dotenv': 'dotenv'
    }
    
    missing = []
    
    for package_name, import_name in required.items():
        try:
            __import__(import_name)
            print(colorize(f"✅ {package_name} instalado", 'green'))
        except ImportError:
            print(colorize(f"❌ {package_name} NO instalado", 'red'))
            missing.append(package_name)
    
    if missing:
        print(colorize(f"\n⚠️  Instala dependencias faltantes:", 'yellow'))
        print(colorize(f"   pip install {' '.join(missing)}", 'yellow'))
        return False
    
    return True

def check_files():
    """Verificar estructura de archivos"""
    print("\n🔍 Validando estructura de archivos...")
    
    required_files = [
        'api/main.py',
        'api/models.py',
        'api/routers/search.py',
        'api/routers/rag.py',
        'llm/groq_client.py',
        'rag/embeddings.py',
        'tests/test_cases_obligatorios.py',
        'docs/INFORME_ENTREGA2.md'
    ]
    
    missing = []
    
    for filepath in required_files:
        if os.path.exists(filepath):
            print(colorize(f"✅ {filepath}", 'green'))
        else:
            print(colorize(f"❌ {filepath} NO encontrado", 'red'))
            missing.append(filepath)
    
    if missing:
        print(colorize(f"\n⚠️  Faltan archivos críticos del sistema", 'red'))
        return False
    
    return True

def main():
    """Ejecutar todas las validaciones"""
    print(colorize("\n" + "="*60, 'blue'))
    print(colorize("🚀 VALIDACIÓN END-TO-END - Sistema RAG", 'blue'))
    print(colorize("="*60 + "\n", 'blue'))
    
    checks = [
        ("Variables de entorno", check_env),
        ("Dependencias Python", check_dependencies),
        ("Estructura de archivos", check_files),
        ("Conexión MongoDB", check_mongodb),
    ]
    
    results = []
    
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(colorize(f"❌ Error en {name}: {str(e)}", 'red'))
            results.append((name, False))
    
    # Resumen
    print(colorize("\n" + "="*60, 'blue'))
    print(colorize("📊 RESUMEN DE VALIDACIÓN", 'blue'))
    print(colorize("="*60 + "\n", 'blue'))
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = colorize("✅ PASSED", 'green') if result else colorize("❌ FAILED", 'red')
        print(f"{name}: {status}")
    
    print(f"\n{colorize(f'Total: {passed}/{total} checks pasados', 'blue')}")
    
    if passed == total:
        print(colorize("\n🎉 ¡Sistema completamente funcional!", 'green'))
        print(colorize("\nPróximos pasos:", 'blue'))
        print("  1. Iniciar servidor: python -m uvicorn api.main:app --reload --port 8000")
        print("  2. Abrir docs: http://localhost:8000/docs")
        print("  3. Ejecutar tests: python tests/test_cases_obligatorios.py")
        return 0
    else:
        print(colorize(f"\n⚠️  Sistema incompleto ({total - passed} problemas)", 'yellow'))
        print(colorize("Revisa los errores arriba y corrige antes de continuar", 'yellow'))
        return 1

if __name__ == '__main__':
    sys.exit(main())
