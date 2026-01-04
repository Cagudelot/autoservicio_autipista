# 📋 Contexto del Proyecto - Sistema Administración Supermercado

> **Última actualización**: Enero 2026  
> **Versión**: 1.0.0

---

## 🎯 Descripción General

Sistema de administración para supermercado desarrollado con **Streamlit**. Integra gestión de cartera (facturas/remisiones), control de empleados, turnos, nómina y sincronización con la API de **Alegra** (software contable colombiano).

---

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                      FRONTEND (Streamlit)                    │
│                         src/app.py                           │
├─────────────────────────────────────────────────────────────┤
│   📊 Cartera    │  👥 Empleados  │  💰 Nómina  │  ⚙️ Config  │
│  - todos_clientes│  - registro    │  - horas    │  - IPs      │
│  - kikes        │  - turnos      │  - extras   │  - usuarios │
│                 │  - gestión     │             │             │
├─────────────────────────────────────────────────────────────┤
│                    CAPA DE DATOS                             │
│           data_base/controler.py (CRUD)                      │
│           data_base/connection.py (PostgreSQL)               │
├─────────────────────────────────────────────────────────────┤
│                  SERVICIOS EXTERNOS                          │
│              services/alegra_api.py                          │
│           (Sincronización facturas/remisiones)               │
└─────────────────────────────────────────────────────────────┘
```

---

## 🗃️ Modelo de Datos (PostgreSQL)

### Tablas Principales

| Tabla | Descripción | Relaciones |
|-------|-------------|------------|
| `clientes` | Datos de clientes (NIT, nombre) | - |
| `negocios` | Negocios asociados a clientes | → clientes |
| `remisiones` | Remisiones de Alegra | → clientes |
| `facturas` | Facturas de Alegra | → clientes |
| `empleados` | Datos de empleados (cédula, salario) | - |
| `turnos` | Registro de entrada/salida | → empleados |
| `total_horas` | Cálculo de horas trabajadas | → turnos |
| `horas_extra` | Horas extra calculadas | → turnos, total_horas |
| `usuarios` | Usuarios del sistema (login) | - |
| `modulos_sistema` | Módulos disponibles (Cartera, Empleados, etc.) | - |
| `usuarios_modulos` | Permisos usuario-módulo | → usuarios, modulos_sistema |
| `direcciones_ip` | IPs autorizadas para acceso | - |

### Campos Importantes de Usuarios
- `es_master`: Acceso total (super admin)
- `es_admin`: Acceso administrativo
- `es_empleado`: Acceso básico de empleado

---

## 🔐 Sistema de Autenticación

- Login con **username/password** (hash SHA256)
- Roles: `master`, `admin`, `empleado`
- Permisos por módulo (`puede_ver`, `puede_editar`)
- Control de acceso por **IP autorizada** (opcional)

---

## 📦 Módulos Actuales

### 1. 📊 Cartera
- **todos_clientes.py**: Vista general de deudas (facturas + remisiones abiertas)
- **kikes.py**: Dashboard específico para negocios "Kikes" (cliente especial)

### 2. 👥 Empleados
- **registro.py**: Formulario registro de empleados
- **turnos.py**: Registro de entrada/salida
- **turnos_hoy.py**: Vista de turnos del día actual
- **gestion_turnos.py** / **gestion_turnos_2.py**: Gestión avanzada de turnos

### 3. 💰 Nómina
- **total_horas_dia.py**: Cálculo de horas trabajadas por día
- **horas_extra.py**: Cálculo y visualización de horas extra

### 4. ⚙️ Configuración
- **direcciones_ip.py**: Gestión de IPs autorizadas
- **usuarios.py**: Gestión de usuarios y permisos

---

## 🔗 Integración Alegra API

**Archivo**: `services/alegra_api.py`

### Funcionalidades:
- Sincronización de **remisiones** (desde última guardada)
- Sincronización de **facturas** (desde última guardada)
- Actualización de estados (`open`, `closed`, `void`)
- Cálculo de estado basado en `missingQuantityToBilled`

### Endpoints usados:
- `GET /remissions` - Listar remisiones
- `GET /invoices` - Listar facturas
- `GET /remissions/{id}` - Detalle de remisión
- `GET /invoices/{id}` - Detalle de factura

---

## ⚙️ Configuración

### Variables de Entorno (.env)
```env
# Base de datos PostgreSQL
DB_HOST=localhost
DB_NAME=Datos_alegra
DB_USER=postgres
DB_PASSWORD=****
DB_PORT=5432

# API Alegra
ALEGRA_EMAIL=email@ejemplo.com
ALEGRA_API_KEY=****
```

### Streamlit Secrets (producción)
Las mismas variables en `secrets.toml` para Streamlit Cloud.

---

## 🚀 Ejecución

```bash
# Desarrollo local
streamlit run src/app.py

# Docker
docker build -t supermercado-admin .
docker run -p 8501:8501 supermercado-admin
```

---

## 📝 Convenciones de Código

- **Idioma código**: Español (docstrings, variables)
- **Nombrado**: snake_case (funciones/variables), PascalCase (clases)
- **Imports**: Agrupados (stdlib → third-party → local)
- **Conexiones BD**: Abrir y cerrar explícitamente en cada función

---

## 🔧 Decisiones Técnicas

| Decisión | Razón |
|----------|-------|
| Streamlit | Rápido desarrollo de dashboards, curva de aprendizaje baja |
| PostgreSQL | Robustez, soporte para concurrencia, tipos de datos avanzados |
| Sin ORM | Simplicidad, control directo de queries |
| psycopg2 | Driver PostgreSQL más estable para Python |
| Alegra | Software contable usado por el cliente |

---

## 🐛 Problemas Conocidos / TODOs

- [ ] `gestion_turnos.py` tiene dos versiones (_2) - consolidar
- [ ] Valor de remisión tiene typo en BD: `valor_remsion` (falta 'i')
- [ ] Manejo de conexiones podría usar context managers
- [ ] Falta logging estructurado (solo prints de debug)

---

## 🔄 Para Adaptar a Nuevo Cliente

1. **Clonar repositorio** a nueva carpeta
2. **Configurar `.env`** con credenciales del nuevo cliente
3. **Ejecutar `schema.sql`** en PostgreSQL del cliente
4. **Modificar/eliminar módulos específicos**:
   - `kikes.py` → Renombrar/eliminar según negocios del cliente
   - Ajustar módulos en `modulos_sistema`
5. **Actualizar este archivo** con contexto del nuevo cliente

---

## 📞 Dependencias Principales

```
streamlit>=1.28.0
streamlit-option-menu>=0.3.6
psycopg2-binary>=2.9.9
plotly>=5.18.0
pandas>=2.0.0
python-dotenv>=1.0.0
requests>=2.31.0
```

---

## 🗂️ Archivos Clave para Modificaciones

| Archivo | Cuándo modificar |
|---------|------------------|
| `src/app.py` | Agregar/quitar módulos del menú |
| `config/settings.py` | Cambiar configuración de BD o API |
| `data_base/controler.py` | Nuevas operaciones CRUD |
| `database/schema.sql` | Cambios en estructura de BD |
| `src/modules/*/` | Lógica de cada módulo |
