"""
Módulo de Configuración - Gestión de Usuarios
"""
import streamlit as st
import pandas as pd
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from data_base.controler import (
    get_all_usuarios,
    get_usuario_by_id,
    insert_usuario,
    update_usuario,
    update_usuario_password,
    delete_usuario,
    check_username_exists,
    get_all_modulos,
    get_permisos_usuario,
    set_permisos_usuario,
    get_all_sedes
)
from src.utils.ui_helpers import CSS_STYLES


# ==================== ESTILOS ====================

USUARIOS_STYLES = """
<style>
    .user-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        padding: 20px;
        color: white;
        margin: 10px 0;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }
    
    .user-card.master {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }
    
    .user-card.empleado {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    }
    
    .user-card.admin_negocio {
        background: linear-gradient(135deg, #f2994a 0%, #f2c94c 100%);
    }
    
    .user-card.inactivo {
        background: linear-gradient(135deg, #636363 0%, #8f8f8f 100%);
        opacity: 0.7;
    }
    
    .user-nombre {
        font-size: 1.3em;
        font-weight: 700;
        margin-bottom: 5px;
    }
    
    .user-username {
        font-family: monospace;
        background: rgba(255,255,255,0.2);
        padding: 3px 10px;
        border-radius: 5px;
        display: inline-block;
    }
    
    .user-badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 15px;
        font-size: 0.8em;
        font-weight: 600;
        margin-top: 10px;
    }
    
    .badge-master {
        background: #f5576c;
        color: white;
    }
    
    .badge-empleado {
        background: #38ef7d;
        color: #1a1a2e;
    }
    
    .badge-normal {
        background: #4facfe;
        color: white;
    }
    
    .badge-admin {
        background: #ffd93d;
        color: #1a1a2e;
    }
    
    .badge-admin-negocio {
        background: #f2994a;
        color: white;
    }
    
    .user-card.admin {
        background: linear-gradient(135deg, #f5af19 0%, #f12711 100%);
    }
    
    .user-sede {
        background: rgba(255,255,255,0.2);
        padding: 3px 10px;
        border-radius: 5px;
        display: inline-block;
        margin-top: 5px;
        font-size: 0.9em;
    }
    
    .usuarios-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        border-radius: 15px;
        padding: 25px;
        color: white;
        text-align: center;
        margin-bottom: 20px;
    }
</style>
"""


def render():
    """Renderiza el módulo de gestión de usuarios"""
    st.markdown(CSS_STYLES, unsafe_allow_html=True)
    st.markdown(USUARIOS_STYLES, unsafe_allow_html=True)
    
    st.title("👥 Gestión de Usuarios")
    st.markdown("---")
    
    # Header
    st.markdown("""
    <div class="usuarios-header">
        <div style="font-size: 3em; margin-bottom: 10px;">🔐</div>
        <div style="font-size: 1.5em; font-weight: 600;">Control de Acceso</div>
        <div style="opacity: 0.8; margin-top: 5px;">Administra usuarios y permisos del sistema</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["📋 Usuarios", "➕ Crear Usuario", "🔑 Permisos"])
    
    with tab1:
        render_lista_usuarios()
    
    with tab2:
        render_formulario_usuario()
    
    with tab3:
        render_permisos()


def render_lista_usuarios():
    """Renderiza la lista de usuarios"""
    
    # Botón actualizar
    col_space, col_btn = st.columns([5, 1])
    with col_btn:
        if st.button("🔄 Actualizar", key="refresh_usuarios"):
            st.rerun()
    
    usuarios = get_all_usuarios()
    
    if usuarios:
        # Resumen
        total = len(usuarios)
        masters = sum(1 for u in usuarios if u['es_master'])
        activos = sum(1 for u in usuarios if u['activo'])
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📊 Total Usuarios", total)
        with col2:
            st.metric("👑 Masters", masters)
        with col3:
            st.metric("✅ Activos", activos)
        
        st.markdown("---")
        
        # Lista de usuarios
        for user in usuarios:
            if user['es_master']:
                card_class = "master"
                badge_class = "badge-master"
                badge_text = "👑 MASTER"
            elif user.get('rol') == 'admin_negocio':
                card_class = "admin_negocio"
                badge_class = "badge-admin-negocio"
                badge_text = f"🏪 ADMIN NEGOCIO"
            elif user.get('es_admin'):
                card_class = "admin"
                badge_class = "badge-admin"
                badge_text = "🛡️ ADMIN"
            elif user['es_empleado']:
                card_class = "empleado"
                badge_class = "badge-empleado"
                badge_text = "👷 EMPLEADOS"
            else:
                card_class = ""
                badge_class = "badge-normal"
                badge_text = "👤 NORMAL"
            
            if not user['activo']:
                card_class = "inactivo"
            
            col_card, col_actions = st.columns([3, 1])
            
            with col_card:
                estado = "✅ Activo" if user['activo'] else "❌ Inactivo"
                sede_info = f"<div class='user-sede'>📍 {user.get('nombre_sede', 'Sin sede')}</div>" if user.get('rol') == 'admin_negocio' and user.get('nombre_sede') else ""
                st.markdown(f"""
                <div class="user-card {card_class}">
                    <div class="user-nombre">{user['nombre_completo']}</div>
                    <div class="user-username">@{user['username']}</div>
                    {sede_info}
                    <div style="margin-top: 10px; opacity: 0.9;">{estado}</div>
                    <span class="user-badge {badge_class}">{badge_text}</span>
                </div>
                """, unsafe_allow_html=True)
            
            with col_actions:
                st.write("")
                st.write("")
                
                # Editar usuario
                with st.expander(f"✏️ Editar #{user['id_usuario']}"):
                    nuevo_nombre = st.text_input(
                        "Nombre",
                        value=user['nombre_completo'],
                        key=f"nombre_{user['id_usuario']}"
                    )
                    nuevo_username = st.text_input(
                        "Username",
                        value=user['username'],
                        key=f"username_{user['id_usuario']}"
                    )
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        es_empleado = st.checkbox(
                            "Es empleado",
                            value=user['es_empleado'],
                            key=f"emp_{user['id_usuario']}",
                            disabled=user['es_master']
                        )
                    with col_b:
                        activo = st.checkbox(
                            "Activo",
                            value=user['activo'],
                            key=f"act_{user['id_usuario']}",
                            disabled=user['es_master']
                        )
                    
                    if st.button("💾 Guardar", key=f"save_{user['id_usuario']}", use_container_width=True):
                        if check_username_exists(nuevo_username, user['id_usuario']):
                            st.error("Username ya existe")
                        else:
                            success, error = update_usuario(
                                user['id_usuario'],
                                username=nuevo_username,
                                nombre_completo=nuevo_nombre,
                                es_empleado=es_empleado,
                                activo=activo
                            )
                            if success:
                                st.success("Usuario actualizado")
                                st.rerun()
                            else:
                                st.error(f"Error: {error}")
                
                # Cambiar contraseña
                with st.expander(f"🔑 Contraseña"):
                    nueva_pwd = st.text_input(
                        "Nueva contraseña",
                        type="password",
                        key=f"pwd_{user['id_usuario']}"
                    )
                    confirmar_pwd = st.text_input(
                        "Confirmar",
                        type="password",
                        key=f"pwd_conf_{user['id_usuario']}"
                    )
                    
                    if st.button("🔄 Cambiar", key=f"chpwd_{user['id_usuario']}", use_container_width=True):
                        if not nueva_pwd:
                            st.error("Ingresa una contraseña")
                        elif nueva_pwd != confirmar_pwd:
                            st.error("Las contraseñas no coinciden")
                        elif len(nueva_pwd) < 6:
                            st.error("Mínimo 6 caracteres")
                        else:
                            success, error = update_usuario_password(user['id_usuario'], nueva_pwd)
                            if success:
                                st.success("Contraseña actualizada")
                            else:
                                st.error(f"Error: {error}")
                
                # Eliminar (solo si no es master)
                if not user['es_master']:
                    if st.button("🗑️ Eliminar", key=f"del_{user['id_usuario']}", use_container_width=True):
                        success, error = delete_usuario(user['id_usuario'])
                        if success:
                            st.success("Usuario eliminado")
                            st.rerun()
                        else:
                            st.error(f"Error: {error}")
    else:
        st.info("📭 No hay usuarios registrados")


def render_formulario_usuario():
    """Renderiza el formulario para crear un nuevo usuario"""
    st.subheader("➕ Crear Nuevo Usuario")
    
    # Estado para mensajes
    if 'usuario_msg' not in st.session_state:
        st.session_state.usuario_msg = None
    
    if st.session_state.usuario_msg:
        msg_type, msg_text = st.session_state.usuario_msg
        if msg_type == "success":
            st.success(msg_text)
        else:
            st.error(msg_text)
        st.session_state.usuario_msg = None
    
    # Obtener sedes para admin_negocio
    sedes = get_all_sedes()
    sedes_opciones = {s['nombre_sede']: s['id_sede'] for s in sedes}
    
    with st.form(key="form_nuevo_usuario", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            nombre_completo = st.text_input(
                "👤 Nombre Completo *",
                placeholder="Ej: Juan Pérez"
            )
            username = st.text_input(
                "📝 Nombre de Usuario *",
                placeholder="Ej: jperez"
            )
        
        with col2:
            password = st.text_input(
                "🔑 Contraseña *",
                type="password",
                placeholder="Mínimo 6 caracteres"
            )
            password_confirm = st.text_input(
                "🔑 Confirmar Contraseña *",
                type="password"
            )
        
        st.markdown("**Tipo de Usuario:**")
        tipo_usuario = st.radio(
            "Selecciona el tipo de usuario:",
            options=["Normal", "Empleados", "Admin Negocio", "Administrador", "Master"],
            horizontal=True,
            help="""
            👤 Normal: Permisos personalizados | 
            👷 Empleados: Solo Control de Turnos | 
            🏪 Admin Negocio: Gestión turnos y pagos de una sede | 
            🛡️ Admin: Todo excepto Config y Nómina | 
            👑 Master: Acceso total
            """
        )
        
        # Selector de sede (se usa solo para Admin Negocio)
        st.markdown("**📍 Sede Asignada** *(requerido para Admin Negocio)*")
        sede_seleccionada = st.selectbox(
            "Selecciona la sede que administrará este usuario",
            options=list(sedes_opciones.keys()),
            help="El Admin Negocio solo podrá ver y gestionar datos de esta sede"
        )
        id_sede_seleccionada = sedes_opciones.get(sede_seleccionada)
        
        es_empleado = tipo_usuario == "Empleados"
        es_admin = tipo_usuario == "Administrador"
        es_master = tipo_usuario == "Master"
        es_admin_negocio = tipo_usuario == "Admin Negocio"
        
        st.markdown("---")
        
        submit = st.form_submit_button("💾 Crear Usuario", use_container_width=True, type="primary")
        
        if submit:
            errores = []
            
            if not nombre_completo or nombre_completo.strip() == "":
                errores.append("El nombre es obligatorio")
            
            if not username or username.strip() == "":
                errores.append("El username es obligatorio")
            elif len(username) < 3:
                errores.append("Username debe tener mínimo 3 caracteres")
            elif check_username_exists(username.strip()):
                errores.append("Este username ya está en uso")
            
            if not password:
                errores.append("La contraseña es obligatoria")
            elif len(password) < 6:
                errores.append("La contraseña debe tener mínimo 6 caracteres")
            elif password != password_confirm:
                errores.append("Las contraseñas no coinciden")
            
            if es_admin_negocio and not id_sede_seleccionada:
                errores.append("Debes seleccionar una sede para Admin Negocio")
            
            if errores:
                for error in errores:
                    st.error(f"❌ {error}")
            else:
                # Determinar rol
                rol = 'normal'
                if es_master:
                    rol = 'master'
                elif es_admin:
                    rol = 'admin'
                elif es_admin_negocio:
                    rol = 'admin_negocio'
                elif es_empleado:
                    rol = 'empleado'
                
                id_usuario, error = insert_usuario(
                    username=username.strip().lower(),
                    password=password,
                    nombre_completo=nombre_completo.strip(),
                    es_master=es_master,
                    es_empleado=es_empleado,
                    es_admin=es_admin,
                    rol=rol,
                    id_sede=id_sede_seleccionada if es_admin_negocio else None
                )
                
                if error:
                    st.session_state.usuario_msg = ("error", f"Error al crear: {error}")
                else:
                    # Asignar permisos según rol
                    modulos = get_all_modulos()
                    
                    if es_master:
                        # Master: todos los permisos
                        permisos = [{'id_modulo': m['id_modulo'], 'puede_ver': True, 'puede_editar': True} for m in modulos]
                        set_permisos_usuario(id_usuario, permisos)
                    elif es_admin:
                        # Admin: todo excepto Configuración y Nómina
                        permisos = []
                        for m in modulos:
                            if m['nombre_modulo'] not in ['Configuración', 'Nómina']:
                                permisos.append({'id_modulo': m['id_modulo'], 'puede_ver': True, 'puede_editar': True})
                        set_permisos_usuario(id_usuario, permisos)
                    elif es_admin_negocio:
                        # Admin Negocio: Empleados (gestión turnos, turnos hoy), Nómina (solo pago día y descuentos limitados)
                        permisos = []
                        for m in modulos:
                            if m['nombre_modulo'] == 'Empleados':
                                permisos.append({'id_modulo': m['id_modulo'], 'puede_ver': True, 'puede_editar': True})
                            elif m['nombre_modulo'] == 'Nómina':
                                permisos.append({'id_modulo': m['id_modulo'], 'puede_ver': True, 'puede_editar': False})
                        set_permisos_usuario(id_usuario, permisos)
                    elif es_empleado:
                        modulos = get_all_modulos()
                        permisos = []
                        for m in modulos:
                            if m['nombre_modulo'] == 'Empleados':
                                permisos.append({'id_modulo': m['id_modulo'], 'puede_ver': True, 'puede_editar': False})
                        set_permisos_usuario(id_usuario, permisos)
                    
                    st.session_state.usuario_msg = ("success", f"✅ Usuario '{username}' creado exitosamente")
                
                st.rerun()


def render_permisos():
    """Renderiza la gestión de permisos de usuarios"""
    st.subheader("🔑 Gestión de Permisos")
    st.markdown("Configura qué módulos puede ver cada usuario")
    
    # Seleccionar usuario
    usuarios = get_all_usuarios()
    
    if not usuarios:
        st.warning("No hay usuarios para configurar")
        return
    
    opciones_usuarios = {f"{u['nombre_completo']} (@{u['username']})": u['id_usuario'] for u in usuarios}
    
    usuario_seleccionado = st.selectbox(
        "Selecciona un usuario:",
        options=list(opciones_usuarios.keys())
    )
    
    id_usuario = opciones_usuarios[usuario_seleccionado]
    user_data = get_usuario_by_id(id_usuario)
    
    if user_data['es_master']:
        st.info("👑 Este usuario es MASTER y tiene acceso total. No se pueden modificar sus permisos.")
        return
    
    st.markdown("---")
    st.markdown("### Módulos Disponibles")
    
    # Obtener módulos y permisos actuales
    permisos = get_permisos_usuario(id_usuario)
    modulos = get_all_modulos()
    
    # Crear formulario de permisos
    nuevos_permisos = []
    
    for modulo in modulos:
        perm_actual = next((p for p in permisos if p['id_modulo'] == modulo['id_modulo']), None)
        
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            st.markdown(f"**{modulo['nombre_modulo']}** - {modulo['descripcion']}")
        
        with col2:
            puede_ver = st.checkbox(
                "Ver",
                value=perm_actual['puede_ver'] if perm_actual else False,
                key=f"ver_{modulo['id_modulo']}"
            )
        
        with col3:
            puede_editar = st.checkbox(
                "Editar",
                value=perm_actual['puede_editar'] if perm_actual else False,
                key=f"edit_{modulo['id_modulo']}",
                disabled=not puede_ver
            )
        
        nuevos_permisos.append({
            'id_modulo': modulo['id_modulo'],
            'puede_ver': puede_ver,
            'puede_editar': puede_editar if puede_ver else False
        })
    
    st.markdown("---")
    
    if st.button("💾 Guardar Permisos", use_container_width=True, type="primary"):
        success, error = set_permisos_usuario(id_usuario, nuevos_permisos)
        if success:
            st.success("✅ Permisos actualizados correctamente")
            st.rerun()
        else:
            st.error(f"Error: {error}")
