# 🔄 Migración de Base de Datos Óptica
## MySQL (Relacional) → MongoDB Atlas (NoSQL)

---

## 📖 Descripción del Proyecto

Este proyecto documenta y automatiza la migración completa de una base de datos relacional MySQL de un negocio de óptica hacia MongoDB Atlas, aplicando principios de diseño NoSQL con **embedding** (documentos embebidos) y **referencing** (referencias entre documentos).

### 🎯 Objetivos

1. **Transformar** 22 tablas relacionales en 12 colecciones NoSQL
2. **Aplicar** estrategias de embedding y referencing apropiadas
3. **Optimizar** consultas eliminando JOINs complejos
4. **Mantener** integridad de datos mediante validación de schemas
5. **Documentar** decisiones de diseño y proceso de migración

---

## 📁 Estructura del Proyecto

```
Óptica/
├── Schema.sql                      # ❌ Schema MySQL original (con problemas)
├── Schema_Fixed.sql                # ✅ Schema MySQL corregido (22 tablas)
│
├── MIGRACION_ESTRATEGIA.md         # 📋 Estrategia y diseño conceptual
├── GUIA_IMPLEMENTACION.md          # 📘 Guía paso a paso para ejecutar
│
├── MongoDB_Schemas.js              # 🏗️ Schemas de validación MongoDB (12 colecciones)
├── MongoDB_Migracion_Datos.js      # 📦 Script de migración manual con datos
│
├── migracion_automatica.py         # 🤖 Script Python para migración automática
├── .env.example                    # 🔧 Plantilla de configuración
└── README.md                       # 📖 Este archivo
```

---

## 🚀 Inicio Rápido

### Opción 1: Migración Manual con Datos de Prueba

```powershell
# 1. Instalar MongoDB Shell
# Descargar de: https://www.mongodb.com/try/download/shell

# 2. Crear cuenta en MongoDB Atlas
# https://www.mongodb.com/cloud/atlas

# 3. Ejecutar schemas
mongosh "tu-connection-string" --file MongoDB_Schemas.js

# 4. Cargar datos de prueba
mongosh "tu-connection-string" --file MongoDB_Migracion_Datos.js
```

### Opción 2: Migración Automática desde MySQL

```powershell
# 1. Instalar dependencias Python
pip install pymongo mysql-connector-python python-dotenv

# 2. Configurar credenciales
cp .env.example .env
# Editar .env con tus credenciales

# 3. Ejecutar migración
python migracion_automatica.py
```

---

## 📊 Transformación de Datos

### De 22 Tablas Relacionales → 12 Colecciones NoSQL

| MySQL (Relacional) | MongoDB (NoSQL) | Estrategia |
|-------------------|-----------------|------------|
| `Cliente` + `DireccionCliente` + `TelefonoCliente` | `clientes` | **EMBEDDING** |
| `Asesor` + `TelefonoAsesor` + `EmailAsesor` | `asesores` | **EMBEDDING** |
| `Especialista` + `EspecialistaEspecialidad` + contactos | `especialistas` | **EMBEDDING** |
| `Producto` + `TipoProducto` | `productos` | **EMBEDDING** (tipo) + **REFERENCING** (suministro) |
| `Cita` + `Motivo` | `citas` | **EMBEDDING** (motivo) + **REFERENCING** (cliente, especialista) |
| `ExamenVista` + `Diagnostico` + `FormulaMedica` | `examenes` | **EMBEDDING** (todo en uno) |
| `Compra` + `DetalleCompra` + `Factura` | `ventas` | **EMBEDDING** (items + factura) |
| 6 tablas de catálogos | `catalogos` | **EMBEDDING** (documento único) |

### Ventajas del Diseño NoSQL

✅ **Menos consultas**: De 5+ JOINs a 1-2 queries  
✅ **Rendimiento**: Datos relacionados en un solo documento  
✅ **Escalabilidad**: Fácil sharding por cliente_id  
✅ **Flexibilidad**: Fácil agregar campos sin ALTER TABLE  
✅ **Atomicidad**: Operaciones atómicas en un documento  

---

## 🔍 Decisiones de Diseño Clave

### 1. **Embedding**: Cuando Embeber Documentos

Se embeben subdocumentos cuando:
- ✅ Relación 1:N donde N es pequeño (1-10 items)
- ✅ Los datos siempre se consultan juntos
- ✅ Los subdocumentos no se consultan independientemente

**Ejemplo: Cliente con direcciones**
```javascript
{
  _id: ObjectId("..."),
  nombre: "Ana Pérez",
  direcciones: [  // EMBEBIDO
    { calle: "Calle 123", ciudad: "Bogotá" }
  ],
  telefonos: [    // EMBEBIDO
    { numero: "3101234567", tipo: "Móvil" }
  ]
}
```

### 2. **Referencing**: Cuando Usar Referencias

Se usan referencias cuando:
- 🔗 Relación N:N (muchos a muchos)
- 🔗 Los documentos pueden crecer sin límite
- 🔗 Los datos se consultan independientemente
- 🔗 Se necesita integridad referencial

**Ejemplo: Cita referenciando Cliente y Especialista**
```javascript
{
  _id: ObjectId("..."),
  fecha_cita: ISODate("2025-10-25"),
  cliente_ref: ObjectId("..."),      // REFERENCIA
  especialista_ref: ObjectId("..."), // REFERENCIA
  motivo: { descripcion: "..." }     // EMBEBIDO
}
```

### 3. **Denormalización Controlada**

Algunos datos se duplican intencionalmente para optimizar consultas:

```javascript
// En colección "ventas"
{
  items: [
    {
      producto_ref: ObjectId("..."),  // Referencia para integridad
      producto_info: {                // Denormalizado para performance
        nombre: "Lente Esférico",
        codigo_barras: "7890123456001"
      },
      cantidad: 2,
      precio_unitario: 150000
    }
  ]
}
```

**Razón**: Evita JOIN al consultar ventas, mantiene datos históricos.

---

## 📚 Documentación Detallada

### 1. **MIGRACION_ESTRATEGIA.md**
- Análisis del esquema relacional original
- Diseño de colecciones MongoDB
- Justificación de embedding vs referencing
- Ejemplos de estructura de datos
- Patrones de consulta optimizados

### 2. **GUIA_IMPLEMENTACION.md**
- Configuración de MongoDB Atlas (paso a paso)
- Creación de usuario y seguridad
- Ejecución de scripts
- Validación de datos migrados
- Consultas de prueba
- Troubleshooting
- Checklist completo

### 3. **MongoDB_Schemas.js**
- Definición de 12 colecciones
- Validación JSON Schema para cada colección
- Índices para optimización de consultas
- Constraints de integridad

### 4. **MongoDB_Migracion_Datos.js**
- Datos de prueba completos
- Ejemplos de inserción con embedding
- Ejemplos de inserción con referencing
- Consultas de validación

---

## 🎓 Conceptos Aprendidos

### Embedding (Documentos Embebidos)

**Ventajas:**
- ✅ Una sola consulta para datos relacionados
- ✅ Mejor performance en lectura
- ✅ Atomicidad garantizada

**Desventajas:**
- ⚠️ Datos duplicados si se embebe en múltiples lugares
- ⚠️ Límite de 16MB por documento
- ⚠️ Dificulta actualizaciones en subdocumentos

**Casos de uso en este proyecto:**
- Cliente + direcciones + teléfonos
- Producto + tipo
- Venta + items + factura
- Examen + diagnóstico + fórmula

### Referencing (Referencias)

**Ventajas:**
- ✅ Sin duplicación de datos
- ✅ Fácil actualizar datos referenciados
- ✅ Documentos más pequeños

**Desventajas:**
- ⚠️ Requiere múltiples consultas o $lookup
- ⚠️ No hay integridad referencial automática
- ⚠️ Requiere validación manual

**Casos de uso en este proyecto:**
- Cita → Cliente, Especialista, Asesor
- Venta → Cliente, Asesor, Productos
- Suministro → Proveedor, Laboratorio

---

## 🔧 Requisitos Técnicos

### Software Necesario:

- **MongoDB Shell (mongosh)** v2.0+
- **MongoDB Atlas** (cuenta gratuita M0)
- **Python** 3.8+ (para migración automática)
- **MySQL** 8.0+ (base de datos origen)

### Librerías Python:

```bash
pip install pymongo mysql-connector-python python-dotenv
```

---

## 📊 Comparación de Performance

### Consulta: Obtener Cliente con Toda su Información

**MySQL (Relacional):**
```sql
SELECT c.*, d.*, t.*
FROM Cliente c
LEFT JOIN DireccionCliente d ON c.id_cliente = d.id_cliente
LEFT JOIN TelefonoCliente t ON c.id_cliente = t.id_cliente
WHERE c.email = 'ana.perez@mail.com';
```
- **Complejidad**: O(n) con 2 JOINs
- **Queries**: 3 tablas escaneadas

**MongoDB (NoSQL):**
```javascript
db.clientes.findOne({ email: "ana.perez@mail.com" })
```
- **Complejidad**: O(1) con índice
- **Queries**: 1 documento

### Resultado: **MongoDB es ~3-5x más rápido** en este caso

---

## 🎯 Casos de Uso Optimizados

### 1. Dashboard de Ventas del Día

**Antes (MySQL):**
```sql
SELECT c.fecha_compra, cl.nombre, a.nombre, c.total
FROM Compra c
JOIN Cliente cl ON c.id_cliente = cl.id_cliente
JOIN Asesor a ON c.id_asesor = a.id_asesor
WHERE DATE(c.fecha_compra) = CURDATE();
```

**Después (MongoDB):**
```javascript
db.ventas.find({
  fecha_compra: {
    $gte: ISODate("2025-10-23T00:00:00Z"),
    $lt: ISODate("2025-10-24T00:00:00Z")
  }
})
```

### 2. Historial Médico Completo

**Antes (MySQL):**
```sql
SELECT e.*, d.*, f.*
FROM ExamenVista e
JOIN Diagnostico d ON e.id_examen = d.id_examen
JOIN FormulaMedica f ON d.id_diagnostico = f.id_diagnostico
WHERE e.id_cliente = 1;
```

**Después (MongoDB):**
```javascript
db.examenes.find({ cliente_ref: ObjectId("...") })
  .sort({ fecha_examen: -1 })
```

Todo en un solo query, datos embebidos.

---

## ⚠️ Consideraciones Importantes

### Limitaciones de MongoDB

1. **Tamaño máximo de documento**: 16MB
   - Solución: Si un cliente tiene 1000+ direcciones, usar referencias

2. **No hay transacciones multi-documento nativas** (en versión gratuita)
   - Solución: Usar transacciones en MongoDB Atlas o diseñar para atomicidad

3. **Denormalización requiere actualizaciones en múltiples lugares**
   - Ejemplo: Si cambia el nombre de un producto, actualizar en `productos` Y en items de `ventas`

### Buenas Prácticas

✅ **Crear índices** en campos de búsqueda frecuente  
✅ **Validar schemas** para mantener calidad de datos  
✅ **Backups regulares** usando `mongodump`  
✅ **Monitorear tamaño** de documentos embebidos  
✅ **Usar aggregation pipeline** para consultas complejas  

---

## 🧪 Testing y Validación

### Script de Validación

```javascript
// Verificar referencias rotas
db.citas.aggregate([
  {
    $lookup: {
      from: "clientes",
      localField: "cliente_ref",
      foreignField: "_id",
      as: "cliente"
    }
  },
  { $match: { cliente: { $size: 0 } } }
])
// Resultado esperado: [] (sin referencias rotas)
```

### Checklist de Calidad

- [ ] Todas las colecciones creadas (12 total)
- [ ] Schemas de validación aplicados
- [ ] Índices creados para campos clave
- [ ] Datos migrados correctamente
- [ ] Referencias válidas (sin rotas)
- [ ] Consultas de prueba funcionando
- [ ] Backup inicial creado

---

## 🌐 Recursos Adicionales

### Documentación Oficial

- [MongoDB Manual](https://docs.mongodb.com/manual/)
- [MongoDB Atlas](https://docs.atlas.mongodb.com/)
- [Data Modeling Guide](https://docs.mongodb.com/manual/core/data-modeling-introduction/)

### Tutoriales

- [MongoDB University](https://university.mongodb.com/) - Cursos gratuitos
- [Schema Design Patterns](https://www.mongodb.com/blog/post/building-with-patterns-a-summary)

### Herramientas

- [MongoDB Compass](https://www.mongodb.com/products/compass) - GUI visual
- [Studio 3T](https://studio3t.com/) - IDE profesional
- [NoSQLBooster](https://nosqlbooster.com/) - Cliente con autocomplete

---

## 📞 Contacto y Soporte

**Proyecto**: Migración Base de Datos Óptica  
**Fecha**: Octubre 23, 2025  
**Versión**: 1.0  

---

## 📝 Licencia

Este proyecto es material educativo para aprendizaje de bases de datos NoSQL y MongoDB.

---

**🚀 ¡Éxito en tu migración a MongoDB!**
