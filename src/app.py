"""
Dashboard Principal - Sistema de Administración Kikes
Punto de entrada de la aplicación Streamlit con Sistema de Autenticación
"""
import sys
import os

# Configurar path ANTES de cualquier otro import
# Esto es crítico para Streamlit Cloud
_current_dir = os.path.dirname(os.path.abspath(__file__))
_root_dir = os.path.dirname(_current_dir)
if _root_dir not in sys.path:
    sys.path.insert(0, _root_dir)

import streamlit as st
from streamlit_option_menu import option_menu
from config.settings import APP_CONFIG
from src.utils.ui_helpers import MENU_STYLES

# Importar módulos
from src.modules.cartera import kikes
from src.modules.empleados import registro as registro_empleado
from src.modules.empleados import turnos as turnos_empleado
from src.modules.empleados import turnos_hoy as turnos_hoy_empleado
from src.modules.empleados import turnos_hoy_fotos
from src.modules.empleados import gestion_turnos_2
from src.modules.empleados import admin_turnos
from src.modules.empleados import lista_empleados
from src.modules.configuracion import direcciones_ip
from src.modules.configuracion import usuarios as gestion_usuarios
from src.modules.configuracion import roles as gestion_roles
from src.modules.nomina import total_horas_dia as nomina_total_horas
from src.modules.nomina import horas_extra as nomina_horas_extra
from src.modules.nomina import descuentos as nomina_descuentos
from src.modules.nomina import liquidacion as nomina_liquidacion
from src.modules.nomina import pago_dia as nomina_pago_dia
from src.modules.dashboard import principal as dashboard_principal

# Importar funciones de autenticación
from data_base.controler import autenticar_usuario, get_modulos_usuario

# Configuración de página
st.set_page_config(
    page_title=APP_CONFIG["title"],
    page_icon=APP_CONFIG["icon"],
    layout=APP_CONFIG["layout"],
    initial_sidebar_state="expanded"
)


# ==================== ESTILOS LOGIN ====================

LOGIN_STYLES = """
<style>
    .login-container {
        max-width: 400px;
        margin: 50px auto;
        padding: 40px;
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border-radius: 20px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    .login-header {
        text-align: center;
        margin-bottom: 30px;
    }
    
    .login-icon {
        font-size: 4em;
        margin-bottom: 15px;
    }
    
    .login-title {
        font-size: 1.8em;
        font-weight: 700;
        color: #4fd1c5;
    }
    
    .login-subtitle {
        color: rgba(255,255,255,0.6);
        font-size: 0.9em;
    }
    
    .empleado-header {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        color: white;
        margin-bottom: 20px;
    }
    
    .user-logged {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        padding: 10px 15px;
        color: white;
        margin: 10px 0;
        font-size: 0.9em;
    }
</style>
"""


# ==================== FUNCIONES DE SESIÓN ====================

def init_session_state():
    """Inicializa las variables de sesión"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'modulos_permitidos' not in st.session_state:
        st.session_state.modulos_permitidos = []
    if 'show_login' not in st.session_state:
        st.session_state.show_login = False


def login(username, password):
    """Intenta autenticar al usuario"""
    user = autenticar_usuario(username, password)
    if user:
        st.session_state.authenticated = True
        st.session_state.user = user
        st.session_state.modulos_permitidos = get_modulos_usuario(user['id_usuario'])
        st.session_state.show_login = False
        return True
    return False


def logout():
    """Cierra la sesión del usuario"""
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.modulos_permitidos = []
    st.session_state.show_login = False


def tiene_permiso(nombre_modulo):
    """Verifica si el usuario tiene permiso para ver un módulo"""
    if not st.session_state.authenticated:
        return False
    if st.session_state.user.get('es_master'):
        return True
    return any(m['nombre_modulo'] == nombre_modulo for m in st.session_state.modulos_permitidos)


# ==================== RENDER LOGIN ====================

def render_login_page():
    """Renderiza la página de login"""
    st.markdown(LOGIN_STYLES, unsafe_allow_html=True)
    st.markdown(MENU_STYLES, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div class="login-header">
            <div class="login-icon">🔐</div>
            <div class="login-title">Iniciar Sesión</div>
            <div class="login-subtitle">Sistema de Administración</div>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form(key="login_form"):
            username = st.text_input("👤 Usuario", placeholder="Ingresa tu usuario")
            password = st.text_input("🔑 Contraseña", type="password", placeholder="Ingresa tu contraseña")
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                submit = st.form_submit_button("🚀 Ingresar", use_container_width=True, type="primary")
            with col_btn2:
                cancelar = st.form_submit_button("❌ Cancelar", use_container_width=True)
            
            if submit:
                if not username or not password:
                    st.error("❌ Ingresa usuario y contraseña")
                elif login(username, password):
                    st.success(f"✅ Bienvenido, {st.session_state.user['nombre_completo']}")
                    st.rerun()
                else:
                    st.error("❌ Usuario o contraseña incorrectos")
            
            if cancelar:
                st.session_state.show_login = False
                st.rerun()


# ==================== RENDER VISTA EMPLEADOS ====================

def render_vista_empleados():
    """Renderiza la vista por defecto para empleados (solo control de turnos)"""
    st.markdown(LOGIN_STYLES, unsafe_allow_html=True)
    st.markdown(MENU_STYLES, unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-brand">
            <div class="sidebar-brand-icon">🏪</div>
            <div class="sidebar-brand-title">KIKES</div>
            <div class="sidebar-brand-subtitle">Control de Empleados</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Botón de login
        if st.button("🔐 Iniciar Sesión", use_container_width=True, type="primary"):
            st.session_state.show_login = True
            st.rerun()
        
        st.markdown("""
        <div class="sidebar-footer">
            <small>© 2025 Sistema Kikes</small>
        </div>
        """, unsafe_allow_html=True)
    
    # Contenido principal - Gestión de Turnos 2.0
    st.markdown("""
    <div class="empleado-header">
        <div style="font-size: 2.5em;">⏰</div>
        <div style="font-size: 1.5em; font-weight: 600;">Gestión de Turnos 2.0</div>
        <div style="opacity: 0.9;">Registra tu turno de trabajo</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Renderizar módulo de turnos 2.0
    gestion_turnos_2.render()


# ==================== SIDEBAR AUTENTICADO ====================

def render_sidebar_autenticado():
    """Renderiza el sidebar para usuarios autenticados"""
    
    with st.sidebar:
        # Brand/Logo area
        st.markdown("""
        <div class="sidebar-brand">
            <div class="sidebar-brand-icon">🏪</div>
            <div class="sidebar-brand-title">KIKES</div>
            <div class="sidebar-brand-subtitle">Sistema de Administración</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Info usuario logueado
        user = st.session_state.user
        if user['es_master']:
            tipo = "👑 MASTER"
        elif user.get('es_admin'):
            tipo = "🛡️ ADMIN"
        elif user.get('rol') == 'admin_negocio':
            nombre_sede = user.get('nombre_sede', 'sede')
            tipo = f"🏬 ADMIN {nombre_sede}"
        elif user['es_empleado']:
            tipo = "👷 EMPLEADOS"
        else:
            tipo = "👤 USUARIO"
        st.markdown(f"""
        <div class="user-logged">
            <div style="font-weight: 600;">{user['nombre_completo']}</div>
            <div style="opacity: 0.8; font-size: 0.85em;">@{user['username']} • {tipo}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Determinar módulos disponibles
        if user['es_master']:
            modulos_disponibles = ["CXP Supermercado", "Empleados", "Nómina", "Configuración"]
        elif user.get('rol') == 'admin_negocio':
            # Admin negocio solo ve Empleados y Nómina (con submenús limitados), SIN Dashboard
            modulos_disponibles = ["Empleados", "Nómina"]
        else:
            modulos_disponibles = [m['nombre_modulo'] for m in st.session_state.modulos_permitidos]
        
        # Agregar Dashboard al inicio si el usuario tiene acceso a algún módulo (excepto admin_negocio)
        if modulos_disponibles and user.get('rol') != 'admin_negocio':
            modulos_disponibles = ["Dashboard"] + modulos_disponibles
        
        # Crear iconos para los módulos
        iconos = {"Dashboard": "speedometer2", "CXP Supermercado": "wallet2", "Empleados": "people", "Nómina": "cash-stack", "Configuración": "gear"}
        icons_list = [iconos.get(m, "circle") for m in modulos_disponibles]
        
        # Menú de navegación principal
        if modulos_disponibles:
            selected = option_menu(
                menu_title=None,
                options=modulos_disponibles,
                icons=icons_list,
                menu_icon="cast",
                default_index=0,
                styles={
                    "container": {"padding": "0!important", "background-color": "transparent"},
                    "icon": {"color": "#4fd1c5", "font-size": "18px"},
                    "nav-link": {
                        "font-size": "14px",
                        "text-align": "left",
                        "margin": "5px 0",
                        "padding": "12px 20px",
                        "border-radius": "10px",
                        "color": "white",
                        "--hover-color": "rgba(255,255,255,0.1)"
                    },
                    "nav-link-selected": {
                        "background": "linear-gradient(90deg, rgba(79, 209, 197, 0.3) 0%, rgba(79, 209, 197, 0.1) 100%)",
                        "color": "#4fd1c5",
                        "font-weight": "600"
                    },
                }
            )
        else:
            selected = None
        
        # Submenú según la opción seleccionada
        submenu = None
        
        if selected == "CXP Supermercado":
            st.markdown("---")
            submenu = option_menu(
                menu_title="📊 CXP Supermercado",
                options=["Kikes"],
                icons=["shop"],
                default_index=0,
                styles={
                    "container": {"padding": "0!important", "background-color": "transparent"},
                    "icon": {"color": "#f093fb", "font-size": "14px"},
                    "nav-link": {
                        "font-size": "13px",
                        "text-align": "left",
                        "margin": "3px 0",
                        "padding": "10px 15px",
                        "border-radius": "8px",
                        "color": "rgba(255,255,255,0.8)",
                        "--hover-color": "rgba(255,255,255,0.1)"
                    },
                    "nav-link-selected": {
                        "background": "rgba(240, 147, 251, 0.2)",
                        "color": "#f093fb"
                    },
                }
            )
        
        elif selected == "Empleados":
            st.markdown("---")
            # Si es usuario de empleados, solo mostrar Gestión Turnos 2.0
            if user['es_empleado'] and not user['es_master'] and user.get('rol') != 'admin_negocio':
                opciones_empleados = ["Gestión Turnos 2.0"]
                iconos_emp = ["camera"]
            # Si es admin_negocio, mostrar Gestión Turnos 2.0 y Turnos de Hoy
            elif user.get('rol') == 'admin_negocio':
                opciones_empleados = ["Gestión Turnos 2.0", "Turnos de Hoy"]
                iconos_emp = ["camera", "calendar-check"]
            # Si es master, agregar opción de Turnos Hoy con fotos ampliadas
            elif user['es_master']:
                opciones_empleados = ["Gestión Turnos 2.0", "Turnos de Hoy", "Turnos Hoy (Fotos)", "Admin Turnos", "Registro", "Lista de Empleados"]
                iconos_emp = ["camera", "calendar-check", "image", "pencil-square", "person-plus", "list-ul"]
            else:
                opciones_empleados = ["Gestión Turnos 2.0", "Turnos de Hoy", "Admin Turnos", "Registro", "Lista de Empleados"]
                iconos_emp = ["camera", "calendar-check", "pencil-square", "person-plus", "list-ul"]
            
            submenu = option_menu(
                menu_title="👥 Empleados",
                options=opciones_empleados,
                icons=iconos_emp,
                default_index=0,
                styles={
                    "container": {"padding": "0!important", "background-color": "transparent"},
                    "icon": {"color": "#38ef7d", "font-size": "14px"},
                    "nav-link": {
                        "font-size": "13px",
                        "text-align": "left",
                        "margin": "3px 0",
                        "padding": "10px 15px",
                        "border-radius": "8px",
                        "color": "rgba(255,255,255,0.8)",
                        "--hover-color": "rgba(255,255,255,0.1)"
                    },
                    "nav-link-selected": {
                        "background": "rgba(56, 239, 125, 0.2)",
                        "color": "#38ef7d"
                    },
                }
            )
        
        elif selected == "Nómina":
            st.markdown("---")
            # Si es admin_negocio, solo mostrar Pago por Día y Descuentos
            if user.get('rol') == 'admin_negocio':
                opciones_nomina = ["Pago por Día", "Descuentos"]
                iconos_nom = ["cash", "cash-coin"]
            else:
                opciones_nomina = ["Pago por Día", "Liquidación", "Total Horas Día", "Horas Extra", "Descuentos"]
                iconos_nom = ["cash", "calculator", "clock-history", "hourglass-split", "cash-coin"]
            
            submenu = option_menu(
                menu_title="💰 Nómina",
                options=opciones_nomina,
                icons=iconos_nom,
                default_index=0,
                styles={
                    "container": {"padding": "0!important", "background-color": "transparent"},
                    "icon": {"color": "#ffd93d", "font-size": "14px"},
                    "nav-link": {
                        "font-size": "13px",
                        "text-align": "left",
                        "margin": "3px 0",
                        "padding": "10px 15px",
                        "border-radius": "8px",
                        "color": "rgba(255,255,255,0.8)",
                        "--hover-color": "rgba(255,255,255,0.1)"
                    },
                    "nav-link-selected": {
                        "background": "rgba(255, 217, 61, 0.2)",
                        "color": "#ffd93d"
                    },
                }
            )
        
        elif selected == "Configuración":
            st.markdown("---")
            submenu = option_menu(
                menu_title="⚙️ Configuración",
                options=["Direcciones IP", "Usuarios", "Roles", "Parámetros"],
                icons=["hdd-network", "people-fill", "person-badge", "sliders"],
                default_index=0,
                styles={
                    "container": {"padding": "0!important", "background-color": "transparent"},
                    "icon": {"color": "#ffd93d", "font-size": "14px"},
                    "nav-link": {
                        "font-size": "13px",
                        "text-align": "left",
                        "margin": "3px 0",
                        "padding": "10px 15px",
                        "border-radius": "8px",
                        "color": "rgba(255,255,255,0.8)",
                        "--hover-color": "rgba(255,255,255,0.1)"
                    },
                    "nav-link-selected": {
                        "background": "rgba(255, 217, 61, 0.2)",
                        "color": "#ffd93d"
                    },
                }
            )
        
        # Botón cerrar sesión
        st.markdown("---")
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            logout()
            st.rerun()
        
        # Footer
        st.markdown("""
        <div class="sidebar-footer">
            <small>© 2025 Sistema Kikes</small>
        </div>
        """, unsafe_allow_html=True)
        
        return selected, submenu


# ==================== MAIN ====================

def main():
    """Función principal de la aplicación"""
    
    # Inicializar sesión
    init_session_state()
    
    # Aplicar estilos
    st.markdown(MENU_STYLES, unsafe_allow_html=True)
    st.markdown(LOGIN_STYLES, unsafe_allow_html=True)
    
    # Si se pidió mostrar login
    if st.session_state.show_login:
        render_login_page()
        return
    
    # Si no está autenticado, mostrar vista de empleados
    if not st.session_state.authenticated:
        render_vista_empleados()
        return
    
    # Usuario autenticado - mostrar sidebar y contenido
    menu_principal, submenu = render_sidebar_autenticado()
    
    # Renderizar contenido según selección
    if menu_principal == "Dashboard":
        dashboard_principal.render()
    
    elif menu_principal == "CXP Supermercado":
        if submenu == "Kikes":
            kikes.render()
    
    elif menu_principal == "Empleados":
        if submenu == "Gestión Turnos 2.0":
            gestion_turnos_2.render()
        elif submenu == "Turnos de Hoy":
            turnos_hoy_empleado.render()
        elif submenu == "Turnos Hoy (Fotos)":
            turnos_hoy_fotos.render()
        elif submenu == "Admin Turnos":
            admin_turnos.render()
        elif submenu == "Registro":
            registro_empleado.render()
        elif submenu == "Lista de Empleados":
            lista_empleados.render()
    
    elif menu_principal == "Nómina":
        if submenu == "Pago por Día":
            nomina_pago_dia.render()
        elif submenu == "Liquidación":
            nomina_liquidacion.render()
        elif submenu == "Total Horas Día":
            nomina_total_horas.render()
        elif submenu == "Horas Extra":
            nomina_horas_extra.render()
        elif submenu == "Descuentos":
            nomina_descuentos.render()
    
    elif menu_principal == "Configuración":
        if submenu == "Direcciones IP":
            direcciones_ip.render()
        elif submenu == "Usuarios":
            gestion_usuarios.render()
        elif submenu == "Roles":
            gestion_roles.render()
        elif submenu == "Parámetros":
            st.title("⚙️ Parámetros")
            st.info("🚧 Módulo en construcción")


if __name__ == "__main__":
    main()
