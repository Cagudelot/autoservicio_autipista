"""
Módulo de Empleados - Turnos de Hoy (Vista administrativa)
"""
import streamlit as st
import pandas as pd
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.utils.ui_helpers import get_db_connection, CSS_STYLES, format_currency


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
    
    .estado-activo {
        background-color: #38ef7d;
        color: #1a1a2e;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85em;
    }
    
    .estado-completado {
        background-color: #4facfe;
        color: white;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85em;
    }
</style>
"""


# ==================== FUNCIONES DE DATOS ====================

@st.cache_data(ttl=30)
def get_turnos_hoy():
    """Obtiene todos los turnos del día de hoy con información del empleado - Zona horaria Colombia"""
    conn = get_db_connection()
    query = """
        SELECT 
            t.id_turno,
            e.nombre_empleado,
            e.cedula_empleado,
            t.hora_inicio,
            t.hora_salida,
            CASE 
                WHEN t.hora_salida IS NULL THEN 'En curso'
                ELSE 'Completado'
            END as estado
        FROM turnos t
        INNER JOIN empleados e ON t.id_empleado = e.id_empleado
        WHERE DATE(t.hora_inicio AT TIME ZONE 'America/Bogota') = (CURRENT_TIMESTAMP AT TIME ZONE 'America/Bogota')::DATE
        ORDER BY t.hora_inicio DESC
    """
    df = pd.read_sql(query, conn)
    return df


@st.cache_data(ttl=30)
def get_resumen_turnos_hoy():
    """Obtiene resumen de turnos del día - Zona horaria Colombia"""
    conn = get_db_connection()
    
    # Total turnos
    query_total = """
        SELECT COUNT(*) as total
        FROM turnos
        WHERE DATE(hora_inicio AT TIME ZONE 'America/Bogota') = (CURRENT_TIMESTAMP AT TIME ZONE 'America/Bogota')::DATE
    """
    df_total = pd.read_sql(query_total, conn)
    
    # Turnos activos (sin salida)
    query_activos = """
        SELECT COUNT(*) as activos
        FROM turnos
        WHERE DATE(hora_inicio AT TIME ZONE 'America/Bogota') = (CURRENT_TIMESTAMP AT TIME ZONE 'America/Bogota')::DATE AND hora_salida IS NULL
    """
    df_activos = pd.read_sql(query_activos, conn)
    
    # Turnos completados
    query_completados = """
        SELECT COUNT(*) as completados
        FROM turnos
        WHERE DATE(hora_inicio AT TIME ZONE 'America/Bogota') = (CURRENT_TIMESTAMP AT TIME ZONE 'America/Bogota')::DATE AND hora_salida IS NOT NULL
    """
    df_completados = pd.read_sql(query_completados, conn)
    
    return {
        'total': int(df_total['total'].iloc[0]),
        'activos': int(df_activos['activos'].iloc[0]),
        'completados': int(df_completados['completados'].iloc[0])
    }


# ==================== PÁGINA PRINCIPAL ====================

def render():
    """Renderiza la página de turnos de hoy"""
    st.markdown(CSS_STYLES, unsafe_allow_html=True)
    st.markdown(TURNOS_HOY_STYLES, unsafe_allow_html=True)
    
    st.title("📋 Turnos de Hoy")
    import pytz
    tz = pytz.timezone('America/Bogota')
    st.markdown(f"**Fecha:** {datetime.now(tz).strftime('%d de %B de %Y')}")
    st.markdown("---")
    
    # Botón de actualizar
    col_space, col_btn = st.columns([5, 1])
    with col_btn:
        if st.button("🔄 Actualizar", key="refresh_turnos_hoy"):
            st.cache_data.clear()
            st.rerun()
    
    # Resumen
    resumen = get_resumen_turnos_hoy()
    
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
    
    # Filtros
    col_filtro1, col_filtro2 = st.columns(2)
    with col_filtro1:
        filtro_estado = st.selectbox(
            "Filtrar por estado:",
            ["Todos", "En curso", "Completado"]
        )
    
    # Tabla de turnos
    st.subheader("📋 Detalle de Turnos")
    
    df_turnos = get_turnos_hoy()
    
    if not df_turnos.empty:
        # Aplicar filtro
        if filtro_estado != "Todos":
            df_turnos = df_turnos[df_turnos['estado'] == filtro_estado]
        
        if not df_turnos.empty:
            # Formatear columnas
            df_display = df_turnos.copy()
            import pytz
            tz = pytz.timezone('America/Bogota')
            df_display['hora_inicio'] = df_display['hora_inicio'].apply(
                lambda x: x.astimezone(tz).strftime("%I:%M:%S %p") if pd.notna(x) else "—"
            )
            df_display['hora_salida'] = df_display['hora_salida'].apply(
                lambda x: x.astimezone(tz).strftime("%I:%M:%S %p") if pd.notna(x) else "En curso..."
            )
            
            # Renombrar columnas
            df_display.columns = ['ID', 'Empleado', 'Cédula', 'Entrada', 'Salida', 'Estado']
            
            # Mostrar tabla
            st.dataframe(
                df_display[['Empleado', 'Cédula', 'Entrada', 'Salida', 'Estado']],
                use_container_width=True,
                hide_index=True
            )
            
            # Mostrar también en tarjetas para los activos
            if filtro_estado == "En curso" or (filtro_estado == "Todos" and resumen['activos'] > 0):
                st.markdown("---")
                st.subheader("🟢 Empleados Trabajando Actualmente")
                
                df_activos = df_turnos[df_turnos['estado'] == 'En curso']
                
                if not df_activos.empty:
                    cols = st.columns(min(3, len(df_activos)))
                    for i, (_, row) in enumerate(df_activos.iterrows()):
                        with cols[i % 3]:
                            hora_entrada = row['hora_inicio'].astimezone(tz).strftime("%I:%M %p") if pd.notna(row['hora_inicio']) else "—"
                            st.markdown(f"""
                            <div style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); 
                                        border-radius: 10px; padding: 15px; color: white; margin: 5px 0;">
                                <div style="font-weight: 600; font-size: 1.1em;">{row['nombre_empleado']}</div>
                                <div style="opacity: 0.9; font-size: 0.9em;">📄 {row['cedula_empleado']}</div>
                                <div style="margin-top: 10px;">🟢 Entrada: {hora_entrada}</div>
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.info("No hay empleados trabajando actualmente")
        else:
            st.info(f"No hay turnos con estado '{filtro_estado}' el día de hoy")
    else:
        st.info("📭 No hay turnos registrados el día de hoy")
