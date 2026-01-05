"""
Módulo de Empleados - Administración de Turnos
Permite ver, modificar y eliminar turnos
"""
import streamlit as st
import pandas as pd
from datetime import datetime, date, time
import pytz
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from data_base.controler import (
    get_historial_turnos,
    get_turno_by_id,
    update_turno,
    delete_turno,
    get_all_empleados
)
from src.utils.ui_helpers import CSS_STYLES

# Timezone Colombia
TZ_COLOMBIA = pytz.timezone('America/Bogota')


# ==================== ESTILOS ====================
ADMIN_TURNOS_STYLES = """
<style>
    .turno-admin-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        border: 1px solid rgba(79, 209, 197, 0.3);
    }
    
    .turno-admin-card.abierto {
        border-left: 4px solid #38ef7d;
    }
    
    .turno-admin-card.cerrado {
        border-left: 4px solid #4facfe;
    }
    
    .turno-nombre {
        color: #4fd1c5;
        font-size: 1.1em;
        font-weight: 600;
    }
    
    .turno-info {
        color: rgba(255,255,255,0.8);
        font-size: 0.9em;
        margin: 5px 0;
    }
    
    .turno-hora {
        color: #ffd93d;
        font-weight: 500;
    }
    
    .estado-abierto {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        padding: 3px 10px;
        border-radius: 15px;
        font-size: 0.8em;
        font-weight: 600;
    }
    
    .estado-cerrado {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        padding: 3px 10px;
        border-radius: 15px;
        font-size: 0.8em;
        font-weight: 600;
    }
</style>
"""


def format_timestamp(ts, fmt="%I:%M:%S %p", default="—"):
    """Formatea un timestamp a la zona horaria de Colombia"""
    if pd.isna(ts) or ts is None:
        return default
    try:
        if ts.tzinfo is None:
            ts = pytz.UTC.localize(ts)
        return ts.astimezone(TZ_COLOMBIA).strftime(fmt)
    except Exception:
        return default


def parse_time_12h(time_str):
    """Convierte una cadena de tiempo en formato 12h a objeto time"""
    try:
        # Intentar varios formatos
        for fmt in ["%I:%M %p", "%I:%M:%S %p", "%I:%M%p", "%I:%M:%S%p"]:
            try:
                return datetime.strptime(time_str.strip().upper(), fmt).time()
            except ValueError:
                continue
        return None
    except Exception:
        return None


def render():
    """Renderiza el módulo de administración de turnos"""
    st.markdown(CSS_STYLES, unsafe_allow_html=True)
    st.markdown(ADMIN_TURNOS_STYLES, unsafe_allow_html=True)
    
    st.title("🛠️ Administración de Turnos")
    st.markdown("Gestión y modificación de turnos de empleados")
    st.markdown("---")
    
    # Tabs para diferentes vistas
    tab1, tab2 = st.tabs(["📋 Historial de Turnos", "✏️ Editar Turno"])
    
    with tab1:
        render_historial()
    
    with tab2:
        render_editar_turno()


def render_historial():
    """Renderiza el historial de turnos con filtros"""
    st.subheader("📋 Historial de Turnos")
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    
    with col1:
        fecha_inicio = st.date_input(
            "Desde:",
            value=date.today(),
            key="fecha_inicio_hist"
        )
    
    with col2:
        fecha_fin = st.date_input(
            "Hasta:",
            value=date.today(),
            key="fecha_fin_hist"
        )
    
    with col3:
        limite = st.selectbox(
            "Mostrar:",
            [25, 50, 100, 200],
            key="limite_hist"
        )
    
    # Botón de buscar
    if st.button("🔍 Buscar Turnos", use_container_width=True, type="primary"):
        st.session_state.buscar_turnos = True
    
    # Mostrar resultados
    if st.session_state.get('buscar_turnos', False) or True:
        turnos = get_historial_turnos(
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            limit=limite
        )
        
        if not turnos:
            st.info("No se encontraron turnos para los filtros seleccionados")
            return
        
        st.markdown(f"**{len(turnos)} turnos encontrados**")
        st.markdown("---")
        
        # Crear DataFrame para la tabla
        df_turnos = pd.DataFrame(turnos)
        df_display = df_turnos.copy()
        
        # Formatear horas
        df_display['hora_inicio_fmt'] = df_display['hora_inicio'].apply(
            lambda x: format_timestamp(x, "%d/%m/%Y %I:%M:%S %p")
        )
        df_display['hora_salida_fmt'] = df_display['hora_salida'].apply(
            lambda x: format_timestamp(x, "%d/%m/%Y %I:%M:%S %p") if x else "En curso..."
        )
        
        # Mostrar tabla
        st.dataframe(
            df_display[['id_turno', 'nombre_empleado', 'cedula_empleado', 'hora_inicio_fmt', 'hora_salida_fmt', 'estado']].rename(columns={
                'id_turno': 'ID',
                'nombre_empleado': 'Empleado',
                'cedula_empleado': 'Cédula',
                'hora_inicio_fmt': 'Entrada',
                'hora_salida_fmt': 'Salida',
                'estado': 'Estado'
            }),
            use_container_width=True,
            hide_index=True
        )
        
        st.markdown("---")
        st.caption("💡 Para editar o eliminar un turno, ve a la pestaña 'Editar Turno' e ingresa el ID del turno")


def render_editar_turno():
    """Renderiza el formulario para editar/eliminar turnos"""
    st.subheader("✏️ Editar o Eliminar Turno")
    
    # Input para ID del turno
    col1, col2 = st.columns([3, 1])
    
    with col1:
        id_turno = st.number_input(
            "ID del Turno:",
            min_value=1,
            step=1,
            key="id_turno_editar"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        buscar = st.button("🔍 Buscar", key="btn_buscar_turno")
    
    if buscar or st.session_state.get('turno_cargado'):
        turno = get_turno_by_id(int(id_turno))
        
        if not turno:
            st.error("❌ No se encontró un turno con ese ID")
            st.session_state.turno_cargado = False
            return
        
        st.session_state.turno_cargado = True
        
        # Mostrar información del turno
        estado_class = "abierto" if turno['hora_salida'] is None else "cerrado"
        estado_texto = "🟢 Abierto" if turno['hora_salida'] is None else "✅ Cerrado"
        
        hora_entrada = format_timestamp(turno['hora_inicio'], "%d/%m/%Y %I:%M:%S %p")
        hora_salida = format_timestamp(turno['hora_salida'], "%d/%m/%Y %I:%M:%S %p") if turno['hora_salida'] else "En curso..."
        
        st.markdown(f"""
        <div class="turno-admin-card {estado_class}">
            <div class="turno-nombre">👤 {turno['nombre_empleado']}</div>
            <div class="turno-info">📄 Cédula: {turno['cedula_empleado']}</div>
            <div class="turno-info">
                <span class="turno-hora">🟢 Entrada:</span> {hora_entrada}
            </div>
            <div class="turno-info">
                <span class="turno-hora">🔴 Salida:</span> {hora_salida}
            </div>
            <div style="margin-top: 10px;">
                <span class="estado-{estado_class}">{estado_texto}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Formulario de edición
        st.markdown("### 📝 Modificar Turno")
        st.info("💡 Ingresa la hora en formato 12 horas. Ejemplo: **02:30 PM** o **10:15 AM**")
        
        # Obtener fecha y hora actuales del turno
        if turno['hora_inicio']:
            if turno['hora_inicio'].tzinfo is None:
                hora_inicio_local = pytz.UTC.localize(turno['hora_inicio']).astimezone(TZ_COLOMBIA)
            else:
                hora_inicio_local = turno['hora_inicio'].astimezone(TZ_COLOMBIA)
            fecha_entrada_actual = hora_inicio_local.date()
            hora_entrada_actual = hora_inicio_local.strftime("%I:%M %p")
        else:
            fecha_entrada_actual = date.today()
            hora_entrada_actual = ""
        
        if turno['hora_salida']:
            if turno['hora_salida'].tzinfo is None:
                hora_salida_local = pytz.UTC.localize(turno['hora_salida']).astimezone(TZ_COLOMBIA)
            else:
                hora_salida_local = turno['hora_salida'].astimezone(TZ_COLOMBIA)
            fecha_salida_actual = hora_salida_local.date()
            hora_salida_actual = hora_salida_local.strftime("%I:%M %p")
        else:
            fecha_salida_actual = date.today()
            hora_salida_actual = ""
        
        col_e1, col_e2 = st.columns(2)
        
        with col_e1:
            st.markdown("**🟢 Hora de Entrada**")
            fecha_entrada = st.date_input(
                "Fecha entrada:",
                value=fecha_entrada_actual,
                key="fecha_entrada_edit"
            )
            hora_entrada_str = st.text_input(
                "Hora entrada (12h):",
                value=hora_entrada_actual,
                placeholder="Ej: 08:30 AM",
                key="hora_entrada_edit"
            )
        
        with col_e2:
            st.markdown("**🔴 Hora de Salida**")
            fecha_salida = st.date_input(
                "Fecha salida:",
                value=fecha_salida_actual,
                key="fecha_salida_edit"
            )
            hora_salida_str = st.text_input(
                "Hora salida (12h):",
                value=hora_salida_actual,
                placeholder="Ej: 05:00 PM (vacío si está abierto)",
                key="hora_salida_edit"
            )
        
        st.markdown("---")
        
        # Botones de acción
        col_btn1, col_btn2, col_btn3 = st.columns([2, 2, 1])
        
        with col_btn1:
            if st.button("💾 Guardar Cambios", use_container_width=True, type="primary"):
                # Validar y convertir hora de entrada
                hora_entrada_time = parse_time_12h(hora_entrada_str)
                if not hora_entrada_time:
                    st.error("❌ Formato de hora de entrada inválido. Use formato 12h (ej: 08:30 AM)")
                    return
                
                nueva_hora_inicio = datetime.combine(fecha_entrada, hora_entrada_time)
                
                # Validar y convertir hora de salida (puede estar vacía)
                nueva_hora_salida = None
                if hora_salida_str and hora_salida_str.strip():
                    hora_salida_time = parse_time_12h(hora_salida_str)
                    if not hora_salida_time:
                        st.error("❌ Formato de hora de salida inválido. Use formato 12h (ej: 05:00 PM)")
                        return
                    nueva_hora_salida = datetime.combine(fecha_salida, hora_salida_time)
                
                # Actualizar turno
                success, error = update_turno(
                    id_turno=int(id_turno),
                    hora_inicio=nueva_hora_inicio,
                    hora_salida=nueva_hora_salida
                )
                
                if success:
                    st.success("✅ Turno actualizado correctamente")
                    st.session_state.turno_cargado = False
                    st.rerun()
                else:
                    st.error(f"❌ Error al actualizar: {error}")
        
        with col_btn2:
            if st.button("🗑️ Eliminar Turno", use_container_width=True):
                st.session_state.confirmar_eliminar = True
        
        # Confirmación de eliminación
        if st.session_state.get('confirmar_eliminar', False):
            st.warning("⚠️ ¿Estás seguro de que deseas eliminar este turno? Esta acción no se puede deshacer.")
            
            col_conf1, col_conf2 = st.columns(2)
            
            with col_conf1:
                if st.button("✅ Sí, eliminar", use_container_width=True):
                    success, error = delete_turno(int(id_turno))
                    if success:
                        st.success("✅ Turno eliminado correctamente")
                        st.session_state.confirmar_eliminar = False
                        st.session_state.turno_cargado = False
                        st.rerun()
                    else:
                        st.error(f"❌ Error al eliminar: {error}")
            
            with col_conf2:
                if st.button("❌ Cancelar", use_container_width=True):
                    st.session_state.confirmar_eliminar = False
                    st.rerun()
