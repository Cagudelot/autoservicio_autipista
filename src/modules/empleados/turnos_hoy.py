"""
Módulo de Empleados - Turnos de Hoy (Vista administrativa)
Vista mejorada con agrupación por sede y filtros por rol
"""
import streamlit as st
import pandas as pd
from datetime import datetime
import sys
import os
import base64
import pytz

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.utils.ui_helpers import get_db_connection, CSS_STYLES, format_currency

# Timezone Colombia
TZ_COLOMBIA = pytz.timezone('America/Bogota')


def format_timestamp(ts, fmt="%I:%M:%S %p", default="—"):
    """Formatea un timestamp a la zona horaria de Colombia"""
    if pd.isna(ts):
        return default
    try:
        if ts.tzinfo is None:
            ts = pytz.UTC.localize(ts)
        return ts.astimezone(TZ_COLOMBIA).strftime(fmt)
    except Exception:
        return default


# ==================== ESTILOS ====================

TURNOS_HOY_STYLES = """
<style>
    .turno-resumen-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        padding: 20px;
        color: white;
        text-align: center;
        margin: 10px 0;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }
    
    .turno-resumen-card.activos {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    }
    
    .turno-resumen-card.completados {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    }
    
    .turno-resumen-valor {
        font-size: 2.5em;
        font-weight: 700;
        margin: 10px 0;
    }
    
    .turno-resumen-label {
        font-size: 0.9em;
        opacity: 0.9;
    }
    
    .sede-header {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border-radius: 15px;
        padding: 15px 20px;
        margin: 20px 0 15px 0;
        border-left: 4px solid #ffd93d;
    }
    
    .sede-title {
        color: #ffd93d;
        font-size: 1.3em;
        font-weight: 700;
        margin: 0;
    }
    
    .sede-stats {
        color: rgba(255,255,255,0.8);
        font-size: 0.9em;
        margin-top: 5px;
    }
    
    .turno-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border-radius: 15px;
        padding: 15px;
        margin: 10px 0;
        border: 1px solid rgba(79, 209, 197, 0.3);
        min-height: 140px;
    }
    
    .turno-card-activo {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        border: none;
    }
    
    .turno-card-completado {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        border: none;
    }
    
    .turno-foto {
        width: 70px;
        height: 70px;
        border-radius: 50%;
        object-fit: cover;
        border: 3px solid rgba(255,255,255,0.5);
    }
    
    .turno-info {
        color: white;
        flex: 1;
    }
    
    .turno-nombre {
        font-size: 1em;
        font-weight: 600;
        margin-bottom: 3px;
    }
    
    .turno-rol {
        background: rgba(255,255,255,0.2);
        padding: 2px 8px;
        border-radius: 10px;
        font-size: 0.75em;
        display: inline-block;
        margin-bottom: 5px;
    }
    
    .turno-cedula {
        opacity: 0.9;
        font-size: 0.85em;
    }
    
    .turno-hora {
        margin-top: 5px;
        font-size: 0.85em;
    }
    
    .filtro-section {
        background: rgba(255,255,255,0.05);
        border-radius: 10px;
        padding: 10px;
        margin: 10px 0;
    }
</style>
"""


# ==================== FUNCIONES DE DATOS ====================

def get_turnos_hoy(id_sede_filtro=None):
    """Obtiene todos los turnos del día con sede y rol, opcionalmente filtrados por sede"""
    conn = get_db_connection()
    
    base_query = """
        SELECT 
            t.id_turno,
            e.nombre_empleado,
            e.cedula_empleado,
            t.hora_inicio,
            t.hora_salida,
            t.foto_entrada,
            t.foto_salida,
            COALESCE(s.nombre_sede, 'Sin Sede') as nombre_sede,
            COALESCE(r.nombre_rol, 'Sin Rol') as nombre_rol,
            CASE 
                WHEN t.hora_salida IS NULL THEN 'En curso'
                ELSE 'Completado'
            END as estado
        FROM turnos t
        INNER JOIN empleados e ON t.id_empleado = e.id_empleado
        LEFT JOIN sedes s ON e.id_sede = s.id_sede
        LEFT JOIN roles r ON e.id_rol = r.id_rol
        WHERE DATE(t.hora_inicio AT TIME ZONE 'America/Bogota') = (CURRENT_TIMESTAMP AT TIME ZONE 'America/Bogota')::DATE
    """
    
    if id_sede_filtro:
        base_query += " AND e.id_sede = %s"
        base_query += " ORDER BY s.nombre_sede, t.hora_inicio DESC"
        df = pd.read_sql(base_query, conn, params=(id_sede_filtro,))
    else:
        base_query += " ORDER BY s.nombre_sede, t.hora_inicio DESC"
        df = pd.read_sql(base_query, conn)
    
    conn.close()
    return df


def get_resumen_turnos_hoy(id_sede_filtro=None):
    """Obtiene resumen de turnos del día, opcionalmente filtrado por sede"""
    conn = get_db_connection()
    
    if id_sede_filtro:
        query = """
            SELECT 
                COUNT(*) as total,
                COUNT(*) FILTER (WHERE t.hora_salida IS NULL) as activos,
                COUNT(*) FILTER (WHERE t.hora_salida IS NOT NULL) as completados
            FROM turnos t
            INNER JOIN empleados e ON t.id_empleado = e.id_empleado
            WHERE DATE(t.hora_inicio AT TIME ZONE 'America/Bogota') = (CURRENT_TIMESTAMP AT TIME ZONE 'America/Bogota')::DATE
              AND e.id_sede = %s
        """
        df = pd.read_sql(query, conn, params=(id_sede_filtro,))
    else:
        query = """
            SELECT 
                COUNT(*) as total,
                COUNT(*) FILTER (WHERE hora_salida IS NULL) as activos,
                COUNT(*) FILTER (WHERE hora_salida IS NOT NULL) as completados
            FROM turnos
            WHERE DATE(hora_inicio AT TIME ZONE 'America/Bogota') = (CURRENT_TIMESTAMP AT TIME ZONE 'America/Bogota')::DATE
        """
        df = pd.read_sql(query, conn)
    
    conn.close()
    
    return {
        'total': int(df['total'].iloc[0]),
        'activos': int(df['activos'].iloc[0]),
        'completados': int(df['completados'].iloc[0])
    }


def get_resumen_por_sede():
    """Obtiene resumen de turnos agrupado por sede"""
    conn = get_db_connection()
    
    query = """
        SELECT 
            COALESCE(s.nombre_sede, 'Sin Sede') as nombre_sede,
            COUNT(*) as total,
            COUNT(*) FILTER (WHERE t.hora_salida IS NULL) as activos,
            COUNT(*) FILTER (WHERE t.hora_salida IS NOT NULL) as completados
        FROM turnos t
        INNER JOIN empleados e ON t.id_empleado = e.id_empleado
        LEFT JOIN sedes s ON e.id_sede = s.id_sede
        WHERE DATE(t.hora_inicio AT TIME ZONE 'America/Bogota') = (CURRENT_TIMESTAMP AT TIME ZONE 'America/Bogota')::DATE
        GROUP BY s.nombre_sede
        ORDER BY s.nombre_sede
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df


def render_tarjeta_turno(row):
    """Renderiza una tarjeta de turno individual"""
    hora_entrada = format_timestamp(row['hora_inicio'], "%I:%M %p", "—")
    hora_salida = format_timestamp(row['hora_salida'], "%I:%M %p", "—")
    
    # Clase CSS según estado
    card_class = "turno-card-activo" if row['estado'] == 'En curso' else "turno-card-completado"
    
    # Foto
    foto_html = ""
    foto_data = row['foto_salida'] if row['estado'] == 'Completado' and row['foto_salida'] is not None else row['foto_entrada']
    
    if foto_data is not None:
        foto_b64 = base64.b64encode(bytes(foto_data)).decode('utf-8')
        foto_html = f'<img src="data:image/jpeg;base64,{foto_b64}" class="turno-foto" />'
    else:
        foto_html = '<div style="width: 70px; height: 70px; border-radius: 50%; background: rgba(255,255,255,0.2); display: flex; align-items: center; justify-content: center; font-size: 1.8em;">👤</div>'
    
    # Horario según estado
    if row['estado'] == 'En curso':
        horario_html = f'<div class="turno-hora">🟢 Entrada: {hora_entrada}</div>'
    else:
        horario_html = f'<div class="turno-hora">⏰ {hora_entrada} → {hora_salida}</div>'
    
    st.markdown(f"""
    <div class="turno-card {card_class}">
        <div style="display: flex; align-items: center; gap: 12px;">
            {foto_html}
            <div class="turno-info">
                <div class="turno-nombre">{row['nombre_empleado']}</div>
                <div class="turno-rol">🏷️ {row['nombre_rol']}</div>
                <div class="turno-cedula">📄 {row['cedula_empleado']}</div>
                {horario_html}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_seccion_sede(df_sede, nombre_sede, resumen_sede, key_prefix):
    """Renderiza una sección completa de una sede"""
    
    # Header de la sede
    st.markdown(f"""
    <div class="sede-header">
        <div class="sede-title">🏪 {nombre_sede}</div>
        <div class="sede-stats">
            📊 Total: {resumen_sede['total']} | 
            🟢 En curso: {resumen_sede['activos']} | 
            ✅ Completados: {resumen_sede['completados']}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Filtro por rol para esta sede
    roles_sede = ['Todos'] + sorted(df_sede['nombre_rol'].unique().tolist())
    
    col_filtro, col_space = st.columns([1, 3])
    with col_filtro:
        filtro_rol_sede = st.selectbox(
            "Filtrar por rol:",
            roles_sede,
            key=f"filtro_rol_{key_prefix}"
        )
    
    # Aplicar filtro de rol
    df_filtrado = df_sede.copy()
    if filtro_rol_sede != "Todos":
        df_filtrado = df_filtrado[df_filtrado['nombre_rol'] == filtro_rol_sede]
    
    if df_filtrado.empty:
        st.info(f"No hay turnos con el rol '{filtro_rol_sede}' en esta sede")
        return
    
    # Separar activos y completados
    df_activos = df_filtrado[df_filtrado['estado'] == 'En curso']
    df_completados = df_filtrado[df_filtrado['estado'] == 'Completado']
    
    # Mostrar activos
    if not df_activos.empty:
        st.markdown("##### 🟢 En Curso")
        cols = st.columns(min(3, max(1, len(df_activos))))
        for i, (_, row) in enumerate(df_activos.iterrows()):
            with cols[i % 3]:
                render_tarjeta_turno(row)
    
    # Mostrar completados
    if not df_completados.empty:
        st.markdown("##### ✅ Completados")
        cols = st.columns(min(3, max(1, len(df_completados))))
        for i, (_, row) in enumerate(df_completados.iterrows()):
            with cols[i % 3]:
                render_tarjeta_turno(row)


# ==================== PÁGINA PRINCIPAL ====================

def render():
    """Renderiza la página de turnos de hoy"""
    st.markdown(CSS_STYLES, unsafe_allow_html=True)
    st.markdown(TURNOS_HOY_STYLES, unsafe_allow_html=True)
    
    # Verificar si es admin_negocio para filtrar por sede
    user = st.session_state.get('user', {})
    id_sede_filtro = None
    nombre_sede_usuario = None
    if user.get('rol') == 'admin_negocio' and user.get('id_sede'):
        id_sede_filtro = user['id_sede']
        nombre_sede_usuario = user.get('nombre_sede', 'Tu sede')
    
    st.title("📋 Turnos de Hoy")
    st.markdown(f"**Fecha:** {datetime.now(TZ_COLOMBIA).strftime('%d de %B de %Y')}")
    
    # Mostrar sede si es admin_negocio
    if id_sede_filtro:
        st.info(f"📍 Mostrando datos de: **{nombre_sede_usuario}**")
    
    st.markdown("---")
    
    # Botón de actualizar
    col_space, col_btn = st.columns([5, 1])
    with col_btn:
        if st.button("🔄 Actualizar", key="refresh_turnos_hoy"):
            st.rerun()
    
    # Resumen global (filtrado por sede si es admin_negocio)
    resumen = get_resumen_turnos_hoy(id_sede_filtro)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="turno-resumen-card">
            <div class="turno-resumen-label">📊 Total Turnos</div>
            <div class="turno-resumen-valor">{resumen['total']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="turno-resumen-card activos">
            <div class="turno-resumen-label">🟢 En Curso</div>
            <div class="turno-resumen-valor">{resumen['activos']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="turno-resumen-card completados">
            <div class="turno-resumen-label">✅ Completados</div>
            <div class="turno-resumen-valor">{resumen['completados']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Obtener datos (filtrado por sede si es admin_negocio)
    df_turnos = get_turnos_hoy(id_sede_filtro)
    
    if df_turnos.empty:
        st.info("📭 No hay turnos registrados el día de hoy")
        return
    
    # ==================== FILTROS GLOBALES ====================
    st.subheader("🔍 Filtros Globales")
    
    col_f1, col_f2, col_f3 = st.columns(3)
    
    with col_f1:
        # Filtro por estado global
        filtro_estado = st.selectbox(
            "Estado:",
            ["Todos", "En curso", "Completado"],
            key="filtro_estado_global"
        )
    
    with col_f2:
        # Filtro por sede global
        sedes_disponibles = ['Todas'] + sorted(df_turnos['nombre_sede'].unique().tolist())
        filtro_sede = st.selectbox(
            "Sede:",
            sedes_disponibles,
            key="filtro_sede_global"
        )
    
    with col_f3:
        # Filtro por rol global
        roles_disponibles = ['Todos'] + sorted(df_turnos['nombre_rol'].unique().tolist())
        filtro_rol = st.selectbox(
            "Rol:",
            roles_disponibles,
            key="filtro_rol_global"
        )
    
    # Aplicar filtros globales
    df_filtrado = df_turnos.copy()
    
    if filtro_estado != "Todos":
        df_filtrado = df_filtrado[df_filtrado['estado'] == filtro_estado]
    
    if filtro_sede != "Todas":
        df_filtrado = df_filtrado[df_filtrado['nombre_sede'] == filtro_sede]
    
    if filtro_rol != "Todos":
        df_filtrado = df_filtrado[df_filtrado['nombre_rol'] == filtro_rol]
    
    if df_filtrado.empty:
        st.warning("No hay turnos que coincidan con los filtros seleccionados")
        return
    
    st.markdown("---")
    
    # ==================== TABLA RESUMEN ====================
    with st.expander("📋 Ver Tabla de Turnos", expanded=False):
        df_tabla = df_filtrado[['nombre_empleado', 'cedula_empleado', 'nombre_sede', 'nombre_rol', 'hora_inicio', 'hora_salida', 'estado']].copy()
        df_tabla['hora_inicio'] = df_tabla['hora_inicio'].apply(lambda x: format_timestamp(x, "%I:%M:%S %p", "—"))
        df_tabla['hora_salida'] = df_tabla['hora_salida'].apply(lambda x: format_timestamp(x, "%I:%M:%S %p", "En curso..."))
        df_tabla.columns = ['Empleado', 'Cédula', 'Sede', 'Rol', 'Entrada', 'Salida', 'Estado']
        
        st.dataframe(
            df_tabla,
            use_container_width=True,
            hide_index=True
        )
    
    # ==================== VISTA POR SEDES ====================
    st.subheader("🏪 Turnos por Sede")
    
    # Obtener resumen por sede
    df_resumen_sedes = get_resumen_por_sede()
    
    # Agrupar por sede
    sedes = df_filtrado['nombre_sede'].unique()
    
    for sede in sorted(sedes):
        df_sede = df_filtrado[df_filtrado['nombre_sede'] == sede]
        
        # Calcular resumen de esta sede con datos filtrados
        resumen_sede = {
            'total': len(df_sede),
            'activos': len(df_sede[df_sede['estado'] == 'En curso']),
            'completados': len(df_sede[df_sede['estado'] == 'Completado'])
        }
        
        # Crear key único para evitar duplicados
        key_sede = sede.replace(" ", "_").lower()
        
        render_seccion_sede(df_sede, sede, resumen_sede, key_sede)
        
        st.markdown("---")
