"""
Módulo de Nómina - En construcción
"""
import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.utils.ui_helpers import CSS_STYLES


def render():
    """Renderiza el módulo de nómina (en construcción)"""
    st.markdown(CSS_STYLES, unsafe_allow_html=True)
    
    st.title("💰 Nómina")
    st.markdown("---")
    
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
        <div style="font-size: 1.2em; opacity: 0.9;">Estamos trabajando en este módulo</div>
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
    st.info("💡 Este módulo estará disponible próximamente. Por ahora puedes gestionar los turnos de empleados desde el módulo de Empleados.")
