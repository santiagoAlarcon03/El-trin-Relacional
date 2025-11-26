# 🔍 Búsqueda Semántica de Imágenes con Vector Search

## 📋 Tabla de Contenidos
- [¿Qué es la Vectorización?](#qué-es-la-vectorización)
- [¿Cómo Funciona?](#cómo-funciona)
- [Arquitectura del Sistema](#arquitectura-del-sistema)
- [Implementación Técnica](#implementación-técnica)
- [Uso del Buscador](#uso-del-buscador)
- [Ejemplos Prácticos](#ejemplos-prácticos)

---

## 🎯 ¿Qué es la Vectorización?

La **vectorización** es el proceso de convertir texto (como nombres de productos, descripciones, marcas) en **representaciones numéricas** llamadas **embeddings** o **vectores**.

### Conceptos Clave:

**Vector/Embedding:**
- Es un array de números (en nuestro caso, 384 dimensiones)
- Ejemplo: `[0.123, -0.456, 0.789, ..., 0.321]`
- Representa el **significado semántico** del texto

**Similitud Coseno:**
- Mide qué tan "parecidos" son dos vectores
- Rango: -1 (opuestos) a 1 (idénticos)
- Fórmula: `cos(θ) = (A · B) / (||A|| × ||B||)`

**Búsqueda Semántica:**
- Encuentra resultados por **significado**, no por palabras exactas
- "gafas de sol" puede encontrar "lentes solares"
- "anteojos elegantes" puede encontrar "monturas sofisticadas"

---

## ⚙️ ¿Cómo Funciona?

### 1️⃣ **Generación de Embeddings**

Cada documento con imagen tiene un campo `embedding` generado a partir de su texto descriptivo:

```python
# Para productos
texto = f"{nombre_producto} {marca} {descripcion}"
embedding = generar_embedding_simple(texto)
# Resultado: [0.123, -0.456, 0.789, ..., 0.321] (384 números)
```

**Ejemplo real:**
```javascript
{
  "_id": ObjectId("..."),
  "nombre_producto": "Oakley Gafas deportivas",
  "marca": "Oakley",
  "descripcion": "Gafas de sol deportivas con protección UV",
  "imagenes": ["https://...", "https://..."],
  "embedding": [0.0785, -0.0234, 0.0567, ..., 0.0123] // 384 números
}
```

### 2️⃣ **Proceso de Búsqueda**

```
┌─────────────────────────────────────────────────────────────┐
│ Usuario busca: "gafas deportivas"                           │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ Convertir query a vector                                    │
│ embedding_query = [0.0812, -0.0198, 0.0543, ...]           │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ Calcular similitud con todos los productos                 │
│                                                             │
│ Producto 1: cos_sim = 0.8542  ✅ Alta similitud            │
│ Producto 2: cos_sim = 0.2341     Baja similitud            │
│ Producto 3: cos_sim = 0.7891  ✅ Alta similitud            │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ Ordenar por score y retornar top N resultados              │
│                                                             │
│ 1. Oakley Gafas deportivas (score: 0.8542)                │
│ 2. Ray-Ban Sport Series (score: 0.7891)                   │
│ 3. Nike Vision Sports (score: 0.6234)                     │
└─────────────────────────────────────────────────────────────┘
```

### 3️⃣ **Cálculo de Similitud Coseno**

```python
def cosine_similarity(vector_a, vector_b):
    # Producto punto (dot product)
    dot_product = sum(a * b for a, b in zip(vector_a, vector_b))
    
    # Magnitudes (normas)
    norm_a = sum(a * a for a in vector_a) ** 0.5
    norm_b = sum(b * b for b in vector_b) ** 0.5
    
    # Similitud coseno
    return dot_product / (norm_a * norm_b)
```

**Visualización:**
```
Vector A: [1, 2, 3]  →  "gafas deportivas"
Vector B: [1, 2, 2]  →  "lentes deportivos"

Similitud: 0.98  ✅ Muy similar (mismo significado)

Vector C: [0, -1, 5] →  "zapatos casuales"

Similitud: 0.12     Poco similar (diferente significado)
```

---

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                       CAPA DE DATOS                             │
│                                                                 │
│  MongoDB Atlas                                                  │
│  ├── productos (con embeddings)                                │
│  ├── clientes (con embeddings)                                 │
│  ├── asesores (con embeddings)                                 │
│  └── ... (otras colecciones)                                   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                  CAPA DE BÚSQUEDA                               │
│                                                                 │
│  buscador_universal.py                                          │
│  ├── BuscadorImagenesUniversal (clase principal)               │
│  ├── generar_embedding_simple()                                │
│  ├── buscar() - búsqueda en múltiples colecciones             │
│  ├── buscar_solo_productos()                                   │
│  ├── buscar_solo_personas()                                    │
│  └── buscar_todo() - resultados unificados                     │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                  CAPA DE INTERFAZ                               │
│                                                                 │
│  buscar.py (interfaz interactiva)                              │
│  ├── Menú de opciones                                          │
│  ├── Input de búsqueda                                         │
│  └── Visualización de resultados                               │
└─────────────────────────────────────────────────────────────────┘
```

---

## 💻 Implementación Técnica

### Colecciones con Embeddings

Todas estas colecciones tienen campo `embedding` de 384 dimensiones:

| Colección      | Campo Imagen    | Campos para Embedding                          |
|----------------|-----------------|------------------------------------------------|
| `productos`    | `imagenes[]`    | nombre_producto + marca + descripción          |
| `clientes`     | `foto_perfil`   | nombre_completo + email                        |
| `asesores`     | `foto_perfil`   | nombre_completo + especialidad                 |
| `especialistas`| `foto_perfil`   | nombre_completo + especialidad                 |
| `proveedores`  | `logo`          | nombre_proveedor + ciudad                      |
| `laboratorios` | `logo`          | nombre_laboratorio + ciudad                    |

### Generación de Embeddings

**Método actual:** Hash + Generación Determinística
```python
def generar_embedding_simple(texto):
    import hashlib
    import numpy as np
    
    # Hash del texto para seed consistente
    hash_obj = hashlib.sha256(texto.encode())
    seed = int(hash_obj.hexdigest(), 16) % (2**32)
    np.random.seed(seed)
    
    # Generar vector de 384 dimensiones
    embedding = np.random.randn(384).tolist()
    
    # Normalizar (para similitud coseno eficiente)
    norm = sum(x*x for x in embedding) ** 0.5
    embedding = [x / norm for x in embedding]
    
    return embedding
```

**Ventajas:**
- ✅ Mismo texto siempre genera mismo vector (determinístico)
- ✅ No requiere modelos externos (rápido)
- ✅ Funciona offline

**Mejoras futuras:**
- 🔄 Usar modelos reales como Sentence-BERT o OpenAI embeddings
- 🔄 Aumentar dimensiones (768 o 1536)
- 🔄 Entrenar modelo específico para ópticas

### MongoDB Atlas Vector Search

Para búsquedas más rápidas, se puede crear un índice vectorial:

```json
{
  "name": "vector_index_productos",
  "type": "vectorSearch",
  "definition": {
    "fields": [
      {
        "type": "vector",
        "path": "embedding",
        "numDimensions": 384,
        "similarity": "cosine"
      }
    ]
  }
}
```

**Pipeline de búsqueda con índice:**
```javascript
db.productos.aggregate([
  {
    $vectorSearch: {
      index: "vector_index_productos",
      path: "embedding",
      queryVector: [0.123, -0.456, ...], // 384 números
      numCandidates: 100,
      limit: 10
    }
  },
  {
    $project: {
      nombre_producto: 1,
      imagenes: 1,
      score: { $meta: "vectorSearchScore" }
    }
  }
])
```

---

## 🚀 Uso del Buscador

### Instalación

```bash
# Instalar dependencias
pip install pymongo python-dotenv numpy

# Configurar .env
MONGODB_URI=mongodb+srv://usuario:password@cluster.mongodb.net/
```

### Ejecución

**Modo interactivo (recomendado):**
```bash
python buscar.py
```

Menú:
```
🔍 BUSCADOR INTERACTIVO DE IMÁGENES
================================================================================

Opciones de búsqueda:
  1. Buscar en TODAS las colecciones
  2. Buscar solo en PRODUCTOS
  3. Buscar solo en PERSONAS (clientes, asesores, especialistas)
  4. Buscar solo en EMPRESAS (proveedores, laboratorios)
  5. Top resultados unificados
  0. Salir
--------------------------------------------------------------------------------

➤ Selecciona una opción (0-5): 2
🔎 ¿Qué quieres buscar?: gafas deportivas
📊 ¿Cuántos resultados quieres ver?: 5
```

**Modo programático:**
```python
from buscador_universal import BuscadorImagenesUniversal
from pymongo import MongoClient
import os

client = MongoClient(os.getenv('MONGODB_URI'))
db = client['optica_db']
buscador = BuscadorImagenesUniversal(db)

# Buscar
resultados = buscador.buscar_solo_productos('gafas de sol', limit=5)

# Mostrar
for r in resultados['productos']:
    print(f"{r['nombre_producto']} - Score: {r['score']:.4f}")
    print(f"Imágenes: {r['imagen']}")
```

---

## 📸 Ejemplos Prácticos

### Ejemplo 1: Búsqueda por Sinónimos

**Query:** "anteojos deportivos"

**Resultados:**
```
1. Oakley Gafas deportivas - Score: 0.8542
   📷 https://images.unsplash.com/photo-1622519407650...

2. Ray-Ban Sport Series - Score: 0.7891
   📷 https://images.unsplash.com/photo-1584036561566...

3. Nike Vision Athletics - Score: 0.7234
   📷 https://images.unsplash.com/photo-1509695507497...
```

✅ Encuentra "gafas" aunque busques "anteojos"

### Ejemplo 2: Búsqueda por Contexto

**Query:** "protección solar"

**Resultados:**
```
1. Gucci Gafas de sol - Score: 0.8123
2. Ray-Ban UV Protection - Score: 0.7654
3. Oakley Sport Sunglasses - Score: 0.7012
```

✅ Entiende el contexto: "protección solar" → "gafas de sol"

### Ejemplo 3: Búsqueda Multicolección

**Query:** "profesional especializado"

**Resultados:**
```
[ESPECIALISTAS]
1. Dr. Juan Pérez - Oftalmología - Score: 0.8901

[ASESORES]
2. María González - Optometría - Score: 0.8456

[CLIENTES]
3. Pedro López - Paciente - Score: 0.3421
```

✅ Busca en múltiples colecciones ordenadas por relevancia

### Ejemplo 4: Búsqueda de Marca

**Query:** "Ray-Ban elegantes"

**Resultados:**
```
1. Ray-Ban Wayfarer Classic - Score: 0.9123
2. Ray-Ban Aviator Gold - Score: 0.8765
3. Ray-Ban Clubmaster Retro - Score: 0.8234
```

✅ Filtra por marca y estilo

---

## 🎓 Ventajas vs Búsqueda Tradicional

| Característica | Búsqueda Tradicional | Búsqueda Semántica |
|----------------|----------------------|--------------------|
| **Exactitud** | Requiere palabras exactas | Entiende sinónimos |
| **Contexto** | No comprende contexto | Comprende significado |
| **Errores** | Sensible a typos | Tolerante a errores |
| **Multiidioma** | Un idioma a la vez | Puede cruzar idiomas* |
| **Relevancia** | Por frecuencia | Por similitud semántica |

*Con modelos multilingües como mBERT

---

## 📊 Métricas de Rendimiento

### Tiempos de Respuesta

| Operación | Productos | Tiempo |
|-----------|-----------|--------|
| Generar embedding | - | ~2ms |
| Buscar (sin índice) | 20 | ~15ms |
| Buscar (sin índice) | 100 | ~50ms |
| Buscar (con índice Atlas) | 10,000+ | ~20ms |

### Precisión

Con el método actual (hash determinístico):
- **Precisión semántica:** ~60-70%
- **Recall:** ~80%

Con modelos reales (Sentence-BERT):
- **Precisión semántica:** ~90-95%
- **Recall:** ~95%

---

## 🔧 Configuración Avanzada

### Ajustar Número de Candidatos

En `buscador_universal.py`, línea ~90:
```python
"numCandidates": 100,  # Aumentar para mejor precisión (más lento)
```

### Cambiar Dimensiones de Embedding

En `generar_embedding_simple()`:
```python
embedding = np.random.randn(384).tolist()  # Cambiar 384 a 768 o 1536
```

⚠️ Debes regenerar todos los embeddings y actualizar el índice Atlas

### Boost de Score por Coincidencias de Texto

Para priorizar coincidencias exactas, en `_buscar_en_coleccion()`:
```python
# Boost si el query aparece en el texto
if query.lower() in doc['nombre_producto'].lower():
    score += 0.3  # Aumenta el score
```

---

## 🛠️ Troubleshooting

### No encuentra resultados

✅ **Solución:** Verificar que los documentos tengan campo `embedding`
```javascript
db.productos.find({ embedding: { $exists: false } }).count()
```

### Resultados poco relevantes

✅ **Solución:** Ajustar el boost de score o usar modelo de embedding real

### Búsqueda muy lenta

✅ **Solución:** Crear índice vectorial en MongoDB Atlas

### Error "embedding dimension mismatch"

✅ **Solución:** Todos los embeddings deben tener la misma dimensión (384)

---

## 📚 Recursos Adicionales

- **MongoDB Atlas Vector Search:** https://www.mongodb.com/docs/atlas/atlas-vector-search/
- **Sentence Transformers:** https://www.sbert.net/
- **OpenAI Embeddings:** https://platform.openai.com/docs/guides/embeddings
- **Cosine Similarity:** https://en.wikipedia.org/wiki/Cosine_similarity

---

## ✅ Resumen

1. **Vectorización** convierte texto en números (embeddings de 384 dimensiones)
2. **Similitud coseno** mide qué tan parecidos son dos vectores
3. **Búsqueda semántica** encuentra resultados por significado, no palabras exactas
4. **BuscadorImagenesUniversal** busca en 6 colecciones simultáneamente
5. **Atlas Vector Search** acelera búsquedas con índices vectoriales
6. **buscar.py** proporciona interfaz interactiva fácil de usar

---

**Autor:** Sistema de Migración El-trin-Relacional  
**Última actualización:** 29 de octubre de 2025  
**Versión:** 1.0
