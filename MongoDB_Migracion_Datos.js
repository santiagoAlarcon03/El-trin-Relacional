// ============================================================================
// SCRIPT DE MIGRACIÓN: MySQL → MongoDB
// Base de Datos: Optica
// Fecha: Octubre 23, 2025
// ============================================================================

// Este script muestra cómo transformar los datos de MySQL a MongoDB
// Asume que ya tienes los datos extraídos de MySQL

use Optica;

// ============================================================================
// 1. MIGRAR CATÁLOGOS (Un solo documento)
// ============================================================================

db.catalogos.insertOne({
  _id: "catalogos_optica",
  especialidades: [
    { nombre: "Optometría", descripcion: "Especialidad en salud visual y prescripción de lentes" },
    { nombre: "Oftalmología", descripcion: "Especialidad médica para enfermedades oculares" },
    { nombre: "Contactología", descripcion: "Especialidad en lentes de contacto" }
  ],
  motivos: [
    { descripcion: "Examen visual de rutina" },
    { descripcion: "Revisión de lentes" },
    { descripcion: "Ajuste de monturas" },
    { descripcion: "Consulta por molestias visuales" },
    { descripcion: "Control post-compra" }
  ],
  tipos_diagnostico: [
    { nombre: "Miopía", descripcion: "Dificultad para ver objetos lejanos" },
    { nombre: "Hipermetropía", descripcion: "Dificultad para ver objetos cercanos" },
    { nombre: "Astigmatismo", descripcion: "Visión distorsionada o borrosa" },
    { nombre: "Presbicia", descripcion: "Dificultad para enfocar objetos cercanos por edad" }
  ],
  metodos_pago: [
    { nombre: "Efectivo", activo: true },
    { nombre: "Tarjeta de Crédito", activo: true },
    { nombre: "Tarjeta de Débito", activo: true },
    { nombre: "Transferencia Bancaria", activo: true },
    { nombre: "PSE", activo: true }
  ],
  tipos_suministro: [
    { nombre: "Lentes oftálmicos", descripcion: "Cristales para gafas formuladas" },
    { nombre: "Lentes de contacto", descripcion: "Lentes de contacto blandos y rígidos" },
    { nombre: "Monturas", descripcion: "Armazones para lentes" },
    { nombre: "Accesorios", descripcion: "Estuches, paños, líquidos de limpieza" }
  ],
  tipos_producto: [
    { nombre: "Gafas formuladas", categoria: "Lente" },
    { nombre: "Gafas de sol", categoria: "Accesorio" },
    { nombre: "Lentes de contacto", categoria: "Contacto" },
    { nombre: "Monturas oftálmicas", categoria: "Montura" },
    { nombre: "Estuches", categoria: "Accesorio" },
    { nombre: "Líquidos de limpieza", categoria: "Accesorio" }
  ]
});

print("✅ Catálogos migrados");

// ============================================================================
// 2. MIGRAR CLIENTES (Embedding: direcciones y teléfonos)
// ============================================================================

// TRANSFORMACIÓN:
// Cliente (MySQL) + DireccionCliente + TelefonoCliente → clientes (MongoDB)

db.clientes.insertMany([
  {
    _id: ObjectId("67189a1b2c3d4e5f60718901"),  // Generado o mapeado desde MySQL id_cliente=1
    nombre: "Ana",
    apellido: "Pérez",
    email: "ana.perez@mail.com",
    fecha_nacimiento: ISODate("1990-05-15"),
    documento: {
      tipo: "CC",
      numero: "1234567890"
    },
    direcciones: [
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
    telefonos: [
      {
        numero: "3101234567",
        tipo: "Móvil",
        es_principal: true
      }
    ],
    activo: true,
    fecha_registro: ISODate("2025-10-22T00:00:00Z")
  },
  {
    _id: ObjectId("67189a1b2c3d4e5f60718902"),  // id_cliente=2
    nombre: "Carlos",
    apellido: "Gómez",
    email: "carlos.gomez@mail.com",
    fecha_nacimiento: ISODate("1985-08-20"),
    documento: {
      tipo: "CC",
      numero: "9876543210"
    },
    direcciones: [
      {
        tipo: "Principal",
        calle: "Carrera 50 #30-20",
        ciudad: "Medellín",
        estado: "Antioquia",
        codigo_postal: "050001",
        pais: "Colombia",
        es_principal: true
      }
    ],
    telefonos: [
      {
        numero: "3209876543",
        tipo: "Móvil",
        es_principal: true
      }
    ],
    activo: true,
    fecha_registro: ISODate("2025-10-22T00:00:00Z")
  },
  {
    _id: ObjectId("67189a1b2c3d4e5f60718903"),  // id_cliente=3
    nombre: "María",
    apellido: "Rodríguez",
    email: "maria.rodriguez@mail.com",
    fecha_nacimiento: ISODate("1995-03-10"),
    documento: {
      tipo: "CC",
      numero: "5555555555"
    },
    direcciones: [
      {
        tipo: "Principal",
        calle: "Avenida 6 #15-30",
        ciudad: "Cali",
        estado: "Valle del Cauca",
        codigo_postal: "760001",
        pais: "Colombia",
        es_principal: true
      }
    ],
    telefonos: [
      {
        numero: "3155555555",
        tipo: "Móvil",
        es_principal: true
      }
    ],
    activo: true,
    fecha_registro: ISODate("2025-10-22T00:00:00Z")
  }
]);

print("✅ Clientes migrados: 3 documentos");

// ============================================================================
// 3. MIGRAR ASESORES (Embedding: teléfonos y emails)
// ============================================================================

db.asesores.insertMany([
  {
    _id: ObjectId("67189a1b2c3d4e5f60718a01"),  // id_asesor=1
    nombre: "Carlos",
    apellido: "Ruiz",
    numero_documento: "1122334455",
    fecha_contratacion: ISODate("2023-01-15"),
    telefonos: [
      { numero: "3001234567", tipo: "Móvil" }
    ],
    emails: [
      { email: "carlos.ruiz@optica.com", tipo: "Corporativo" }
    ],
    activo: true
  },
  {
    _id: ObjectId("67189a1b2c3d4e5f60718a02"),  // id_asesor=2
    nombre: "Laura",
    apellido: "Martínez",
    numero_documento: "5544332211",
    fecha_contratacion: ISODate("2023-06-01"),
    telefonos: [
      { numero: "3009876543", tipo: "Móvil" }
    ],
    emails: [
      { email: "laura.martinez@optica.com", tipo: "Corporativo" }
    ],
    activo: true
  }
]);

print("✅ Asesores migrados: 2 documentos");

// ============================================================================
// 4. MIGRAR ESPECIALISTAS (Embedding: especialidades y contactos)
// ============================================================================

db.especialistas.insertMany([
  {
    _id: ObjectId("67189a1b2c3d4e5f60718b01"),  // id_especialista=1
    nombre: "Juan",
    apellido: "López",
    numero_licencia: "OPT-12345",
    numero_documento: "7788990011",
    especialidades: [
      {
        nombre: "Optometría",
        descripcion: "Especialidad en salud visual y prescripción de lentes",
        fecha_certificacion: ISODate("2015-06-01")
      }
    ],
    telefonos: [
      { numero: "3208887766", tipo: "Móvil" }
    ],
    emails: [
      { email: "dr.lopez@optica.com", tipo: "Profesional" }
    ],
    activo: true
  },
  {
    _id: ObjectId("67189a1b2c3d4e5f60718b02"),  // id_especialista=2
    nombre: "Diana",
    apellido: "Vargas",
    numero_licencia: "OFT-54321",
    numero_documento: "1122998877",
    especialidades: [
      {
        nombre: "Oftalmología",
        descripcion: "Especialidad médica para enfermedades oculares",
        fecha_certificacion: ISODate("2010-03-15")
      }
    ],
    telefonos: [
      { numero: "3156667788", tipo: "Móvil" }
    ],
    emails: [
      { email: "dra.vargas@optica.com", tipo: "Profesional" }
    ],
    activo: true
  }
]);

print("✅ Especialistas migrados: 2 documentos");

// ============================================================================
// 5. MIGRAR PROVEEDORES (Embedding: direcciones, teléfonos, emails)
// ============================================================================

db.proveedores.insertMany([
  {
    _id: ObjectId("67189a1b2c3d4e5f60718c01"),  // id_proveedor=1
    nombre: "LentesPro Internacional",
    contacto_principal: "Sandra Morales",
    direcciones: [
      {
        calle: "Avenida 9 #45-67",
        ciudad: "Bogotá",
        estado: "Cundinamarca",
        codigo_postal: "110111",
        pais: "Colombia"
      }
    ],
    telefonos: [
      { numero: "3211234567" }
    ],
    emails: [
      { email: "ventas@lentespro.com", tipo: "Ventas" }
    ],
    activo: true
  },
  {
    _id: ObjectId("67189a1b2c3d4e5f60718c02"),  // id_proveedor=2
    nombre: "Monturas Premium",
    contacto_principal: "Diego Castro",
    direcciones: [
      {
        calle: "Calle 72 #10-15",
        ciudad: "Bogotá",
        estado: "Cundinamarca",
        codigo_postal: "110221",
        pais: "Colombia"
      }
    ],
    telefonos: [
      { numero: "3189876543" }
    ],
    emails: [
      { email: "contacto@monturaspremium.com", tipo: "Ventas" }
    ],
    activo: true
  }
]);

print("✅ Proveedores migrados: 2 documentos");

// ============================================================================
// 6. MIGRAR LABORATORIOS (Embedding: direcciones y teléfonos)
// ============================================================================

db.laboratorios.insertOne({
  _id: ObjectId("67189a1b2c3d4e5f60718d01"),  // id_laboratorio=1
  nombre: "LabVisión Colombia",
  contacto_principal: "Roberto Sánchez",
  direcciones: [
    {
      calle: "Carrera 45 #12-34",
      ciudad: "Bogotá",
      estado: "Cundinamarca",
      codigo_postal: "110111",
      pais: "Colombia"
    }
  ],
  telefonos: [
    { numero: "6011234567", extension: "101" }
  ],
  activo: true
});

print("✅ Laboratorios migrados: 1 documento");

// ============================================================================
// 7. MIGRAR SUMINISTROS (Referencing: proveedor_ref, laboratorio_ref)
// ============================================================================

db.suministros.insertMany([
  {
    _id: ObjectId("67189a1b2c3d4e5f60718e01"),  // id_suministro=1
    tipo: {
      nombre: "Lentes oftálmicos",
      descripcion: "Cristales para gafas formuladas"
    },
    cantidad: 100,
    precio_unitario: 50000,
    fecha_ingreso: ISODate("2025-10-01"),
    numero_lote: "LOTE-2025-001",
    fecha_vencimiento: null,
    proveedor_ref: ObjectId("67189a1b2c3d4e5f60718c01"),
    laboratorio_ref: ObjectId("67189a1b2c3d4e5f60718d01"),
    observaciones: ""
  },
  {
    _id: ObjectId("67189a1b2c3d4e5f60718e02"),  // id_suministro=2
    tipo: {
      nombre: "Lentes de contacto",
      descripcion: "Lentes de contacto blandos y rígidos"
    },
    cantidad: 50,
    precio_unitario: 80000,
    fecha_ingreso: ISODate("2025-10-05"),
    numero_lote: "LOTE-2025-002",
    fecha_vencimiento: null,
    proveedor_ref: ObjectId("67189a1b2c3d4e5f60718c01"),
    laboratorio_ref: null,
    observaciones: ""
  },
  {
    _id: ObjectId("67189a1b2c3d4e5f60718e03"),  // id_suministro=3
    tipo: {
      nombre: "Monturas",
      descripcion: "Armazones para lentes"
    },
    cantidad: 30,
    precio_unitario: 120000,
    fecha_ingreso: ISODate("2025-10-10"),
    numero_lote: "LOTE-2025-003",
    fecha_vencimiento: null,
    proveedor_ref: ObjectId("67189a1b2c3d4e5f60718c02"),
    laboratorio_ref: null,
    observaciones: ""
  }
]);

print("✅ Suministros migrados: 3 documentos");

// ============================================================================
// 8. MIGRAR PRODUCTOS (Embedding: tipo, Referencing: suministro_ref)
// ============================================================================

db.productos.insertMany([
  {
    _id: ObjectId("67189a1b2c3d4e5f60718f01"),  // id_producto=1
    nombre: "Lente Esférico -1.00",
    codigo_barras: "7890123456001",
    tipo: {
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
    suministro_ref: ObjectId("67189a1b2c3d4e5f60718e01"),
    activo: true,
    fecha_creacion: ISODate("2025-10-22T00:00:00Z")
  },
  {
    _id: ObjectId("67189a1b2c3d4e5f60718f02"),  // id_producto=2
    nombre: "Lente de Contacto Mensual",
    codigo_barras: "7890123456002",
    tipo: {
      nombre: "Lentes de contacto",
      categoria: "Contacto"
    },
    marca: "Acuvue",
    descripcion: "Lente de contacto blando de uso mensual",
    precio_venta: 120000,
    stock: {
      actual: 25,
      minimo: 5
    },
    suministro_ref: ObjectId("67189a1b2c3d4e5f60718e02"),
    activo: true,
    fecha_creacion: ISODate("2025-10-22T00:00:00Z")
  },
  {
    _id: ObjectId("67189a1b2c3d4e5f60718f03"),  // id_producto=3
    nombre: "Montura Ray-Ban Aviador",
    codigo_barras: "7890123456003",
    tipo: {
      nombre: "Monturas oftálmicas",
      categoria: "Montura"
    },
    marca: "Ray-Ban",
    descripcion: "Montura metálica estilo aviador",
    precio_venta: 350000,
    stock: {
      actual: 15,
      minimo: 3
    },
    suministro_ref: ObjectId("67189a1b2c3d4e5f60718e03"),
    activo: true,
    fecha_creacion: ISODate("2025-10-22T00:00:00Z")
  },
  {
    _id: ObjectId("67189a1b2c3d4e5f60718f04"),  // id_producto=4
    nombre: "Gafas de Sol Oakley",
    codigo_barras: "7890123456004",
    tipo: {
      nombre: "Gafas de sol",
      categoria: "Accesorio"
    },
    marca: "Oakley",
    descripcion: "Gafas de sol deportivas con protección UV",
    precio_venta: 450000,
    stock: {
      actual: 10,
      minimo: 2
    },
    suministro_ref: null,
    activo: true,
    fecha_creacion: ISODate("2025-10-22T00:00:00Z")
  }
]);

print("✅ Productos migrados: 4 documentos");

// ============================================================================
// 9. MIGRAR CITAS (Embedding: motivo, Referencing: cliente, asesor, especialista)
// ============================================================================

db.citas.insertMany([
  {
    _id: ObjectId("67189a1b2c3d4e5f60719001"),  // id_cita=1
    fecha_cita: ISODate("2025-10-25"),
    hora_cita: "10:00:00",
    motivo: {
      descripcion: "Examen visual de rutina"
    },
    cliente_ref: ObjectId("67189a1b2c3d4e5f60718901"),
    asesor_ref: ObjectId("67189a1b2c3d4e5f60718a01"),
    especialista_ref: ObjectId("67189a1b2c3d4e5f60718b01"),
    estado: "Programada",
    observaciones: "",
    fecha_creacion: ISODate("2025-10-22T00:00:00Z")
  },
  {
    _id: ObjectId("67189a1b2c3d4e5f60719002"),  // id_cita=2
    fecha_cita: ISODate("2025-10-26"),
    hora_cita: "14:00:00",
    motivo: {
      descripcion: "Consulta por molestias visuales"
    },
    cliente_ref: ObjectId("67189a1b2c3d4e5f60718902"),
    asesor_ref: ObjectId("67189a1b2c3d4e5f60718a02"),
    especialista_ref: ObjectId("67189a1b2c3d4e5f60718b02"),
    estado: "Confirmada",
    observaciones: "",
    fecha_creacion: ISODate("2025-10-22T00:00:00Z")
  }
]);

print("✅ Citas migradas: 2 documentos");

// ============================================================================
// 10. MIGRAR EXÁMENES (Embedding: examen, diagnostico, formula)
// ============================================================================

db.examenes.insertOne({
  _id: ObjectId("67189a1b2c3d4e5f60719101"),  // id_examen=1
  fecha_examen: ISODate("2025-10-20T10:30:00Z"),
  cliente_ref: ObjectId("67189a1b2c3d4e5f60718901"),
  especialista_ref: ObjectId("67189a1b2c3d4e5f60718b01"),
  cita_ref: null,
  
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
    observaciones: "Visión ligeramente reducida, se recomienda corrección"
  },
  
  // Diagnóstico EMBEBIDO (id_diagnostico=1)
  diagnostico: {
    tipo: {
      nombre: "Miopía",
      descripcion: "Dificultad para ver objetos lejanos"
    },
    descripcion: "Miopía leve bilateral con componente astigmático",
    fecha: ISODate("2025-10-20")
  },
  
  // Fórmula médica EMBEBIDA (id_formula=1)
  formula: {
    descripcion: "OD: -1.00 -0.50 x 90, OI: -1.25 -0.75 x 85, ADD: +0.00, DP: 63mm",
    fecha_emision: ISODate("2025-10-20"),
    fecha_vencimiento: ISODate("2026-10-20"),
    activa: true
  }
});

print("✅ Exámenes migrados: 1 documento (con diagnóstico y fórmula embebidos)");

// ============================================================================
// 11. MIGRAR VENTAS (Embedding: items y factura, Referencing: cliente, asesor)
// ============================================================================

db.ventas.insertMany([
  {
    _id: ObjectId("67189a1b2c3d4e5f60719201"),  // id_compra=1
    numero_factura: "F-2025-001",
    fecha_compra: ISODate("2025-10-21T11:00:00Z"),
    cliente_ref: ObjectId("67189a1b2c3d4e5f60718901"),
    asesor_ref: ObjectId("67189a1b2c3d4e5f60718a01"),
    metodo_pago: {
      nombre: "Tarjeta de Crédito",
      activo: true
    },
    items: [
      {
        producto_ref: ObjectId("67189a1b2c3d4e5f60718f01"),
        producto_info: {
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
  },
  {
    _id: ObjectId("67189a1b2c3d4e5f60719202"),  // id_compra=2
    numero_factura: "F-2025-002",
    fecha_compra: ISODate("2025-10-22T15:30:00Z"),
    cliente_ref: ObjectId("67189a1b2c3d4e5f60718902"),
    asesor_ref: ObjectId("67189a1b2c3d4e5f60718a02"),
    metodo_pago: {
      nombre: "Efectivo",
      activo: true
    },
    items: [
      {
        producto_ref: ObjectId("67189a1b2c3d4e5f60718f04"),
        producto_info: {
          nombre: "Gafas de Sol Oakley",
          codigo_barras: "7890123456004"
        },
        cantidad: 1,
        precio_unitario: 450000,
        subtotal: 450000,
        descuento: 45000,
        total: 405000
      }
    ],
    subtotal: 450000,
    descuento: 45000,
    impuesto: 76950,
    total: 481950,
    estado: "Completada",
    observaciones: ""
  }
]);

print("✅ Ventas migradas: 2 documentos (con items y factura embebidos)");

// ============================================================================
// 12. CONSULTAS DE VALIDACIÓN
// ============================================================================

print("\n📊 VALIDACIÓN DE DATOS MIGRADOS:\n");

print("Clientes: " + db.clientes.countDocuments());
print("Asesores: " + db.asesores.countDocuments());
print("Especialistas: " + db.especialistas.countDocuments());
print("Proveedores: " + db.proveedores.countDocuments());
print("Laboratorios: " + db.laboratorios.countDocuments());
print("Suministros: " + db.suministros.countDocuments());
print("Productos: " + db.productos.countDocuments());
print("Citas: " + db.citas.countDocuments());
print("Exámenes: " + db.examenes.countDocuments());
print("Ventas: " + db.ventas.countDocuments());
print("Catálogos: " + db.catalogos.countDocuments());

print("\n✅ MIGRACIÓN COMPLETADA EXITOSAMENTE");

// ============================================================================
// EJEMPLOS DE CONSULTAS MONGODB
// ============================================================================

print("\n📝 EJEMPLOS DE CONSULTAS:\n");

// 1. Buscar cliente por email
print("1. Cliente por email:");
printjson(db.clientes.findOne({ email: "ana.perez@mail.com" }));

// 2. Citas del día específico
print("\n2. Citas programadas:");
printjson(db.citas.find({ estado: "Programada" }).toArray());

// 3. Productos con stock bajo
print("\n3. Productos con stock bajo:");
printjson(db.productos.find({ 
  $expr: { $lte: ["$stock.actual", "$stock.minimo"] },
  activo: true 
}).toArray());

// 4. Ventas del día
print("\n4. Ventas del día 2025-10-21:");
printjson(db.ventas.find({
  fecha_compra: {
    $gte: ISODate("2025-10-21T00:00:00Z"),
    $lt: ISODate("2025-10-22T00:00:00Z")
  }
}).toArray());

// 5. Historial médico de un cliente
print("\n5. Historial médico de Ana Pérez:");
printjson(db.examenes.find({ 
  cliente_ref: ObjectId("67189a1b2c3d4e5f60718901") 
}).sort({ fecha_examen: -1 }).toArray());

print("\n✅ Script de migración finalizado");
