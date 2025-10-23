-- ============================================================================
-- SCHEMA NORMALIZADO Y FUNCIONAL PARA ÓPTICA 
-- Nivel de Normalización: 3NF (Tercera Forma Normal)
-- ============================================================================

-- Crear y usar la base de datos
CREATE DATABASE IF NOT EXISTS Optica;
USE Optica;

-- Catálogo de especialidades médicas
CREATE TABLE Especialidad (
    id_especialidad INT AUTO_INCREMENT PRIMARY KEY,
    nombre_especialidad VARCHAR(100) UNIQUE NOT NULL,
    descripcion TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Catálogo de motivos de cita
CREATE TABLE Motivo (
    id_motivo INT AUTO_INCREMENT PRIMARY KEY,
    descripcion VARCHAR(100) UNIQUE NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Catálogo de tipos de diagnóstico
CREATE TABLE TipoDiagnostico (
    id_tipo_diagnostico INT AUTO_INCREMENT PRIMARY KEY,
    nombre_diagnostico VARCHAR(100) UNIQUE NOT NULL,
    descripcion TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Catálogo de métodos de pago
CREATE TABLE MetodoPago (
    id_metodo INT AUTO_INCREMENT PRIMARY KEY,
    nombre_metodo VARCHAR(50) UNIQUE NOT NULL,
    activo BOOLEAN DEFAULT TRUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Catálogo de tipos de suministro
CREATE TABLE TipoSuministro (
    id_tipo INT AUTO_INCREMENT PRIMARY KEY,
    nombre_tipo VARCHAR(100) UNIQUE NOT NULL,
    descripcion TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Catálogo de tipos de producto
CREATE TABLE TipoProducto (
    id_tipo INT AUTO_INCREMENT PRIMARY KEY,
    nombre_tipo VARCHAR(100) UNIQUE NOT NULL,
    categoria VARCHAR(50)  -- 'Montura', 'Lente', 'Accesorio', 'Contacto'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- TABLAS DE ENTIDADES PRINCIPALES
-- ============================================================================

-- Tabla de Clientes
CREATE TABLE Cliente (
    id_cliente INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    fecha_nacimiento DATE,
    numero_documento VARCHAR(50) UNIQUE,
    tipo_documento VARCHAR(20),  -- 'CC', 'TI', 'Pasaporte', etc.
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    activo BOOLEAN DEFAULT TRUE,
    INDEX idx_email (email),
    INDEX idx_documento (numero_documento)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Direcciones de clientes (un cliente puede tener múltiples direcciones)
CREATE TABLE DireccionCliente (
    id_direccion INT AUTO_INCREMENT PRIMARY KEY,
    id_cliente INT NOT NULL,
    tipo_direccion VARCHAR(20) DEFAULT 'Principal',  -- 'Principal', 'Trabajo', 'Envío'
    calle VARCHAR(150) NOT NULL,
    ciudad VARCHAR(100) NOT NULL,
    estado VARCHAR(100),
    codigo_postal VARCHAR(20),
    pais VARCHAR(50) NOT NULL DEFAULT 'Colombia',
    es_principal BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (id_cliente) REFERENCES Cliente(id_cliente) ON DELETE CASCADE,
    INDEX idx_cliente (id_cliente)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Teléfonos de clientes
CREATE TABLE TelefonoCliente (
    id_telefono INT AUTO_INCREMENT PRIMARY KEY,
    id_cliente INT NOT NULL,
    telefono VARCHAR(20) NOT NULL,
    tipo_telefono VARCHAR(20) DEFAULT 'Móvil',  -- 'Móvil', 'Fijo', 'Trabajo'
    es_principal BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (id_cliente) REFERENCES Cliente(id_cliente) ON DELETE CASCADE,
    INDEX idx_cliente (id_cliente)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla de Asesores/Vendedores
CREATE TABLE Asesor (
    id_asesor INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    numero_documento VARCHAR(50) UNIQUE NOT NULL,
    fecha_contratacion DATE,
    activo BOOLEAN DEFAULT TRUE,
    INDEX idx_activo (activo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Teléfonos de asesores
CREATE TABLE TelefonoAsesor (
    id_telefono INT AUTO_INCREMENT PRIMARY KEY,
    id_asesor INT NOT NULL,
    telefono VARCHAR(20) NOT NULL,
    tipo_telefono VARCHAR(20) DEFAULT 'Móvil',
    FOREIGN KEY (id_asesor) REFERENCES Asesor(id_asesor) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Emails de asesores
CREATE TABLE EmailAsesor (
    id_email INT AUTO_INCREMENT PRIMARY KEY,
    id_asesor INT NOT NULL,
    email VARCHAR(100) NOT NULL,
    tipo_email VARCHAR(20) DEFAULT 'Corporativo',
    FOREIGN KEY (id_asesor) REFERENCES Asesor(id_asesor) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla de Especialistas (Optómetras, Oftalmólogos)
CREATE TABLE Especialista (
    id_especialista INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    numero_licencia VARCHAR(50) UNIQUE,  -- Licencia profesional
    numero_documento VARCHAR(50) UNIQUE NOT NULL,
    activo BOOLEAN DEFAULT TRUE,
    INDEX idx_activo (activo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Relación muchos a muchos: Especialista - Especialidad
CREATE TABLE EspecialistaEspecialidad (
    id_especialista INT NOT NULL,
    id_especialidad INT NOT NULL,
    fecha_certificacion DATE,
    PRIMARY KEY (id_especialista, id_especialidad),
    FOREIGN KEY (id_especialista) REFERENCES Especialista(id_especialista) ON DELETE CASCADE,
    FOREIGN KEY (id_especialidad) REFERENCES Especialidad(id_especialidad) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Teléfonos de especialistas
CREATE TABLE TelefonoEspecialista (
    id_telefono INT AUTO_INCREMENT PRIMARY KEY,
    id_especialista INT NOT NULL,
    telefono VARCHAR(20) NOT NULL,
    tipo_telefono VARCHAR(20) DEFAULT 'Móvil',
    FOREIGN KEY (id_especialista) REFERENCES Especialista(id_especialista) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Emails de especialistas
CREATE TABLE EmailEspecialista (
    id_email INT AUTO_INCREMENT PRIMARY KEY,
    id_especialista INT NOT NULL,
    email VARCHAR(100) NOT NULL,
    tipo_email VARCHAR(20) DEFAULT 'Profesional',
    FOREIGN KEY (id_especialista) REFERENCES Especialista(id_especialista) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla de Laboratorios
CREATE TABLE Laboratorio (
    id_laboratorio INT AUTO_INCREMENT PRIMARY KEY,
    nombre_laboratorio VARCHAR(100) UNIQUE NOT NULL,
    contacto_principal VARCHAR(100),
    activo BOOLEAN DEFAULT TRUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Direcciones de laboratorios
CREATE TABLE DireccionLaboratorio (
    id_direccion INT AUTO_INCREMENT PRIMARY KEY,
    id_laboratorio INT NOT NULL,
    calle VARCHAR(150) NOT NULL,
    ciudad VARCHAR(100) NOT NULL,
    estado VARCHAR(100),
    codigo_postal VARCHAR(20),
    pais VARCHAR(50) NOT NULL,
    FOREIGN KEY (id_laboratorio) REFERENCES Laboratorio(id_laboratorio) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Teléfonos de laboratorios
CREATE TABLE TelefonoLaboratorio (
    id_telefono INT AUTO_INCREMENT PRIMARY KEY,
    id_laboratorio INT NOT NULL,
    telefono VARCHAR(20) NOT NULL,
    extension VARCHAR(10),
    FOREIGN KEY (id_laboratorio) REFERENCES Laboratorio(id_laboratorio) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla de Proveedores
CREATE TABLE Proveedor (
    id_proveedor INT AUTO_INCREMENT PRIMARY KEY,
    nombre_proveedor VARCHAR(100) UNIQUE NOT NULL,
    contacto_principal VARCHAR(100),
    activo BOOLEAN DEFAULT TRUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Direcciones de proveedores
CREATE TABLE DireccionProveedor (
    id_direccion INT AUTO_INCREMENT PRIMARY KEY,
    id_proveedor INT NOT NULL,
    calle VARCHAR(150) NOT NULL,
    ciudad VARCHAR(100) NOT NULL,
    estado VARCHAR(100),
    codigo_postal VARCHAR(20),
    pais VARCHAR(50) NOT NULL,
    FOREIGN KEY (id_proveedor) REFERENCES Proveedor(id_proveedor) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Teléfonos de proveedores
CREATE TABLE TelefonoProveedor (
    id_telefono INT AUTO_INCREMENT PRIMARY KEY,
    id_proveedor INT NOT NULL,
    telefono VARCHAR(20) NOT NULL,
    extension VARCHAR(10),
    FOREIGN KEY (id_proveedor) REFERENCES Proveedor(id_proveedor) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Emails de proveedores
CREATE TABLE EmailProveedor (
    id_email INT AUTO_INCREMENT PRIMARY KEY,
    id_proveedor INT NOT NULL,
    email VARCHAR(100) NOT NULL,
    tipo_email VARCHAR(20) DEFAULT 'Ventas',
    FOREIGN KEY (id_proveedor) REFERENCES Proveedor(id_proveedor) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- TABLAS DE PROCESOS CLÍNICOS
-- ============================================================================

-- Tabla de Citas
CREATE TABLE Cita (
    id_cita INT AUTO_INCREMENT PRIMARY KEY,
    fecha_cita DATE NOT NULL,
    hora_cita TIME NOT NULL,
    id_motivo INT NOT NULL,
    id_cliente INT NOT NULL,
    id_asesor INT,
    id_especialista INT,
    estado VARCHAR(20) DEFAULT 'Programada',  -- 'Programada', 'Confirmada', 'Completada', 'Cancelada'
    observaciones TEXT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_motivo) REFERENCES Motivo(id_motivo),
    FOREIGN KEY (id_cliente) REFERENCES Cliente(id_cliente),
    FOREIGN KEY (id_asesor) REFERENCES Asesor(id_asesor),
    FOREIGN KEY (id_especialista) REFERENCES Especialista(id_especialista),
    INDEX idx_fecha (fecha_cita),
    INDEX idx_cliente (id_cliente),
    INDEX idx_estado (estado)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla de Exámenes de la Vista
CREATE TABLE ExamenVista (
    id_examen INT AUTO_INCREMENT PRIMARY KEY,
    fecha_examen DATETIME NOT NULL,
    -- Ojo Derecho (OD)
    agudeza_visual_od VARCHAR(20),
    esfera_od DECIMAL(4,2),
    cilindro_od DECIMAL(4,2),
    eje_od INT,
    -- Ojo Izquierdo (OI)
    agudeza_visual_oi VARCHAR(20),
    esfera_oi DECIMAL(4,2),
    cilindro_oi DECIMAL(4,2),
    eje_oi INT,
    -- Adicional
    adicion DECIMAL(4,2),
    distancia_pupilar DECIMAL(4,1),
    presion_intraocular_od DECIMAL(4,1),
    presion_intraocular_oi DECIMAL(4,1),
    observaciones TEXT,
    id_cliente INT NOT NULL,
    id_especialista INT NOT NULL,
    id_cita INT,
    FOREIGN KEY (id_cliente) REFERENCES Cliente(id_cliente),
    FOREIGN KEY (id_especialista) REFERENCES Especialista(id_especialista),
    FOREIGN KEY (id_cita) REFERENCES Cita(id_cita),
    INDEX idx_cliente (id_cliente),
    INDEX idx_fecha (fecha_examen)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla de Diagnósticos
CREATE TABLE Diagnostico (
    id_diagnostico INT AUTO_INCREMENT PRIMARY KEY,
    id_tipo_diagnostico INT NOT NULL,
    descripcion TEXT,
    fecha_diagnostico DATE NOT NULL,
    id_cliente INT NOT NULL,
    id_especialista INT NOT NULL,
    id_examen INT,
    FOREIGN KEY (id_tipo_diagnostico) REFERENCES TipoDiagnostico(id_tipo_diagnostico),
    FOREIGN KEY (id_cliente) REFERENCES Cliente(id_cliente),
    FOREIGN KEY (id_especialista) REFERENCES Especialista(id_especialista),
    FOREIGN KEY (id_examen) REFERENCES ExamenVista(id_examen),
    INDEX idx_cliente (id_cliente),
    INDEX idx_fecha (fecha_diagnostico)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla de Fórmulas Médicas/Prescripciones
CREATE TABLE FormulaMedica (
    id_formula INT AUTO_INCREMENT PRIMARY KEY,
    descripcion_formula TEXT,
    fecha_emision DATE NOT NULL,
    fecha_vencimiento DATE,
    id_especialista INT NOT NULL,
    id_cliente INT NOT NULL,
    id_diagnostico INT,
    activa BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (id_especialista) REFERENCES Especialista(id_especialista),
    FOREIGN KEY (id_cliente) REFERENCES Cliente(id_cliente),
    FOREIGN KEY (id_diagnostico) REFERENCES Diagnostico(id_diagnostico),
    INDEX idx_cliente (id_cliente),
    INDEX idx_activa (activa)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- TABLAS DE INVENTARIO Y PRODUCTOS
-- ============================================================================

-- Tabla de Suministros (Entrada de inventario)
CREATE TABLE Suministro (
    id_suministro INT AUTO_INCREMENT PRIMARY KEY,
    id_tipo INT NOT NULL,
    cantidad INT NOT NULL CHECK (cantidad > 0),
    precio_unitario DECIMAL(10,2) NOT NULL CHECK (precio_unitario >= 0),
    fecha_ingreso DATE NOT NULL,
    numero_lote VARCHAR(50),
    fecha_vencimiento DATE,
    id_laboratorio INT,
    id_proveedor INT NOT NULL,
    observaciones TEXT,
    FOREIGN KEY (id_tipo) REFERENCES TipoSuministro(id_tipo),
    FOREIGN KEY (id_laboratorio) REFERENCES Laboratorio(id_laboratorio),
    FOREIGN KEY (id_proveedor) REFERENCES Proveedor(id_proveedor),
    INDEX idx_fecha (fecha_ingreso),
    INDEX idx_proveedor (id_proveedor)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla de Productos
CREATE TABLE Producto (
    id_producto INT AUTO_INCREMENT PRIMARY KEY,
    nombre_producto VARCHAR(100) NOT NULL,
    id_tipo INT NOT NULL,
    marca VARCHAR(100),  -- Campo simple para marca (sin FK)
    descripcion TEXT,
    precio_venta DECIMAL(10,2) NOT NULL CHECK (precio_venta >= 0),
    stock INT NOT NULL DEFAULT 0 CHECK (stock >= 0),
    stock_minimo INT DEFAULT 5,
    codigo_barras VARCHAR(50) UNIQUE,
    id_suministro INT,
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_tipo) REFERENCES TipoProducto(id_tipo),
    FOREIGN KEY (id_suministro) REFERENCES Suministro(id_suministro),
    INDEX idx_nombre (nombre_producto),
    INDEX idx_tipo (id_tipo),
    INDEX idx_stock (stock),
    INDEX idx_activo (activo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- TABLAS DE VENTAS Y FACTURACIÓN
-- ============================================================================

-- Tabla de Compras/Ventas
CREATE TABLE Compra (
    id_compra INT AUTO_INCREMENT PRIMARY KEY,
    fecha_compra DATETIME DEFAULT CURRENT_TIMESTAMP,
    id_metodo INT NOT NULL,
    id_cliente INT NOT NULL,
    id_asesor INT NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL CHECK (subtotal >= 0),
    descuento DECIMAL(10,2) DEFAULT 0 CHECK (descuento >= 0),
    impuesto DECIMAL(10,2) DEFAULT 0 CHECK (impuesto >= 0),
    total DECIMAL(10,2) NOT NULL CHECK (total >= 0),
    estado VARCHAR(20) DEFAULT 'Completada',  -- 'Pendiente', 'Completada', 'Cancelada', 'Reembolsada'
    observaciones TEXT,
    FOREIGN KEY (id_metodo) REFERENCES MetodoPago(id_metodo),
    FOREIGN KEY (id_cliente) REFERENCES Cliente(id_cliente),
    FOREIGN KEY (id_asesor) REFERENCES Asesor(id_asesor),
    INDEX idx_fecha (fecha_compra),
    INDEX idx_cliente (id_cliente),
    INDEX idx_estado (estado)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla de Detalle de Compra (relación muchos a muchos)
CREATE TABLE DetalleCompra (
    id_detalle INT AUTO_INCREMENT PRIMARY KEY,
    id_compra INT NOT NULL,
    id_producto INT NOT NULL,
    cantidad INT NOT NULL CHECK (cantidad > 0),
    precio_unitario DECIMAL(10,2) NOT NULL CHECK (precio_unitario >= 0),
    subtotal DECIMAL(10,2) NOT NULL CHECK (subtotal >= 0),
    descuento DECIMAL(10,2) DEFAULT 0 CHECK (descuento >= 0),
    total DECIMAL(10,2) NOT NULL CHECK (total >= 0),
    FOREIGN KEY (id_compra) REFERENCES Compra(id_compra) ON DELETE CASCADE,
    FOREIGN KEY (id_producto) REFERENCES Producto(id_producto),
    INDEX idx_compra (id_compra),
    INDEX idx_producto (id_producto)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla de Facturas
CREATE TABLE Factura (
    id_factura INT AUTO_INCREMENT PRIMARY KEY,
    numero_factura VARCHAR(50) UNIQUE NOT NULL,
    fecha_factura DATETIME DEFAULT CURRENT_TIMESTAMP,
    id_compra INT UNIQUE NOT NULL,  -- Una factura por compra
    observaciones TEXT,
    FOREIGN KEY (id_compra) REFERENCES Compra(id_compra),
    INDEX idx_numero (numero_factura),
    INDEX idx_fecha (fecha_factura)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- TABLAS ADICIONALES PARA GESTIÓN COMPLETA
-- ============================================================================

-- Tabla de Devoluciones
CREATE TABLE Devolucion (
    id_devolucion INT AUTO_INCREMENT PRIMARY KEY,
    id_compra INT NOT NULL,
    id_detalle INT NOT NULL,
    fecha_devolucion DATE NOT NULL,
    cantidad_devuelta INT NOT NULL CHECK (cantidad_devuelta > 0),
    motivo TEXT NOT NULL,
    estado VARCHAR(20) DEFAULT 'Pendiente',  -- 'Pendiente', 'Aprobada', 'Rechazada', 'Reembolsada'
    monto_reembolso DECIMAL(10,2) DEFAULT 0,
    id_asesor INT,
    FOREIGN KEY (id_compra) REFERENCES Compra(id_compra),
    FOREIGN KEY (id_detalle) REFERENCES DetalleCompra(id_detalle),
    FOREIGN KEY (id_asesor) REFERENCES Asesor(id_asesor),
    INDEX idx_compra (id_compra),
    INDEX idx_fecha (fecha_devolucion),
    INDEX idx_estado (estado)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- VISTAS ÚTILES PARA CONSULTAS COMUNES
-- ============================================================================

-- Vista de inventario bajo stock
CREATE VIEW VistaStockBajo AS
SELECT 
    p.id_producto,
    p.nombre_producto,
    tp.nombre_tipo,
    p.marca,
    p.stock,
    p.stock_minimo,
    (p.stock_minimo - p.stock) AS unidades_faltantes
FROM Producto p
JOIN TipoProducto tp ON p.id_tipo = tp.id_tipo
WHERE p.stock <= p.stock_minimo AND p.activo = TRUE;

-- Vista de ventas del día
CREATE VIEW VistaVentasHoy AS
SELECT 
    c.id_compra,
    c.fecha_compra,
    CONCAT(cl.nombre, ' ', cl.apellido) AS cliente,
    CONCAT(a.nombre, ' ', a.apellido) AS asesor,
    c.total,
    c.estado
FROM Compra c
JOIN Cliente cl ON c.id_cliente = cl.id_cliente
JOIN Asesor a ON c.id_asesor = a.id_asesor
WHERE DATE(c.fecha_compra) = CURDATE();

-- Vista de citas pendientes
CREATE VIEW VistaCitasPendientes AS
SELECT 
    ci.id_cita,
    ci.fecha_cita,
    ci.hora_cita,
    CONCAT(cl.nombre, ' ', cl.apellido) AS cliente,
    m.descripcion AS motivo,
    CONCAT(e.nombre, ' ', e.apellido) AS especialista,
    ci.estado
FROM Cita ci
JOIN Cliente cl ON ci.id_cliente = cl.id_cliente
JOIN Motivo m ON ci.id_motivo = m.id_motivo
LEFT JOIN Especialista e ON ci.id_especialista = e.id_especialista
WHERE ci.estado IN ('Programada', 'Confirmada') AND ci.fecha_cita >= CURDATE()
ORDER BY ci.fecha_cita, ci.hora_cita;

-- ============================================================================
-- DATOS DE PRUEBA (INSERTS)
-- ============================================================================

-- Catálogos
INSERT INTO Especialidad (nombre_especialidad, descripcion) VALUES 
    ('Optometría', 'Especialidad en salud visual y prescripción de lentes'),
    ('Oftalmología', 'Especialidad médica para enfermedades oculares'),
    ('Contactología', 'Especialidad en lentes de contacto');

INSERT INTO Motivo (descripcion) VALUES 
    ('Examen visual de rutina'),
    ('Revisión de lentes'),
    ('Ajuste de monturas'),
    ('Consulta por molestias visuales'),
    ('Control post-compra');

INSERT INTO TipoDiagnostico (nombre_diagnostico, descripcion) VALUES 
    ('Miopía', 'Dificultad para ver objetos lejanos'),
    ('Hipermetropía', 'Dificultad para ver objetos cercanos'),
    ('Astigmatismo', 'Visión distorsionada o borrosa'),
    ('Presbicia', 'Dificultad para enfocar objetos cercanos por edad');

INSERT INTO MetodoPago (nombre_metodo) VALUES 
    ('Efectivo'),
    ('Tarjeta de Crédito'),
    ('Tarjeta de Débito'),
    ('Transferencia Bancaria'),
    ('PSE');

INSERT INTO TipoSuministro (nombre_tipo, descripcion) VALUES 
    ('Lentes oftálmicos', 'Cristales para gafas formuladas'),
    ('Lentes de contacto', 'Lentes de contacto blandos y rígidos'),
    ('Monturas', 'Armazones para lentes'),
    ('Accesorios', 'Estuches, paños, líquidos de limpieza');

INSERT INTO TipoProducto (nombre_tipo, categoria) VALUES 
    ('Gafas formuladas', 'Lente'),
    ('Gafas de sol', 'Accesorio'),
    ('Lentes de contacto', 'Contacto'),
    ('Monturas oftálmicas', 'Montura'),
    ('Estuches', 'Accesorio'),
    ('Líquidos de limpieza', 'Accesorio');

-- Clientes
INSERT INTO Cliente (nombre, apellido, email, fecha_nacimiento, numero_documento, tipo_documento) VALUES 
    ('Ana', 'Pérez', 'ana.perez@mail.com', '1990-05-15', '1234567890', 'CC'),
    ('Carlos', 'Gómez', 'carlos.gomez@mail.com', '1985-08-20', '9876543210', 'CC'),
    ('María', 'Rodríguez', 'maria.rodriguez@mail.com', '1995-03-10', '5555555555', 'CC');

INSERT INTO DireccionCliente (id_cliente, tipo_direccion, calle, ciudad, estado, codigo_postal, pais, es_principal) VALUES 
    (1, 'Principal', 'Calle 123 #45-67', 'Bogotá', 'Cundinamarca', '110111', 'Colombia', TRUE),
    (2, 'Principal', 'Carrera 50 #30-20', 'Medellín', 'Antioquia', '050001', 'Colombia', TRUE),
    (3, 'Principal', 'Avenida 6 #15-30', 'Cali', 'Valle del Cauca', '760001', 'Colombia', TRUE);

INSERT INTO TelefonoCliente (id_cliente, telefono, tipo_telefono, es_principal) VALUES 
    (1, '3101234567', 'Móvil', TRUE),
    (2, '3209876543', 'Móvil', TRUE),
    (3, '3155555555', 'Móvil', TRUE);

-- Asesores
INSERT INTO Asesor (nombre, apellido, numero_documento, fecha_contratacion) VALUES 
    ('Carlos', 'Ruiz', '1122334455', '2023-01-15'),
    ('Laura', 'Martínez', '5544332211', '2023-06-01');

INSERT INTO TelefonoAsesor (id_asesor, telefono) VALUES 
    (1, '3001234567'),
    (2, '3009876543');

INSERT INTO EmailAsesor (id_asesor, email) VALUES 
    (1, 'carlos.ruiz@optica.com'),
    (2, 'laura.martinez@optica.com');

-- Especialistas
INSERT INTO Especialista (nombre, apellido, numero_licencia, numero_documento) VALUES 
    ('Juan', 'López', 'OPT-12345', '7788990011'),
    ('Diana', 'Vargas', 'OFT-54321', '1122998877');

INSERT INTO EspecialistaEspecialidad (id_especialista, id_especialidad, fecha_certificacion) VALUES 
    (1, 1, '2015-06-01'),  -- Dr. López - Optometría
    (2, 2, '2010-03-15');  -- Dra. Vargas - Oftalmología

INSERT INTO TelefonoEspecialista (id_especialista, telefono) VALUES 
    (1, '3208887766'),
    (2, '3156667788');

INSERT INTO EmailEspecialista (id_especialista, email) VALUES 
    (1, 'dr.lopez@optica.com'),
    (2, 'dra.vargas@optica.com');

-- Proveedores y Laboratorios
INSERT INTO Laboratorio (nombre_laboratorio, contacto_principal) VALUES 
    ('LabVisión Colombia', 'Roberto Sánchez');

INSERT INTO DireccionLaboratorio (id_laboratorio, calle, ciudad, estado, codigo_postal, pais) VALUES 
    (1, 'Carrera 45 #12-34', 'Bogotá', 'Cundinamarca', '110111', 'Colombia');

INSERT INTO TelefonoLaboratorio (id_laboratorio, telefono, extension) VALUES 
    (1, '6011234567', '101');

INSERT INTO Proveedor (nombre_proveedor, contacto_principal) VALUES 
    ('LentesPro Internacional', 'Sandra Morales'),
    ('Monturas Premium', 'Diego Castro');

INSERT INTO DireccionProveedor (id_proveedor, calle, ciudad, estado, codigo_postal, pais) VALUES 
    (1, 'Avenida 9 #45-67', 'Bogotá', 'Cundinamarca', '110111', 'Colombia'),
    (2, 'Calle 72 #10-15', 'Bogotá', 'Cundinamarca', '110221', 'Colombia');

INSERT INTO TelefonoProveedor (id_proveedor, telefono) VALUES 
    (1, '3211234567'),
    (2, '3189876543');

INSERT INTO EmailProveedor (id_proveedor, email, tipo_email) VALUES 
    (1, 'ventas@lentespro.com', 'Ventas'),
    (2, 'contacto@monturaspremium.com', 'Ventas');

-- Suministros y Productos
INSERT INTO Suministro (id_tipo, cantidad, precio_unitario, fecha_ingreso, numero_lote, id_laboratorio, id_proveedor) VALUES 
    (1, 100, 50000, '2025-10-01', 'LOTE-2025-001', 1, 1),
    (2, 50, 80000, '2025-10-05', 'LOTE-2025-002', NULL, 1),
    (3, 30, 120000, '2025-10-10', 'LOTE-2025-003', NULL, 2);

INSERT INTO Producto (nombre_producto, id_tipo, marca, descripcion, precio_venta, stock, stock_minimo, codigo_barras, id_suministro) VALUES 
    ('Lente Esférico -1.00', 1, 'Transitions', 'Lente oftálmico esférico con graduación -1.00', 150000, 50, 10, '7890123456001', 1),
    ('Lente de Contacto Mensual', 3, 'Acuvue', 'Lente de contacto blando de uso mensual', 120000, 25, 5, '7890123456002', 2),
    ('Montura Ray-Ban Aviador', 4, 'Ray-Ban', 'Montura metálica estilo aviador', 350000, 15, 3, '7890123456003', 3),
    ('Gafas de Sol Oakley', 2, 'Oakley', 'Gafas de sol deportivas con protección UV', 450000, 10, 2, '7890123456004', NULL);

-- Citas
INSERT INTO Cita (fecha_cita, hora_cita, id_motivo, id_cliente, id_asesor, id_especialista, estado) VALUES 
    ('2025-10-25', '10:00:00', 1, 1, 1, 1, 'Programada'),
    ('2025-10-26', '14:00:00', 4, 2, 2, 2, 'Confirmada');

-- Exámenes
INSERT INTO ExamenVista (fecha_examen, agudeza_visual_od, agudeza_visual_oi, esfera_od, esfera_oi, cilindro_od, cilindro_oi, eje_od, eje_oi, distancia_pupilar, observaciones, id_cliente, id_especialista, id_cita) VALUES 
    ('2025-10-20 10:30:00', '20/30', '20/40', -1.00, -1.25, -0.50, -0.75, 90, 85, 63.0, 'Visión ligeramente reducida, se recomienda corrección', 1, 1, NULL);

-- Diagnósticos
INSERT INTO Diagnostico (id_tipo_diagnostico, descripcion, fecha_diagnostico, id_cliente, id_especialista, id_examen) VALUES 
    (1, 'Miopía leve bilateral con componente astigmático', '2025-10-20', 1, 1, 1);

-- Fórmula Médica
INSERT INTO FormulaMedica (descripcion_formula, fecha_emision, fecha_vencimiento, id_especialista, id_cliente, id_diagnostico) VALUES 
    ('OD: -1.00 -0.50 x 90, OI: -1.25 -0.75 x 85, ADD: +0.00, DP: 63mm', '2025-10-20', '2026-10-20', 1, 1, 1);

-- Compras
INSERT INTO Compra (fecha_compra, id_metodo, id_cliente, id_asesor, subtotal, descuento, impuesto, total, estado) VALUES 
    ('2025-10-21 11:00:00', 2, 1, 1, 300000, 0, 57000, 357000, 'Completada'),
    ('2025-10-22 15:30:00', 1, 2, 2, 450000, 45000, 76950, 481950, 'Completada');

INSERT INTO DetalleCompra (id_compra, id_producto, cantidad, precio_unitario, subtotal, descuento, total) VALUES 
    (1, 1, 2, 150000, 300000, 0, 300000),
    (2, 4, 1, 450000, 450000, 45000, 405000);

-- Facturas
INSERT INTO Factura (numero_factura, fecha_factura, id_compra) VALUES 
    ('F-2025-001', '2025-10-21 11:05:00', 1),
    ('F-2025-002', '2025-10-22 15:35:00', 2);

-- ============================================================================
-- FIN DEL SCRIPT
-- ============================================================================
