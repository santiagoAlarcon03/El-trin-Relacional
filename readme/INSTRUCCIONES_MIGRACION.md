# 🚀 INSTRUCCIONES DE MIGRACIÓN: MySQL → MongoDB Atlas

## Base de Datos: `optica_db`

---

## 📋 RESUMEN

Este script migra automáticamente tu base de datos relacional MySQL de óptica a MongoDB Atlas aplicando los siguientes patrones:

### ✅ **EMBEDDING** (Documentos Embebidos)
- Cliente + Direcciones + Teléfonos → `clientes`
- Asesor + Teléfonos + Emails → `asesores`
- Especialista + Especialidades + Contactos → `especialistas`
- Proveedor + Direcciones + Teléfonos + Emails → `proveedores`
- Laboratorio + Direcciones + Teléfonos → `laboratorios`
- Producto + TipoProducto → `productos`
- Cita + Motivo → `citas`
- ExamenVista + Diagnóstico + Fórmula → `examenes`
- Compra + DetalleCompra + Factura → `ventas`
- Todos los catálogos → `catalogos` (documento único)

### 🔗 **REFERENCING** (Referencias entre Documentos)
- Citas → Cliente, Asesor, Especialista
- Suministros → Proveedor, Laboratorio
- Productos → Suministro
- Exámenes → Cliente, Especialista, Cita
- Ventas → Cliente, Asesor, Productos

---

## 📦 REQUISITOS PREVIOS

### 1. Instalar Python 3.8 o superior
```powershell
python --version
```

### 2. Instalar dependencias
```powershell
pip install pymongo mysql-connector-python python-dotenv
```

### 3. Tener acceso a MySQL
- Base de datos MySQL corriendo
- Credenciales de acceso
- Base de datos "Optica" con datos

### 4. Crear cuenta en MongoDB Atlas
1. Ir a https://www.mongodb.com/cloud/atlas
2. Crear cuenta gratuita
3. Crear un cluster (M0 FREE tier)
4. Configurar usuario y contraseña
5. Permitir acceso desde cualquier IP (0.0.0.0/0) en Network Access
6. Obtener el connection string

---

## ⚙️ CONFIGURACIÓN

### Paso 1: Copiar archivo de configuración

```powershell
# En la carpeta del proyecto
Copy-Item .env.example .env
```

### Paso 2: Editar archivo .env con tus credenciales

Abrir `.env` en un editor de texto y completar:

```env
# MySQL Configuration
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=tu_password_mysql
MYSQL_DATABASE=Optica

# MongoDB Atlas Configuration
MONGODB_URI=mongodb+srv://usuario:password@cluster.xxxxx.mongodb.net/
MONGODB_DATABASE=optica_db
```

**Ejemplo real:**
```env
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=miPassword123
MYSQL_DATABASE=Optica

MONGODB_URI=mongodb+srv://admin_optica:MiClave456@optica-cluster.abc123.mongodb.net/
MONGODB_DATABASE=optica_db
```

---

## 🚀 EJECUTAR MIGRACIÓN

### Opción 1: Desde PowerShell

```powershell
cd "d:\BasesdeDatos\ProyectoOptica\El-trin-Relacional"
python migracion_mysql_a_mongodb.py
```

### Opción 2: Desde VS Code

1. Abrir el archivo `migracion_mysql_a_mongodb.py`
2. Presionar `F5` o clic derecho → "Run Python File in Terminal"

---

## 📊 SALIDA ESPERADA

```
================================================================================
MIGRACIÓN: MySQL → MongoDB Atlas
Base de datos destino: optica_db
================================================================================
✅ Conectado a MySQL: Optica
✅ Conectado a MongoDB Atlas: optica_db

🔄 Transformando catálogos...
✅ Catálogos transformados (1 documento)
💾 Catálogos guardados en MongoDB

🔄 Transformando clientes...
✅ 3 clientes transformados
💾 Clientes guardados en MongoDB

🔄 Transformando asesores...
✅ 2 asesores transformados
💾 Asesores guardados en MongoDB

🔄 Transformando especialistas...
✅ 2 especialistas transformados
💾 Especialistas guardados en MongoDB

🔄 Transformando proveedores...
✅ 2 proveedores transformados
💾 Proveedores guardados en MongoDB

🔄 Transformando laboratorios...
✅ 1 laboratorios transformados
💾 Laboratorios guardados en MongoDB

🔄 Transformando suministros...
✅ 3 suministros transformados
💾 Suministros guardados en MongoDB

🔄 Transformando productos...
✅ 4 productos transformados
💾 Productos guardados en MongoDB

🔄 Transformando citas...
✅ 2 citas transformadas
💾 Citas guardadas en MongoDB

🔄 Transformando exámenes...
✅ 1 exámenes transformados
💾 Exámenes guardados en MongoDB

🔄 Transformando ventas...
✅ 2 ventas transformadas
💾 Ventas guardadas en MongoDB

================================================================================
📊 VALIDACIÓN DE DATOS MIGRADOS:
================================================================================
Catálogos:      1
Clientes:       3
Asesores:       2
Especialistas:  2
Proveedores:    2
Laboratorios:   1
Suministros:    3
Productos:      4
Citas:          2
Exámenes:       1
Ventas:         2

✅ MIGRACIÓN COMPLETADA EXITOSAMENTE

🔒 Conexiones cerradas
```

---

## 🔍 VERIFICAR DATOS EN MONGODB

### Opción 1: MongoDB Compass (GUI)

1. Abrir MongoDB Compass
2. Conectar usando tu connection string
3. Navegar a la base de datos `optica_db`
4. Explorar colecciones

### Opción 2: MongoDB Shell (mongosh)

```powershell
# Conectar
mongosh "mongodb+srv://usuario:password@cluster.xxxxx.mongodb.net/"

# Usar la base de datos
use optica_db

# Ver colecciones
show collections

# Ver un cliente
db.clientes.findOne()

# Contar documentos
db.clientes.countDocuments()

# Ver productos con stock bajo
db.productos.find({ $expr: { $lte: ["$stock.actual", "$stock.minimo"] } })

# Ver ventas con items embebidos
db.ventas.findOne()
```

---

## 📈 ESTRUCTURA DE COLECCIONES CREADAS

| Colección | Documentos | Estrategia | Descripción |
|-----------|-----------|-----------|-------------|
| `catalogos` | 1 | Embedding | Documento único con todos los catálogos |
| `clientes` | Variable | Embedding | Cliente con direcciones y teléfonos embebidos |
| `asesores` | Variable | Embedding | Asesor con contactos embebidos |
| `especialistas` | Variable | Embedding | Especialista con especialidades embebidas |
| `proveedores` | Variable | Embedding | Proveedor con contactos embebidos |
| `laboratorios` | Variable | Embedding | Laboratorio con contactos embebidos |
| `suministros` | Variable | Referencing | Referencias a proveedor y laboratorio |
| `productos` | Variable | Hybrid | Tipo embebido, referencia a suministro |
| `citas` | Variable | Hybrid | Motivo embebido, referencias a cliente/especialista |
| `examenes` | Variable | Embedding | Examen + diagnóstico + fórmula completo |
| `ventas` | Variable | Embedding | Venta con items y factura embebidos |

---

## 🎯 VENTAJAS DEL DISEÑO

### ✅ Rendimiento
- **Menos consultas**: De 5+ JOINs a 1-2 queries
- **Datos relacionados**: Todo en un solo documento
- **Caché eficiente**: Documentos completos en memoria

### ✅ Escalabilidad
- **Sharding fácil**: Por cliente_id o fecha
- **Réplicas**: Alta disponibilidad automática
- **Crecimiento horizontal**: Agregar nodos según demanda

### ✅ Flexibilidad
- **Schema dinámico**: Agregar campos sin ALTER TABLE
- **Versionado**: Diferentes versiones de documentos coexisten
- **Evolución**: Fácil adaptar estructura según necesidades

### ✅ Mantenimiento
- **Atomicidad**: Operaciones atómicas en un documento
- **Transacciones**: Soporte para transacciones multi-documento
- **Backups**: Snapshots automáticos en Atlas

---

## 🛠️ TROUBLESHOOTING

### Error: "Access Denied for user"
**Solución:** Verificar credenciales MySQL en `.env`

### Error: "Authentication failed"
**Solución:** Verificar credenciales MongoDB Atlas en `.env`

### Error: "No module named 'pymongo'"
**Solución:** 
```powershell
pip install pymongo mysql-connector-python python-dotenv
```

### Error: "Connection timeout"
**Solución:** 
1. Verificar Network Access en MongoDB Atlas
2. Agregar IP 0.0.0.0/0 para desarrollo
3. Verificar firewall local

### Error: "Database 'Optica' doesn't exist"
**Solución:** 
1. Verificar que la base de datos MySQL existe
2. Ejecutar el script `Schema_Fixed.sql` primero

### Datos no coinciden
**Solución:**
1. Verificar que MySQL tiene los datos
2. Revisar logs de migración
3. Ejecutar validación manual

---

## 📚 RECURSOS ADICIONALES

### Archivos del Proyecto
- `migracion_mysql_a_mongodb.py` - Script de migración
- `Schema_Fixed.sql` - Schema MySQL original
- `MongoDB_Schemas.mongodb` - Schemas de validación MongoDB
- `MongoDB_Consultas_Ejemplos.mongodb` - Ejemplos de consultas
- `MIGRACION_ESTRATEGIA.md` - Estrategia detallada
- `RESUMEN_VISUAL.md` - Diagrama visual

### Documentación
- MongoDB Manual: https://docs.mongodb.com/
- MongoDB Atlas: https://docs.atlas.mongodb.com/
- PyMongo: https://pymongo.readthedocs.io/

---

## 📞 SOPORTE

Si encuentras algún problema durante la migración:

1. Revisar logs de error
2. Verificar configuración en `.env`
3. Consultar sección de Troubleshooting
4. Revisar documentación de MongoDB Atlas

---

**¡Éxito en tu migración! 🎉**
