# Dataset - Base de Datos Óptica

## 📊 Descripción

Dataset completo para sistema de gestión de óptica con **128 documentos** y **92 imágenes asociadas**.

## 📁 Estructura del Dataset

```
dataset_json/
├── catalogos.json          (1 documento - Catálogos del sistema)
├── clientes.json           (30 documentos - Clientes con fotos)
├── asesores.json           (8 documentos - Asesores/Vendedores)
├── especialistas.json      (6 documentos - Optómetras/Oftalmólogos)
├── proveedores.json        (5 documentos - Proveedores con logos)
├── laboratorios.json       (3 documentos - Laboratorios)
├── suministros.json        (10 documentos - Inventario entrada)
├── productos.json          (20 documentos - Productos con imágenes)
├── citas.json              (15 documentos - Citas programadas)
├── examenes.json           (12 documentos - Exámenes visuales)
├── ventas.json             (18 documentos - Ventas realizadas)
├── dataset_completo.json   (Todos los datos consolidados)
├── metadatos.json          (Información del dataset)
└── README.md               (Este archivo)
```

## 🖼️ Imágenes Incluidas

- **44 fotos de perfil** (clientes, asesores, especialistas)
- **8 logos** (proveedores y laboratorios)
- **40 imágenes de productos** (gafas, monturas, etc.)

**Total: 92 imágenes**

## 📋 Detalles por Colección

| Colección | Documentos | Imágenes | Descripción |
|-----------|------------|----------|-------------|
| catalogos | 1 | 0 | Catálogos estáticos del sistema |
| clientes | 30 | 30 | Clientes con fotos de perfil |
| asesores | 8 | 8 | Asesores/vendedores con fotos |
| especialistas | 6 | 6 | Optómetras/oftalmólogos con fotos |
| proveedores | 5 | 5 | Proveedores con logos |
| laboratorios | 3 | 3 | Laboratorios con logos |
| suministros | 10 | 0 | Entradas de inventario |
| productos | 20 | 40 | Productos con 2 imágenes cada uno |
| citas | 15 | 0 | Citas programadas |
| examenes | 12 | 0 | Exámenes visuales completos |
| ventas | 18 | 0 | Ventas con items embebidos |

## 🔗 Fuentes de Imágenes

- **Avatares**: https://pravatar.cc (avatares aleatorios)
- **Productos**: https://unsplash.com (fotos gratuitas de alta calidad)
- **Logos**: https://via.placeholder.com (placeholders personalizados)

## 📦 Formato de Datos

- **Formato**: JSON válido
- **Encoding**: UTF-8
- **Tipos especiales**: 
  - ObjectId: `{"$oid": "..."}`
  - DateTime: `{"$date": "..."}`
  - Decimals: números flotantes

## 🔄 Carga del Dataset

### Opción 1: MongoDB Compass
1. Abrir MongoDB Compass
2. Conectar a tu cluster
3. Seleccionar base de datos `optica_db`
4. Para cada colección: Import Data → JSON → Seleccionar archivo

### Opción 2: mongoimport (CLI)
```bash
mongoimport --uri "tu-connection-string" --db optica_db --collection clientes --file dataset_json/clientes.json --jsonArray
```

### Opción 3: Python (pymongo)
```python
from pymongo import MongoClient
import json
from bson import json_util

client = MongoClient("tu-connection-string")
db = client['optica_db']

with open('dataset_json/clientes.json', 'r') as f:
    data = json_util.loads(f.read())
    db.clientes.insert_many(data)
```

## ✅ Validación del Dataset

- ✅ Mínimo 100 documentos: **128 documentos** ✓
- ✅ Mínimo 50 imágenes: **92 imágenes** ✓
- ✅ Formato JSON válido: **Sí** ✓
- ✅ Relaciones consistentes: **Sí** ✓
- ✅ Datos realistas: **Sí** ✓

## 🎯 Casos de Uso

1. **Gestión de clientes**: Perfiles completos con historial
2. **Control de inventario**: Suministros y productos con trazabilidad
3. **Agenda médica**: Citas y exámenes visuales
4. **Sistema de ventas**: Transacciones completas con items
5. **Reportes**: Datos suficientes para análisis y dashboards

## 📝 Notas

- Todos los datos son ficticios y generados aleatoriamente
- Las imágenes son de dominio público o placeholders
- Los ObjectIds y referencias son consistentes entre colecciones
- Fechas distribuidas en últimos 2 años para simular actividad real

---

**Generado**: 2023-02-19  
**Base de Datos**: MongoDB Atlas - optica_db  
**Total Documentos**: 128  
**Total Imágenes**: 92
