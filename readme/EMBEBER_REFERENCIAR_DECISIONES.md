# Decisiones de diseño: Embeber (Embedding) vs Referenciar (Referencing)

Este documento explica las razones detrás de elegir embeber (embedding) o referenciar (referencing) documentos en una base de datos NoSQL (MongoDB) para el proyecto "El-trin-Relacional". Incluye criterios de decisión, ventajas y desventajas, ejemplos aplicados al dataset del proyecto y recomendaciones concretas.

## Objetivo

Dar una guía práctica y justificable para decidir cuándo usar embeber y cuándo usar referencias en el diseño de esquemas para los datos del proyecto (clientes, ventas, productos, citas, especialistas, etc.). El documento está pensado para desarrolladores y arquitectos que deben equilibrar rendimiento, consistencia, escalabilidad y simplicidad.

**Total de colecciones:** 14 (incluyendo `ordenes_compra` para inventario genérico y `pedidos_laboratorio` para productos personalizados)

## Resumen rápido

- Embeber (embedding): mejor cuando los datos se leen juntos con alta frecuencia, la relación es 1:1 o 1:N con N pequeño, y la atomicidad de actualización local es importante.
- Referenciar (referencing): mejor cuando las subcolecciones crecen sin límite, cuando se requiere compartir entidades entre documentos distintos o cuando se necesitan consultas independientes y frecuentes sobre la entidad referenciada.

## Criterios de decisión (qué mirar primero)

1. Patrón de acceso (read-heavy vs write-heavy):
   - Si se lee la entidad y sus subdocumentos juntos casi siempre => embeber.
   - Si se accede a la subentidad independientemente (por ejemplo, listar productos sin cargar ventas) => referenciar.

2. Cardinalidad y tamaño:
   - Relaciones 1:1 o 1:N con N pequeño y límite razonable => embeber.
   - Relaciones 1:N con N grande o N sin límite (por ejemplo historial de muchos eventos) => referenciar.

3. Atomicidad requerida:
   - Si necesitas actualizaciones atómicas sobre la entidad y sus subdatos => embeber (operación atómica en un documento).

4. Dinámica de crecimiento y hotspots:
   - Si un subdocumento puede crecer indefinidamente y causar documentos de gran tamaño (>16 MB) o hotspots en escritura => referenciar.

5. Reutilización y consistencia referencial:
   - Si la subentidad se comparte entre múltiples entidades (ej. detalles de producto usados por muchas ventas) y debe mantenerse consistente => referenciar.

6. Índices y consultas:
   - Embeber facilita lecturas sin joins, pero puede complicar índices si necesitas filtrar por campos embebidos frecuentemente.
   - Referenciar permite indexación independiente y consultas directas sobre la entidad referenciada.

## Ventajas y desventajas

Embeber (embedding)
- Ventajas:
  - Lecturas más rápidas cuando necesitas el conjunto completo (evita múltiples consultas).
  - Operaciones atómicas (un solo documento) para cambios relacionados.
  - Modelo natural para datos jerárquicos y altamente cohesivos.
- Desventajas:
  - Los documentos pueden crecer demasiado y acercarse al límite de tamaño.
  - Actualizaciones repetidas de subdocumentos grandes pueden impactar rendimiento (reescritura del documento).
  - Difícil de compartir subentidades entre documentos distintos sin duplicación.

Referenciar (referencing)
- Ventajas:
  - Documentos más pequeños y controlables.
  - Entidades reutilizables y actualizables de forma independiente (evita duplicación de datos).
  - Mejor para relaciones muchos-a-muchos o listas largas.
- Desventajas:
  - Requiere más consultas (o agregaciones con $lookup) para juntar datos, lo que aumenta latencia.
  - No hay joins automáticos: la consistencia entre documentos no es garantizada por la base de datos (sin transacciones o lógica adicional).

## 📊 Análisis detallado de las 14 colecciones del proyecto

El proyecto "El-trin-Relacional" migró datos de MySQL a MongoDB con las siguientes 14 colecciones (13 entidades + 1 catálogo de referencia).

```
╔═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║                                    DECISIONES DE DISEÑO: EMBEDDING vs REFERENCING                                                         ║
╚═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝

┌────────────────────────┬──────────┬─────────────────────────────────┬────────────────────────────────┬──────────────────────────────────┐
│      Colección         │   Docs   │       Datos Embebidos           │      Datos Referenciados       │         Justificación            │
├────────────────────────┼──────────┼─────────────────────────────────┼────────────────────────────────┼──────────────────────────────────┤
│ 🧑 Clientes            │    30    │ • documento {tipo, número}      │  Ninguna                       │ EMBEDDING total                  │
│                        │          │ • direcciones[] (1-3 items)     │                                │ Datos cohesivos, siempre se      │
│                        │          │ • telefonos[] (1-3 items)       │                                │ consultan juntos                 │
│                        │          │                                 │                                │ ✅ 1 query vs 3 JOINs (MySQL)   │
├────────────────────────┼──────────┼─────────────────────────────────┼────────────────────────────────┼──────────────────────────────────┤
│ 👔 Asesores            │     8    │ • telefonos[] (1-2 items)       │  Ninguna                       │ EMBEDDING total                  │
│                        │          │ • emails[] (1-2 items)          │                                │ Contactos limitados, parte del   │
│                        │          │                                 │                                │ perfil del asesor                │
│                        │          │                                 │                                │ ✅ Perfil completo en 1 doc      │
├────────────────────────┼──────────┼─────────────────────────────────┼────────────────────────────────┼──────────────────────────────────┤
│ 👨‍⚕️ Especialistas      │     6    │ • especialidades[] + fechas     │  Ninguna                       │ EMBEDDING total                  │
│                        │          │ • telefonos[] (1-2 items)       │                                │ Perfil profesional completo      │
│                        │          │ • emails[] (1-2 items)          │                                │ sin fragmentación                │
│                        │          │                                 │                                │ ✅ 1 doc vs 5 tablas (MySQL)     │
├────────────────────────┼──────────┼─────────────────────────────────┼────────────────────────────────┼──────────────────────────────────┤
│ 🏭 Proveedores         │     5    │ • direcciones[] (1-3 items)     │  Ninguna                       │ EMBEDDING total                  │
│                        │          │ • telefonos[] + extensión       │                                │ Información de contacto como     │
│                        │          │ • emails[] + tipo               │                                │ unidad atómica                   │
│                        │          │                                 │                                │ ✅ Datos completos en 1 query    │
├────────────────────────┼──────────┼─────────────────────────────────┼────────────────────────────────┼──────────────────────────────────┤
│ 🔬 Laboratorios        │     3    │ • direcciones[] (1-2 items)     │  Ninguna                       │ EMBEDDING total                  │
│                        │          │ • telefonos[] + extensión       │                                │ Similar a proveedores, contacto  │
│                        │          │                                 │                                │ integral del laboratorio         │
│                        │          │                                 │                                │ ✅ Sin fragmentación             │
├────────────────────────┼──────────┼─────────────────────────────────┼────────────────────────────────┼──────────────────────────────────┤
│ 🛒 Órdenes Compra      │    10    │ • proveedor_snapshot {nombre,   │ • proveedor_ref (ObjectId)     │ HÍBRIDO (Embed + Ref) ⭐ NUEVO   │
│                        │          │   contacto, email, tel}         │ • items.suministro_ref (array) │ Snapshot del proveedor preserva  │
│                        │          │ • items[] array con:            │                                │ histórico, referencia bidirecc.  │
│                        │          │   - tipo_suministro embebido    │                                │ 🎯 Trazabilidad completa:        │
│                        │          │   - cantidades, precios         │                                │    Solicitud → Recepción         │
│                        │          │ • historial_estados[]           │                                │ ⭐ 1 Orden ↔ N Suministros       │
├────────────────────────┼──────────┼─────────────────────────────────┼────────────────────────────────┼──────────────────────────────────┤
│ 📦 Suministros         │    41    │ • tipo {nombre, descripción}    │ • proveedor_ref (ObjectId)     │ HÍBRIDO (Embed + Ref)            │
│                        │          │                                 │ • laboratorio_ref (ObjectId)   │ Referencias a entidades          │
│                        │          │                                 │ • orden_compra_ref (ObjectId)⭐│ independientes compartidas       │
│                        │          │                                 │                                │ 🎯 1:N → Un proveedor tiene      │
│                        │          │                                 │                                │    múltiples suministros         │
│                        │          │                                 │                                │ ⭐ 1 Suministro → 1 Orden Compra │
├────────────────────────┼──────────┼─────────────────────────────────┼────────────────────────────────┼──────────────────────────────────┤
│ 🛍️ Productos           │    23    │ • tipo {nombre, categoría}      │ • suministro_ref (ObjectId)    │ HÍBRIDO (Embed + Ref)            │
│                        │          │ • imagenes[] (URLs)             │ • pedido_laboratorio_ref ⭐⭐  │ Dos origenes: inventario genérico│
│                        │          │                                 │                                │ o fabricación personalizada      │
│                        │          │                                 │                                │ 🎯 Tipo embebido = metadata      │
│                        │          │                                 │                                │ ⭐⭐ Trazabilidad dual:           │
│                        │          │                                 │                                │    Genérico: suministro_ref      │
│                        │          │                                 │                                │    Personal: pedido_lab_ref      │
├────────────────────────┼──────────┼─────────────────────────────────┼────────────────────────────────┼──────────────────────────────────┤
│ 📅 Citas               │    15    │ • motivo {descripción}          │ • cliente_ref (ObjectId)       │ HÍBRIDO (Embed + Ref)            │
│                        │          │                                 │ • asesor_ref (ObjectId)        │ Referencias a entidades que      │
│                        │          │                                 │ • especialista_ref (ObjectId)  │ se consultan independientemente  │
│                        │          │                                 │ • examen_ref (ObjectId) ⭐     │ 🎯 Queries: "citas de cliente X" │
│                        │          │                                 │                                │    "agenda del especialista Y"   │
│                        │          │                                 │                                │ ⭐ Relación bidireccional:       │
│                        │          │                                 │                                │    1 Cita ↔ 0..1 Examen          │
├────────────────────────┼──────────┼─────────────────────────────────┼────────────────────────────────┼──────────────────────────────────┤
│ 👁️ Examenes            │    15    │ • diagnostico {tipo, desc}      │ • cliente_ref (ObjectId)       │ HÍBRIDO (Embed + Ref)            │
│                        │          │ • formula {desc, fechas}        │ • especialista_ref (ObjectId)  │ Historial médico completo        │
│                        │          │                                 │ • cita_ref (ObjectId) ⭐       │ embebido (diagnóstico + fórmula) │
│                        │          │                                 │ • pedido_laboratorio_ref ⭐⭐  │ ✅ 1 doc vs 6 tablas (MySQL)     │
│                        │          │                                 │                                │ 🎯 Atomicidad de actualización   │
│                        │          │                                 │                                │ ⭐ Relación bidireccional:       │
│                        │          │                                 │                                │    1 Examen → 1 Cita             │
│                        │          │                                 │                                │ ⭐⭐ Trazabilidad completa:       │
│                        │          │                                 │                                │    Examen → Pedido Lab → Prod    │
├────────────────────────┼──────────┼─────────────────────────────────┼────────────────────────────────┼──────────────────────────────────┤
│ 🔬 Pedidos Laboratorio │    10    │ • cliente_snapshot {nombre,     │ • cliente_ref (ObjectId)       │ HÍBRIDO (Embed + Ref) ⭐⭐ NUEVO  │
│                        │          │   apellido, email}              │ • examen_ref (ObjectId)        │ Snapshot de cliente/lab preserva │
│                        │          │ • laboratorio_snapshot {nombre, │ • laboratorio_ref (ObjectId)   │ histórico. Formula copiada del   │
│                        │          │   contacto}                     │ • asesor_ref (ObjectId)        │ examen para registro permanente  │
│                        │          │ • formula_snapshot {OD, OI, DP} │ • producto_ref (ObjectId) ⭐⭐ │ 🎯 Flujo completo personalizado: │
│                        │          │ • especificaciones {tipo_lente, │                                │    Examen → Pedido Lab →         │
│                        │          │   material, tratamientos[]}     │                                │    Fabricación → Producto        │
│                        │          │ • historial_estados[]           │                                │ ⭐⭐ Relación bidireccional:      │
│                        │          │                                 │                                │    1 Pedido ↔ 1 Examen           │
│                        │          │                                 │                                │    1 Pedido ↔ 0..1 Producto      │
├────────────────────────┼──────────┼─────────────────────────────────┼────────────────────────────────┼──────────────────────────────────┤
│ 💰 Ventas              │    18    │ • metodo_pago {nombre}          │ • cliente_ref (ObjectId)       │ HÍBRIDO (Embed + Ref)            │
│                        │          │ • items[] array con:            │ • asesor_ref (ObjectId)        │ Items embebidos (líneas de venta)│
│                        │          │   - nombre (SNAPSHOT)           │ • examen_ref (ObjectId) ⭐⭐   │ + referencias para trazabilidad  │
│                        │          │   - cantidad, precio            │ • En cada item:                │ ✅ Snapshot preserva histórico   │
│                        │          │   - subtotal, descuento         │   - producto_ref (ObjectId)    │ 🎯 Venta completa en 1 doc       │
│                        │          │                                 │                                │    (vs 6 tablas + 5 JOINs MySQL) │
│                        │          │                                 │                                │ ⭐⭐ examen_ref: vincula venta    │
│                        │          │                                 │                                │    con su examen originario      │
├────────────────────────┼──────────┼─────────────────────────────────┼────────────────────────────────┼──────────────────────────────────┤
│ 📋 Catálogos           │     1    │ • especialidades[]              │  Ninguna                       │ EMBEDDING total                  │
│                        │          │ • motivos[]                     │                                │ Documento único de configuración │
│                        │          │ • tipos_diagnostico[]           │                                │ Todos los lookups en 1 consulta  │
│                        │          │ • metodos_pago[]                │                                │ ✅ Catálogos estáticos pequeños  │
│                        │          │ • tipos_suministro[]            │                                │ 🎯 Cargados en memoria al inicio │
│                        │          │ • tipos_producto[]              │                                │                                  │
├────────────────────────┼──────────┼─────────────────────────────────┼────────────────────────────────┼──────────────────────────────────┤
│ 📊 Metadatos           │     1    │ • info_proyecto                 │  Ninguna                       │ EMBEDDING total                  │
│                        │          │ • contadores_colecciones        │                                │ Documento administrativo único   │
│                        │          │ • tipos_imagenes                │                                │ Estadísticas del dataset         │
│                        │          │ • fuentes_datos                 │                                │ ✅ Se consulta como unidad       │
└────────────────────────┴──────────┴─────────────────────────────────┴────────────────────────────────┴──────────────────────────────────┘

📊 TOTALES: 128 documentos en 12 colecciones | 92 imágenes | Reducción: 64% vs MySQL (22 tablas → 11 colecciones)
```

---

## 🎯 Resumen de patrones identificados

### ✅ **Datos Embebidos** (Embedding)
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Arrays pequeños (1-10 items)   → direcciones[], telefonos[], emails[]      │
│ Snapshots históricos            → nombre_producto en items de venta        │
│ Subdocumentos descriptivos      → tipo, motivo, diagnostico, formula       │
│ URLs e imágenes                 → imagenes[] (strings ligeros)             │
│ Catálogos de configuración      → todo en 1 documento único                │
└─────────────────────────────────────────────────────────────────────────────┘
✨ Ventaja: Siempre se leen con la entidad padre, evitan JOINs
```

### 🔗 **Datos Referenciados** (Referencing)
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Entidades compartidas           → clientes, asesores, especialistas        │
│ Ciclo de vida independiente     → productos, suministros                   │
│ Relaciones N:N implícitas       → cliente → muchas ventas/citas            │
│ Consultas independientes        → "citas del especialista X"               │
└─────────────────────────────────────────────────────────────────────────────┘
✨ Ventaja: Sin duplicación, integridad referencial, updates centralizados
```

### 🎨 **Patrón Híbrido** (Embed + Ref)
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Ventas:             items[] embebidos + producto_ref + snapshot nombre/pre  │
│                     + examen_ref (venta originada por examen) ⭐⭐⭐         │
│ Órdenes Compra:     items[] embebidos + suministro_ref (bidireccional) ⭐⭐ │
│                     + proveedor_snapshot {nombre, contacto, email, tel}     │
│                     + proveedor_ref (referencia al actual)                  │
│ Pedidos Lab:        formula_snapshot + especificaciones embebidas ⭐⭐⭐     │
│                     + examen_ref + laboratorio_ref + producto_ref           │
│                     Flujo: Examen → Pedido Lab → Fabricación → Producto     │
│ Suministros:        tipo embebido + proveedor_ref + orden_compra_ref ⭐⭐   │
│ Productos:          tipo embebido + suministro_ref O pedido_laboratorio_ref│
│                     Origen dual: genérico (inventario) o personalizado ⭐⭐⭐│
│ Examenes:           diagnostico/formula embebidos + cliente_ref/especial   │
│                     + cita_ref (bidireccional) ⭐                           │
│                     + pedido_laboratorio_ref (fabricación) ⭐⭐⭐            │
│ Citas:              motivo embebido + cliente_ref/asesor_ref/especialista  │
│                     + examen_ref (bidireccional) ⭐                         │
└─────────────────────────────────────────────────────────────────────────────┘
✨ Ventaja: Performance + flexibilidad + datos históricos preservados
⭐ Relación bidireccional entre Citas y Exámenes para integridad referencial
⭐⭐ Sistema completo de órdenes de compra con trazabilidad bidireccional
    desde pedido → recepción → inventario
⭐⭐⭐ NUEVO: Flujo completo de productos personalizados basados en exámenes
    Cliente → Cita → Examen → Pedido Laboratorio → Producto → Venta
```

---

## 🏆 Decisiones técnicas clave

| Decisión | Razonamiento | Impacto |
|----------|--------------|---------|
| **Snapshot en Ventas** | `producto_ref` + nombre embebido | ✅ Histórico inmutable + trazabilidad |
| **Diagnóstico embebido** | Parte del examen, no se reutiliza | ✅ Atomicidad: 1 operación para examen completo |
| **Cliente solo referenciado** | Sin snapshot en ventas | ⚠️ Requiere $lookup pero evita duplicación |
| **Catálogos centralizados** | 1 documento vs 6 colecciones | ✅ 1 query carga todo, ideal para cache |

## Reglas prácticas y heurísticas

- Si la relación es obligatoriamente leída junto al padre y la subcolección es pequeña -> embeber.
- Si la subcolección crece sin límite o debe ser consultada por separado -> referenciar.
- Para datos históricos (logs, snapshots) preferir embeber solo si el historial es corto; si es largo, externalizar a una colección propia.
- Si necesitas transacciones entre entidades múltiples, usar referencias + transacciones (si tu versión de MongoDB y tu despliegue lo soportan) o diseñar compensaciones idempotentes.

## Índices y rendimiento

- Campos embebidos pueden indexarse con índices compuestos o con índices de campo interno (`'lineas.producto_id'`). Aun así, si filtras frecuentemente por el campo embebido, considera mantener un índice apropiado.
- En colecciones referenciadas, indexa los campos de referencia (`cliente_id`, `producto_id`, `especialista_id`) para acelerar joins/lookup.
- Evita arrays enormes en documentos porque impactan las escrituras (documento completo se reescribe).

## Consistencia y actualizaciones

- Embeber: actualizaciones atómicas (si todo está en el mismo documento) facilitan consistencia local.
- Referenciar: si necesitas consistencia cross-document, considera:
  - Transacciones (si están disponibles y necesarias).
  - Versionado / timestamps y reconciliación eventual.
  - Snapshots embebidos (copiar el estado necesario al momento de la operación) para preservar histórico.

## Migración y operaciones futuras

- Si decides migrar datos de embeber a referenciar (o viceversa), planifica una migración por etapas:
  1. Añadir campo de referencia nuevo (por ejemplo `producto_id`) en documentos existentes.
  2. Duplicar los datos en la nueva colección si es necesario.
  3. Actualizar el código para escribir tanto en la estructura vieja como en la nueva durante un periodo de transición.
  4. Migrar lecturas gradualmente y, cuando todo esté estabilizado, eliminar la duplicación.

## Recomendaciones de mejora para el proyecto actual

Basándome en el análisis del dataset real, estas son oportunidades de optimización:

### 1. Considerar snapshots en Ventas para Cliente y Asesor
**Estado actual**: Solo referencias (`cliente_ref`, `asesor_ref`)  
**Mejora propuesta**: Embeber snapshot de campos inmutables/históricos
```javascript
{
  cliente_ref: ObjectId("..."),
  cliente_snapshot: {
    nombre: "Carolina Castro",
    documento: { tipo: "TI", numero: "1933638521" }
  },
  asesor_snapshot: {
    nombre: "Pablo Jiménez"
  }
}
```
**Beneficio**: reportes de ventas sin necesidad de $lookup, preservar histórico si el cliente cambia datos

### 2. Índices recomendados para referencias
```javascript
// Colección: ventas
db.ventas.createIndex({ "cliente_ref": 1, "fecha_compra": -1 });
db.ventas.createIndex({ "asesor_ref": 1, "fecha_compra": -1 });
db.ventas.createIndex({ "items.producto_ref": 1 });

// Colección: citas
db.citas.createIndex({ "cliente_ref": 1, "fecha_cita": -1 });
db.citas.createIndex({ "especialista_ref": 1, "fecha_cita": -1 });
db.citas.createIndex({ "estado": 1, "fecha_cita": 1 });
db.citas.createIndex({ "examen_ref": 1 }); // ⭐ Nuevo: índice bidireccional

// Colección: examenes
db.examenes.createIndex({ "cliente_ref": 1, "fecha_examen": -1 });
db.examenes.createIndex({ "especialista_ref": 1 });
db.examenes.createIndex({ "cita_ref": 1 }); // ⭐ Índice bidireccional
db.examenes.createIndex({ "formula.activa": 1, "formula.fecha_vencimiento": 1 });

// Colección: productos
db.productos.createIndex({ "suministro_ref": 1 });
db.productos.createIndex({ "tipo.categoria": 1, "activo": 1 });
db.productos.createIndex({ "stock": 1, "stock_minimo": 1 }); // alertas stock bajo

// Colección: suministros
db.suministros.createIndex({ "proveedor_ref": 1 });
db.suministros.createIndex({ "laboratorio_ref": 1 });
db.suministros.createIndex({ "fecha_vencimiento": 1 }); // alertas vencimiento
db.suministros.createIndex({ "orden_compra_ref": 1 }); // ⭐⭐ Nuevo: trazabilidad a órdenes

// Colección: ordenes_compra ⭐⭐ Nuevo
db.ordenes_compra.createIndex({ "numero_orden": 1 }, { unique: true });
db.ordenes_compra.createIndex({ "proveedor_ref": 1, "fecha_solicitud": -1 });
db.ordenes_compra.createIndex({ "estado": 1 });
db.ordenes_compra.createIndex({ "fecha_solicitud": -1 });
db.ordenes_compra.createIndex({ "fecha_estimada_entrega": 1 });
db.ordenes_compra.createIndex({ "items.suministro_ref": 1 }); // bidireccional

// Colección: pedidos_laboratorio ⭐⭐⭐ Nuevo
db.pedidos_laboratorio.createIndex({ "numero_pedido": 1 }, { unique: true });
db.pedidos_laboratorio.createIndex({ "laboratorio_ref": 1, "fecha_solicitud": -1 });
db.pedidos_laboratorio.createIndex({ "estado": 1 });
db.pedidos_laboratorio.createIndex({ "cliente_ref": 1, "fecha_solicitud": -1 });
db.pedidos_laboratorio.createIndex({ "examen_ref": 1 }); // bidireccional
db.pedidos_laboratorio.createIndex({ "fecha_estimada_entrega": 1 }, { sparse: true });
db.pedidos_laboratorio.createIndex({ "producto_ref": 1 }, { sparse: true }); // bidireccional

// Colección: productos (actualizada) ⭐⭐⭐
db.productos.createIndex({ "pedido_laboratorio_ref": 1 }, { sparse: true }); // nuevo

// Colección: ventas (actualizada) ⭐⭐⭐
db.ventas.createIndex({ "examen_ref": 1 }, { sparse: true }); // nuevo

// Colección: examenes (actualizada) ⭐⭐⭐
db.examenes.createIndex({ "pedido_laboratorio_ref": 1 }, { sparse: true }); // nuevo
```

### 3. Validación de esquemas (Schema Validation)
Para garantizar consistencia, se recomienda implementar validación:
```javascript
// Ejemplo para ventas
db.createCollection("ventas", {
  validator: {
    $jsonSchema: {
      required: ["numero_factura", "fecha_compra", "cliente_ref", "items", "total"],
      properties: {
        cliente_ref: { bsonType: "objectId" },
        asesor_ref: { bsonType: "objectId" },
        items: {
          bsonType: "array",
          minItems: 1,
          items: {
            required: ["producto_ref", "nombre", "cantidad", "precio_unitario"],
            properties: {
              producto_ref: { bsonType: "objectId" },
              cantidad: { bsonType: "int", minimum: 1 }
            }
          }
        }
      }
    }
  }
});

// ⭐⭐ Ejemplo para ordenes_compra (nuevo)
db.createCollection("ordenes_compra", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["numero_orden", "fecha_solicitud", "proveedor_ref", "items", "estado", "total"],
      properties: {
        numero_orden: { bsonType: "string" },
        fecha_solicitud: { bsonType: "date" },
        fecha_estimada_entrega: { bsonType: ["date", "null"] },
        fecha_entrega_real: { bsonType: ["date", "null"] },
        proveedor_ref: { bsonType: "objectId" },
        proveedor_snapshot: {
          bsonType: "object",
          required: ["nombre", "contacto", "email", "telefono"],
          properties: {
            nombre: { bsonType: "string" },
            contacto: { bsonType: "string" },
            email: { bsonType: "string" },
            telefono: { bsonType: "string" }
          }
        },
        items: {
          bsonType: "array",
          minItems: 1,
          items: {
            bsonType: "object",
            required: ["tipo_suministro", "cantidad_solicitada", "precio_unitario", "total"],
            properties: {
              tipo_suministro: {
                bsonType: "object",
                required: ["nombre", "descripcion"],
                properties: {
                  nombre: { bsonType: "string" },
                  descripcion: { bsonType: "string" }
                }
              },
              cantidad_solicitada: { bsonType: "int", minimum: 1 },
              cantidad_recibida: { bsonType: "int", minimum: 0 },
              precio_unitario: { bsonType: "double", minimum: 0 },
              total: { bsonType: "double", minimum: 0 },
              suministro_ref: { bsonType: ["objectId", "null"] },
              laboratorio_ref: { bsonType: ["objectId", "null"] }
            }
          }
        },
        estado: {
          bsonType: "string",
          enum: ["Solicitado", "Confirmado", "En proceso", "En tránsito", "Recibido", "Recibido parcial", "Cancelado"]
        },
        total: { bsonType: "double", minimum: 0 },
        historial_estados: {
          bsonType: "array",
          items: {
            bsonType: "object",
            required: ["estado", "fecha", "usuario"],
            properties: {
              estado: { bsonType: "string" },
              fecha: { bsonType: "date" },
              usuario: { bsonType: "string" },
              observaciones: { bsonType: ["string", "null"] }
            }
          }
        },
        observaciones: { bsonType: ["string", "null"] }
      }
    }
  }
});
```

### 4. Separar catálogos si crecen
**Estado actual**: 1 documento con todos los catálogos embebidos  
**Cuándo separar**: si algún catálogo supera 100-200 items o se actualiza frecuentemente
```javascript
// Opción futura: colección independiente para productos con muchas variantes
db.tipos_producto.find({ categoria: "Lente" });
```

### 5. TTL (Time To Live) para datos temporales
Si hay datos que expiran (fórmulas vencidas, citas antiguas), considerar índices TTL:
```javascript
// Archivar citas completadas después de 2 años
db.citas.createIndex(
  { "fecha_cita": 1 },
  { expireAfterSeconds: 63072000, partialFilterExpression: { estado: "Completada" } }
);
```

### 6. Monitoreo de tamaño de documentos
```javascript
// Query para detectar documentos grandes (>1MB)
db.ventas.aggregate([
  {
    $project: {
      numero_factura: 1,
      size: { $bsonSize: "$$ROOT" }
    }
  },
  { $match: { size: { $gt: 1048576 } } },
  { $sort: { size: -1 } }
]);
```

## Casos límite y consideraciones adicionales

- Documentos grandes: monitorizar tamaño medio de documentos y explotar sharding si la carga y el volumen lo requieren.
- Concurrencia: si una misma entidad recibe muchas escrituras concurrentes en subdocumentos embebidos, eso puede causar contención; en esos casos preferir referencias o particionar por otra clave.
- Backups y restauración: embeber simplifica restauración de conjuntos lógicos (todo en un documento) pero aumenta tamaño de documentos; referenciar reparte la restauración por colecciones.

## Consultas de ejemplo con $lookup (Join en MongoDB)

A continuación se muestran consultas reales para trabajar con las referencias del proyecto:

### Ejemplo 1: Ventas con información completa de cliente
```javascript
db.ventas.aggregate([
  {
    $match: {
      fecha_compra: {
        $gte: ISODate("2025-01-01"),
        $lt: ISODate("2026-01-01")
      }
    }
  },
  {
    $lookup: {
      from: "clientes",
      localField: "cliente_ref",
      foreignField: "_id",
      as: "cliente_info"
    }
  },
  {
    $lookup: {
      from: "asesores",
      localField: "asesor_ref",
      foreignField: "_id",
      as: "asesor_info"
    }
  },
  {
    $unwind: "$cliente_info"
  },
  {
    $unwind: "$asesor_info"
  },
  {
    $project: {
      numero_factura: 1,
      fecha_compra: 1,
      total: 1,
      "cliente_info.nombre": 1,
      "cliente_info.apellido": 1,
      "cliente_info.email": 1,
      "asesor_info.nombre": 1,
      "asesor_info.apellido": 1
    }
  }
]);
```

### Ejemplo 2: Productos con información de suministro y proveedor
```javascript
db.productos.aggregate([
  {
    $match: { activo: true, stock: { $lt: "$stock_minimo" } }
  },
  {
    $lookup: {
      from: "suministros",
      localField: "suministro_ref",
      foreignField: "_id",
      as: "suministro"
    }
  },
  {
    $unwind: "$suministro"
  },
  {
    $lookup: {
      from: "proveedores",
      localField: "suministro.proveedor_ref",
      foreignField: "_id",
      as: "proveedor"
    }
  },
  {
    $unwind: "$proveedor"
  },
  {
    $project: {
      nombre_producto: 1,
      stock: 1,
      stock_minimo: 1,
      "suministro.tipo.nombre": 1,
      "proveedor.nombre_proveedor": 1,
      "proveedor.emails": 1
    }
  }
]);
```

### Ejemplo 3: Citas con especialista, cliente y examen (incluye datos embebidos y relación bidireccional) ⭐
```javascript
db.citas.aggregate([
  {
    $match: {
      estado: "Completada",
      examen_ref: { $exists: true }  // ⭐ Solo citas con examen asociado
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
    $lookup: {
      from: "clientes",
      localField: "cliente_ref",
      foreignField: "_id",
      as: "cliente"
    }
  },
  {
    $lookup: {
      from: "examenes",  // ⭐ Nuevo: lookup del examen relacionado
      localField: "examen_ref",
      foreignField: "_id",
      as: "examen"
    }
  },
  {
    $unwind: "$especialista"
  },
  {
    $unwind: "$cliente"
  },
  {
    $unwind: "$examen"
  },
  {
    $project: {
      fecha_cita: 1,
      hora_cita: 1,
      "motivo.descripcion": 1,  // Dato embebido
      "especialista.nombre": 1,
      "especialista.apellido": 1,
      "especialista.especialidades": 1,  // Array embebido
      "cliente.nombre": 1,
      "cliente.apellido": 1,
      "cliente.telefonos": 1,  // Array embebido
      "examen.diagnostico": 1,  // ⭐ Nuevo: datos del examen
      "examen.formula": 1,
      "examen.fecha_examen": 1
    }
  },
  {
    $sort: { fecha_cita: -1 }
  }
]);
```

### Ejemplo 4: Reporte de ventas por producto
```javascript
db.ventas.aggregate([
  {
    $unwind: "$items"  // Descomponer array embebido de items
  },
  {
    $group: {
      _id: "$items.producto_ref",
      nombre_producto: { $first: "$items.nombre" },  // Snapshot embebido
      total_vendido: { $sum: "$items.cantidad" },
      ingresos_totales: { $sum: "$items.total" }
    }
  },
  {
    $lookup: {
      from: "productos",
      localField: "_id",
      foreignField: "_id",
      as: "producto_actual"
    }
  },
  {
    $unwind: "$producto_actual"
  },
  {
    $project: {
      nombre_producto: 1,
      total_vendido: 1,
      ingresos_totales: 1,
      stock_actual: "$producto_actual.stock",
      precio_actual: "$producto_actual.precio_venta"
    }
  },
  {
    $sort: { ingresos_totales: -1 }
  }
]);
```

### Ejemplo 5: Examenes de un cliente con historial de fórmulas
```javascript
db.examenes.aggregate([
  {
    $match: {
      cliente_ref: ObjectId("6901afaa1a3e87e1645cd6f4")
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
    $unwind: "$especialista"
  },
  {
    $project: {
      fecha_examen: 1,
      agudeza_visual_od: 1,
      agudeza_visual_oi: 1,
      "diagnostico.tipo.nombre": 1,  // Subdocumento embebido
      "diagnostico.descripcion": 1,
      "formula.descripcion": 1,       // Subdocumento embebido
      "formula.activa": 1,
      "formula.fecha_vencimiento": 1,
      "especialista.nombre": 1,
      "especialista.apellido": 1
    }
  },
  {
    $sort: { fecha_examen: -1 }
  }
]);
```

## Ejemplo de esquema (pseudo-Mongo)

Venta (documento embeber líneas):
{
  _id: ObjectId,
  cliente_id: ObjectId,        // referencia
  cliente_nombre: String,      // snapshot
  fecha: ISODate,
  total: Number,
  lineas: [
    { producto_id: ObjectId, nombre_producto: String, cantidad: Number, precio_unitario: Number }
  ]
}

Producto (colección independiente):
{
  _id: ObjectId,
  sku: String,
  nombre: String,
  precio_actual: Number,
  categorias: [String]
}

### Ejemplo 6: Órdenes de compra con trazabilidad completa ⭐⭐ Nuevo
```javascript
// Consulta de órdenes con suministros recibidos y estado de inventario
db.ordenes_compra.aggregate([
  {
    $match: {
      estado: { $in: ["Recibido", "Recibido parcial"] }
    }
  },
  {
    $lookup: {
      from: "proveedores",
      localField: "proveedor_ref",
      foreignField: "_id",
      as: "proveedor_actual"
    }
  },
  {
    $unwind: "$proveedor_actual"
  },
  {
    $unwind: "$items"
  },
  {
    $lookup: {
      from: "suministros",
      localField: "items.suministro_ref",
      foreignField: "_id",
      as: "suministro"
    }
  },
  {
    $unwind: { path: "$suministro", preserveNullAndEmptyArrays: true }
  },
  {
    $project: {
      numero_orden: 1,
      fecha_solicitud: 1,
      fecha_entrega_real: 1,
      estado: 1,
      total: 1,
      // Snapshot histórico del proveedor
      "proveedor_snapshot.nombre": 1,
      "proveedor_snapshot.contacto": 1,
      // Datos actuales del proveedor
      "proveedor_actual.nombre_proveedor": 1,
      "proveedor_actual.emails": 1,
      // Detalle del item de la orden
      "items.tipo_suministro.nombre": 1,
      "items.cantidad_solicitada": 1,
      "items.cantidad_recibida": 1,
      "items.precio_unitario": 1,
      "items.total": 1,
      // Suministro recibido vinculado
      "suministro.tipo.nombre": 1,
      "suministro.fecha_recepcion": 1,
      "suministro.fecha_vencimiento": 1,
      "suministro.lote": 1
    }
  },
  {
    $sort: { fecha_solicitud: -1 }
  }
]);

// Consulta de suministros con su orden de compra original
db.suministros.aggregate([
  {
    $match: {
      orden_compra_ref: { $exists: true }
    }
  },
  {
    $lookup: {
      from: "ordenes_compra",
      localField: "orden_compra_ref",
      foreignField: "_id",
      as: "orden"
    }
  },
  {
    $unwind: "$orden"
  },
  {
    $lookup: {
      from: "proveedores",
      localField: "proveedor_ref",
      foreignField: "_id",
      as: "proveedor"
    }
  },
  {
    $unwind: "$proveedor"
  },
  {
    $project: {
      "tipo.nombre": 1,
      "tipo.descripcion": 1,
      fecha_recepcion: 1,
      lote: 1,
      "orden.numero_orden": 1,
      "orden.fecha_solicitud": 1,
      "orden.estado": 1,
      "orden.proveedor_snapshot.nombre": 1,  // Histórico
      "proveedor.nombre_proveedor": 1,       // Actual
      dias_desde_solicitud: {
        $dateDiff: {
          startDate: "$orden.fecha_solicitud",
          endDate: "$fecha_recepcion",
          unit: "day"
        }
      }
    }
  },
  {
    $sort: { fecha_recepcion: -1 }
  }
]);

// Alerta: Órdenes con recepción parcial pendiente
db.ordenes_compra.aggregate([
  {
    $match: {
      estado: "Recibido parcial"
    }
  },
  {
    $unwind: "$items"
  },
  {
    $match: {
      $expr: { $lt: ["$items.cantidad_recibida", "$items.cantidad_solicitada"] }
    }
  },
  {
    $project: {
      numero_orden: 1,
      fecha_solicitud: 1,
      "proveedor_snapshot.nombre": 1,
      "items.tipo_suministro.nombre": 1,
      solicitado: "$items.cantidad_solicitada",
      recibido: "$items.cantidad_recibida",
      pendiente: {
        $subtract: ["$items.cantidad_solicitada", "$items.cantidad_recibida"]
      },
      dias_transcurridos: {
        $dateDiff: {
          startDate: "$fecha_solicitud",
          endDate: "$$NOW",
          unit: "day"
        }
      }
    }
  },
  {
    $sort: { dias_transcurridos: -1 }
  }
]);
```

### Ejemplo 7: Flujo completo de productos personalizados ⭐⭐⭐ Nuevo
```javascript
// Consulta: Examen → Pedido Laboratorio → Producto → Venta (trazabilidad completa)
db.ventas.aggregate([
  {
    $match: {
      examen_ref: { $exists: true },
      estado: "Completada"
    }
  },
  {
    $lookup: {
      from: "examenes",
      localField: "examen_ref",
      foreignField: "_id",
      as: "examen"
    }
  },
  {
    $unwind: "$examen"
  },
  {
    $lookup: {
      from: "pedidos_laboratorio",
      localField: "examen_ref",
      foreignField: "examen_ref",
      as: "pedido_lab"
    }
  },
  {
    $unwind: "$pedido_lab"
  },
  {
    $lookup: {
      from: "productos",
      localField: "pedido_lab.producto_ref",
      foreignField: "_id",
      as: "producto"
    }
  },
  {
    $unwind: "$producto"
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
    $unwind: "$cliente"
  },
  {
    $project: {
      numero_factura: 1,
      fecha_compra: 1,
      total: 1,
      cliente_nombre: { $concat: ["$cliente.nombre", " ", "$cliente.apellido"] },
      // Datos del examen
      examen_fecha: "$examen.fecha_examen",
      diagnostico: "$examen.diagnostico.tipo.nombre",
      // Datos del pedido laboratorio
      pedido_numero: "$pedido_lab.numero_pedido",
      pedido_laboratorio: "$pedido_lab.laboratorio_snapshot.nombre",
      tipo_lente: "$pedido_lab.especificaciones.tipo_lente",
      material: "$pedido_lab.especificaciones.material",
      tratamientos: "$pedido_lab.especificaciones.tratamientos",
      fecha_fabricacion: "$pedido_lab.fecha_solicitud",
      fecha_entrega: "$pedido_lab.fecha_entrega_real",
      dias_fabricacion: {
        $dateDiff: {
          startDate: "$pedido_lab.fecha_solicitud",
          endDate: "$pedido_lab.fecha_entrega_real",
          unit: "day"
        }
      },
      // Datos del producto personalizado
      producto_nombre: "$producto.nombre_producto",
      producto_precio: "$producto.precio_venta"
    }
  },
  {
    $sort: { fecha_compra: -1 }
  }
]);

// Consulta: Examenes con pedidos pendientes o en fabricación
db.examenes.aggregate([
  {
    $match: {
      pedido_laboratorio_ref: { $exists: true }
    }
  },
  {
    $lookup: {
      from: "pedidos_laboratorio",
      localField: "pedido_laboratorio_ref",
      foreignField: "_id",
      as: "pedido"
    }
  },
  {
    $unwind: "$pedido"
  },
  {
    $match: {
      "pedido.estado": { $in: ["Solicitado", "Confirmado", "En fabricación", "Control de calidad"] }
    }
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
    $unwind: "$cliente"
  },
  {
    $lookup: {
      from: "laboratorios",
      localField: "pedido.laboratorio_ref",
      foreignField: "_id",
      as: "laboratorio"
    }
  },
  {
    $unwind: "$laboratorio"
  },
  {
    $project: {
      fecha_examen: 1,
      cliente_nombre: { $concat: ["$cliente.nombre", " ", "$cliente.apellido"] },
      cliente_email: "$cliente.email",
      pedido_numero: "$pedido.numero_pedido",
      pedido_estado: "$pedido.estado",
      laboratorio: "$laboratorio.nombre_laboratorio",
      tipo_lente: "$pedido.especificaciones.tipo_lente",
      fecha_estimada: "$pedido.fecha_estimada_entrega",
      dias_desde_solicitud: {
        $dateDiff: {
          startDate: "$pedido.fecha_solicitud",
          endDate: "$$NOW",
          unit: "day"
        }
      },
      formula_od: "$pedido.formula_snapshot.ojo_derecho",
      formula_oi: "$pedido.formula_snapshot.ojo_izquierdo"
    }
  },
  {
    $sort: { "pedido.fecha_solicitud": 1 }
  }
]);

// Estadísticas de pedidos laboratorio por estado y tiempo promedio
db.pedidos_laboratorio.aggregate([
  {
    $match: {
      fecha_entrega_real: { $exists: true }
    }
  },
  {
    $addFields: {
      dias_fabricacion: {
        $dateDiff: {
          startDate: "$fecha_solicitud",
          endDate: "$fecha_entrega_real",
          unit: "day"
        }
      }
    }
  },
  {
    $group: {
      _id: {
        laboratorio: "$laboratorio_snapshot.nombre",
        tipo_lente: "$especificaciones.tipo_lente"
      },
      total_pedidos: { $sum: 1 },
      dias_promedio: { $avg: "$dias_fabricacion" },
      dias_minimo: { $min: "$dias_fabricacion" },
      dias_maximo: { $max: "$dias_fabricacion" },
      costo_promedio: { $avg: "$costo_fabricacion" },
      precio_venta_promedio: { $avg: "$precio_venta_estimado" }
    }
  },
  {
    $project: {
      laboratorio: "$_id.laboratorio",
      tipo_lente: "$_id.tipo_lente",
      total_pedidos: 1,
      dias_promedio: { $round: ["$dias_promedio", 1] },
      dias_minimo: 1,
      dias_maximo: 1,
      costo_promedio: { $round: ["$costo_promedio", 2] },
      precio_venta_promedio: { $round: ["$precio_venta_promedio", 2] },
      margen_promedio: {
        $round: [
          {
            $multiply: [
              {
                $divide: [
                  { $subtract: ["$precio_venta_promedio", "$costo_promedio"] },
                  "$costo_promedio"
                ]
              },
              100
            ]
          },
          2
        ]
      }
    }
  },
  {
    $sort: { total_pedidos: -1 }
  }
]);
```

## Próximos pasos sugeridos

Basándose en el análisis de las 14 colecciones del proyecto:

### Implementación inmediata (Alto impacto)
1. **Crear índices para referencias** (ver sección "Recomendaciones de mejora #2")
   - Ejecutar script de creación de índices en MongoDB
   - Medir mejora en tiempos de consulta con $lookup
   - Prioridad: ventas, citas, examenes (colecciones más consultadas)

2. **Validar esquemas en producción**
   - Implementar schema validation (sección "Recomendaciones #3")
   - Detectar documentos que no cumplan el esquema esperado
   - Migrar/corregir documentos inconsistentes

3. **Benchmark de consultas comunes**
   - Ejecutar las 5 consultas de ejemplo y medir tiempos
   - Identificar consultas lentas (>100ms)
   - Optimizar con índices o desnormalización adicional

### Mejoras a mediano plazo (Optimización)
4. **Evaluar snapshots en Ventas**
   - Implementar snapshot de cliente/asesor (recomendación #1)
   - Comparar rendimiento: consultas con $lookup vs sin $lookup
   - Decidir si el trade-off (duplicación vs velocidad) vale la pena

5. **Monitoreo de tamaño de documentos**
   - Ejecutar query de detección de documentos grandes (recomendación #6)
   - Establecer alertas para documentos >500KB
   - Planificar estrategia de paginación si alguna colección crece mucho

6. **Sistema de archivado para datos históricos**
   - Definir política de retención (ej: citas >2 años, ventas >5 años)
   - Implementar colecciones de archivo (_archived)
   - Considerar índices TTL para auto-archivado (recomendación #5)

### Scripts disponibles para generar
Puedo crear scripts para:
- ✅ Crear todos los índices recomendados
- ✅ Implementar schema validation para cada colección
- ✅ Script de migración para agregar snapshots en ventas existentes
- ✅ Queries de monitoreo y alertas (stock bajo, fórmulas vencidas, etc.)
- ✅ Benchmark automatizado de las consultas más comunes
- ✅ Script de detección de documentos grandes o inconsistentes

---

**¿Quieres que genere alguno de estos scripts? Indícame cuál y lo creo de inmediato.**
