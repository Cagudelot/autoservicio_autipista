"""
Módulo de Configuración - Gestión de Direcciones IP autorizadas
"""
import streamlit as st
import pandas as pd
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from data_base.controler import (
    get_all_direcciones_ip,
    insert_direccion_ip,
    update_direccion_ip_estado,
    delete_direccion_ip,
    check_ip_exists
)
from src.utils.ui_helpers import CSS_STYLES


# ==================== ESTILOS ====================

CONFIG_STYLES = """
<style>
    .ip-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        padding: 20px;
        color: white;
        margin: 10px 0;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }
    
    .ip-card.activo {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    }
    
    .ip-card.inactivo {
        background: linear-gradient(135deg, #636363 0%, #8f8f8f 100%);
        opacity: 0.7;
    }
    
    .ip-nombre {
        font-size: 1.3em;
        font-weight: 700;
        margin-bottom: 5px;
    }
    
    .ip-direccion {
        font-size: 1.1em;
        font-family: monospace;
        background: rgba(255,255,255,0.2);
        padding: 5px 10px;
        border-radius: 5px;
        display: inline-block;
    }
    
    .ip-estado {
        margin-top: 10px;
        font-size: 0.9em;
        opacity: 0.9;
    }
    
    .config-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        border-radius: 15px;
        padding: 25px;
        color: white;
        text-align: center;
        margin-bottom: 20px;
    }
    
    .config-header-icon {
        font-size: 3em;
        margin-bottom: 10px;
    }
    
    .config-header-title {
        font-size: 1.5em;
        font-weight: 600;
    }
</style>
"""


def render():
    """Renderiza el módulo de configuración de direcciones IP"""
    st.markdown(CSS_STYLES, unsafe_allow_html=True)
    st.markdown(CONFIG_STYLES, unsafe_allow_html=True)
    
    st.title("⚙️ Configuración")
    st.markdown("---")
    
    # Header
    st.markdown("""
    <div class="config-header">
        <div class="config-header-icon">🖥️</div>
        <div class="config-header-title">Gestión de Equipos Autorizados</div>
        <div style="opacity: 0.8; margin-top: 5px;">Administra las direcciones IP que pueden acceder a la aplicación</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Tabs
    tab1, tab2 = st.tabs(["📋 Equipos Registrados", "➕ Agregar Equipo"])
    
    with tab1:
        render_lista_equipos()
    
    with tab2:
        render_formulario_agregar()


def render_lista_equipos():
    """Renderiza la lista de equipos registrados"""
    
    # Botón actualizar
    col_space, col_btn = st.columns([5, 1])
    with col_btn:
        if st.button("🔄 Actualizar", key="refresh_ips"):
            st.rerun()
    
    direcciones = get_all_direcciones_ip()
    
    if direcciones:
        # Resumen
        total = len(direcciones)
        activos = sum(1 for d in direcciones if d['activo'])
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("📊 Total Equipos", total)
        with col2:
            st.metric("✅ Activos", activos)
        
        st.markdown("---")
        
        # Lista de equipos
        for ip_data in direcciones:
            estado_class = "activo" if ip_data['activo'] else "inactivo"
            estado_texto = "✅ Activo" if ip_data['activo'] else "❌ Inactivo"
            
            col_card, col_actions = st.columns([3, 1])
            
            with col_card:
                st.markdown(f"""
                <div class="ip-card {estado_class}">
                    <div class="ip-nombre">🖥️ {ip_data['nombre_equipo']}</div>
                    <div class="ip-direccion">{ip_data['direccion_ip']}</div>
                    <div class="ip-estado">{estado_texto}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col_actions:
                st.write("")  # Espaciado
                st.write("")
                
                # Botón activar/desactivar
                if ip_data['activo']:
                    if st.button("🔴 Desactivar", key=f"deactivate_{ip_data['id_direccion']}", use_container_width=True):
                        success, error = update_direccion_ip_estado(ip_data['id_direccion'], False)
                        if success:
                            st.success("Equipo desactivado")
                            st.rerun()
                        else:
                            st.error(f"Error: {error}")
                else:
                    if st.button("🟢 Activar", key=f"activate_{ip_data['id_direccion']}", use_container_width=True):
                        success, error = update_direccion_ip_estado(ip_data['id_direccion'], True)
                        if success:
                            st.success("Equipo activado")
                            st.rerun()
                        else:
                            st.error(f"Error: {error}")
                
                # Botón eliminar
                if st.button("🗑️ Eliminar", key=f"delete_{ip_data['id_direccion']}", use_container_width=True):
                    success, error = delete_direccion_ip(ip_data['id_direccion'])
                    if success:
                        st.success("Equipo eliminado")
                        st.rerun()
                    else:
                        st.error(f"Error: {error}")
    else:
        st.info("📭 No hay equipos registrados. Agrega uno en la pestaña 'Agregar Equipo'.")


def render_formulario_agregar():
    """Renderiza el formulario para agregar un nuevo equipo"""
    
    st.subheader("➕ Registrar Nuevo Equipo")
    st.markdown("Ingresa la información del equipo que deseas autorizar")
    
    # Inicializar estado para mensajes
    if 'ip_mensaje' not in st.session_state:
        st.session_state.ip_mensaje = None
    
    # Mostrar mensaje si existe
    if st.session_state.ip_mensaje:
        st.success(st.session_state.ip_mensaje)
        st.session_state.ip_mensaje = None
    
    with st.form(key="form_agregar_ip", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            nombre_equipo = st.text_input(
                "🖥️ Nombre del Equipo *",
                placeholder="Ej: pc_mario, laptop_ventas",
                help="Un nombre descriptivo para identificar el equipo"
            )
        
        with col2:
            direccion_ip = st.text_input(
                "🌐 Dirección IP *",
                placeholder="Ej: 192.168.1.100",
                help="Dirección IP del equipo (IPv4 o IPv6)"
            )
        
        st.markdown("---")
        
        submit = st.form_submit_button(
            "💾 Registrar Equipo",
            use_container_width=True,
            type="primary"
        )
        
        if submit:
            errores = []
            
            if not nombre_equipo or nombre_equipo.strip() == "":
                errores.append("El nombre del equipo es obligatorio")
            
            if not direccion_ip or direccion_ip.strip() == "":
                errores.append("La dirección IP es obligatoria")
            
            # Validar formato básico de IP
            if direccion_ip:
                ip_parts = direccion_ip.strip().split('.')
                if len(ip_parts) != 4:
                    errores.append("La dirección IP debe tener formato válido (ej: 192.168.1.100)")
                else:
                    try:
                        for part in ip_parts:
                            num = int(part)
                            if num < 0 or num > 255:
                                errores.append("Cada parte de la IP debe estar entre 0 y 255")
                                break
                    except ValueError:
                        errores.append("La dirección IP debe contener solo números")
            
            # Verificar si ya existe
            if direccion_ip and check_ip_exists(direccion_ip.strip()):
                errores.append("Esta dirección IP ya está registrada")
            
            if errores:
                for error in errores:
                    st.error(f"❌ {error}")
            else:
                id_direccion, error = insert_direccion_ip(
                    direccion_ip=direccion_ip.strip(),
                    nombre_equipo=nombre_equipo.strip()
                )
                
                if error:
                    st.error(f"❌ Error al registrar: {error}")
                else:
                    st.session_state.ip_mensaje = f"✅ Equipo '{nombre_equipo.strip()}' registrado exitosamente"
                    st.rerun()
    
    # Info adicional
    st.markdown("---")
    st.caption("* Campos obligatorios")
    st.info("💡 **Tip:** Para encontrar la IP de un equipo Windows, abre CMD y escribe `ipconfig`. En Linux/Mac usa `ip addr` o `ifconfig`.")
