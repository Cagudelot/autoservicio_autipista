"""
Módulo de Empleados - Gestión de Turnos (Ingreso manual, modificación y historial)
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, time, date
import pytz
import sys
import os

# Zona horaria Colombia
TZ_COLOMBIA = pytz.timezone('America/Bogota')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from data_base.controler import (
    get_all_empleados_activos,
    insert_turno_manual,
    update_turno,
    cerrar_turno_abierto,
    delete_turno,
    get_turnos_abiertos,
    get_historial_turnos,
    get_turno_by_id
)
from src.utils.ui_helpers import CSS_STYLES


# ==================== ESTILOS ====================

GESTION_STYLES = """
<style>
    .gestion-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        padding: 25px;
        color: white;
        text-align: center;
        margin-bottom: 20px;
    }
    
    .gestion-header-icon {
        font-size: 3em;
        margin-bottom: 10px;
    }
    
    .gestion-header-title {
        font-size: 1.5em;
        font-weight: 600;
    }
    
    .turno-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px;
        padding: 15px;
        margin: 10px 0;
    }
    
    .turno-card.abierto {
        border-left: 4px solid #38ef7d;
    }
    
    .turno-card.cerrado {
        border-left: 4px solid #4facfe;
    }
    
    .turno-empleado {
        font-weight: 600;
        font-size: 1.1em;
        color: #4fd1c5;
    }
    
    .turno-info {
        color: rgba(255,255,255,0.7);
        font-size: 0.9em;
        margin-top: 5px;
    }
    
    .estado-badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 15px;
        font-size: 0.8em;
        font-weight: 600;
    }
    
    .estado-abierto {
        background-color: #38ef7d;
        color: #1a1a2e;
    }
    
    .estado-cerrado {
        background-color: #4facfe;
        color: white;
    }
</style>
"""


def render():
    """Renderiza el módulo de gestión de turnos"""
    st.markdown(CSS_STYLES, unsafe_allow_html=True)
    st.markdown(GESTION_STYLES, unsafe_allow_html=True)
    
    st.title("🛠️ Gestión de Turnos")
    st.markdown("---")
    
    # Header
    st.markdown("""
    <div class="gestion-header">
        <div class="gestion-header-icon">⚙️</div>
        <div class="gestion-header-title">Panel de Administración de Turnos</div>
        <div style="opacity: 0.8; margin-top: 5px;">Ingreso manual, modificación y control de turnos</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Tabs principales
    tab1, tab2, tab3 = st.tabs([
        "➕ Ingresar Turno Manual", 
        "🔓 Turnos Abiertos", 
        "📜 Historial de Turnos"
    ])
    
    with tab1:
        render_ingreso_manual()
    
    with tab2:
        render_turnos_abiertos()
    
    with tab3:
        render_historial()


def render_ingreso_manual():
    """Renderiza el formulario de ingreso manual de turnos"""
    st.subheader("➕ Registrar Turno Manualmente")
    st.markdown("Ingresa los datos del turno que deseas registrar")
    
    # Obtener empleados
    empleados = get_all_empleados_activos()
    
    if not empleados:
        st.warning("⚠️ No hay empleados registrados. Registra empleados primero.")
        return
    
    # Crear opciones para el selectbox
    opciones_empleados = {f"{e['nombre_empleado']} ({e['cedula_empleado']})": e['id_empleado'] for e in empleados}
    
    # Inicializar estado para mensajes
    if 'turno_manual_msg' not in st.session_state:
        st.session_state.turno_manual_msg = None
    
    # Mostrar mensaje si existe
    if st.session_state.turno_manual_msg:
        msg_type, msg_text = st.session_state.turno_manual_msg
        if msg_type == "success":
            st.success(msg_text)
        else:
            st.error(msg_text)
        st.session_state.turno_manual_msg = None
    
    with st.form(key="form_turno_manual", clear_on_submit=True):
        # Empleado
        empleado_seleccionado = st.selectbox(
            "👤 Empleado *",
            options=list(opciones_empleados.keys()),
            index=0
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🟢 Entrada**")
            fecha_entrada = st.date_input(
                "Fecha de entrada *",
                value=date.today(),
                key="fecha_entrada"
            )
            hora_entrada = st.time_input(
                "Hora de entrada *",
                value=time(8, 0),
                key="hora_entrada"
            )
        
        with col2:
            st.markdown("**🔴 Salida (opcional)**")
            incluir_salida = st.checkbox("Incluir hora de salida", value=False)
            fecha_salida = st.date_input(
                "Fecha de salida",
                value=date.today(),
                key="fecha_salida",
                disabled=not incluir_salida
            )
            hora_salida = st.time_input(
                "Hora de salida",
                value=time(17, 0),
                key="hora_salida",
                disabled=not incluir_salida
            )
        
        st.markdown("---")
        
        submit = st.form_submit_button(
            "💾 Registrar Turno",
            use_container_width=True,
            type="primary"
        )
        
        if submit:
            # Construir datetime de entrada
            dt_entrada = datetime.combine(fecha_entrada, hora_entrada)
            
            # Construir datetime de salida si aplica
            dt_salida = None
            if incluir_salida:
                dt_salida = datetime.combine(fecha_salida, hora_salida)
                
                # Validar que la salida sea posterior a la entrada
                if dt_salida <= dt_entrada:
                    st.error("❌ La hora de salida debe ser posterior a la hora de entrada")
                    return
            
            # Obtener id del empleado
            id_empleado = opciones_empleados[empleado_seleccionado]
            
            # Insertar turno
            id_turno, error = insert_turno_manual(id_empleado, dt_entrada, dt_salida)
            
            if error:
                st.session_state.turno_manual_msg = ("error", f"Error al registrar: {error}")
            else:
                nombre = empleado_seleccionado.split(" (")[0]
                st.session_state.turno_manual_msg = ("success", f"✅ Turno registrado para {nombre}")
            
            st.rerun()


def render_turnos_abiertos():
    """Renderiza la lista de turnos abiertos con opción de cerrarlos"""
    st.subheader("🔓 Turnos Abiertos")
    st.markdown("Turnos sin hora de salida registrada")
    
    # Botón actualizar
    col_space, col_btn = st.columns([5, 1])
    with col_btn:
        if st.button("🔄 Actualizar", key="refresh_abiertos"):
            st.rerun()
    
    turnos_abiertos = get_turnos_abiertos()
    
    if not turnos_abiertos:
        st.info("📭 No hay turnos abiertos actualmente")
        return
    
    st.markdown(f"**Total:** {len(turnos_abiertos)} turno(s) abierto(s)")
    st.markdown("---")
    
    for turno in turnos_abiertos:
        with st.container():
            col_info, col_actions = st.columns([3, 2])
            
            with col_info:
                hora_entrada = turno['hora_inicio'].strftime("%d/%m/%Y %H:%M") if turno['hora_inicio'] else "—"
                tiempo_transcurrido = ""
                if turno['hora_inicio']:
                    now = datetime.now(TZ_COLOMBIA)
                    delta = now - turno['hora_inicio']
                    horas = int(delta.total_seconds() // 3600)
                    minutos = int((delta.total_seconds() % 3600) // 60)
                    tiempo_transcurrido = f"⏱️ {horas}h {minutos}m trabajando"
                
                st.markdown(f"""
                <div class="turno-card abierto">
                    <div class="turno-empleado">👤 {turno['nombre_empleado']}</div>
                    <div class="turno-info">📄 CC: {turno['cedula_empleado']}</div>
                    <div class="turno-info">🟢 Entrada: {hora_entrada}</div>
                    <div class="turno-info">{tiempo_transcurrido}</div>
                    <span class="estado-badge estado-abierto">Abierto</span>
                </div>
                """, unsafe_allow_html=True)
            
            with col_actions:
                st.write("")  # Espaciado
                
                # Formulario para cerrar turno
                with st.expander(f"🔴 Cerrar turno #{turno['id_turno']}"):
                    fecha_cierre = st.date_input(
                        "Fecha salida",
                        value=date.today(),
                        key=f"fecha_cierre_{turno['id_turno']}"
                    )
                    hora_cierre = st.time_input(
                        "Hora salida",
                        value=datetime.now(TZ_COLOMBIA).time(),
                        key=f"hora_cierre_{turno['id_turno']}"
                    )
                    
                    if st.button("✅ Cerrar", key=f"cerrar_{turno['id_turno']}", use_container_width=True):
                        dt_cierre = datetime.combine(fecha_cierre, hora_cierre)
                        
                        if dt_cierre <= turno['hora_inicio']:
                            st.error("La salida debe ser posterior a la entrada")
                        else:
                            success, error = cerrar_turno_abierto(turno['id_turno'], dt_cierre)
                            if success:
                                st.success("Turno cerrado")
                                st.rerun()
                            else:
                                st.error(f"Error: {error}")
                
                # Botón eliminar
                if st.button("🗑️ Eliminar", key=f"del_abierto_{turno['id_turno']}", use_container_width=True):
                    success, error = delete_turno(turno['id_turno'])
                    if success:
                        st.success("Turno eliminado")
                        st.rerun()
                    else:
                        st.error(f"Error: {error}")
            
            st.markdown("---")


def render_historial():
    """Renderiza el historial de turnos con filtros y opciones de edición"""
    st.subheader("📜 Historial de Turnos")
    st.markdown("Consulta y modifica turnos anteriores")
    
    # Filtros
    col_filtro1, col_filtro2, col_filtro3 = st.columns(3)
    
    # Obtener empleados para filtro
    empleados = get_all_empleados_activos()
    opciones_empleados = {"Todos": None}
    opciones_empleados.update({f"{e['nombre_empleado']} ({e['cedula_empleado']})": e['id_empleado'] for e in empleados})
    
    with col_filtro1:
        fecha_desde = st.date_input(
            "Desde",
            value=date.today() - timedelta(days=30),
            key="hist_fecha_desde"
        )
    
    with col_filtro2:
        fecha_hasta = st.date_input(
            "Hasta",
            value=date.today(),
            key="hist_fecha_hasta"
        )
    
    with col_filtro3:
        empleado_filtro = st.selectbox(
            "Empleado",
            options=list(opciones_empleados.keys()),
            key="hist_empleado"
        )
    
    col_space, col_btn = st.columns([5, 1])
    with col_btn:
        buscar = st.button("🔍 Buscar", key="buscar_historial")
    
    st.markdown("---")
    
    # Obtener historial
    id_empleado_filtro = opciones_empleados[empleado_filtro]
    historial = get_historial_turnos(
        fecha_inicio=fecha_desde,
        fecha_fin=fecha_hasta,
        id_empleado=id_empleado_filtro,
        limit=200
    )
    
    if not historial:
        st.info("📭 No se encontraron turnos con los filtros seleccionados")
        return
    
    st.markdown(f"**Total:** {len(historial)} turno(s) encontrado(s)")
    
    # Crear DataFrame para mostrar
    df = pd.DataFrame(historial)
    df['hora_inicio'] = df['hora_inicio'].apply(
        lambda x: x.strftime("%d/%m/%Y %H:%M") if pd.notna(x) else "—"
    )
    df['hora_salida'] = df['hora_salida'].apply(
        lambda x: x.strftime("%d/%m/%Y %H:%M") if pd.notna(x) else "Sin cerrar"
    )
    
    df_display = df[['id_turno', 'nombre_empleado', 'cedula_empleado', 'hora_inicio', 'hora_salida', 'estado']].copy()
    df_display.columns = ['ID', 'Empleado', 'Cédula', 'Entrada', 'Salida', 'Estado']
    
    st.dataframe(df_display, use_container_width=True, hide_index=True)
    
    # Sección de edición
    st.markdown("---")
    st.subheader("✏️ Editar Turno")
    
    col_edit1, col_edit2 = st.columns([1, 3])
    
    with col_edit1:
        id_turno_editar = st.number_input(
            "ID del turno a editar",
            min_value=1,
            step=1,
            key="id_turno_editar"
        )
        
        cargar_turno = st.button("📥 Cargar Turno", key="cargar_turno")
    
    with col_edit2:
        # Inicializar estado
        if 'turno_cargado' not in st.session_state:
            st.session_state.turno_cargado = None
        
        if cargar_turno:
            turno = get_turno_by_id(id_turno_editar)
            if turno:
                st.session_state.turno_cargado = turno
            else:
                st.error(f"No se encontró turno con ID {id_turno_editar}")
                st.session_state.turno_cargado = None
        
        if st.session_state.turno_cargado:
            turno = st.session_state.turno_cargado
            
            st.info(f"**Empleado:** {turno['nombre_empleado']} ({turno['cedula_empleado']})")
            
            col_e1, col_e2 = st.columns(2)
            
            with col_e1:
                st.markdown("**🟢 Entrada**")
                nueva_fecha_entrada = st.date_input(
                    "Nueva fecha entrada",
                    value=turno['hora_inicio'].date() if turno['hora_inicio'] else date.today(),
                    key="edit_fecha_entrada"
                )
                nueva_hora_entrada = st.time_input(
                    "Nueva hora entrada",
                    value=turno['hora_inicio'].time() if turno['hora_inicio'] else time(8, 0),
                    key="edit_hora_entrada"
                )
            
            with col_e2:
                st.markdown("**🔴 Salida**")
                tiene_salida = turno['hora_salida'] is not None
                nueva_fecha_salida = st.date_input(
                    "Nueva fecha salida",
                    value=turno['hora_salida'].date() if tiene_salida else date.today(),
                    key="edit_fecha_salida"
                )
                nueva_hora_salida = st.time_input(
                    "Nueva hora salida",
                    value=turno['hora_salida'].time() if tiene_salida else time(17, 0),
                    key="edit_hora_salida"
                )
                aplicar_salida = st.checkbox(
                    "Aplicar/modificar salida",
                    value=tiene_salida,
                    key="edit_aplicar_salida"
                )
            
            col_btn1, col_btn2, col_btn3 = st.columns(3)
            
            with col_btn1:
                if st.button("💾 Guardar Cambios", key="guardar_edicion", use_container_width=True, type="primary"):
                    nueva_dt_entrada = datetime.combine(nueva_fecha_entrada, nueva_hora_entrada)
                    nueva_dt_salida = None
                    
                    if aplicar_salida:
                        nueva_dt_salida = datetime.combine(nueva_fecha_salida, nueva_hora_salida)
                        if nueva_dt_salida <= nueva_dt_entrada:
                            st.error("La salida debe ser posterior a la entrada")
                            st.stop()
                    
                    success, error = update_turno(
                        turno['id_turno'],
                        hora_inicio=nueva_dt_entrada,
                        hora_salida=nueva_dt_salida
                    )
                    
                    if success:
                        st.success("✅ Turno actualizado correctamente")
                        st.session_state.turno_cargado = None
                        st.rerun()
                    else:
                        st.error(f"Error: {error}")
            
            with col_btn2:
                if st.button("🗑️ Eliminar Turno", key="eliminar_turno", use_container_width=True):
                    success, error = delete_turno(turno['id_turno'])
                    if success:
                        st.success("Turno eliminado")
                        st.session_state.turno_cargado = None
                        st.rerun()
                    else:
                        st.error(f"Error: {error}")
            
            with col_btn3:
                if st.button("❌ Cancelar", key="cancelar_edicion", use_container_width=True):
                    st.session_state.turno_cargado = None
                    st.rerun()
