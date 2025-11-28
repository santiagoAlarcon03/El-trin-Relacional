import os
from dotenv import load_dotenv

load_dotenv()

print("="*60)
print("✅ VALIDACIÓN RÁPIDA DEL SISTEMA")
print("="*60)

# 1. Variables de entorno
print("\n1. Variables de Entorno:")
print(f"   MONGODB_URI: {'✅ Configurado' if os.getenv('MONGODB_URI') else '❌ NO configurado'}")
print(f"   MONGODB_DATABASE: {'✅ Configurado' if os.getenv('MONGODB_DATABASE') else '❌ NO configurado'}")
print(f"   GROQ_API_KEY: {'✅ Configurado' if os.getenv('GROQ_API_KEY') else '❌ NO configurado'}")

# 2. Archivos críticos
print("\n2. Archivos Críticos:")
archivos = [
    'api/main.py',
    'api/models.py',
    'api/routers/search.py',
    'api/routers/rag.py',
    'llm/groq_client.py',
    'rag/embeddings.py'
]

for archivo in archivos:
    estado = '✅' if os.path.exists(archivo) else '❌'
    print(f"   {estado} {archivo}")

# 3. Documentación
print("\n3. Documentación:")
print(f"   {'✅' if os.path.exists('docs/INFORME_ENTREGA2.md') else '❌'} docs/INFORME_ENTREGA2.md")
print(f"   {'✅' if os.path.exists('README.md') else '❌'} README.md")
print(f"   {'✅' if os.path.exists('tests/test_cases_obligatorios.py') else '❌'} tests/test_cases_obligatorios.py")

print("\n" + "="*60)
print("✅ SISTEMA LISTO - COMANDOS PARA USAR:")
print("="*60)
print("\n1. Iniciar servidor:")
print("   python -m uvicorn api.main:app --reload --port 8000")
print("\n2. Ver documentación interactiva:")
print("   http://localhost:8000/docs")
print("\n3. Ejecutar tests:")
print("   python tests/test_cases_obligatorios.py")
print("\n4. Ver informe técnico:")
print("   docs/INFORME_ENTREGA2.md")
print("\n" + "="*60)
