"""
Módulo de Nómina
"""
import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.utils.ui_helpers import CSS_STYLES
from src.modules.nomina.total_horas_dia import render as render_total_horas
from src.modules.nomina.horas_extra import render as render_horas_extra


def render():
    """Renderiza el módulo de nómina con pestañas"""
    st.markdown(CSS_STYLES, unsafe_allow_html=True)
    
    st.title("💰 Nómina")
    st.markdown("---")
    
    # Crear pestañas
    tab1, tab2, tab3 = st.tabs(["⏱️ Total Horas Día", "⏰ Horas Extra", "🚧 Más Opciones"])
    
    with tab1:
        render_total_horas()
    
    with tab2:
        render_horas_extra()
    
    with tab3:
        render_en_construccion()


def render_en_construccion():
    """Renderiza la sección en construcción"""
    # Header en construcción
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        border-radius: 20px;
        padding: 50px;
        text-align: center;
        color: white;
        margin: 20px 0;
    ">
        <div style="font-size: 5em; margin-bottom: 20px;">🚧</div>
        <div style="font-size: 2em; font-weight: 700; margin-bottom: 10px;">Módulo en Construcción</div>
        <div style="font-size: 1.2em; opacity: 0.9;">Estamos trabajando en más funcionalidades</div>
        <div style="margin-top: 20px; opacity: 0.8;">
            Próximamente podrás gestionar:
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Características futuras
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 15px;
            padding: 25px;
            text-align: center;
            color: white;
            height: 150px;
        ">
            <div style="font-size: 2.5em; margin-bottom: 10px;">📊</div>
            <div style="font-weight: 600;">Cálculo de Nómina</div>
            <div style="opacity: 0.8; font-size: 0.9em; margin-top: 5px;">Automático basado en turnos</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            border-radius: 15px;
            padding: 25px;
            text-align: center;
            color: white;
            height: 150px;
        ">
            <div style="font-size: 2.5em; margin-bottom: 10px;">💵</div>
            <div style="font-weight: 600;">Gestión de Pagos</div>
            <div style="opacity: 0.8; font-size: 0.9em; margin-top: 5px;">Control de pagos realizados</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            border-radius: 15px;
            padding: 25px;
            text-align: center;
            color: white;
            height: 150px;
        ">
            <div style="font-size: 2.5em; margin-bottom: 10px;">📋</div>
            <div style="font-weight: 600;">Reportes</div>
            <div style="opacity: 0.8; font-size: 0.9em; margin-top: 5px;">Historial y estadísticas</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.info("💡 Estas funcionalidades estarán disponibles próximamente.")
