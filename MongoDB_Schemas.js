// ============================================================================
// SCHEMAS DE VALIDACIÓN PARA MONGODB ATLAS
// Base de Datos: Optica
// Fecha: Octubre 23, 2025
// ============================================================================

// Usar la base de datos
use Optica;

// ============================================================================
// 1. COLECCIÓN: clientes
// ============================================================================
db.createCollection("clientes", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["nombre", "apellido", "email", "activo"],
      properties: {
        nombre: {
          bsonType: "string",
          description: "Nombre del cliente - requerido"
        },
        apellido: {
          bsonType: "string",
          description: "Apellido del cliente - requerido"
        },
        email: {
          bsonType: "string",
          pattern: "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$",
          description: "Email único del cliente - requerido"
        },
        fecha_nacimiento: {
          bsonType: "date",
          description: "Fecha de nacimiento"
        },
        documento: {
          bsonType: "object",
          required: ["tipo", "numero"],
          properties: {
            tipo: {
              enum: ["CC", "TI", "CE", "Pasaporte"],
              description: "Tipo de documento"
            },
            numero: {
              bsonType: "string",
              description: "Número de documento único"
            }
          }
        },
        direcciones: {
          bsonType: "array",
          items: {
            bsonType: "object",
            required: ["calle", "ciudad", "pais"],
            properties: {
              tipo: {
                enum: ["Principal", "Trabajo", "Envío"],
                description: "Tipo de dirección"
              },
              calle: { bsonType: "string" },
              ciudad: { bsonType: "string" },
              estado: { bsonType: "string" },
              codigo_postal: { bsonType: "string" },
              pais: { bsonType: "string" },
              es_principal: { bsonType: "bool" }
            }
          }
        },
        telefonos: {
          bsonType: "array",
          items: {
            bsonType: "object",
            required: ["numero"],
            properties: {
              numero: { bsonType: "string" },
              tipo: {
                enum: ["Móvil", "Fijo", "Trabajo"],
                description: "Tipo de teléfono"
              },
              es_principal: { bsonType: "bool" }
            }
          }
        },
        activo: {
          bsonType: "bool",
          description: "Estado activo/inactivo del cliente"
        },
        fecha_registro: {
          bsonType: "date",
          description: "Fecha de registro del cliente"
        }
      }
    }
  }
});

// Índices para clientes
db.clientes.createIndex({ email: 1 }, { unique: true });
db.clientes.createIndex({ "documento.numero": 1 }, { unique: true, sparse: true });
db.clientes.createIndex({ apellido: 1, nombre: 1 });
db.clientes.createIndex({ activo: 1 });

// ============================================================================
// 2. COLECCIÓN: asesores
// ============================================================================
db.createCollection("asesores", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["nombre", "apellido", "numero_documento", "activo"],
      properties: {
        nombre: { bsonType: "string" },
        apellido: { bsonType: "string" },
        numero_documento: {
          bsonType: "string",
          description: "Número de documento único"
        },
        fecha_contratacion: { bsonType: "date" },
        telefonos: {
          bsonType: "array",
          items: {
            bsonType: "object",
            required: ["numero"],
            properties: {
              numero: { bsonType: "string" },
              tipo: { enum: ["Móvil", "Fijo", "Trabajo"] }
            }
          }
        },
        emails: {
          bsonType: "array",
          items: {
            bsonType: "object",
            required: ["email"],
            properties: {
              email: { bsonType: "string" },
              tipo: { enum: ["Corporativo", "Personal"] }
            }
          }
        },
        activo: { bsonType: "bool" }
      }
    }
  }
});

// Índices para asesores
db.asesores.createIndex({ numero_documento: 1 }, { unique: true });
db.asesores.createIndex({ activo: 1 });

// ============================================================================
// 3. COLECCIÓN: especialistas
// ============================================================================
db.createCollection("especialistas", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["nombre", "apellido", "numero_documento", "activo"],
      properties: {
        nombre: { bsonType: "string" },
        apellido: { bsonType: "string" },
        numero_licencia: {
          bsonType: "string",
          description: "Licencia profesional única"
        },
        numero_documento: {
          bsonType: "string",
          description: "Número de documento único"
        },
        especialidades: {
          bsonType: "array",
          items: {
            bsonType: "object",
            required: ["nombre"],
            properties: {
              nombre: { bsonType: "string" },
              descripcion: { bsonType: "string" },
              fecha_certificacion: { bsonType: "date" }
            }
          }
        },
        telefonos: {
          bsonType: "array",
          items: {
            bsonType: "object",
            required: ["numero"],
            properties: {
              numero: { bsonType: "string" },
              tipo: { enum: ["Móvil", "Fijo", "Trabajo"] }
            }
          }
        },
        emails: {
          bsonType: "array",
          items: {
            bsonType: "object",
            required: ["email"],
            properties: {
              email: { bsonType: "string" },
              tipo: { enum: ["Profesional", "Personal"] }
            }
          }
        },
        activo: { bsonType: "bool" }
      }
    }
  }
});

// Índices para especialistas
db.especialistas.createIndex({ numero_licencia: 1 }, { unique: true, sparse: true });
db.especialistas.createIndex({ numero_documento: 1 }, { unique: true });
db.especialistas.createIndex({ activo: 1 });

// ============================================================================
// 4. COLECCIÓN: productos
// ============================================================================
db.createCollection("productos", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["nombre", "tipo", "precio_venta", "stock", "activo"],
      properties: {
        nombre: {
          bsonType: "string",
          description: "Nombre del producto"
        },
        codigo_barras: {
          bsonType: "string",
          description: "Código de barras único"
        },
        tipo: {
          bsonType: "object",
          required: ["nombre"],
          properties: {
            nombre: { bsonType: "string" },
            categoria: {
              enum: ["Montura", "Lente", "Accesorio", "Contacto"]
            }
          }
        },
        marca: { bsonType: "string" },
        descripcion: { bsonType: "string" },
        precio_venta: {
          bsonType: "double",
          minimum: 0,
          description: "Precio de venta mayor o igual a 0"
        },
        stock: {
          bsonType: "object",
          required: ["actual", "minimo"],
          properties: {
            actual: {
              bsonType: "int",
              minimum: 0
            },
            minimo: {
              bsonType: "int",
              minimum: 0
            }
          }
        },
        suministro_ref: {
          bsonType: "objectId",
          description: "Referencia al suministro origen"
        },
        activo: { bsonType: "bool" },
        fecha_creacion: { bsonType: "date" }
      }
    }
  }
});

// Índices para productos
db.productos.createIndex({ codigo_barras: 1 }, { unique: true, sparse: true });
db.productos.createIndex({ nombre: 1 });
db.productos.createIndex({ "tipo.categoria": 1 });
db.productos.createIndex({ "stock.actual": 1 });
db.productos.createIndex({ activo: 1 });

// ============================================================================
// 5. COLECCIÓN: citas
// ============================================================================
db.createCollection("citas", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["fecha_cita", "hora_cita", "motivo", "cliente_ref", "estado"],
      properties: {
        fecha_cita: { bsonType: "date" },
        hora_cita: { bsonType: "string" },
        motivo: {
          bsonType: "object",
          required: ["descripcion"],
          properties: {
            descripcion: { bsonType: "string" }
          }
        },
        cliente_ref: {
          bsonType: "objectId",
          description: "Referencia al cliente"
        },
        asesor_ref: {
          bsonType: "objectId",
          description: "Referencia al asesor (opcional)"
        },
        especialista_ref: {
          bsonType: "objectId",
          description: "Referencia al especialista (opcional)"
        },
        estado: {
          enum: ["Programada", "Confirmada", "Completada", "Cancelada"],
          description: "Estado de la cita"
        },
        observaciones: { bsonType: "string" },
        fecha_creacion: { bsonType: "date" }
      }
    }
  }
});

// Índices para citas
db.citas.createIndex({ fecha_cita: 1, hora_cita: 1 });
db.citas.createIndex({ cliente_ref: 1 });
db.citas.createIndex({ especialista_ref: 1 });
db.citas.createIndex({ estado: 1 });

// ============================================================================
// 6. COLECCIÓN: examenes
// ============================================================================
db.createCollection("examenes", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["fecha_examen", "cliente_ref", "especialista_ref", "examen"],
      properties: {
        fecha_examen: { bsonType: "date" },
        cliente_ref: { bsonType: "objectId" },
        especialista_ref: { bsonType: "objectId" },
        cita_ref: {
          bsonType: "objectId",
          description: "Referencia a la cita (opcional)"
        },
        examen: {
          bsonType: "object",
          properties: {
            ojo_derecho: {
              bsonType: "object",
              properties: {
                agudeza_visual: { bsonType: "string" },
                esfera: { bsonType: "double" },
                cilindro: { bsonType: "double" },
                eje: { bsonType: "int" },
                presion_intraocular: { bsonType: "double" }
              }
            },
            ojo_izquierdo: {
              bsonType: "object",
              properties: {
                agudeza_visual: { bsonType: "string" },
                esfera: { bsonType: "double" },
                cilindro: { bsonType: "double" },
                eje: { bsonType: "int" },
                presion_intraocular: { bsonType: "double" }
              }
            },
            adicion: { bsonType: "double" },
            distancia_pupilar: { bsonType: "double" },
            observaciones: { bsonType: "string" }
          }
        },
        diagnostico: {
          bsonType: "object",
          properties: {
            tipo: {
              bsonType: "object",
              properties: {
                nombre: { bsonType: "string" },
                descripcion: { bsonType: "string" }
              }
            },
            descripcion: { bsonType: "string" },
            fecha: { bsonType: "date" }
          }
        },
        formula: {
          bsonType: "object",
          properties: {
            descripcion: { bsonType: "string" },
            fecha_emision: { bsonType: "date" },
            fecha_vencimiento: { bsonType: "date" },
            activa: { bsonType: "bool" }
          }
        }
      }
    }
  }
});

// Índices para examenes
db.examenes.createIndex({ cliente_ref: 1, fecha_examen: -1 });
db.examenes.createIndex({ especialista_ref: 1 });
db.examenes.createIndex({ "formula.activa": 1 });

// ============================================================================
// 7. COLECCIÓN: ventas
// ============================================================================
db.createCollection("ventas", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["fecha_compra", "cliente_ref", "asesor_ref", "metodo_pago", "items", "total", "estado"],
      properties: {
        numero_factura: {
          bsonType: "string",
          description: "Número de factura único"
        },
        fecha_compra: { bsonType: "date" },
        cliente_ref: {
          bsonType: "objectId",
          description: "Referencia al cliente"
        },
        asesor_ref: {
          bsonType: "objectId",
          description: "Referencia al asesor"
        },
        metodo_pago: {
          bsonType: "object",
          required: ["nombre"],
          properties: {
            nombre: { bsonType: "string" },
            activo: { bsonType: "bool" }
          }
        },
        items: {
          bsonType: "array",
          minItems: 1,
          items: {
            bsonType: "object",
            required: ["producto_ref", "cantidad", "precio_unitario", "total"],
            properties: {
              producto_ref: {
                bsonType: "objectId",
                description: "Referencia al producto"
              },
              producto_info: {
                bsonType: "object",
                properties: {
                  nombre: { bsonType: "string" },
                  codigo_barras: { bsonType: "string" }
                }
              },
              cantidad: {
                bsonType: "int",
                minimum: 1
              },
              precio_unitario: {
                bsonType: "double",
                minimum: 0
              },
              subtotal: {
                bsonType: "double",
                minimum: 0
              },
              descuento: {
                bsonType: "double",
                minimum: 0
              },
              total: {
                bsonType: "double",
                minimum: 0
              }
            }
          }
        },
        subtotal: {
          bsonType: "double",
          minimum: 0
        },
        descuento: {
          bsonType: "double",
          minimum: 0
        },
        impuesto: {
          bsonType: "double",
          minimum: 0
        },
        total: {
          bsonType: "double",
          minimum: 0
        },
        estado: {
          enum: ["Pendiente", "Completada", "Cancelada", "Reembolsada"]
        },
        observaciones: { bsonType: "string" }
      }
    }
  }
});

// Índices para ventas
db.ventas.createIndex({ numero_factura: 1 }, { unique: true, sparse: true });
db.ventas.createIndex({ fecha_compra: -1 });
db.ventas.createIndex({ cliente_ref: 1 });
db.ventas.createIndex({ asesor_ref: 1 });
db.ventas.createIndex({ estado: 1 });

// ============================================================================
// 8. COLECCIÓN: catalogos (Documento único)
// ============================================================================
db.createCollection("catalogos", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["_id"],
      properties: {
        _id: {
          enum: ["catalogos_optica"],
          description: "ID fijo para el documento de catálogos"
        },
        especialidades: {
          bsonType: "array",
          items: {
            bsonType: "object",
            required: ["nombre"],
            properties: {
              nombre: { bsonType: "string" },
              descripcion: { bsonType: "string" }
            }
          }
        },
        motivos: {
          bsonType: "array",
          items: {
            bsonType: "object",
            required: ["descripcion"],
            properties: {
              descripcion: { bsonType: "string" }
            }
          }
        },
        tipos_diagnostico: {
          bsonType: "array",
          items: {
            bsonType: "object",
            required: ["nombre"],
            properties: {
              nombre: { bsonType: "string" },
              descripcion: { bsonType: "string" }
            }
          }
        },
        metodos_pago: {
          bsonType: "array",
          items: {
            bsonType: "object",
            required: ["nombre"],
            properties: {
              nombre: { bsonType: "string" },
              activo: { bsonType: "bool" }
            }
          }
        },
        tipos_suministro: {
          bsonType: "array",
          items: {
            bsonType: "object",
            required: ["nombre"],
            properties: {
              nombre: { bsonType: "string" },
              descripcion: { bsonType: "string" }
            }
          }
        },
        tipos_producto: {
          bsonType: "array",
          items: {
            bsonType: "object",
            required: ["nombre"],
            properties: {
              nombre: { bsonType: "string" },
              categoria: {
                enum: ["Montura", "Lente", "Accesorio", "Contacto"]
              }
            }
          }
        }
      }
    }
  }
});

// ============================================================================
// 9. COLECCIÓN: proveedores
// ============================================================================
db.createCollection("proveedores", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["nombre", "activo"],
      properties: {
        nombre: {
          bsonType: "string",
          description: "Nombre del proveedor"
        },
        contacto_principal: { bsonType: "string" },
        direcciones: {
          bsonType: "array",
          items: {
            bsonType: "object",
            required: ["calle", "ciudad", "pais"],
            properties: {
              calle: { bsonType: "string" },
              ciudad: { bsonType: "string" },
              estado: { bsonType: "string" },
              codigo_postal: { bsonType: "string" },
              pais: { bsonType: "string" }
            }
          }
        },
        telefonos: {
          bsonType: "array",
          items: {
            bsonType: "object",
            required: ["numero"],
            properties: {
              numero: { bsonType: "string" },
              extension: { bsonType: "string" }
            }
          }
        },
        emails: {
          bsonType: "array",
          items: {
            bsonType: "object",
            required: ["email"],
            properties: {
              email: { bsonType: "string" },
              tipo: { enum: ["Ventas", "Soporte", "General"] }
            }
          }
        },
        activo: { bsonType: "bool" }
      }
    }
  }
});

// Índices para proveedores
db.proveedores.createIndex({ nombre: 1 }, { unique: true });
db.proveedores.createIndex({ activo: 1 });

// ============================================================================
// 10. COLECCIÓN: laboratorios
// ============================================================================
db.createCollection("laboratorios", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["nombre", "activo"],
      properties: {
        nombre: {
          bsonType: "string",
          description: "Nombre del laboratorio"
        },
        contacto_principal: { bsonType: "string" },
        direcciones: {
          bsonType: "array",
          items: {
            bsonType: "object",
            required: ["calle", "ciudad", "pais"],
            properties: {
              calle: { bsonType: "string" },
              ciudad: { bsonType: "string" },
              estado: { bsonType: "string" },
              codigo_postal: { bsonType: "string" },
              pais: { bsonType: "string" }
            }
          }
        },
        telefonos: {
          bsonType: "array",
          items: {
            bsonType: "object",
            required: ["numero"],
            properties: {
              numero: { bsonType: "string" },
              extension: { bsonType: "string" }
            }
          }
        },
        activo: { bsonType: "bool" }
      }
    }
  }
});

// Índices para laboratorios
db.laboratorios.createIndex({ nombre: 1 }, { unique: true });
db.laboratorios.createIndex({ activo: 1 });

// ============================================================================
// 11. COLECCIÓN: suministros
// ============================================================================
db.createCollection("suministros", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["tipo", "cantidad", "precio_unitario", "fecha_ingreso", "proveedor_ref"],
      properties: {
        tipo: {
          bsonType: "object",
          required: ["nombre"],
          properties: {
            nombre: { bsonType: "string" },
            descripcion: { bsonType: "string" }
          }
        },
        cantidad: {
          bsonType: "int",
          minimum: 1
        },
        precio_unitario: {
          bsonType: "double",
          minimum: 0
        },
        fecha_ingreso: { bsonType: "date" },
        numero_lote: { bsonType: "string" },
        fecha_vencimiento: { bsonType: "date" },
        proveedor_ref: {
          bsonType: "objectId",
          description: "Referencia al proveedor"
        },
        laboratorio_ref: {
          bsonType: "objectId",
          description: "Referencia al laboratorio (opcional)"
        },
        observaciones: { bsonType: "string" }
      }
    }
  }
});

// Índices para suministros
db.suministros.createIndex({ fecha_ingreso: -1 });
db.suministros.createIndex({ proveedor_ref: 1 });
db.suministros.createIndex({ laboratorio_ref: 1 });
db.suministros.createIndex({ numero_lote: 1 });

// ============================================================================
// 12. COLECCIÓN: devoluciones
// ============================================================================
db.createCollection("devoluciones", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["venta_ref", "fecha_devolucion", "cantidad_devuelta", "motivo", "estado"],
      properties: {
        venta_ref: {
          bsonType: "objectId",
          description: "Referencia a la venta"
        },
        item_index: {
          bsonType: "int",
          description: "Índice del item en el array de items de la venta"
        },
        fecha_devolucion: { bsonType: "date" },
        cantidad_devuelta: {
          bsonType: "int",
          minimum: 1
        },
        motivo: {
          bsonType: "string",
          minLength: 10
        },
        estado: {
          enum: ["Pendiente", "Aprobada", "Rechazada", "Reembolsada"]
        },
        monto_reembolso: {
          bsonType: "double",
          minimum: 0
        },
        asesor_ref: {
          bsonType: "objectId",
          description: "Referencia al asesor que gestiona la devolución"
        }
      }
    }
  }
});

// Índices para devoluciones
db.devoluciones.createIndex({ venta_ref: 1 });
db.devoluciones.createIndex({ fecha_devolucion: -1 });
db.devoluciones.createIndex({ estado: 1 });

// ============================================================================
// FIN DE SCHEMAS
// ============================================================================

print("✅ Schemas de validación creados exitosamente");
print("📊 Total de colecciones: 12");
print("🔒 Validaciones JSON Schema aplicadas");
print("📑 Índices creados para optimizar consultas");
