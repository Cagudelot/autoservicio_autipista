"""
Módulo de Empleados - Lista de empleados con edición y eliminación
"""
import streamlit as st
import sys
import os
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.settings import TIPOS_DOCUMENTO
from data_base.controler import (
    get_all_empleados_completo, get_all_sedes, get_all_roles,
    get_empleado_by_id, update_empleado, delete_empleado, check_cedula_exists_excluding
)
from src.utils.ui_helpers import CSS_STYLES


# Estilos específicos para este módulo
LISTA_STYLES = """
<style>
    .empleado-card {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        color: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    .empleado-nombre {
        font-size: 1.3em;
        font-weight: 700;
        margin-bottom: 10px;
    }
    
    .empleado-info {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-bottom: 10px;
    }
    
    .info-badge {
        background: rgba(255,255,255,0.2);
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 0.85em;
    }
    
    .sede-badge {
        background: linear-gradient(90deg, #11998e, #38ef7d);
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 0.85em;
    }
    
    .rol-badge {
        background: linear-gradient(90deg, #667eea, #764ba2);
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 0.85em;
    }
    
    .stats-container {
        display: flex;
        gap: 15px;
        margin-bottom: 20px;
    }
    
    .stat-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        padding: 15px 20px;
        text-align: center;
        color: white;
        flex: 1;
    }
    
    .stat-number {
        font-size: 2em;
        font-weight: 700;
    }
    
    .stat-label {
        font-size: 0.85em;
        opacity: 0.9;
    }
    
    .filter-container {
        background: rgba(255,255,255,0.05);
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 20px;
    }
</style>
"""


def render():
    """Renderiza la lista de empleados"""
    st.markdown(CSS_STYLES, unsafe_allow_html=True)
    st.markdown(LISTA_STYLES, unsafe_allow_html=True)
    
    st.title("👥 Lista de Empleados")
    st.markdown("---")
    
    # Inicializar estados
    if 'modo_edicion' not in st.session_state:
        st.session_state.modo_edicion = False
    if 'empleado_editar' not in st.session_state:
        st.session_state.empleado_editar = None
    if 'confirmar_eliminar' not in st.session_state:
        st.session_state.confirmar_eliminar = None
    
    # Tabs principales
    if st.session_state.modo_edicion and st.session_state.empleado_editar:
        render_editar_empleado()
    else:
        render_lista()


def render_lista():
    """Renderiza la lista de empleados con filtros"""
    # Obtener datos
    empleados = get_all_empleados_completo()
    sedes = get_all_sedes()
    roles = get_all_roles()
    
    if not empleados:
        st.info("📭 No hay empleados registrados")
        return
    
    # Estadísticas
    total = len(empleados)
    sedes_unicas = len(set(e['nombre_sede'] for e in empleados))
    roles_unicos = len(set(e['nombre_rol'] for e in empleados))
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">{total}</div>
            <div class="stat-label">Total Empleados</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="stat-box" style="background: linear-gradient(135deg, #11998e, #38ef7d);">
            <div class="stat-number">{sedes_unicas}</div>
            <div class="stat-label">Sedes</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="stat-box" style="background: linear-gradient(135deg, #f093fb, #f5576c);">
            <div class="stat-number">{roles_unicos}</div>
            <div class="stat-label">Roles</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Filtros
    with st.expander("🔍 Filtros", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            buscar = st.text_input("🔎 Buscar por nombre o cédula", key="buscar_empleado")
        
        with col2:
            opciones_sedes = ["Todas"] + [s['nombre_sede'] for s in sedes]
            filtro_sede = st.selectbox("📍 Filtrar por Sede", opciones_sedes, key="filtro_sede")
        
        with col3:
            opciones_roles = ["Todos"] + [r['nombre_rol'] for r in roles]
            filtro_rol = st.selectbox("👤 Filtrar por Rol", opciones_roles, key="filtro_rol")
    
    # Aplicar filtros
    empleados_filtrados = empleados
    
    if buscar:
        buscar_lower = buscar.lower()
        empleados_filtrados = [e for e in empleados_filtrados 
                              if buscar_lower in e['nombre_empleado'].lower() 
                              or buscar_lower in e['cedula_empleado'].lower()]
    
    if filtro_sede != "Todas":
        empleados_filtrados = [e for e in empleados_filtrados if e['nombre_sede'] == filtro_sede]
    
    if filtro_rol != "Todos":
        empleados_filtrados = [e for e in empleados_filtrados if e['nombre_rol'] == filtro_rol]
    
    # Mostrar resultados
    st.markdown(f"### 📋 Mostrando {len(empleados_filtrados)} empleado(s)")
    st.markdown("---")
    
    if not empleados_filtrados:
        st.warning("No se encontraron empleados con los filtros aplicados")
        return
    
    # Mostrar empleados en tarjetas
    for empleado in empleados_filtrados:
        render_tarjeta_empleado(empleado)


def render_tarjeta_empleado(empleado):
    """Renderiza una tarjeta de empleado con opciones de edición"""
    with st.container():
        col_info, col_acciones = st.columns([4, 1])
        
        with col_info:
            salario_fmt = f"${empleado['salario_dia']:,.0f}" if empleado['salario_dia'] else "N/A"
            celular = empleado['celular'] if empleado['celular'] else "Sin celular"
            tipo_emp = "✅ Asegurado" if empleado['tipo_empleado'] == 'asegurado' else "⚠️ No Asegurado"
            tipo_emp_color = "background: linear-gradient(90deg, #11998e, #38ef7d);" if empleado['tipo_empleado'] == 'asegurado' else "background: linear-gradient(90deg, #f5576c, #f093fb);"
            
            st.markdown(f"""
            <div class="empleado-card">
                <div class="empleado-nombre">👤 {empleado['nombre_empleado']}</div>
                <div class="empleado-info">
                    <span class="info-badge">📄 {empleado['tipo_documento']}: {empleado['cedula_empleado']}</span>
                    <span class="sede-badge">📍 {empleado['nombre_sede']}</span>
                    <span class="rol-badge">🏷️ {empleado['nombre_rol']}</span>
                </div>
                <div class="empleado-info">
                    <span class="info-badge">💰 Salario/día: {salario_fmt}</span>
                    <span class="info-badge">📱 {celular}</span>
                    <span style="{tipo_emp_color} padding: 5px 12px; border-radius: 20px; font-size: 0.85em;">{tipo_emp}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_acciones:
            st.write("")  # Espaciador
            st.write("")
            
            # Botón Editar
            if st.button("✏️ Editar", key=f"edit_{empleado['id_empleado']}", use_container_width=True):
                st.session_state.modo_edicion = True
                st.session_state.empleado_editar = empleado['id_empleado']
                st.rerun()
            
            # Botón Eliminar con confirmación
            if st.session_state.confirmar_eliminar == empleado['id_empleado']:
                st.error("¿Confirmar eliminación?")
                col_si, col_no = st.columns(2)
                with col_si:
                    if st.button("✅ Sí", key=f"confirm_del_{empleado['id_empleado']}", use_container_width=True):
                        exito, error = delete_empleado(empleado['id_empleado'])
                        if exito:
                            st.success("Empleado eliminado")
                            st.session_state.confirmar_eliminar = None
                            st.rerun()
                        else:
                            st.error(f"Error: {error}")
                with col_no:
                    if st.button("❌ No", key=f"cancel_del_{empleado['id_empleado']}", use_container_width=True):
                        st.session_state.confirmar_eliminar = None
                        st.rerun()
            else:
                if st.button("🗑️ Eliminar", key=f"del_{empleado['id_empleado']}", use_container_width=True, type="secondary"):
                    st.session_state.confirmar_eliminar = empleado['id_empleado']
                    st.rerun()
        
        st.markdown("---")


def render_editar_empleado():
    """Renderiza el formulario de edición de empleado"""
    id_empleado = st.session_state.empleado_editar
    empleado = get_empleado_by_id(id_empleado)
    
    if not empleado:
        st.error("No se encontró el empleado")
        st.session_state.modo_edicion = False
        st.session_state.empleado_editar = None
        st.rerun()
        return
    
    # Botón volver
    if st.button("⬅️ Volver a la Lista", type="secondary"):
        st.session_state.modo_edicion = False
        st.session_state.empleado_editar = None
        st.rerun()
    
    st.markdown(f"### ✏️ Editando: {empleado['nombre_empleado']}")
    st.markdown("---")
    
    # Obtener sedes y roles
    sedes = get_all_sedes()
    roles = get_all_roles()
    
    opciones_sedes = {s['nombre_sede']: s['id_sede'] for s in sedes}
    opciones_roles = {r['nombre_rol']: r['id_rol'] for r in roles}
    
    # Obtener índices actuales
    lista_sedes = list(opciones_sedes.keys())
    lista_roles = list(opciones_roles.keys())
    
    idx_sede = 0
    if empleado['id_sede']:
        for i, s in enumerate(sedes):
            if s['id_sede'] == empleado['id_sede']:
                idx_sede = i
                break
    
    idx_rol = 0
    if empleado['id_rol']:
        for i, r in enumerate(roles):
            if r['id_rol'] == empleado['id_rol']:
                idx_rol = i
                break
    
    # Índice tipo documento
    idx_tipo_doc = 0
    if empleado['tipo_documento'] in TIPOS_DOCUMENTO:
        idx_tipo_doc = TIPOS_DOCUMENTO.index(empleado['tipo_documento'])
    
    # Índice tipo empleado
    tipos_empleado = ["asegurado", "no_asegurado"]
    idx_tipo_emp = 0
    if empleado['tipo_empleado'] in tipos_empleado:
        idx_tipo_emp = tipos_empleado.index(empleado['tipo_empleado'])
    
    # Formulario
    with st.form(key="form_editar_empleado"):
        col1, col2 = st.columns(2)
        
        with col1:
            nombre = st.text_input(
                "Nombre Completo *",
                value=empleado['nombre_empleado'],
                help="Nombre completo del empleado"
            )
        
        with col2:
            sede_seleccionada = st.selectbox(
                "Sede *",
                options=lista_sedes,
                index=idx_sede,
                help="Sede donde trabaja el empleado"
            )
        
        col2a, col2b = st.columns(2)
        
        with col2a:
            tipo_documento = st.selectbox(
                "Tipo de Documento *",
                options=TIPOS_DOCUMENTO,
                index=idx_tipo_doc
            )
        
        with col2b:
            numero_documento = st.text_input(
                "Número de Documento *",
                value=empleado['cedula_empleado']
            )
        
        col3a, col3b = st.columns(2)
        
        with col3a:
            rol_seleccionado = st.selectbox(
                "Rol *",
                options=lista_roles,
                index=idx_rol
            )
        
        with col3b:
            celular = st.text_input(
                "Celular",
                value=empleado['celular'] or ""
            )
        
        col4a, col4b = st.columns(2)
        
        with col4a:
            salario_dia = st.number_input(
                "Salario por Día *",
                min_value=0,
                value=int(empleado['salario_dia']) if empleado['salario_dia'] else 0,
                step=1000,
                format="%d"
            )
        
        with col4b:
            tipo_empleado = st.selectbox(
                "Tipo de Empleado *",
                options=tipos_empleado,
                index=idx_tipo_emp,
                format_func=lambda x: "Asegurado" if x == "asegurado" else "No Asegurado",
                help="Tipo de contrato del empleado (uso interno)"
            )
        
        st.markdown("---")
        
        col_guardar, col_cancelar = st.columns(2)
        
        with col_guardar:
            guardar = st.form_submit_button("💾 Guardar Cambios", use_container_width=True, type="primary")
        
        with col_cancelar:
            cancelar = st.form_submit_button("❌ Cancelar", use_container_width=True)
        
        if guardar:
            # Validaciones
            errores = []
            
            if not nombre or nombre.strip() == "":
                errores.append("El nombre es obligatorio")
            
            if not numero_documento or numero_documento.strip() == "":
                errores.append("El número de documento es obligatorio")
            
            if salario_dia <= 0:
                errores.append("El salario debe ser mayor a 0")
            
            # Verificar cédula duplicada (excluyendo el empleado actual)
            if numero_documento and check_cedula_exists_excluding(numero_documento.strip(), id_empleado):
                errores.append("Ya existe otro empleado con ese número de documento")
            
            if errores:
                for error in errores:
                    st.error(f"❌ {error}")
            else:
                # Obtener IDs
                id_sede = opciones_sedes.get(sede_seleccionada)
                id_rol = opciones_roles.get(rol_seleccionado)
                
                # Actualizar
                exito, error = update_empleado(
                    id_empleado=id_empleado,
                    nombre_empleado=nombre.strip(),
                    tipo_documento=tipo_documento,
                    cedula_empleado=numero_documento.strip(),
                    salario_dia=int(salario_dia),
                    id_sede=id_sede,
                    id_rol=id_rol,
                    celular=celular.strip() if celular else None,
                    tipo_empleado=tipo_empleado
                )
                
                if exito:
                    st.success(f"✅ Empleado '{nombre.strip()}' actualizado correctamente")
                    st.session_state.modo_edicion = False
                    st.session_state.empleado_editar = None
                    st.rerun()
                else:
                    st.error(f"❌ Error al actualizar: {error}")
        
        if cancelar:
            st.session_state.modo_edicion = False
            st.session_state.empleado_editar = None
            st.rerun()
