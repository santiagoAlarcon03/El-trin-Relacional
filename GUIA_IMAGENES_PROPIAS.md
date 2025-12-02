# GUÍA: Cómo usar imágenes propias en el proyecto

## 📁 Estructura recomendada:

```
El-trin-Relacional/
├── static/
│   └── imagenes/
│       ├── gafas-sol/
│       │   ├── ray-ban-aviator-1.jpg
│       │   ├── ray-ban-aviator-2.jpg
│       │   ├── oakley-holbrook-1.jpg
│       │   └── ...
│       ├── lentes-contacto/
│       │   ├── acuvue-oasys-1.jpg
│       │   └── ...
│       ├── soluciones/
│       │   ├── renu-360ml-1.jpg
│       │   └── ...
│       ├── accesorios/
│       │   ├── estuche-eva-1.jpg
│       │   └── ...
│       └── monturas/
│           ├── silhouette-titan-1.jpg
│           └── ...
```

## 🔧 Pasos para implementar:

### 1. Crear estructura de carpetas
```bash
mkdir -p static/imagenes/gafas-sol
mkdir -p static/imagenes/lentes-contacto
mkdir -p static/imagenes/soluciones
mkdir -p static/imagenes/accesorios
mkdir -p static/imagenes/monturas
```

### 2. Descargar imágenes reales
- Busca en Google Images imágenes de productos reales
- Descarga 2 imágenes por producto
- Renómbralas descriptivamente

### 3. Configurar FastAPI para servir imágenes estáticas

Edita `api/main.py` y agrega:

```python
from fastapi.staticfiles import StaticFiles

# Después de crear la app
app.mount("/static", StaticFiles(directory="static"), name="static")
```

### 4. Actualizar URLs en MongoDB

Las URLs serían:
```python
"imagenes": [
    "http://localhost:8000/static/imagenes/gafas-sol/ray-ban-aviator-1.jpg",
    "http://localhost:8000/static/imagenes/gafas-sol/ray-ban-aviator-2.jpg"
]
```

### 5. Script de actualización automática

Crea `actualizar_imagenes_locales.py`:

```python
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

client = MongoClient(os.getenv('MONGODB_URI'))
db = client['optica_db']

# Actualiza según tus archivos
actualizaciones = {
    "Ray-Ban Aviator Classic RB3025": [
        "http://localhost:8000/static/imagenes/gafas-sol/ray-ban-aviator-1.jpg",
        "http://localhost:8000/static/imagenes/gafas-sol/ray-ban-aviator-2.jpg"
    ],
    # ... más productos
}

for nombre, imagenes in actualizaciones.items():
    db.productos.update_one(
        {'nombre_producto': nombre},
        {'$set': {'imagenes': imagenes}}
    )
```

## ✅ Ventajas de imágenes locales:

- ✅ **Control total**: Tú decides qué imágenes mostrar
- ✅ **Sin errores 404**: Las imágenes siempre están disponibles
- ✅ **Mejor relevancia**: Imágenes exactas del producto
- ✅ **Rendimiento**: Más rápido que URLs externas
- ✅ **Sin dependencias**: No depende de servicios externos

## 🎯 Por ahora:

Las imágenes actuales de Unsplash funcionan, pero son **genéricas**.
Si quieres precisión en el buscador visual, debes usar imágenes reales
de cada producto específico.

¿Quieres que te ayude a implementar el sistema de imágenes locales?
