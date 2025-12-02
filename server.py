#!/usr/bin/env python3
"""
Servidor simple sin auto-reload
"""

if __name__ == "__main__":
    import uvicorn
    
    print("=" * 60)
    print("🚀 Servidor RAG - Modo Simple")
    print("=" * 60)
    print("\n📡 Servidor: http://localhost:8000")
    print("📖 Docs: http://localhost:8000/docs")
    print("🔍 Buscador: http://localhost:8000/buscador\n")
    print("=" * 60)
    
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
