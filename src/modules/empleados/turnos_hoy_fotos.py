"""
Módulo de Empleados - Turnos de Hoy (Vista con Fotos Ampliadas)
Vista exclusiva para Master con tarjetas de empleados con fotos más grandes
"""
import streamlit as st
import pandas as pd
from datetime import datetime
import sys
import os
import base64
import pytz

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.utils.ui_helpers import get_db_connection, CSS_STYLES

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


# ==================== ESTILOS PARA FOTOS GRANDES ====================

TURNOS_FOTOS_STYLES = """
<style>
    .turno-foto-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border-radius: 20px;
        padding: 20px;
        margin: 15px 0;
        border: 2px solid rgba(79, 209, 197, 0.4);
        text-align: center;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .turno-foto-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(79, 209, 197, 0.3);
    }
    
    .turno-foto-card.activo {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        border: 2px solid rgba(255, 255, 255, 0.3);
    }
    
    .turno-foto-card.completado {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        border: 2px solid rgba(255, 255, 255, 0.3);
    }
    
    .foto-grande {
        width: 250px;
        height: 250px;
        border-radius: 50%;
        object-fit: cover;
        border: 5px solid rgba(255, 255, 255, 0.6);
        margin: 15px auto;
        display: block;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
    }
    
    .foto-placeholder {
        width: 250px;
        height: 250px;
        border-radius: 50%;
        background: linear-gradient(135deg, rgba(255,255,255,0.2) 0%, rgba(255,255,255,0.1) 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 4em;
        margin: 15px auto;
        border: 5px solid rgba(255, 255, 255, 0.3);
    }
    
    .empleado-nombre-grande {
        color: white;
        font-size: 1.4em;
        font-weight: 700;
        margin: 15px 0 10px 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    .empleado-rol-badge {
        background: rgba(255, 255, 255, 0.25);
        padding: 6px 16px;
        border-radius: 20px;
        font-size: 0.9em;
        display: inline-block;
        margin: 8px 0;
        color: white;
        font-weight: 500;
    }
    
    .empleado-cedula-grande {
        color: rgba(255, 255, 255, 0.9);
        font-size: 1em;
        margin: 8px 0;
    }
    
    .empleado-sede-badge {
        background: rgba(255, 217, 61, 0.3);
        padding: 4px 12px;
        border-radius: 15px;
        font-size: 0.85em;
        display: inline-block;
        margin: 5px 0;
        color: #ffd93d;
    }
    
    .horario-grande {
        background: rgba(0, 0, 0, 0.2);
        border-radius: 15px;
        padding: 12px;
        margin-top: 15px;
        color: white;
    }
    
    .horario-item {
        font-size: 1.1em;
        margin: 5px 0;
    }
    
    .estado-badge {
        position: absolute;
        top: 15px;
        right: 15px;
        padding: 8px 15px;
        border-radius: 20px;
        font-size: 0.85em;
        font-weight: 600;
    }
    
    .estado-activo {
        background: #00ff88;
        color: #003322;
    }
    
    .estado-completado {
        background: #00d4ff;
        color: #002233;
    }
    
    .resumen-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        padding: 25px;
        text-align: center;
        margin-bottom: 30px;
        color: white;
    }
    
    .resumen-titulo {
        font-size: 1.5em;
        font-weight: 700;
        margin-bottom: 15px;
    }
    
    .resumen-stats {
        display: flex;
        justify-content: center;
        gap: 40px;
        flex-wrap: wrap;
    }
    
    .resumen-stat {
        text-align: center;
    }
    
    .resumen-numero {
        font-size: 2.5em;
        font-weight: 700;
    }
    
    .resumen-label {
        font-size: 0.9em;
        opacity: 0.9;
    }
    
    .filtros-container {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 20px;
    }
</style>
"""


# ==================== FUNCIONES DE DATOS ====================

def get_turnos_hoy_con_fotos(id_sede_filtro=None):
    """Obtiene todos los turnos del día con sede y rol"""
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
        base_query += " ORDER BY t.hora_inicio DESC"
        df = pd.read_sql(base_query, conn, params=(id_sede_filtro,))
    else:
        base_query += " ORDER BY s.nombre_sede, t.hora_inicio DESC"
        df = pd.read_sql(base_query, conn)
    
    conn.close()
    return df


def get_resumen_turnos():
    """Obtiene resumen de turnos del día"""
    conn = get_db_connection()
    
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


def get_sedes():
    """Obtiene lista de sedes"""
    conn = get_db_connection()
    query = "SELECT id_sede, nombre_sede FROM sedes ORDER BY nombre_sede"
    df = pd.read_sql(query, conn)
    conn.close()
    return df


# ==================== FUNCIONES DE RENDER ====================

def render_tarjeta_foto_grande(row):
    """Renderiza una tarjeta con foto grande del empleado"""
    hora_entrada = format_timestamp(row['hora_inicio'], "%I:%M %p", "—")
    hora_salida = format_timestamp(row['hora_salida'], "%I:%M %p", "—")
    
    # Determinar clase CSS según estado
    card_class = "activo" if row['estado'] == 'En curso' else "completado"
    
    # Prioridad de fotos: foto_salida > foto_entrada
    foto_data = None
    if row['estado'] == 'Completado' and row['foto_salida'] is not None:
        foto_data = row['foto_salida']
    elif row['foto_entrada'] is not None:
        foto_data = row['foto_entrada']
    
    # Generar HTML de la foto
    if foto_data is not None:
        foto_b64 = base64.b64encode(bytes(foto_data)).decode('utf-8')
        foto_html = f'<img src="data:image/jpeg;base64,{foto_b64}" class="foto-grande" />'
    else:
        foto_html = '<div class="foto-placeholder">👤</div>'
    
    # Estado badge
    estado_class = "estado-activo" if row['estado'] == 'En curso' else "estado-completado"
    estado_icon = "🟢" if row['estado'] == 'En curso' else "✅"
    
    # Horario HTML
    if row['estado'] == 'En curso':
        horario_html = f'<div class="horario-grande"><div class="horario-item">🟢 <strong>Entrada:</strong> {hora_entrada}</div><div class="horario-item">⏳ En turno actualmente</div></div>'
    else:
        horario_html = f'<div class="horario-grande"><div class="horario-item">🕐 <strong>Entrada:</strong> {hora_entrada}</div><div class="horario-item">🕐 <strong>Salida:</strong> {hora_salida}</div></div>'
    
    html_content = f'''
    <div class="turno-foto-card {card_class}" style="position: relative;">
        <span class="{estado_class}" style="position: absolute; top: 15px; right: 15px; padding: 8px 15px; border-radius: 20px; font-size: 0.85em; font-weight: 600;">
            {estado_icon} {row['estado']}
        </span>
        {foto_html}
        <div class="empleado-nombre-grande">{row['nombre_empleado']}</div>
        <div class="empleado-rol-badge">🏷️ {row['nombre_rol']}</div>
        <div class="empleado-cedula-grande">📄 CC: {row['cedula_empleado']}</div>
        <div class="empleado-sede-badge">🏪 {row['nombre_sede']}</div>
        {horario_html}
    </div>
    '''
    st.markdown(html_content, unsafe_allow_html=True)


# ==================== PÁGINA PRINCIPAL ====================

def render():
    """Renderiza la página de turnos con fotos grandes - Solo para Master"""
    
    # Verificar que el usuario sea master
    user = st.session_state.get('user', {})
    if user.get('rol') != 'master':
        st.error("⛔ Acceso denegado. Esta vista es exclusiva para el usuario Master.")
        return
    
    st.markdown(CSS_STYLES, unsafe_allow_html=True)
    st.markdown(TURNOS_FOTOS_STYLES, unsafe_allow_html=True)
    
    st.title("📸 Turnos de Hoy - Vista con Fotos")
    st.markdown(f"**Fecha:** {datetime.now(TZ_COLOMBIA).strftime('%d de %B de %Y')}")
    
    st.markdown("---")
    
    # Resumen general
    resumen = get_resumen_turnos()
    
    st.markdown(f"""
    <div class="resumen-header">
        <div class="resumen-titulo">📊 Resumen del Día</div>
        <div class="resumen-stats">
            <div class="resumen-stat">
                <div class="resumen-numero">{resumen['total']}</div>
                <div class="resumen-label">Total Turnos</div>
            </div>
            <div class="resumen-stat">
                <div class="resumen-numero" style="color: #00ff88;">{resumen['activos']}</div>
                <div class="resumen-label">🟢 En Curso</div>
            </div>
            <div class="resumen-stat">
                <div class="resumen-numero" style="color: #00d4ff;">{resumen['completados']}</div>
                <div class="resumen-label">✅ Completados</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Filtros
    st.markdown('<div class="filtros-container">', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
    
    with col1:
        # Filtro por sede
        sedes_df = get_sedes()
        sedes_opciones = ['Todas las sedes'] + sedes_df['nombre_sede'].tolist()
        sede_filtro = st.selectbox("🏪 Filtrar por Sede:", sedes_opciones, key="filtro_sede_fotos")
    
    with col2:
        # Filtro por estado
        estado_filtro = st.selectbox("📊 Filtrar por Estado:", ["Todos", "En curso", "Completado"], key="filtro_estado_fotos")
    
    with col3:
        # Cantidad de columnas
        num_columnas = st.selectbox("📐 Tarjetas por fila:", [2, 3, 4], index=0, key="num_cols_fotos")
    
    with col4:
        st.write("")
        st.write("")
        if st.button("🔄 Actualizar", key="refresh_fotos"):
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Obtener datos
    id_sede_filtro = None
    if sede_filtro != 'Todas las sedes':
        sede_row = sedes_df[sedes_df['nombre_sede'] == sede_filtro]
        if not sede_row.empty:
            id_sede_filtro = int(sede_row['id_sede'].iloc[0])
    
    df_turnos = get_turnos_hoy_con_fotos(id_sede_filtro)
    
    # Aplicar filtro de estado
    if estado_filtro != "Todos":
        df_turnos = df_turnos[df_turnos['estado'] == estado_filtro]
    
    if df_turnos.empty:
        st.info("📭 No hay turnos registrados hoy con los filtros seleccionados.")
        return
    
    st.markdown(f"### 👥 Mostrando {len(df_turnos)} turnos")
    
    # Renderizar tarjetas
    cols = st.columns(num_columnas)
    for i, (_, row) in enumerate(df_turnos.iterrows()):
        with cols[i % num_columnas]:
            render_tarjeta_foto_grande(row)
