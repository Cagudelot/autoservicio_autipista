"""
Módulo de Empleados - Control de Turnos (Entrada/Salida)
"""
import streamlit as st
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from data_base.controler import (
    get_empleado_by_cedula,
    get_turno_abierto_hoy,
    get_turno_completo_hoy,
    registrar_entrada,
    registrar_salida,
    get_turnos_empleado_hoy
)
from src.utils.ui_helpers import CSS_STYLES


# ==================== ESTILOS ADICIONALES ====================

TURNOS_STYLES = """
<style>
    .turno-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        padding: 25px;
        color: white;
        text-align: center;
        margin: 20px 0;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }
    
    .turno-card.entrada {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        box-shadow: 0 10px 30px rgba(17, 153, 142, 0.3);
    }
    
    .turno-card.salida {
        background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
        box-shadow: 0 10px 30px rgba(235, 51, 73, 0.3);
    }
    
    .turno-card.completado {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        box-shadow: 0 10px 30px rgba(79, 172, 254, 0.3);
    }
    
    .turno-card.bloqueado {
        background: linear-gradient(135deg, #636363 0%, #a2ab58 100%);
        box-shadow: 0 10px 30px rgba(99, 99, 99, 0.3);
    }
    
    .empleado-nombre {
        font-size: 1.8em;
        font-weight: 700;
        margin-bottom: 5px;
    }
    
    .empleado-cedula {
        font-size: 1em;
        opacity: 0.9;
        margin-bottom: 15px;
    }
    
    .turno-hora {
        font-size: 2.5em;
        font-weight: 700;
        margin: 15px 0;
    }
    
    .turno-label {
        font-size: 0.9em;
        opacity: 0.8;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    
    .turno-info-box {
        background: rgba(255,255,255,0.15);
        border-radius: 10px;
        padding: 15px;
        margin-top: 15px;
    }
    
    .welcome-box {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        border-radius: 20px;
        padding: 40px;
        text-align: center;
        color: white;
        margin: 30px 0;
    }
    
    .welcome-icon {
        font-size: 4em;
        margin-bottom: 20px;
    }
    
    .welcome-title {
        font-size: 1.5em;
        font-weight: 600;
        margin-bottom: 10px;
    }
    
    .welcome-subtitle {
        opacity: 0.8;
        font-size: 1em;
    }
</style>
"""


def render():
    """Renderiza el módulo de control de turnos"""
    st.markdown(CSS_STYLES, unsafe_allow_html=True)
    st.markdown(TURNOS_STYLES, unsafe_allow_html=True)
    
    st.title("⏰ Control de Turnos")
    st.markdown("Registro de entrada y salida de empleados")
    st.markdown("---")
    
    # Inicializar session_state para mensajes
    if 'turno_mensaje' not in st.session_state:
        st.session_state.turno_mensaje = None
    if 'turno_tipo' not in st.session_state:
        st.session_state.turno_tipo = None
    
    # Mostrar mensaje si existe
    if st.session_state.turno_mensaje:
        if st.session_state.turno_tipo == 'entrada':
            st.success(st.session_state.turno_mensaje)
            st.balloons()
        elif st.session_state.turno_tipo == 'salida':
            st.success(st.session_state.turno_mensaje)
            st.balloons()
        # Limpiar mensaje después de mostrarlo
        st.session_state.turno_mensaje = None
        st.session_state.turno_tipo = None
    
    # Input para cédula
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        cedula = st.text_input(
            "🔍 Número de Documento",
            placeholder="Ingrese su número de cédula",
            help="Digite su número de documento y presione Enter",
            key="cedula_turno"
        )
        
        buscar = st.button("🔎 Consultar", use_container_width=True, type="primary")
    
    # Placeholder para mensajes
    mensaje_placeholder = st.empty()
    contenido_placeholder = st.empty()
    
    # Lógica de búsqueda
    if buscar or cedula:
        if cedula and cedula.strip():
            empleado = get_empleado_by_cedula(cedula.strip())
            
            if empleado:
                # Empleado encontrado - verificar estado de turno
                id_empleado = empleado['id_empleado']
                nombre = empleado['nombre_empleado']
                
                turno_abierto = get_turno_abierto_hoy(id_empleado)
                turno_completo = get_turno_completo_hoy(id_empleado)
                
                with contenido_placeholder.container():
                    st.markdown("---")
                    
                    # CASO 1: Ya tiene un turno completo hoy - BLOQUEADO
                    if turno_completo and not turno_abierto:
                        hora_entrada = turno_completo['hora_inicio'].strftime("%H:%M")
                        hora_salida = turno_completo['hora_salida'].strftime("%H:%M")
                        
                        st.markdown(f"""
                        <div class="turno-card bloqueado">
                            <div class="empleado-nombre">{nombre}</div>
                            <div class="empleado-cedula">📄 {cedula}</div>
                            <div class="turno-info-box">
                                <div class="turno-label">⚠️ Ya completaste tu turno de hoy</div>
                                <div style="margin-top: 10px;">
                                    <span>🟢 Entrada: {hora_entrada}</span> | 
                                    <span>🔴 Salida: {hora_salida}</span>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.warning("⚠️ No puedes registrar una nueva entrada. Ya completaste tu turno del día.")
                    
                    # CASO 2: Tiene turno abierto - puede marcar SALIDA
                    elif turno_abierto:
                        hora_entrada = turno_abierto['hora_inicio'].strftime("%H:%M")
                        
                        st.markdown(f"""
                        <div class="turno-card salida">
                            <div class="empleado-nombre">{nombre}</div>
                            <div class="empleado-cedula">📄 {cedula}</div>
                            <div class="turno-label">🟢 Turno iniciado a las</div>
                            <div class="turno-hora">{hora_entrada}</div>
                            <div class="turno-info-box">
                                <div>¿Deseas registrar tu salida?</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
                        with col_btn2:
                            if st.button("🔴 Registrar Salida", use_container_width=True, type="primary", key="btn_salida"):
                                resultado, error = registrar_salida(turno_abierto['id_turno'])
                                if error:
                                    st.error(f"❌ Error al registrar salida: {error}")
                                else:
                                    hora_salida = resultado['hora_salida'].strftime("%H:%M:%S")
                                    st.session_state.turno_mensaje = f"✅ ¡Salida registrada exitosamente a las {hora_salida}!"
                                    st.session_state.turno_tipo = 'salida'
                                    st.rerun()
                    
                    # CASO 3: No tiene turno hoy - puede marcar ENTRADA
                    else:
                        st.markdown(f"""
                        <div class="turno-card entrada">
                            <div class="empleado-nombre">{nombre}</div>
                            <div class="empleado-cedula">📄 {cedula}</div>
                            <div class="turno-label">👋 ¡Bienvenido!</div>
                            <div class="turno-hora">{datetime.now().strftime("%H:%M")}</div>
                            <div class="turno-info-box">
                                <div>¿Deseas registrar tu entrada?</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
                        with col_btn2:
                            if st.button("🟢 Registrar Entrada", use_container_width=True, type="primary", key="btn_entrada"):
                                resultado, error = registrar_entrada(id_empleado)
                                if error:
                                    st.error(f"❌ Error al registrar entrada: {error}")
                                else:
                                    hora_entrada = resultado['hora_inicio'].strftime("%H:%M:%S")
                                    st.session_state.turno_mensaje = f"✅ ¡Entrada registrada exitosamente a las {hora_entrada}!"
                                    st.session_state.turno_tipo = 'entrada'
                                    st.rerun()
            else:
                # Empleado NO encontrado
                with contenido_placeholder.container():
                    st.markdown("---")
                    st.error("❌ No se encontró ningún empleado con ese número de documento.")
                    st.info("💡 Verifica que el número de documento sea correcto o contacta al administrador.")
        else:
            # Sin cédula ingresada - mostrar pantalla de bienvenida
            with contenido_placeholder.container():
                st.markdown("""
                <div class="welcome-box">
                    <div class="welcome-icon">👋</div>
                    <div class="welcome-title">Sistema de Control de Turnos</div>
                    <div class="welcome-subtitle">Ingresa tu número de documento para registrar entrada o salida</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        # Estado inicial
        with contenido_placeholder.container():
            st.markdown("""
            <div class="welcome-box">
                <div class="welcome-icon">👋</div>
                <div class="welcome-title">Sistema de Control de Turnos</div>
                <div class="welcome-subtitle">Ingresa tu número de documento para registrar entrada o salida</div>
            </div>
            """, unsafe_allow_html=True)
