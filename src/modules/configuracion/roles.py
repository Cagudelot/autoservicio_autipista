"""
Módulo de Configuración - Gestión de Roles
"""
import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from data_base.controler import get_all_roles, insert_rol, update_rol, delete_rol
from src.utils.ui_helpers import CSS_STYLES


def render():
    """Renderiza la gestión de roles"""
    st.markdown(CSS_STYLES, unsafe_allow_html=True)
    
    st.title("🎭 Gestión de Roles")
    st.markdown("---")
    
    # Tabs para diferentes acciones
    tab1, tab2 = st.tabs(["📋 Lista de Roles", "➕ Nuevo Rol"])
    
    with tab1:
        render_lista_roles()
    
    with tab2:
        render_nuevo_rol()


def render_lista_roles():
    """Renderiza la lista de roles existentes"""
    roles = get_all_roles()
    
    if not roles:
        st.info("No hay roles registrados")
        return
    
    st.subheader(f"Total de roles: {len(roles)}")
    
    # Mostrar roles en cards
    for rol in roles:
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.markdown(f"### 🏷️ {rol['nombre_rol']}")
            
            with col2:
                # Botón para editar
                if st.button("✏️ Editar", key=f"edit_{rol['id_rol']}"):
                    st.session_state[f"editing_rol_{rol['id_rol']}"] = True
            
            with col3:
                # Botón para eliminar
                if st.button("🗑️ Eliminar", key=f"delete_{rol['id_rol']}"):
                    success, error = delete_rol(rol['id_rol'])
                    if success:
                        st.success(f"Rol '{rol['nombre_rol']}' eliminado correctamente")
                        st.rerun()
                    else:
                        st.error(f"Error al eliminar: {error}")
            
            # Formulario de edición (si está activo)
            if st.session_state.get(f"editing_rol_{rol['id_rol']}", False):
                with st.form(key=f"form_edit_{rol['id_rol']}"):
                    nuevo_nombre = st.text_input(
                        "Nuevo nombre",
                        value=rol['nombre_rol'],
                        key=f"input_edit_{rol['id_rol']}"
                    )
                    
                    col_save, col_cancel = st.columns(2)
                    
                    with col_save:
                        if st.form_submit_button("💾 Guardar", use_container_width=True):
                            if nuevo_nombre and nuevo_nombre.strip():
                                success, error = update_rol(rol['id_rol'], nuevo_nombre.strip())
                                if success:
                                    st.session_state[f"editing_rol_{rol['id_rol']}"] = False
                                    st.success("Rol actualizado correctamente")
                                    st.rerun()
                                else:
                                    st.error(f"Error al actualizar: {error}")
                            else:
                                st.error("El nombre no puede estar vacío")
                    
                    with col_cancel:
                        if st.form_submit_button("❌ Cancelar", use_container_width=True):
                            st.session_state[f"editing_rol_{rol['id_rol']}"] = False
                            st.rerun()
            
            st.markdown("---")


def render_nuevo_rol():
    """Renderiza el formulario para crear un nuevo rol"""
    st.subheader("Crear Nuevo Rol")
    
    with st.form(key="form_nuevo_rol", clear_on_submit=True):
        nombre_rol = st.text_input(
            "Nombre del Rol *",
            placeholder="Ej: Supervisor, Mesero, etc.",
            help="Ingrese el nombre del nuevo rol"
        )
        
        submit = st.form_submit_button(
            "➕ Crear Rol",
            use_container_width=True,
            type="primary"
        )
        
        if submit:
            if not nombre_rol or nombre_rol.strip() == "":
                st.error("❌ El nombre del rol es obligatorio")
            else:
                # Verificar si ya existe un rol con ese nombre
                roles_existentes = get_all_roles()
                nombres_existentes = [r['nombre_rol'].lower() for r in roles_existentes]
                
                if nombre_rol.strip().lower() in nombres_existentes:
                    st.error("❌ Ya existe un rol con ese nombre")
                else:
                    id_rol, error = insert_rol(nombre_rol.strip())
                    
                    if error:
                        st.error(f"❌ Error al crear el rol: {error}")
                    else:
                        st.success(f"✅ Rol '{nombre_rol.strip()}' creado exitosamente")
                        st.rerun()
    
    # Roles predeterminados como referencia
    st.markdown("---")
    st.caption("**Roles predeterminados del sistema:**")
    st.caption("Parrillero, Cocinero, Cajero, Administrador, Domiciliario")
