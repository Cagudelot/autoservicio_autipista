"""
Módulo de Nómina - Horas Extra
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from data_base.controler import (
    get_horas_extra,
    get_resumen_horas_extra_por_empleado,
    get_all_empleados_activos,
    sincronizar_horas_extra,
    sincronizar_total_horas,
    get_all_sedes
)
from src.utils.ui_helpers import CSS_STYLES


# ==================== ESTILOS ====================

HORAS_EXTRA_STYLES = """
<style>
    .extra-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        border-radius: 15px;
        padding: 20px;
        color: white;
        text-align: center;
        margin: 10px 0;
        box-shadow: 0 10px 30px rgba(240, 147, 251, 0.3);
    }
    
    .extra-card.total {
        background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
    }
    
    .extra-card.turnos {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .extra-card.promedio {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    }
    
    .extra-valor {
        font-size: 2.5em;
        font-weight: 700;
        margin: 10px 0;
    }
    
    .extra-label {
        font-size: 0.9em;
        opacity: 0.9;
    }
</style>
"""


def render():
    """Renderiza la vista de Horas Extra"""
    st.markdown(CSS_STYLES, unsafe_allow_html=True)
    st.markdown(HORAS_EXTRA_STYLES, unsafe_allow_html=True)
    
    st.markdown("### ⏰ Horas Extra")
    st.caption("Registro de turnos con más de 8 horas trabajadas")
    
    # ==================== FILTROS ====================
    with st.container():
        st.markdown("#### 🔍 Filtros")
        
        col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 1])
        
        with col1:
            fecha_inicio = st.date_input(
                "Fecha inicio",
                value=datetime.now().date() - timedelta(days=30),
                key="fecha_inicio_extra"
            )
        
        with col2:
            fecha_fin = st.date_input(
                "Fecha fin",
                value=datetime.now().date(),
                key="fecha_fin_extra"
            )
        
        with col3:
            # Filtro por sede
            sedes = get_all_sedes()
            opciones_sedes = {"Todas": None}
            for sede in sedes:
                opciones_sedes[sede['nombre_sede']] = sede['id_sede']
            
            sede_seleccionada = st.selectbox(
                "Sede",
                options=list(opciones_sedes.keys()),
                key="sede_filtro_extra"
            )
            id_sede = opciones_sedes[sede_seleccionada]
        
        with col4:
            empleados = get_all_empleados_activos()
            opciones_empleados = {"Todos": None}
            for emp in empleados:
                opciones_empleados[emp['nombre_empleado']] = emp['id_empleado']
            
            empleado_seleccionado = st.selectbox(
                "Empleado",
                options=list(opciones_empleados.keys()),
                key="empleado_filtro_extra"
            )
            id_empleado = opciones_empleados[empleado_seleccionado]
        
        with col5:
            st.write("")
            st.write("")
            if st.button("🔄 Sincronizar", help="Sincronizar horas extra", key="sync_extra"):
                # Primero sincronizar total_horas
                cant_horas, err_horas = sincronizar_total_horas()
                # Luego sincronizar horas_extra
                cantidad, error = sincronizar_horas_extra()
                if error:
                    st.error(f"Error: {error}")
                else:
                    st.success(f"✅ {cantidad} horas extra sincronizadas")
                    st.rerun()
    
    st.markdown("---")
    
    # ==================== OBTENER DATOS ====================
    turnos_extra = get_horas_extra(
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        id_empleado=id_empleado,
        id_sede=id_sede
    )
    
    if not turnos_extra:
        st.info("📭 No se encontraron turnos con horas extra para los filtros seleccionados.")
        return
    
    # ==================== MÉTRICAS RESUMEN ====================
    total_horas_extra = sum(t['horas_extra'] for t in turnos_extra)
    total_turnos = len(turnos_extra)
    promedio_extra = total_horas_extra / total_turnos if total_turnos > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="extra-card total">
            <div class="extra-label">⏰ Total Horas Extra</div>
            <div class="extra-valor">{total_horas_extra:.1f}h</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="extra-card turnos">
            <div class="extra-label">📋 Turnos con Extra</div>
            <div class="extra-valor">{total_turnos}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="extra-card promedio">
            <div class="extra-label">📊 Promedio Extra/Turno</div>
            <div class="extra-valor">{promedio_extra:.1f}h</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ==================== TABLA DE HORAS EXTRA ====================
    st.markdown("#### 📋 Detalle de Horas Extra")
    
    df = pd.DataFrame(turnos_extra)
    
    # Formatear columnas
    df['fecha'] = pd.to_datetime(df['fecha']).dt.strftime('%Y-%m-%d')
    df['hora_entrada'] = pd.to_datetime(df['hora_entrada']).dt.strftime('%I:%M %p')
    df['hora_salida'] = pd.to_datetime(df['hora_salida']).dt.strftime('%I:%M %p')
    df['total_horas'] = df['total_horas'].apply(lambda x: f"{x:.2f}h")
    df['horas_extra'] = df['horas_extra'].apply(lambda x: f"{x:.2f}h")
    
    # Renombrar columnas
    df_display = df.rename(columns={
        'nombre_empleado': 'Empleado',
        'nombre_sede': 'Sede',
        'fecha': 'Fecha',
        'hora_entrada': 'Entrada',
        'hora_salida': 'Salida',
        'total_horas': 'Total Horas',
        'horas_extra': 'Horas Extra'
    })
    
    # Columnas a mostrar (sin cédula según solicitado)
    columnas_mostrar = ['Empleado', 'Sede', 'Fecha', 'Entrada', 'Salida', 'Total Horas', 'Horas Extra']
    
    st.dataframe(
        df_display[columnas_mostrar],
        use_container_width=True,
        hide_index=True
    )
    
    # ==================== RESUMEN POR EMPLEADO ====================
    if id_empleado is None:
        st.markdown("---")
        st.markdown("#### 👥 Resumen por Empleado")
        
        resumen = get_resumen_horas_extra_por_empleado(
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        )
        
        if resumen:
            df_resumen = pd.DataFrame(resumen)
            df_resumen['total_horas_extra'] = df_resumen['total_horas_extra'].apply(lambda x: f"{x:.2f}h")
            
            df_resumen_display = df_resumen.rename(columns={
                'nombre_empleado': 'Empleado',
                'total_turnos_extra': 'Turnos con Extra',
                'total_horas_extra': 'Total Horas Extra'
            })
            
            st.dataframe(
                df_resumen_display[['Empleado', 'Turnos con Extra', 'Total Horas Extra']],
                use_container_width=True,
                hide_index=True
            )
    
    # ==================== EXPORTAR ====================
    st.markdown("---")
    col_export1, col_export2 = st.columns([1, 4])
    
    with col_export1:
        df_export = df_display[columnas_mostrar].copy()
        csv = df_export.to_csv(index=False).encode('utf-8')
        
        st.download_button(
            label="📥 Exportar CSV",
            data=csv,
            file_name=f"horas_extra_{fecha_inicio}_{fecha_fin}.csv",
            mime="text/csv"
        )
