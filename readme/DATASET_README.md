# 📦 DATASET COMPLETO - Base de Datos Óptica

## ✅ Requisitos Cumplidos

```
╔═══════════════════════════════════════════════════════════════════════╗
║               VERIFICACIÓN DE REQUISITOS DEL DATASET                  ║
╚═══════════════════════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────────────────────┐
│ Requisito                    │ Requerido │ Entregado │ Estado      │
├──────────────────────────────┼───────────┼───────────┼─────────────┤
│ Documentos de texto          │   ≥ 100   │    128    │ ✅ CUMPLIDO │
│ Imágenes asociadas           │   ≥ 50    │     92    │ ✅ CUMPLIDO │
│ Formato JSON válido          │    Sí     │    Sí     │ ✅ CUMPLIDO │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 📊 Composición del Dataset

### Documentos por Colección (128 total)

```
┌─────────────────────┬──────────────┬──────────────┬────────────────────────┐
│    Colección        │  Documentos  │   Imágenes   │      Descripción       │
├─────────────────────┼──────────────┼──────────────┼────────────────────────┤
│ catalogos           │      1       │      0       │ Catálogos del sistema  │
│ clientes            │     30       │     30       │ Clientes con fotos     │
│ asesores            │      8       │      8       │ Vendedores con fotos   │
│ especialistas       │      6       │      6       │ Médicos con fotos      │
│ proveedores         │      5       │      5       │ Proveedores con logos  │
│ laboratorios        │      3       │      3       │ Laboratorios con logos │
│ suministros         │     10       │      0       │ Inventario entrada     │
│ productos           │     20       │     40       │ Productos con imágenes │
│ citas               │     15       │      0       │ Citas programadas      │
│ examenes            │     12       │      0       │ Exámenes visuales      │
│ ventas              │     18       │      0       │ Ventas con items       │
├─────────────────────┼──────────────┼──────────────┼────────────────────────┤
│ TOTAL               │    128       │     92       │                        │
└─────────────────────┴──────────────┴──────────────┴────────────────────────┘
```

---

## 🖼️ Distribución de Imágenes (92 total)

```
Fotos de Perfil (44):
├── Clientes:        30 fotos  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 68%
├── Asesores:         8 fotos  ━━━━━━━━ 18%
└── Especialistas:    6 fotos  ━━━━━━ 14%

Logos Corporativos (8):
├── Proveedores:      5 logos  ━━━━━━━━━━ 62.5%
└── Laboratorios:     3 logos  ━━━━━━ 37.5%

Imágenes de Productos (40):
└── Productos:       40 fotos  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100%
                    (2 por producto × 20 productos)
```

---

## 📁 Estructura de Archivos Generados

```
dataset_json/
│
├── 📄 Archivos JSON Individuales (11)
│   ├── catalogos.json          (1 documento)
│   ├── clientes.json           (30 documentos)
│   ├── asesores.json           (8 documentos)
│   ├── especialistas.json      (6 documentos)
│   ├── proveedores.json        (5 documentos)
│   ├── laboratorios.json       (3 documentos)
│   ├── suministros.json        (10 documentos)
│   ├── productos.json          (20 documentos)
│   ├── citas.json              (15 documentos)
│   ├── examenes.json           (12 documentos)
│   └── ventas.json             (18 documentos)
│
├── 📦 dataset_completo.json    (Todos consolidados)
├── 📋 metadatos.json           (Información del dataset)
└── 📖 README.md                (Documentación completa)
```

---

## 🔗 Fuentes de Imágenes

| Tipo | Cantidad | Fuente | URL Base |
|------|----------|--------|----------|
| **Avatares** | 44 | Pravatar | `https://i.pravatar.cc/300?img=N` |
| **Productos** | 40 | Unsplash | `https://images.unsplash.com/photo-...` |
| **Logos** | 8 | Placeholder | `https://via.placeholder.com/200x80/...` |

### Ejemplos de URLs:

```javascript
// Avatar de cliente
"foto_perfil": "https://i.pravatar.cc/300?img=15"

// Imagen de producto (gafas)
"imagenes": [
  "https://images.unsplash.com/photo-1574258495973-f010dfbb5371",
  "https://images.unsplash.com/photo-1511499767150-a48a237f0083"
]

// Logo de proveedor
"logo": "https://via.placeholder.com/200x80/0066cc/ffffff?text=LentesPro"
```

---

## 💾 Formato de Datos

### Ejemplo: Cliente con Imagen

```json
{
  "_id": { "$oid": "67214a1b2c3d4e5f6789abcd" },
  "nombre": "María",
  "apellido": "García",
  "email": "maria.garcia0@mail.com",
  "fecha_nacimiento": { "$date": "1985-03-15T00:00:00.000Z" },
  "foto_perfil": "https://i.pravatar.cc/300?img=5",
  "documento": {
    "tipo": "CC",
    "numero": "1234567890"
  },
  "direcciones": [
    {
      "tipo": "Principal",
      "calle": "Calle 123 #45-67",
      "ciudad": "Bogotá",
      "es_principal": true
    }
  ],
  "telefonos": [
    {
      "numero": "3101234567",
      "tipo": "Móvil"
    }
  ]
}
```

### Ejemplo: Producto con Imágenes

```json
{
  "_id": { "$oid": "67214b2c3d4e5f6789abcdef" },
  "nombre_producto": "Ray-Ban Gafas de sol Modelo-1",
  "marca": "Ray-Ban",
  "precio_venta": 450000,
  "stock": 25,
  "imagenes": [
    "https://images.unsplash.com/photo-1574258495973-f010dfbb5371",
    "https://images.unsplash.com/photo-1511499767150-a48a237f0083"
  ],
  "descripcion": "Gafas de sol de alta calidad marca Ray-Ban"
}
```

---

## 📈 Estadísticas del Dataset

### Distribución Temporal

- **Registros de Clientes**: Últimos 1000 días
- **Citas**: Últimos 30 días a próximos 60 días
- **Exámenes**: Últimos 180 días
- **Ventas**: Últimos 180 días

### Datos Realistas

- ✅ Nombres y apellidos colombianos comunes
- ✅ Ciudades principales de Colombia
- ✅ Teléfonos con prefijos colombianos (3XX)
- ✅ Direcciones formato colombiano
- ✅ Marcas reales de gafas (Ray-Ban, Oakley, Prada, etc.)
- ✅ Precios realistas en pesos colombianos
- ✅ Fórmulas oftalmológicas válidas

---

## 🚀 Cómo Usar el Dataset

### 1. Verificar Archivos

```bash
cd dataset_json
ls
# Deberías ver 14 archivos (11 JSON + dataset_completo + metadatos + README)
```

### 2. Importar a MongoDB

#### Opción A: MongoDB Compass (GUI)
1. Abrir MongoDB Compass
2. Conectar a tu cluster
3. Crear/seleccionar database `optica_db`
4. Para cada colección:
   - Click en "Add Data" → "Import File"
   - Seleccionar archivo JSON correspondiente
   - Format: JSON
   - Click "Import"

#### Opción B: mongoimport (Terminal)
```bash
mongoimport --uri "mongodb+srv://user:pass@cluster.mongodb.net/optica_db" \
  --collection clientes \
  --file clientes.json \
  --jsonArray
```

#### Opción C: Python Script
```python
from pymongo import MongoClient
from bson import json_util
import json

client = MongoClient("tu-connection-string")
db = client['optica_db']

# Importar una colección
with open('dataset_json/clientes.json', 'r', encoding='utf-8') as f:
    data = json_util.loads(f.read())
    db.clientes.insert_many(data)
```

### 3. Verificar Importación

```javascript
// En mongosh o MongoDB Compass
use optica_db;

// Verificar conteos
db.clientes.countDocuments();      // Debe ser 30
db.productos.countDocuments();     // Debe ser 20
db.ventas.countDocuments();        // Debe ser 18

// Ver un documento con imagen
db.clientes.findOne({ foto_perfil: { $exists: true } });
db.productos.findOne({ imagenes: { $exists: true } });
```

---

## ✅ Checklist de Entrega

- [x] **128 documentos** (requerido: ≥100) ✓
- [x] **92 imágenes** (requerido: ≥50) ✓
- [x] **Formato JSON válido** ✓
- [x] **11 archivos individuales** por colección ✓
- [x] **1 archivo consolidado** (dataset_completo.json) ✓
- [x] **Metadatos** (metadatos.json) ✓
- [x] **Documentación** (README.md) ✓
- [x] **Relaciones consistentes** (ObjectIds válidos) ✓
- [x] **Imágenes accesibles** (URLs públicas) ✓
- [x] **Datos realistas** (nombres, ciudades, precios) ✓

---

## 🎯 Casos de Uso Demostrados

1. **Gestión de Clientes**: 30 perfiles con fotos, direcciones y teléfonos
2. **Catálogo de Productos**: 20 productos con imágenes y stock
3. **Sistema de Citas**: 15 citas con especialistas
4. **Historial Médico**: 12 exámenes visuales completos
5. **Ventas**: 18 transacciones con items embebidos
6. **Inventario**: 10 suministros con trazabilidad
7. **Red de Proveedores**: 5 proveedores + 3 laboratorios con logos

---

## 📝 Notas Importantes

- Todos los datos son **ficticios** y generados aleatoriamente
- Las imágenes son de **dominio público** o placeholders
- Los **ObjectIds** son consistentes entre colecciones (referencias válidas)
- Las **fechas** están distribuidas realísticamente
- Los **precios** están en pesos colombianos (COP)
- Las **URLs de imágenes** son accesibles públicamente

---

## 🔧 Herramientas de Generación

- **Script**: `generar_dataset.py` (generación de datos)
- **Script**: `exportar_dataset.py` (exportación a JSON)
- **Script**: `crear_indices.py` (61 índices optimizados)
- **Script**: `migracion_mysql_a_mongodb.py` (migración inicial)

---

## 📞 Información Adicional

**Base de Datos**: MongoDB Atlas - `optica_db`  
**Total Colecciones**: 11  
**Total Documentos**: 128  
**Total Imágenes**: 92  
**Formato**: JSON con soporte BSON (ObjectId, DateTime)  
**Encoding**: UTF-8  
**Tamaño aprox**: ~500KB (dataset_completo.json)

---

✅ **Dataset listo para entregar y evaluar** 🎉
