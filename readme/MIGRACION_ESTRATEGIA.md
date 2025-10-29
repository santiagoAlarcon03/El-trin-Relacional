# 🔄 ESTRATEGIA DE MIGRACIÓN: MySQL → MongoDB Atlas
## Base de Datos Óptica

---

## 📋 ÍNDICE
1. [Análisis del Esquema Relacional](#análisis)
2. [Diseño de Colecciones MongoDB](#diseño)
3. [Decisiones de Embedding vs Referencing](#decisiones)
4. [Estructura de Colecciones](#estructura)
5. [Patrones de Consulta](#patrones)

---

## 1️⃣ ANÁLISIS DEL ESQUEMA RELACIONAL

### Tablas Actuales (22 tablas + auxiliares)

#### **CATÁLOGOS** (7 tablas)
- Especialidad
- Motivo
- TipoDiagnostico
- MetodoPago
- TipoSuministro
- TipoProducto

#### **ENTIDADES PRINCIPALES** (5 tablas + 9 auxiliares)
- Cliente → DireccionCliente, TelefonoCliente
- Asesor → TelefonoAsesor, EmailAsesor
- Especialista → EspecialistaEspecialidad, TelefonoEspecialista, EmailEspecialista
- Laboratorio → DireccionLaboratorio, TelefonoLaboratorio
- Proveedor → DireccionProveedor, TelefonoProveedor, EmailProveedor

#### **PROCESOS CLÍNICOS** (4 tablas)
- Cita
- ExamenVista
- Diagnostico
- FormulaMedica

#### **INVENTARIO** (2 tablas)
- Suministro
- Producto

#### **VENTAS** (3 tablas)
- Compra
- DetalleCompra
- Factura

#### **GESTIÓN** (1 tabla)
- Devolucion

---

## 2️⃣ DISEÑO DE COLECCIONES MONGODB

### 🎯 De 22 tablas relacionales → 8 Colecciones NoSQL

```
COLECCIONES PRINCIPALES:
1. clientes          (Cliente + direcciones + teléfonos EMBEBIDOS)
2. asesores          (Asesor + teléfonos + emails EMBEBIDOS)
3. especialistas     (Especialista + especialidades + contactos EMBEBIDOS)
4. productos         (Producto + tipo EMBEBIDO)
5. citas             (Cita + motivo EMBEBIDO, referencias a cliente/especialista)
6. examenes          (ExamenVista + Diagnostico + FormulaMedica EMBEBIDOS)
7. ventas            (Compra + DetalleCompra + Factura EMBEBIDOS)
8. catalogos         (Documento único con todos los catálogos)

COLECCIONES AUXILIARES:
9. proveedores       (Proveedor + contactos EMBEBIDOS)
10. laboratorios     (Laboratorio + contactos EMBEBIDOS)
11. suministros      (Suministro con referencia a proveedor/laboratorio)
12. devoluciones     (Devolucion con referencia a venta)
```

---

## 3️⃣ DECISIONES: EMBEDDING vs REFERENCING

### ✅ EMBEDDING (Documentos Embebidos)

#### **Cliente + Direcciones + Teléfonos**
```javascript
{
  _id: ObjectId("..."),
  nombre: "Ana",
  apellido: "Pérez",
  email: "ana.perez@mail.com",
  documento: { tipo: "CC", numero: "1234567890" },
  fecha_nacimiento: ISODate("1990-05-15"),
  direcciones: [  // EMBEBIDO (1:N pequeño)
    {
      tipo: "Principal",
      calle: "Calle 123 #45-67",
      ciudad: "Bogotá",
      estado: "Cundinamarca",
      codigo_postal: "110111",
      pais: "Colombia",
      es_principal: true
    }
  ],
  telefonos: [  // EMBEBIDO (1:N pequeño)
    { numero: "3101234567", tipo: "Móvil", es_principal: true }
  ],
  activo: true,
  fecha_registro: ISODate("2025-10-22T00:00:00Z")
}
```
**Razón**: Un cliente tiene pocas direcciones/teléfonos (1-3), siempre se consultan juntos.

---

#### **Asesor + Teléfonos + Emails**
```javascript
{
  _id: ObjectId("..."),
  nombre: "Carlos",
  apellido: "Ruiz",
  numero_documento: "1122334455",
  fecha_contratacion: ISODate("2023-01-15"),
  telefonos: [  // EMBEBIDO
    { numero: "3001234567", tipo: "Móvil" }
  ],
  emails: [  // EMBEBIDO
    { email: "carlos.ruiz@optica.com", tipo: "Corporativo" }
  ],
  activo: true
}
```
**Razón**: Contactos limitados, siempre se consultan con el asesor.

---

#### **Especialista + Especialidades + Contactos**
```javascript
{
  _id: ObjectId("..."),
  nombre: "Juan",
  apellido: "López",
  numero_licencia: "OPT-12345",
  numero_documento: "7788990011",
  especialidades: [  // EMBEBIDO (denormalizado)
    {
      nombre: "Optometría",
      descripcion: "Especialidad en salud visual",
      fecha_certificacion: ISODate("2015-06-01")
    }
  ],
  telefonos: [  // EMBEBIDO
    { numero: "3208887766", tipo: "Móvil" }
  ],
  emails: [  // EMBEBIDO
    { email: "dr.lopez@optica.com", tipo: "Profesional" }
  ],
  activo: true
}
```
**Razón**: Un especialista tiene 1-3 especialidades, los contactos son limitados.

---

#### **Producto + TipoProducto**
```javascript
{
  _id: ObjectId("..."),
  nombre: "Lente Esférico -1.00",
  codigo_barras: "7890123456001",
  tipo: {  // EMBEBIDO (denormalizado)
    nombre: "Gafas formuladas",
    categoria: "Lente"
  },
  marca: "Transitions",
  descripcion: "Lente oftálmico esférico con graduación -1.00",
  precio_venta: 150000,
  stock: {
    actual: 50,
    minimo: 10
  },
  suministro_ref: ObjectId("..."),  // REFERENCIA a suministro
  activo: true,
  fecha_creacion: ISODate("2025-10-22T00:00:00Z")
}
```
**Razón**: El tipo de producto es un catálogo pequeño, mejor embeber para evitar JOINs.

---

#### **Venta + Detalle + Factura**
```javascript
{
  _id: ObjectId("..."),
  numero_factura: "F-2025-001",
  fecha_compra: ISODate("2025-10-21T11:00:00Z"),
  cliente: {  // REFERENCIA
    _id: ObjectId("..."),
    nombre: "Ana Pérez",
    email: "ana.perez@mail.com"
  },
  asesor: {  // REFERENCIA
    _id: ObjectId("..."),
    nombre: "Carlos Ruiz"
  },
  metodo_pago: {  // EMBEBIDO
    nombre: "Tarjeta de Crédito"
  },
  items: [  // EMBEBIDO (DetalleCompra)
    {
      producto: {  // REFERENCIA
        _id: ObjectId("..."),
        nombre: "Lente Esférico -1.00",
        codigo_barras: "7890123456001"
      },
      cantidad: 2,
      precio_unitario: 150000,
      subtotal: 300000,
      descuento: 0,
      total: 300000
    }
  ],
  subtotal: 300000,
  descuento: 0,
  impuesto: 57000,
  total: 357000,
  estado: "Completada",
  observaciones: ""
}
```
**Razón**: Los items de la venta SIEMPRE se consultan con la venta, nunca por separado. La factura es 1:1 con la venta, se embebe todo.

---

#### **Examen + Diagnóstico + Fórmula**
```javascript
{
  _id: ObjectId("..."),
  fecha_examen: ISODate("2025-10-20T10:30:00Z"),
  cliente_ref: ObjectId("..."),  // REFERENCIA
  especialista_ref: ObjectId("..."),  // REFERENCIA
  cita_ref: ObjectId("..."),  // REFERENCIA (opcional)
  
  // Datos del examen EMBEBIDOS
  examen: {
    ojo_derecho: {
      agudeza_visual: "20/30",
      esfera: -1.00,
      cilindro: -0.50,
      eje: 90,
      presion_intraocular: 15.5
    },
    ojo_izquierdo: {
      agudeza_visual: "20/40",
      esfera: -1.25,
      cilindro: -0.75,
      eje: 85,
      presion_intraocular: 16.0
    },
    adicion: 0.00,
    distancia_pupilar: 63.0,
    observaciones: "Visión ligeramente reducida"
  },
  
  // Diagnóstico EMBEBIDO
  diagnostico: {
    tipo: {
      nombre: "Miopía",
      descripcion: "Dificultad para ver objetos lejanos"
    },
    descripcion: "Miopía leve bilateral con componente astigmático",
    fecha: ISODate("2025-10-20")
  },
  
  // Fórmula médica EMBEBIDA
  formula: {
    descripcion: "OD: -1.00 -0.50 x 90, OI: -1.25 -0.75 x 85, ADD: +0.00, DP: 63mm",
    fecha_emision: ISODate("2025-10-20"),
    fecha_vencimiento: ISODate("2026-10-20"),
    activa: true
  }
}
```
**Razón**: Examen → Diagnóstico → Fórmula son un flujo único, siempre se consultan juntos. Representa un "expediente médico" completo.

---

### 🔗 REFERENCING (Referencias)

#### **Cita → Cliente, Especialista, Asesor**
```javascript
{
  _id: ObjectId("..."),
  fecha_cita: ISODate("2025-10-25"),
  hora_cita: "10:00:00",
  motivo: {  // EMBEBIDO (catálogo pequeño)
    descripcion: "Examen visual de rutina"
  },
  cliente_ref: ObjectId("..."),  // REFERENCIA
  asesor_ref: ObjectId("..."),  // REFERENCIA
  especialista_ref: ObjectId("..."),  // REFERENCIA
  estado: "Programada",
  observaciones: "",
  fecha_creacion: ISODate("2025-10-22T00:00:00Z")
}
```
**Razón**: Cliente, Asesor y Especialista son entidades independientes que se consultan por separado. Usar referencias para mantener integridad.

---

#### **Suministro → Proveedor, Laboratorio**
```javascript
{
  _id: ObjectId("..."),
  tipo: {  // EMBEBIDO
    nombre: "Lentes oftálmicos",
    descripcion: "Cristales para gafas formuladas"
  },
  cantidad: 100,
  precio_unitario: 50000,
  fecha_ingreso: ISODate("2025-10-01"),
  numero_lote: "LOTE-2025-001",
  fecha_vencimiento: null,
  proveedor_ref: ObjectId("..."),  // REFERENCIA
  laboratorio_ref: ObjectId("..."),  // REFERENCIA (opcional)
  observaciones: ""
}
```
**Razón**: Proveedores y laboratorios son entidades independientes que se consultan en otros contextos.

---

### 📚 CATÁLOGOS UNIFICADOS

```javascript
// Colección: catalogos
{
  _id: "catalogos_optica",
  especialidades: [
    { _id: ObjectId("..."), nombre: "Optometría", descripcion: "..." },
    { _id: ObjectId("..."), nombre: "Oftalmología", descripcion: "..." }
  ],
  motivos: [
    { _id: ObjectId("..."), descripcion: "Examen visual de rutina" },
    { _id: ObjectId("..."), descripcion: "Revisión de lentes" }
  ],
  tipos_diagnostico: [
    { _id: ObjectId("..."), nombre: "Miopía", descripcion: "..." },
    { _id: ObjectId("..."), nombre: "Hipermetropía", descripcion: "..." }
  ],
  metodos_pago: [
    { _id: ObjectId("..."), nombre: "Efectivo", activo: true },
    { _id: ObjectId("..."), nombre: "Tarjeta de Crédito", activo: true }
  ],
  tipos_suministro: [
    { _id: ObjectId("..."), nombre: "Lentes oftálmicos", descripcion: "..." }
  ],
  tipos_producto: [
    { _id: ObjectId("..."), nombre: "Gafas formuladas", categoria: "Lente" }
  ]
}
```
**Razón**: Catálogos pequeños y estáticos, mejor tener un único documento para carga rápida en memoria.

---

## 4️⃣ RESUMEN DE COLECCIONES

| # | Colección | Tablas MySQL Origen | Embedding | Referencing |
|---|-----------|-------------------|-----------|-------------|
| 1 | `clientes` | Cliente + DireccionCliente + TelefonoCliente | ✅ Direcciones, Teléfonos | - |
| 2 | `asesores` | Asesor + TelefonoAsesor + EmailAsesor | ✅ Teléfonos, Emails | - |
| 3 | `especialistas` | Especialista + EspecialistaEspecialidad + contactos | ✅ Especialidades, Teléfonos, Emails | - |
| 4 | `productos` | Producto + TipoProducto | ✅ Tipo | 🔗 Suministro |
| 5 | `citas` | Cita + Motivo | ✅ Motivo | 🔗 Cliente, Especialista, Asesor |
| 6 | `examenes` | ExamenVista + Diagnostico + FormulaMedica + TipoDiagnostico | ✅ Examen, Diagnóstico, Fórmula | 🔗 Cliente, Especialista, Cita |
| 7 | `ventas` | Compra + DetalleCompra + Factura + MetodoPago | ✅ Items, Factura, Método Pago | 🔗 Cliente, Asesor, Productos |
| 8 | `catalogos` | Todos los catálogos | ✅ Todo en un doc | - |
| 9 | `proveedores` | Proveedor + contactos | ✅ Direcciones, Teléfonos, Emails | - |
| 10 | `laboratorios` | Laboratorio + contactos | ✅ Direcciones, Teléfonos | - |
| 11 | `suministros` | Suministro + TipoSuministro | ✅ Tipo | 🔗 Proveedor, Laboratorio |
| 12 | `devoluciones` | Devolucion | - | 🔗 Venta, Asesor |

---

## 5️⃣ PATRONES DE CONSULTA

### Consultas Optimizadas en MongoDB

#### 1. **Buscar cliente con toda su información**
```javascript
db.clientes.findOne({ email: "ana.perez@mail.com" })
// ✅ Un solo query, todo embebido
```

#### 2. **Listar citas de un cliente**
```javascript
db.citas.find({ cliente_ref: ObjectId("...") })
// 🔗 Referencia, después populate si necesitas datos del cliente
```

#### 3. **Ver historial médico completo**
```javascript
db.examenes.find({ cliente_ref: ObjectId("...") }).sort({ fecha_examen: -1 })
// ✅ Todo el expediente en un solo documento
```

#### 4. **Consultar venta con todos sus detalles**
```javascript
db.ventas.findOne({ numero_factura: "F-2025-001" })
// ✅ Un solo query: venta + items + factura embebidos
```

#### 5. **Productos con stock bajo**
```javascript
db.productos.find({ 
  "stock.actual": { $lte: "$stock.minimo" },
  activo: true 
})
// ✅ Sin JOINs, consulta directa
```

---

## 6️⃣ VENTAJAS DEL DISEÑO NoSQL

### ✅ Beneficios Principales

1. **Menos consultas**: De 5+ JOINs a 1-2 queries
2. **Rendimiento**: Datos relacionados en un solo documento
3. **Escalabilidad**: Fácil sharding por cliente_id
4. **Flexibilidad**: Fácil agregar campos sin ALTER TABLE
5. **Atomicidad**: Operaciones atómicas en un documento

### ⚖️ Trade-offs

1. **Denormalización**: Algunos datos duplicados (nombres de catálogos)
2. **Actualizaciones**: Si cambia un tipo de producto, actualizar todos los productos
3. **Tamaño**: Documentos más grandes (límite 16MB en MongoDB)

---

## 📝 PRÓXIMOS PASOS

1. ✅ Estrategia definida
2. ⏭️ Crear schemas de validación MongoDB
3. ⏭️ Crear scripts de migración
4. ⏭️ Configurar MongoDB Atlas
5. ⏭️ Ejecutar migración
6. ⏭️ Validar datos migrados

---

**Fecha**: Octubre 23, 2025  
**Proyecto**: Migración Base de Datos Óptica  
**Origen**: MySQL (22 tablas relacionales)  
**Destino**: MongoDB Atlas (8-12 colecciones NoSQL)
