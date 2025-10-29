# 🚀 GUÍA DE IMPLEMENTACIÓN: Migración a MongoDB Atlas
## Base de Datos Óptica - Paso a Paso

---

## 📋 TABLA DE CONTENIDOS

1. [Requisitos Previos](#requisitos-previos)
2. [Paso 1: Configurar MongoDB Atlas](#paso-1-configurar-mongodb-atlas)
3. [Paso 2: Crear los Schemas](#paso-2-crear-los-schemas)
4. [Paso 3: Migrar los Datos](#paso-3-migrar-los-datos)
5. [Paso 4: Validar la Migración](#paso-4-validar-la-migración)
6. [Paso 5: Consultas de Prueba](#paso-5-consultas-de-prueba)
7. [Herramientas y Scripts](#herramientas-y-scripts)
8. [Troubleshooting](#troubleshooting)

---

## 📦 REQUISITOS PREVIOS

### Herramientas Necesarias:

1. **Cuenta MongoDB Atlas** (gratuita)
   - Crear cuenta en: https://www.mongodb.com/cloud/atlas
   
2. **MongoDB Shell (mongosh)**
   - Descargar: https://www.mongodb.com/try/download/shell
   - Verificar instalación: `mongosh --version`

3. **MongoDB Compass** (opcional, GUI visual)
   - Descargar: https://www.mongodb.com/try/download/compass

4. **Datos de MySQL exportados** (opcional si usas script manual)
   - Exportar datos actuales de MySQL

---

## 🌐 PASO 1: CONFIGURAR MONGODB ATLAS

### 1.1 Crear Cluster en MongoDB Atlas

1. Iniciar sesión en https://cloud.mongodb.com/
2. Clic en **"Create"** → **"Database"**
3. Configurar:
   - **Cluster Tier**: M0 Sandbox (FREE)
   - **Provider**: AWS / Google Cloud / Azure (el que prefieras)
   - **Region**: Selecciona la más cercana (ej: `us-east-1`, `sa-east-1`)
   - **Cluster Name**: `Optica-Cluster`
4. Clic en **"Create Cluster"** (tarda ~3-5 minutos)

### 1.2 Configurar Acceso y Seguridad

#### A. Crear Usuario de Base de Datos

1. En el menú lateral: **"Database Access"**
2. Clic en **"Add New Database User"**
3. Configurar:
   - **Authentication Method**: Password
   - **Username**: `admin_optica`
   - **Password**: `TuContraseñaSegura123!` (guarda esto)
   - **Database User Privileges**: `Atlas admin` o `Read and write to any database`
4. Clic en **"Add User"**

#### B. Configurar Red (Network Access)

1. En el menú lateral: **"Network Access"**
2. Clic en **"Add IP Address"**
3. Opciones:
   - **Opción 1** (Desarrollo): Clic en **"Allow Access from Anywhere"** (0.0.0.0/0)
   - **Opción 2** (Producción): Agregar tu IP específica
4. Clic en **"Confirm"**

### 1.3 Obtener Connection String

1. Ir a **"Database"** en el menú lateral
2. Clic en **"Connect"** en tu cluster
3. Seleccionar **"MongoDB Shell"**
4. Copiar el connection string:
   ```
   mongodb+srv://admin_optica:<password>@optica-cluster.xxxxx.mongodb.net/
   ```
5. Reemplazar `<password>` con tu contraseña

---

## 🏗️ PASO 2: CREAR LOS SCHEMAS

### 2.1 Conectar a MongoDB Atlas

Abrir terminal (PowerShell) y ejecutar:

```powershell
mongosh "mongodb+srv://admin_optica:TuContraseñaSegura123!@optica-cluster.xxxxx.mongodb.net/"
```

### 2.2 Ejecutar Script de Schemas

```powershell
# Cargar el archivo de schemas
mongosh "mongodb+srv://admin_optica:TuContraseñaSegura123!@optica-cluster.xxxxx.mongodb.net/" --file "C:\Users\USER\Desktop\Proyecto-BasesNoRelacionales\Óptica\MongoDB_Schemas.js"
```

**Resultado esperado:**
```
✅ Schemas de validación creados exitosamente
📊 Total de colecciones: 12
🔒 Validaciones JSON Schema aplicadas
📑 Índices creados para optimizar consultas
```

### 2.3 Verificar Colecciones Creadas

```javascript
// Dentro de mongosh
use Optica
show collections
```

**Salida esperada:**
```
asesores
catalogos
citas
clientes
devoluciones
especialistas
examenes
laboratorios
productos
proveedores
suministros
ventas
```

---

## 📥 PASO 3: MIGRAR LOS DATOS

### Opción A: Script Manual (Datos de Prueba)

```powershell
# Ejecutar script de migración con datos de prueba
mongosh "mongodb+srv://admin_optica:TuContraseñaSegura123!@optica-cluster.xxxxx.mongodb.net/" --file "C:\Users\USER\Desktop\Proyecto-BasesNoRelacionales\Óptica\MongoDB_Migracion_Datos.js"
```

### Opción B: Migración desde MySQL (Datos Reales)

#### 3.1 Exportar Datos de MySQL

```sql
-- Exportar cada tabla a JSON
SELECT JSON_OBJECT(
  'id_cliente', id_cliente,
  'nombre', nombre,
  'apellido', apellido,
  'email', email,
  'fecha_nacimiento', fecha_nacimiento
) FROM Cliente
INTO OUTFILE '/tmp/clientes.json';
```

#### 3.2 Transformar y Cargar

Crear script en Node.js o Python para transformar y cargar:

```javascript
// transform_data.js
const fs = require('fs');
const { MongoClient } = require('mongodb');

const uri = "mongodb+srv://admin_optica:password@optica-cluster.xxxxx.mongodb.net/";
const client = new MongoClient(uri);

async function migrate() {
  try {
    await client.connect();
    const db = client.db("Optica");
    
    // Leer datos de MySQL exportados
    const mysqlClientes = JSON.parse(fs.readFileSync('clientes.json'));
    const mysqlDirecciones = JSON.parse(fs.readFileSync('direcciones.json'));
    const mysqlTelefonos = JSON.parse(fs.readFileSync('telefonos.json'));
    
    // Transformar: agrupar por cliente con embedding
    const clientesMongoDB = mysqlClientes.map(cliente => {
      return {
        nombre: cliente.nombre,
        apellido: cliente.apellido,
        email: cliente.email,
        documento: {
          tipo: cliente.tipo_documento,
          numero: cliente.numero_documento
        },
        direcciones: mysqlDirecciones
          .filter(dir => dir.id_cliente === cliente.id_cliente)
          .map(dir => ({
            tipo: dir.tipo_direccion,
            calle: dir.calle,
            ciudad: dir.ciudad,
            estado: dir.estado,
            codigo_postal: dir.codigo_postal,
            pais: dir.pais,
            es_principal: dir.es_principal
          })),
        telefonos: mysqlTelefonos
          .filter(tel => tel.id_cliente === cliente.id_cliente)
          .map(tel => ({
            numero: tel.telefono,
            tipo: tel.tipo_telefono,
            es_principal: tel.es_principal
          })),
        activo: cliente.activo,
        fecha_registro: new Date(cliente.fecha_registro)
      };
    });
    
    // Insertar en MongoDB
    await db.collection('clientes').insertMany(clientesMongoDB);
    console.log('✅ Clientes migrados');
    
  } finally {
    await client.close();
  }
}

migrate().catch(console.error);
```

**Ejecutar:**
```powershell
node transform_data.js
```

---

## ✅ PASO 4: VALIDAR LA MIGRACIÓN

### 4.1 Verificar Conteo de Documentos

```javascript
// Dentro de mongosh
use Optica

db.clientes.countDocuments()       // Debe ser 3
db.asesores.countDocuments()       // Debe ser 2
db.especialistas.countDocuments()  // Debe ser 2
db.productos.countDocuments()      // Debe ser 4
db.citas.countDocuments()          // Debe ser 2
db.examenes.countDocuments()       // Debe ser 1
db.ventas.countDocuments()         // Debe ser 2
db.proveedores.countDocuments()    // Debe ser 2
db.laboratorios.countDocuments()   // Debe ser 1
db.suministros.countDocuments()    // Debe ser 3
db.catalogos.countDocuments()      // Debe ser 1
```

### 4.2 Verificar Integridad de Datos

```javascript
// Verificar que las referencias existen
db.citas.aggregate([
  {
    $lookup: {
      from: "clientes",
      localField: "cliente_ref",
      foreignField: "_id",
      as: "cliente"
    }
  },
  {
    $match: { cliente: { $size: 0 } }  // Referencias rotas
  }
])
// Resultado esperado: [] (array vacío, sin referencias rotas)
```

### 4.3 Verificar Embedding

```javascript
// Verificar que los clientes tienen direcciones embebidas
db.clientes.findOne({ email: "ana.perez@mail.com" })

// Debe mostrar:
// {
//   _id: ...,
//   nombre: "Ana",
//   apellido: "Pérez",
//   direcciones: [ { calle: "...", ciudad: "..." } ],  ✅
//   telefonos: [ { numero: "..." } ]  ✅
// }
```

---

## 🔍 PASO 5: CONSULTAS DE PRUEBA

### 5.1 Consultas Básicas

```javascript
// 1. Buscar cliente por email (con toda su info embebida)
db.clientes.findOne({ email: "ana.perez@mail.com" })

// 2. Listar productos activos
db.productos.find({ activo: true })

// 3. Citas del día específico
db.citas.find({
  fecha_cita: ISODate("2025-10-25")
})

// 4. Ventas completadas
db.ventas.find({ estado: "Completada" })
```

### 5.2 Consultas con Agregación

```javascript
// 1. Total de ventas por asesor
db.ventas.aggregate([
  {
    $group: {
      _id: "$asesor_ref",
      total_ventas: { $sum: "$total" },
      cantidad_ventas: { $count: {} }
    }
  }
])

// 2. Productos con stock bajo
db.productos.aggregate([
  {
    $match: {
      $expr: { $lte: ["$stock.actual", "$stock.minimo"] },
      activo: true
    }
  },
  {
    $project: {
      nombre: 1,
      marca: 1,
      stock_actual: "$stock.actual",
      stock_minimo: "$stock.minimo",
      faltante: { $subtract: ["$stock.minimo", "$stock.actual"] }
    }
  }
])

// 3. Historial médico de un cliente (con lookup)
db.examenes.aggregate([
  {
    $match: { cliente_ref: ObjectId("67189a1b2c3d4e5f60718901") }
  },
  {
    $lookup: {
      from: "clientes",
      localField: "cliente_ref",
      foreignField: "_id",
      as: "cliente"
    }
  },
  {
    $lookup: {
      from: "especialistas",
      localField: "especialista_ref",
      foreignField: "_id",
      as: "especialista"
    }
  },
  {
    $sort: { fecha_examen: -1 }
  }
])
```

### 5.3 Consultas con Referencing

```javascript
// Obtener cita con información completa del cliente
db.citas.aggregate([
  {
    $lookup: {
      from: "clientes",
      localField: "cliente_ref",
      foreignField: "_id",
      as: "cliente"
    }
  },
  {
    $lookup: {
      from: "especialistas",
      localField: "especialista_ref",
      foreignField: "_id",
      as: "especialista"
    }
  },
  {
    $unwind: "$cliente"
  },
  {
    $unwind: "$especialista"
  },
  {
    $project: {
      fecha_cita: 1,
      hora_cita: 1,
      "motivo.descripcion": 1,
      "cliente.nombre": 1,
      "cliente.apellido": 1,
      "cliente.email": 1,
      "especialista.nombre": 1,
      "especialista.apellido": 1,
      estado: 1
    }
  }
])
```

---

## 🛠️ HERRAMIENTAS Y SCRIPTS

### MongoDB Compass (GUI)

1. Descargar: https://www.mongodb.com/try/download/compass
2. Conectar usando el connection string
3. Explorar colecciones visualmente
4. Crear consultas con interfaz gráfica

### Scripts Útiles

#### Backup de Base de Datos

```powershell
# Exportar toda la base de datos
mongodump --uri="mongodb+srv://admin_optica:password@optica-cluster.xxxxx.mongodb.net/Optica" --out="C:\backup\optica_backup"
```

#### Restaurar Base de Datos

```powershell
# Restaurar desde backup
mongorestore --uri="mongodb+srv://admin_optica:password@optica-cluster.xxxxx.mongodb.net/Optica" "C:\backup\optica_backup\Optica"
```

#### Exportar Colección a JSON

```powershell
mongoexport --uri="mongodb+srv://admin_optica:password@optica-cluster.xxxxx.mongodb.net/Optica" --collection=clientes --out=clientes.json --jsonArray
```

#### Importar Colección desde JSON

```powershell
mongoimport --uri="mongodb+srv://admin_optica:password@optica-cluster.xxxxx.mongodb.net/Optica" --collection=clientes --file=clientes.json --jsonArray
```

---

## 🔧 TROUBLESHOOTING

### Error: "Authentication failed"

**Causa**: Usuario o contraseña incorrectos

**Solución**:
1. Verificar credenciales en MongoDB Atlas → Database Access
2. Asegurar que el password no tenga caracteres especiales sin encodear
3. URL encode la contraseña si tiene caracteres especiales

```javascript
// Ejemplo: si tu password es "Pass@123!"
// Usar: Pass%40123%21
```

### Error: "IP not whitelisted"

**Causa**: Tu IP no está en la lista de acceso

**Solución**:
1. Ir a MongoDB Atlas → Network Access
2. Agregar tu IP actual o usar 0.0.0.0/0 (todos)

### Error: "Document failed validation"

**Causa**: Datos no cumplen el schema de validación

**Solución**:
```javascript
// Ver errores de validación
db.runCommand({
  collMod: "clientes",
  validationAction: "warn"  // Cambiar a "warn" temporalmente
})

// Intentar insertar de nuevo y ver warnings
```

### Performance Lenta

**Solución**: Crear índices adicionales

```javascript
// Índice compuesto para búsquedas frecuentes
db.ventas.createIndex({ fecha_compra: -1, estado: 1 })

// Ver índices existentes
db.ventas.getIndexes()

// Ver estadísticas de uso de índices
db.ventas.aggregate([{ $indexStats: {} }])
```

---

## 📊 COMPARACIÓN: Antes vs Después

| Aspecto | MySQL (Relacional) | MongoDB (NoSQL) |
|---------|-------------------|----------------|
| **Tablas/Colecciones** | 22 tablas + 9 auxiliares | 12 colecciones |
| **JOINs** | Múltiples JOINs (5+) | Embedding: 0 JOINs, Referencing: 1-2 |
| **Query para Cliente** | `SELECT * FROM Cliente JOIN DireccionCliente JOIN TelefonoCliente` | `db.clientes.findOne({email: "..."})` |
| **Escalabilidad** | Vertical (mejor servidor) | Horizontal (sharding) |
| **Flexibilidad Schema** | Rígido (ALTER TABLE) | Flexible (agregar campos) |
| **Atomicidad** | Nivel transaccional | Nivel documento |

---

## 📚 RECURSOS ADICIONALES

### Documentación Oficial

- MongoDB Manual: https://docs.mongodb.com/manual/
- MongoDB Atlas: https://docs.atlas.mongodb.com/
- MongoDB Shell: https://docs.mongodb.com/mongodb-shell/

### Tutoriales

- MongoDB University (cursos gratuitos): https://university.mongodb.com/
- Data Modeling: https://docs.mongodb.com/manual/core/data-modeling-introduction/

### Comunidad

- MongoDB Community Forums: https://www.mongodb.com/community/forums/
- Stack Overflow: Tag [mongodb]

---

## ✅ CHECKLIST DE MIGRACIÓN

- [ ] Cuenta MongoDB Atlas creada
- [ ] Cluster configurado (M0 Free)
- [ ] Usuario de BD creado
- [ ] IP whitelisted en Network Access
- [ ] MongoDB Shell instalado (`mongosh --version`)
- [ ] Connection string obtenido
- [ ] Conexión exitosa a cluster
- [ ] Script de schemas ejecutado (`MongoDB_Schemas.js`)
- [ ] 12 colecciones creadas
- [ ] Script de migración ejecutado (`MongoDB_Migracion_Datos.js`)
- [ ] Conteo de documentos validado
- [ ] Referencias verificadas (sin rotas)
- [ ] Consultas de prueba ejecutadas
- [ ] Backup inicial creado
- [ ] MongoDB Compass configurado (opcional)

---

## 🎓 CONCEPTOS CLAVE APRENDIDOS

### Embedding
- ✅ Cliente + direcciones + teléfonos
- ✅ Producto + tipo
- ✅ Venta + items + factura
- ✅ Examen + diagnóstico + fórmula

### Referencing
- 🔗 Cita → cliente_ref, especialista_ref
- 🔗 Venta → cliente_ref, asesor_ref
- 🔗 Suministro → proveedor_ref, laboratorio_ref

### Denormalización
- 📋 Catálogos embebidos en documentos principales
- 📋 Información del producto copiada en items de venta

---

**Fecha**: Octubre 23, 2025  
**Versión**: 1.0  
**Autor**: Proyecto Base de Datos Óptica  
**Destino**: MongoDB Atlas (M0 Free Tier)
