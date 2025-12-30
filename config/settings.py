"""
Configuración centralizada del proyecto
"""
import os

# Intentar cargar dotenv (desarrollo local)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Intentar cargar desde Streamlit Secrets (producción)
try:
    import streamlit as st
    if hasattr(st, 'secrets'):
        # Cargar desde st.secrets si existen
        for key in ['DB_HOST', 'DB_PORT', 'DB_NAME', 'DB_USER', 'DB_PASSWORD', 
                    'ALEGRA_API_KEY', 'ALEGRA_EMAIL']:
            if key in st.secrets:
                os.environ[key] = str(st.secrets[key])
except Exception:
    pass

# ==================== BASE DE DATOS ====================
# IMPORTANTE: Configurar las credenciales en archivo .env o Streamlit Secrets
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "database": os.getenv("DB_NAME", ""),
    "user": os.getenv("DB_USER", ""),
    "password": os.getenv("DB_PASSWORD", ""),
    "port": int(os.getenv("DB_PORT", 5432))
}

# Validar que las credenciales estén configuradas
def validar_db_config():
    """Valida que las credenciales de BD estén configuradas"""
    campos_requeridos = ["database", "user", "password"]
    faltantes = [c for c in campos_requeridos if not DB_CONFIG.get(c)]
    if faltantes:
        raise ValueError(
            f"Faltan variables de entorno de BD: {', '.join(faltantes)}. "
            "Configura el archivo .env basándote en .env.example"
        )

# ==================== API ALEGRA ====================
ALEGRA_CONFIG = {
    "base_url": "https://api.alegra.com/api/v1",
    "email": os.getenv("ALEGRA_EMAIL"),
    "api_key": os.getenv("ALEGRA_API_KEY")
}

# ==================== APLICACIÓN ====================
APP_CONFIG = {
    "title": "Sistema Administración Supermercado",
    "icon": "🏪",
    "layout": "wide"
}

# ==================== TIPOS DE DOCUMENTO ====================
TIPOS_DOCUMENTO = [
    "Cédula de Ciudadanía",
    "Tarjeta de Identidad",
    "Permiso Especial de Permanencia (PEP)",
    "Permiso por Protección Temporal (PPT)",
    "Cédula de Extranjería"
]
