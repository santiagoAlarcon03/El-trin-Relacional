// ============================================================================
// EJEMPLOS DE CONSULTAS MONGODB
// Base de Datos: Optica
// Fecha: Octubre 23, 2025
// ============================================================================

use Optica;

print("\n" + "=".repeat(80));
print("EJEMPLOS DE CONSULTAS MONGODB - BASE DE DATOS ÓPTICA");
print("=".repeat(80) + "\n");

// ============================================================================
// 1. CONSULTAS BÁSICAS (CRUD)
// ============================================================================

print("1️⃣ CONSULTAS BÁSICAS\n");

// 1.1 Buscar un cliente por email
print("1.1 Buscar cliente por email:");
db.clientes.findOne({ email: "ana.perez@mail.com" });

// 1.2 Listar todos los productos activos
print("\n1.2 Productos activos:");
db.productos.find({ activo: true }).pretty();

// 1.3 Buscar especialista por licencia
print("\n1.3 Especialista por licencia:");
db.especialistas.findOne({ numero_licencia: "OPT-12345" });

// 1.4 Citas de un día específico
print("\n1.4 Citas del 25 de octubre:");
db.citas.find({ fecha_cita: ISODate("2025-10-25") }).pretty();

// ============================================================================
// 2. CONSULTAS CON PROYECCIÓN (Seleccionar campos específicos)
// ============================================================================

print("\n2️⃣ PROYECCIONES\n");

// 2.1 Solo nombre y email de clientes
print("2.1 Lista de clientes (solo nombre y email):");
db.clientes.find(
  {},
  { nombre: 1, apellido: 1, email: 1, _id: 0 }
).pretty();

// 2.2 Productos con stock y precio
print("\n2.2 Inventario (nombre, stock, precio):");
db.productos.find(
  { activo: true },
  { nombre: 1, "stock.actual": 1, precio_venta: 1, _id: 0 }
).pretty();

// ============================================================================
// 3. CONSULTAS CON OPERADORES DE COMPARACIÓN
// ============================================================================

print("\n3️⃣ OPERADORES DE COMPARACIÓN\n");

// 3.1 Productos con precio mayor a 200,000
print("3.1 Productos caros (> $200,000):");
db.productos.find({
  precio_venta: { $gt: 200000 }
}).pretty();

// 3.2 Clientes nacidos después de 1990
print("\n3.2 Clientes jóvenes (nacidos después de 1990):");
db.clientes.find({
  fecha_nacimiento: { $gte: ISODate("1990-01-01") }
}).pretty();

// 3.3 Productos con stock entre 10 y 50
print("\n3.3 Productos con stock medio (10-50 unidades):");
db.productos.find({
  "stock.actual": { $gte: 10, $lte: 50 }
}).pretty();

// 3.4 Ventas mayores o iguales a $400,000
print("\n3.4 Ventas grandes (>= $400,000):");
db.ventas.find({
  total: { $gte: 400000 }
}).pretty();

// ============================================================================
// 4. CONSULTAS CON OPERADORES LÓGICOS
// ============================================================================

print("\n4️⃣ OPERADORES LÓGICOS\n");

// 4.1 Productos de marca Ray-Ban O Oakley
print("4.1 Productos de marcas premium:");
db.productos.find({
  $or: [
    { marca: "Ray-Ban" },
    { marca: "Oakley" }
  ]
}).pretty();

// 4.2 Clientes activos Y con email de Gmail
print("\n4.2 Clientes activos con Gmail:");
db.clientes.find({
  $and: [
    { activo: true },
    { email: { $regex: "@gmail.com$" } }
  ]
}).pretty();

// 4.3 Citas NO completadas ni canceladas
print("\n4.3 Citas pendientes:");
db.citas.find({
  estado: { $nin: ["Completada", "Cancelada"] }
}).pretty();

// ============================================================================
// 5. CONSULTAS EN SUBDOCUMENTOS (Embedding)
// ============================================================================

print("\n5️⃣ CONSULTAS EN SUBDOCUMENTOS\n");

// 5.1 Clientes con dirección en Bogotá
print("5.1 Clientes de Bogotá:");
db.clientes.find({
  "direcciones.ciudad": "Bogotá"
}).pretty();

// 5.2 Especialistas con especialidad en Optometría
print("\n5.2 Optómetras:");
db.especialistas.find({
  "especialidades.nombre": "Optometría"
}).pretty();

// 5.3 Productos tipo Lente
print("\n5.3 Productos de tipo Lente:");
db.productos.find({
  "tipo.categoria": "Lente"
}).pretty();

// 5.4 Exámenes con miopía diagnosticada
print("\n5.4 Exámenes con diagnóstico de miopía:");
db.examenes.find({
  "diagnostico.tipo.nombre": "Miopía"
}).pretty();

// ============================================================================
// 6. CONSULTAS CON EXPRESIONES ($expr)
// ============================================================================

print("\n6️⃣ EXPRESIONES Y COMPARACIONES ENTRE CAMPOS\n");

// 6.1 Productos con stock bajo (actual <= mínimo)
print("6.1 Productos con stock bajo:");
db.productos.find({
  $expr: { $lte: ["$stock.actual", "$stock.minimo"] }
}).pretty();

// 6.2 Ventas con descuento mayor al 10%
print("\n6.2 Ventas con buen descuento (> 10%):");
db.ventas.find({
  $expr: {
    $gt: [
      { $divide: ["$descuento", "$subtotal"] },
      0.10
    ]
  }
}).pretty();

// ============================================================================
// 7. CONSULTAS CON ARRAYS
// ============================================================================

print("\n7️⃣ OPERACIONES CON ARRAYS\n");

// 7.1 Clientes con más de 1 teléfono
print("7.1 Clientes con múltiples teléfonos:");
db.clientes.find({
  telefonos: { $size: { $gt: 1 } }  // Nota: $size solo acepta número exacto
}).pretty();

// Alternativa correcta:
db.clientes.find({
  "telefonos.1": { $exists: true }  // Tiene al menos 2 elementos
}).pretty();

// 7.2 Especialistas con al menos 1 especialidad
print("\n7.2 Especialistas certificados:");
db.especialistas.find({
  especialidades: { $ne: [] }
}).pretty();

// 7.3 Ventas con más de 1 item
print("\n7.3 Ventas con múltiples productos:");
db.ventas.find({
  "items.1": { $exists: true }
}).pretty();

// ============================================================================
// 8. CONSULTAS CON REGEX (Búsqueda de patrones)
// ============================================================================

print("\n8️⃣ BÚSQUEDA CON EXPRESIONES REGULARES\n");

// 8.1 Clientes cuyo nombre empiece con "A"
print("8.1 Clientes con nombre que empieza con A:");
db.clientes.find({
  nombre: { $regex: "^A", $options: "i" }  // i = case insensitive
}).pretty();

// 8.2 Productos que contengan "Lente"
print("\n8.2 Productos con 'Lente' en el nombre:");
db.productos.find({
  nombre: { $regex: "Lente", $options: "i" }
}).pretty();

// 8.3 Emails corporativos (.com)
print("\n8.3 Asesores con email corporativo:");
db.asesores.find({
  "emails.email": { $regex: "@.*\\.com$" }
}).pretty();

// ============================================================================
// 9. AGREGACIONES BÁSICAS
// ============================================================================

print("\n9️⃣ AGREGACIONES\n");

// 9.1 Contar clientes por ciudad
print("9.1 Clientes por ciudad:");
db.clientes.aggregate([
  { $unwind: "$direcciones" },
  {
    $group: {
      _id: "$direcciones.ciudad",
      cantidad: { $sum: 1 }
    }
  },
  { $sort: { cantidad: -1 } }
]);

// 9.2 Total de ventas por asesor
print("\n9.2 Total vendido por asesor:");
db.ventas.aggregate([
  {
    $group: {
      _id: "$asesor_ref",
      total_ventas: { $sum: "$total" },
      cantidad_ventas: { $count: {} }
    }
  },
  { $sort: { total_ventas: -1 } }
]);

// 9.3 Valor total del inventario
print("\n9.3 Valor total del inventario:");
db.productos.aggregate([
  {
    $group: {
      _id: null,
      valor_total: {
        $sum: { $multiply: ["$stock.actual", "$precio_venta"] }
      },
      total_productos: { $sum: "$stock.actual" }
    }
  }
]);

// 9.4 Promedio de precio por tipo de producto
print("\n9.4 Precio promedio por tipo:");
db.productos.aggregate([
  {
    $group: {
      _id: "$tipo.categoria",
      precio_promedio: { $avg: "$precio_venta" },
      cantidad: { $count: {} }
    }
  },
  { $sort: { precio_promedio: -1 } }
]);

// ============================================================================
// 10. AGREGACIONES CON LOOKUP (JOIN)
// ============================================================================

print("\n🔟 AGREGACIONES CON LOOKUP (Simular JOIN)\n");

// 10.1 Citas con información del cliente
print("10.1 Citas con datos del cliente:");
db.citas.aggregate([
  {
    $lookup: {
      from: "clientes",
      localField: "cliente_ref",
      foreignField: "_id",
      as: "cliente"
    }
  },
  { $unwind: "$cliente" },
  {
    $project: {
      fecha_cita: 1,
      hora_cita: 1,
      "cliente.nombre": 1,
      "cliente.apellido": 1,
      "cliente.email": 1,
      "motivo.descripcion": 1,
      estado: 1
    }
  }
]);

// 10.2 Ventas con información del cliente y asesor
print("\n10.2 Ventas con cliente y asesor:");
db.ventas.aggregate([
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
      from: "asesores",
      localField: "asesor_ref",
      foreignField: "_id",
      as: "asesor"
    }
  },
  { $unwind: "$cliente" },
  { $unwind: "$asesor" },
  {
    $project: {
      numero_factura: 1,
      fecha_compra: 1,
      cliente_nombre: { $concat: ["$cliente.nombre", " ", "$cliente.apellido"] },
      asesor_nombre: { $concat: ["$asesor.nombre", " ", "$asesor.apellido"] },
      total: 1,
      estado: 1
    }
  }
]);

// 10.3 Productos con información del proveedor
print("\n10.3 Productos con su proveedor:");
db.productos.aggregate([
  {
    $lookup: {
      from: "suministros",
      localField: "suministro_ref",
      foreignField: "_id",
      as: "suministro"
    }
  },
  { $unwind: { path: "$suministro", preserveNullAndEmptyArrays: true } },
  {
    $lookup: {
      from: "proveedores",
      localField: "suministro.proveedor_ref",
      foreignField: "_id",
      as: "proveedor"
    }
  },
  { $unwind: { path: "$proveedor", preserveNullAndEmptyArrays: true } },
  {
    $project: {
      nombre: 1,
      marca: 1,
      precio_venta: 1,
      "stock.actual": 1,
      proveedor_nombre: "$proveedor.nombre"
    }
  }
]);

// ============================================================================
// 11. CONSULTAS ANALÍTICAS AVANZADAS
// ============================================================================

print("\n1️⃣1️⃣ ANÁLISIS AVANZADO\n");

// 11.1 Top 3 productos más vendidos
print("11.1 Top 3 productos más vendidos:");
db.ventas.aggregate([
  { $unwind: "$items" },
  {
    $group: {
      _id: "$items.producto_info.nombre",
      total_vendido: { $sum: "$items.cantidad" },
      ingresos: { $sum: "$items.total" }
    }
  },
  { $sort: { total_vendido: -1 } },
  { $limit: 3 }
]);

// 11.2 Ventas por día de la semana
print("\n11.2 Ventas por día de la semana:");
db.ventas.aggregate([
  {
    $group: {
      _id: { $dayOfWeek: "$fecha_compra" },
      cantidad_ventas: { $count: {} },
      total: { $sum: "$total" }
    }
  },
  { $sort: { _id: 1 } },
  {
    $project: {
      dia_semana: {
        $switch: {
          branches: [
            { case: { $eq: ["$_id", 1] }, then: "Domingo" },
            { case: { $eq: ["$_id", 2] }, then: "Lunes" },
            { case: { $eq: ["$_id", 3] }, then: "Martes" },
            { case: { $eq: ["$_id", 4] }, then: "Miércoles" },
            { case: { $eq: ["$_id", 5] }, then: "Jueves" },
            { case: { $eq: ["$_id", 6] }, then: "Viernes" },
            { case: { $eq: ["$_id", 7] }, then: "Sábado" }
          ]
        }
      },
      cantidad_ventas: 1,
      total: 1
    }
  }
]);

// 11.3 Clientes con mayor gasto
print("\n11.3 Top 5 clientes con mayor gasto:");
db.ventas.aggregate([
  {
    $group: {
      _id: "$cliente_ref",
      gasto_total: { $sum: "$total" },
      cantidad_compras: { $count: {} }
    }
  },
  {
    $lookup: {
      from: "clientes",
      localField: "_id",
      foreignField: "_id",
      as: "cliente"
    }
  },
  { $unwind: "$cliente" },
  {
    $project: {
      nombre_completo: { $concat: ["$cliente.nombre", " ", "$cliente.apellido"] },
      email: "$cliente.email",
      gasto_total: 1,
      cantidad_compras: 1,
      ticket_promedio: { $divide: ["$gasto_total", "$cantidad_compras"] }
    }
  },
  { $sort: { gasto_total: -1 } },
  { $limit: 5 }
]);

// 11.4 Rendimiento de asesores
print("\n11.4 Rendimiento de asesores:");
db.ventas.aggregate([
  {
    $group: {
      _id: "$asesor_ref",
      ventas_realizadas: { $count: {} },
      total_vendido: { $sum: "$total" },
      ticket_promedio: { $avg: "$total" }
    }
  },
  {
    $lookup: {
      from: "asesores",
      localField: "_id",
      foreignField: "_id",
      as: "asesor"
    }
  },
  { $unwind: "$asesor" },
  {
    $project: {
      nombre_asesor: { $concat: ["$asesor.nombre", " ", "$asesor.apellido"] },
      ventas_realizadas: 1,
      total_vendido: 1,
      ticket_promedio: { $round: ["$ticket_promedio", 2] }
    }
  },
  { $sort: { total_vendido: -1 } }
]);

// ============================================================================
// 12. ACTUALIZACIONES
// ============================================================================

print("\n1️⃣2️⃣ OPERACIONES DE ACTUALIZACIÓN\n");

// 12.1 Actualizar stock de un producto
print("12.1 Actualizar stock:");
db.productos.updateOne(
  { codigo_barras: "7890123456001" },
  { $inc: { "stock.actual": -2 } }  // Restar 2 unidades
);

// 12.2 Agregar un nuevo teléfono a un cliente
print("\n12.2 Agregar teléfono a cliente:");
db.clientes.updateOne(
  { email: "ana.perez@mail.com" },
  {
    $push: {
      telefonos: {
        numero: "3159998877",
        tipo: "Trabajo",
        es_principal: false
      }
    }
  }
);

// 12.3 Cambiar estado de cita
print("\n12.3 Cambiar estado de cita:");
db.citas.updateOne(
  { _id: ObjectId("67189a1b2c3d4e5f60719001") },
  { $set: { estado: "Completada" } }
);

// 12.4 Desactivar producto
print("\n12.4 Desactivar producto:");
db.productos.updateOne(
  { codigo_barras: "7890123456004" },
  { $set: { activo: false } }
);

// 12.5 Actualizar múltiples productos (aumentar precios 5%)
print("\n12.5 Aumentar precios 5%:");
db.productos.updateMany(
  { "tipo.categoria": "Lente" },
  { $mul: { precio_venta: 1.05 } }
);

// ============================================================================
// 13. CONSULTAS ÚTILES PARA REPORTES
// ============================================================================

print("\n1️⃣3️⃣ CONSULTAS PARA REPORTES\n");

// 13.1 Reporte de stock bajo
print("13.1 Reporte de productos con stock bajo:");
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
      codigo_barras: 1,
      stock_actual: "$stock.actual",
      stock_minimo: "$stock.minimo",
      faltante: { $subtract: ["$stock.minimo", "$stock.actual"] },
      valor_faltante: {
        $multiply: [
          { $subtract: ["$stock.minimo", "$stock.actual"] },
          "$precio_venta"
        ]
      }
    }
  },
  { $sort: { faltante: -1 } }
]);

// 13.2 Reporte de ventas mensuales
print("\n13.2 Ventas mensuales:");
db.ventas.aggregate([
  {
    $group: {
      _id: {
        mes: { $month: "$fecha_compra" },
        anio: { $year: "$fecha_compra" }
      },
      total_ventas: { $sum: "$total" },
      cantidad: { $count: {} },
      ticket_promedio: { $avg: "$total" }
    }
  },
  { $sort: { "_id.anio": -1, "_id.mes": -1 } }
]);

// 13.3 Clientes sin compras
print("\n13.3 Clientes sin compras:");
db.clientes.aggregate([
  {
    $lookup: {
      from: "ventas",
      localField: "_id",
      foreignField: "cliente_ref",
      as: "compras"
    }
  },
  {
    $match: {
      compras: { $size: 0 },
      activo: true
    }
  },
  {
    $project: {
      nombre: 1,
      apellido: 1,
      email: 1,
      fecha_registro: 1
    }
  }
]);

// ============================================================================
// FIN DE EJEMPLOS
// ============================================================================

print("\n" + "=".repeat(80));
print("✅ EJEMPLOS DE CONSULTAS COMPLETADOS");
print("=".repeat(80) + "\n");
