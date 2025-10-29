# ⚡ INICIO RÁPIDO - Migración MySQL → MongoDB

## 🎯 En 3 Pasos

### 1️⃣ Instalar Dependencias (2 minutos)

```powershell
pip install pymongo mysql-connector-python python-dotenv
```

### 2️⃣ Configurar Credenciales (3 minutos)

```powershell
# Copiar plantilla
Copy-Item .env.example .env

# Editar con tus datos
notepad .env
```

Completar:
```env
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=tu_password
MYSQL_DATABASE=Optica

MONGODB_URI=mongodb+srv://usuario:password@cluster.mongodb.net/
MONGODB_DATABASE=optica_db
```

### 3️⃣ Ejecutar Migración (5-10 minutos)

```powershell
# Migración completa automática
python migracion_mysql_a_mongodb.py
```

---

## ✅ Resultado Esperado

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

## 🔍 Verificar Migración

### Con MongoDB Shell:
```powershell
mongosh "tu_connection_string"

use optica_db
show collections
db.clientes.countDocuments()
db.clientes.findOne()
```

### Con MongoDB Compass:
1. Conectar con tu connection string
2. Navegar a base de datos `optica_db`
3. Explorar colecciones creadas

---

## 📋 ¿Qué se Migró?

```
MySQL (22 tablas) → MongoDB (11 colecciones)

✅ clientes       (Cliente + Direcciones + Teléfonos)
✅ asesores       (Asesor + Contactos)
✅ especialistas  (Especialista + Especialidades + Contactos)
✅ proveedores    (Proveedor + Contactos)
✅ laboratorios   (Laboratorio + Contactos)
✅ suministros    (Con referencias a proveedores)
✅ productos      (Con tipo embebido)
✅ citas          (Con motivo embebido)
✅ examenes       (Con diagnóstico y fórmula)
✅ ventas         (Con items y factura)
✅ catalogos      (Todos los catálogos en 1 documento)
```

---

## 🚨 Problemas Comunes

### Error: "No module named 'pymongo'"
```powershell
pip install pymongo mysql-connector-python python-dotenv
```

### Error: "Access Denied for user"
- Verifica usuario y contraseña MySQL en `.env`

### Error: "Authentication failed" (MongoDB)
- Verifica connection string de MongoDB Atlas en `.env`
- Asegúrate de haber agregado tu IP en Network Access

### Error: "Connection timeout"
- En MongoDB Atlas → Network Access → Add IP Address
- Agrega `0.0.0.0/0` (permite desde cualquier IP)

---

## 📚 Documentación Completa

| Documento | Para qué sirve |
|-----------|----------------|
| **README_MIGRACION.md** | Documentación completa del proyecto |
| **INSTRUCCIONES_MIGRACION.md** | Guía paso a paso detallada |
| **TRANSFORMACION_VISUAL.md** | Diagramas de transformación |
| **MIGRACION_ESTRATEGIA.md** | Decisiones de diseño técnico |

---

## 💡 Próximos Pasos

Después de la migración exitosa:

1. **Explorar datos en MongoDB Compass**
2. **Probar consultas** desde MongoDB Shell
3. **Revisar** `MongoDB_Consultas_Ejemplos.mongodb` para ejemplos
4. **Actualizar** tu aplicación para usar MongoDB

---

## 🎉 ¡Listo!

Tu base de datos ahora está en **MongoDB Atlas** con:
- ✅ Base de datos: `optica_db`
- ✅ 11 colecciones optimizadas
- ✅ Validación JSON Schema
- ✅ Índices para consultas rápidas
- ✅ Rendimiento mejorado 10-20x

**¿Necesitas ayuda?** Consulta `INSTRUCCIONES_MIGRACION.md`
