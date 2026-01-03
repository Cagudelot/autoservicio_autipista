"""
Módulo de Nómina - Total de Horas por Día
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from data_base.controler import (
    get_total_horas_por_fecha,
    get_resumen_horas_por_empleado,
    get_all_empleados_activos,
    sincronizar_total_horas
)
from src.utils.ui_helpers import CSS_STYLES


# ==================== ESTILOS ====================

TOTAL_HORAS_STYLES = """
<style>
    .horas-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        padding: 20px;
        color: white;
        text-align: center;
        margin: 10px 0;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }
    
    .horas-card.total {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    }
    
    .horas-card.turnos {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    }
    
    .horas-card.promedio {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }
    
    .horas-valor {
        font-size: 2.5em;
        font-weight: 700;
        margin: 10px 0;
    }
    
    .horas-label {
        font-size: 0.9em;
        opacity: 0.9;
    }
    
    .filtros-container {
        background: #f8f9fa;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
    }
    
    .tabla-horas {
        background: white;
        border-radius: 10px;
        overflow: hidden;
    }
</style>
"""


def render():
    """Renderiza la vista de Total de Horas por Día"""
    st.markdown(CSS_STYLES, unsafe_allow_html=True)
    st.markdown(TOTAL_HORAS_STYLES, unsafe_allow_html=True)
    
    st.title("⏱️ Total de Horas por Día")
    st.markdown("---")
    
    # ==================== FILTROS ====================
    with st.container():
        st.markdown("### 🔍 Filtros")
        
        col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
        
        with col1:
            # Filtro por rango de fechas
            fecha_inicio = st.date_input(
                "Fecha inicio",
                value=datetime.now().date() - timedelta(days=30),
                key="fecha_inicio_horas"
            )
        
        with col2:
            fecha_fin = st.date_input(
                "Fecha fin",
                value=datetime.now().date(),
                key="fecha_fin_horas"
            )
        
        with col3:
            # Filtro por empleado
            empleados = get_all_empleados_activos()
            opciones_empleados = {"Todos": None}
            for emp in empleados:
                opciones_empleados[f"{emp['nombre_empleado']} ({emp['cedula_empleado']})"] = emp['id_empleado']
            
            empleado_seleccionado = st.selectbox(
                "Empleado",
                options=list(opciones_empleados.keys()),
                key="empleado_filtro_horas"
            )
            id_empleado = opciones_empleados[empleado_seleccionado]
        
        with col4:
            st.write("")
            st.write("")
            if st.button("🔄 Sincronizar", help="Sincronizar turnos con la tabla de horas"):
                cantidad, error = sincronizar_total_horas()
                if error:
                    st.error(f"Error: {error}")
                else:
                    st.success(f"✅ {cantidad} turnos sincronizados")
                    st.rerun()
    
    st.markdown("---")
    
    # ==================== OBTENER DATOS ====================
    turnos = get_total_horas_por_fecha(
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        id_empleado=id_empleado
    )
    
    if not turnos:
        st.info("📭 No se encontraron turnos completados para los filtros seleccionados.")
        return
    
    # ==================== MÉTRICAS RESUMEN ====================
    total_horas = sum(t['total_horas'] for t in turnos)
    total_turnos = len(turnos)
    promedio_horas = total_horas / total_turnos if total_turnos > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="horas-card total">
            <div class="horas-label">⏱️ Total Horas</div>
            <div class="horas-valor">{total_horas:.1f}h</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="horas-card turnos">
            <div class="horas-label">📋 Total Turnos</div>
            <div class="horas-valor">{total_turnos}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="horas-card promedio">
            <div class="horas-label">📊 Promedio por Turno</div>
            <div class="horas-valor">{promedio_horas:.1f}h</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ==================== TABLA DE TURNOS ====================
    st.markdown("### 📋 Detalle de Turnos")
    
    # Convertir a DataFrame para mostrar
    df = pd.DataFrame(turnos)
    
    # Formatear columnas
    df['fecha'] = pd.to_datetime(df['fecha']).dt.strftime('%Y-%m-%d')
    df['hora_entrada'] = pd.to_datetime(df['hora_entrada']).dt.strftime('%I:%M %p')
    df['hora_salida'] = pd.to_datetime(df['hora_salida']).dt.strftime('%I:%M %p')
    df['total_horas'] = df['total_horas'].apply(lambda x: f"{x:.2f}h")
    
    # Renombrar columnas para mostrar
    df_display = df.rename(columns={
        'id_turno': 'ID Turno',
        'nombre_empleado': 'Empleado',
        'cedula_empleado': 'Cédula',
        'fecha': 'Fecha',
        'hora_entrada': 'Entrada',
        'hora_salida': 'Salida',
        'total_horas': 'Horas Trabajadas'
    })
    
    # Seleccionar columnas a mostrar
    columnas_mostrar = ['ID Turno', 'Empleado', 'Cédula', 'Fecha', 'Entrada', 'Salida', 'Horas Trabajadas']
    
    st.dataframe(
        df_display[columnas_mostrar],
        use_container_width=True,
        hide_index=True
    )
    
    # ==================== RESUMEN POR EMPLEADO ====================
    if id_empleado is None:
        st.markdown("---")
        st.markdown("### 👥 Resumen por Empleado")
        
        resumen = get_resumen_horas_por_empleado(
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        )
        
        if resumen:
            df_resumen = pd.DataFrame(resumen)
            df_resumen['total_horas'] = df_resumen['total_horas'].apply(lambda x: f"{x:.2f}h")
            
            df_resumen_display = df_resumen.rename(columns={
                'nombre_empleado': 'Empleado',
                'cedula_empleado': 'Cédula',
                'total_turnos': 'Total Turnos',
                'total_horas': 'Total Horas'
            })
            
            st.dataframe(
                df_resumen_display[['Empleado', 'Cédula', 'Total Turnos', 'Total Horas']],
                use_container_width=True,
                hide_index=True
            )
    
    # ==================== EXPORTAR ====================
    st.markdown("---")
    col_export1, col_export2 = st.columns([1, 4])
    
    with col_export1:
        # Preparar CSV para exportar
        df_export = df_display[columnas_mostrar].copy()
        csv = df_export.to_csv(index=False).encode('utf-8')
        
        st.download_button(
            label="📥 Exportar CSV",
            data=csv,
            file_name=f"horas_trabajadas_{fecha_inicio}_{fecha_fin}.csv",
            mime="text/csv"
        )
