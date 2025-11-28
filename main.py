#!/usr/bin/env python3
"""
Punto de entrada principal para el servidor RAG
Uso: python main.py
"""

import uvicorn
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def main():
    """Iniciar servidor FastAPI"""
    print("="*60)
    print("🚀 Iniciando servidor RAG...")
    print("="*60)
    print(f"\n📡 API disponible en: http://localhost:8000")
    print(f"📖 Documentación en: http://localhost:8000/docs")
    print(f"📘 ReDoc en: http://localhost:8000/redoc")
    print(f"\n⏹️  Para detener: Ctrl+C\n")
    print("="*60 + "\n")
    
    # Iniciar servidor
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()
