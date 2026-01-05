# Sistema de Administración - Kikes 🏪

Sistema de administración para Kikes desarrollado con Streamlit, que incluye gestión de CXP Supermercado, empleados y sincronización con Alegra.

## 📁 Estructura del Proyecto

```
reportes_alegra/
├── config/                     # Configuración centralizada
│   ├── __init__.py
│   └── settings.py            # Variables de configuración
│
├── data_base/                  # Capa de acceso a datos
│   ├── __init__.py
│   ├── connection.py          # Conexión a PostgreSQL
│   └── controler.py           # Operaciones CRUD
│
├── services/                   # Servicios externos
│   └── alegra_api.py          # Integración con API de Alegra
│
├── src/                        # Código fuente principal
│   ├── __init__.py
│   ├── app.py                 # 🚀 Punto de entrada de la aplicación
│   │
│   ├── modules/               # Módulos de la aplicación
│   │   ├── cartera/          # Módulo CXP Supermercado
│   │   │   ├── __init__.py
│   │   │   └── kikes.py
│   │   │
│   │   └── empleados/        # Módulo de empleados
│   │       ├── __init__.py
│   │       └── registro.py
│   │
│   └── utils/                 # Utilidades compartidas
│       ├── __init__.py
│       └── ui_helpers.py      # Helpers de interfaz
│
├── .env                        # Variables de entorno (NO commitear)
├── .gitignore                 # Archivos ignorados por Git
├── requirements.txt           # Dependencias del proyecto
└── README.md                  # Este archivo
```

## 🚀 Instalación

### 1. Clonar el repositorio
```bash
git clone <url-del-repositorio>
cd reportes_alegra
```

### 2. Crear entorno virtual
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate     # Windows
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno
Crear archivo `.env` en la raíz del proyecto:
```env
# Base de datos
DB_HOST=localhost
DB_NAME=Datos_alegra
DB_USER=postgres
DB_PASSWORD=tu_password
DB_PORT=5432

# API Alegra
ALEGRA_EMAIL=tu_email@ejemplo.com
ALEGRA_API_KEY=tu_api_key
```

### 5. Ejecutar la aplicación
```bash
streamlit run src/app.py
```

## 📦 Módulos

### 📊 CXP Supermercado
- **Kikes**: Dashboard de cuentas por pagar del supermercado

### 👥 Empleados
- **Registro**: Formulario para registrar nuevos empleados
- **Gestión Turnos 2.0**: Gestión avanzada de turnos

### ⚙️ Configuración
- (En construcción)

## 🛠️ Tecnologías

- **Frontend**: Streamlit + Streamlit Option Menu
- **Visualización**: Plotly
- **Base de datos**: PostgreSQL + psycopg2
- **API**: Integración con Alegra
- **Entorno**: Python 3.10+

## 📝 Convenciones de Código

- Docstrings en español
- Nombres de variables y funciones en snake_case
- Clases en PascalCase
- Constantes en UPPER_CASE

## 👤 Autor

Sistema desarrollado para administración de Kikes.
