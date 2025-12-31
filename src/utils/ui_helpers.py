"""
Utilidades compartidas para la interfaz de usuario
"""
import streamlit as st
import psycopg2
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import DB_CONFIG


def get_db_connection():
    """Crea una nueva conexión a la base de datos cada vez (no cacheada para evitar conexiones cerradas)"""
    return psycopg2.connect(
        host=DB_CONFIG["host"],
        database=DB_CONFIG["database"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        port=DB_CONFIG["port"]
    )


def format_currency(value):
    """Formatea valor como moneda colombiana"""
    return f"${value:,.0f}"


def create_metric_card(label, value, icon, color_class=""):
    """Crea una tarjeta métrica personalizada"""
    return f"""
    <div class="metric-card {color_class}">
        <div class="metric-label">{icon} {label}</div>
        <div class="metric-value">{value}</div>
    </div>
    """


# CSS común para toda la aplicación
CSS_STYLES = """
<style>
    /* Estilos para las tarjetas métricas */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        margin-bottom: 10px;
    }
    .metric-card-green {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    }
    .metric-card-orange {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }
    .metric-card-blue {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    }
    .metric-card-red {
        background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
    }
    .metric-card-yellow {
        background: linear-gradient(135deg, #f7971e 0%, #ffd200 100%);
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        margin: 10px 0;
    }
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    
    /* Responsividad */
    @media (max-width: 768px) {
        .metric-value {
            font-size: 1.5rem;
        }
        .metric-label {
            font-size: 0.8rem;
        }
    }
    
    /* Estilo para tablas */
    .dataframe {
        font-size: 0.85rem;
    }
    
    /* Header personalizado */
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f2937;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        color: #6b7280;
        margin-bottom: 2rem;
    }
    
    /* Negocio card */
    .negocio-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 10px 20px;
        border-radius: 10px;
        color: white;
        margin-bottom: 15px;
    }
    
    /* Ocultar elementos innecesarios de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: white;
    }
</style>
"""


# Estilos del menú lateral
MENU_STYLES = """
<style>
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e3c72 0%, #2a5298 100%);
        min-width: 280px;
    }
    
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 2rem;
    }
    
    /* Logo/Brand area */
    .sidebar-brand {
        text-align: center;
        padding: 20px 0 30px 0;
        border-bottom: 1px solid rgba(255,255,255,0.1);
        margin-bottom: 20px;
    }
    
    .sidebar-brand-icon {
        font-size: 3em;
        margin-bottom: 10px;
    }
    
    .sidebar-brand-title {
        color: white;
        font-size: 1.5em;
        font-weight: 700;
        letter-spacing: 1px;
    }
    
    .sidebar-brand-subtitle {
        color: rgba(255,255,255,0.6);
        font-size: 0.85em;
        margin-top: 5px;
    }
    
    /* Footer */
    .sidebar-footer {
        position: fixed;
        bottom: 20px;
        left: 20px;
        color: rgba(255,255,255,0.5);
        font-size: 0.75em;
    }
    
    /* Main content */
    .main .block-container {
        padding-top: 2rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    
    /* Keep sidebar collapse button visible */
    [data-testid="collapsedControl"] {
        display: flex !important;
    }
</style>
"""
