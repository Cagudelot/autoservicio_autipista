"""
Módulo Dashboard Global del Negocio
Panel de control con KPIs y métricas principales
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from data_base.controler import (
    get_dashboard_resumen_general,
    get_dashboard_cuentas_pagar,
    get_dashboard_deuda_supermercado,
    get_dashboard_deuda_por_negocio,
    get_dashboard_gastos_por_sede,
    get_dashboard_resumen_nomina_mes
)
from src.utils.ui_helpers import CSS_STYLES


# ==================== ESTILOS ====================
DASHBOARD_STYLES = """
<style>
    .dashboard-hero {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        border-radius: 20px;
        padding: 30px;
        margin-bottom: 25px;
        text-align: center;
        box-shadow: 0 15px 40px rgba(30, 60, 114, 0.4);
    }
    
    .hero-title {
        font-size: 1.8em;
        font-weight: 700;
        color: white;
        margin-bottom: 10px;
    }
    
    .hero-subtitle {
        color: rgba(255,255,255,0.8);
        font-size: 1em;
    }
    
    .mega-kpi {
        background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
        border-radius: 20px;
        padding: 30px;
        text-align: center;
        margin: 15px 0;
        box-shadow: 0 10px 30px rgba(235, 51, 73, 0.3);
    }
    
    .mega-kpi.success {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        box-shadow: 0 10px 30px rgba(17, 153, 142, 0.3);
    }
    
    .mega-kpi.warning {
        background: linear-gradient(135deg, #f2994a 0%, #f2c94c 100%);
        box-shadow: 0 10px 30px rgba(242, 153, 74, 0.3);
    }
    
    .mega-kpi.info {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }
    
    .mega-kpi-icon {
        font-size: 2.5em;
        margin-bottom: 10px;
    }
    
    .mega-kpi-valor {
        font-size: 2.8em;
        font-weight: 700;
        color: white;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .mega-kpi-label {
        color: rgba(255,255,255,0.9);
        font-size: 1em;
        margin-top: 5px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .mega-kpi-sublabel {
        color: rgba(255,255,255,0.7);
        font-size: 0.85em;
        margin-top: 8px;
    }
    
    .kpi-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        border: 1px solid rgba(255,255,255,0.1);
        text-align: center;
    }
    
    .kpi-card.success { border-left: 4px solid #38ef7d; }
    .kpi-card.warning { border-left: 4px solid #f2994a; }
    .kpi-card.danger { border-left: 4px solid #eb3349; }
    .kpi-card.info { border-left: 4px solid #667eea; }
    .kpi-card.purple { border-left: 4px solid #764ba2; }
    
    .kpi-valor {
        font-size: 2em;
        font-weight: 700;
        margin: 10px 0;
    }
    
    .kpi-label {
        font-size: 0.85em;
        opacity: 0.8;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .kpi-icon {
        font-size: 1.8em;
        margin-bottom: 10px;
    }
    
    .section-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        padding: 15px 20px;
        margin: 25px 0 15px 0;
        color: white;
    }
    
    .section-header.danger {
        background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
    }
    
    .section-header.success {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    }
    
    .section-header.warning {
        background: linear-gradient(135deg, #f2994a 0%, #f2c94c 100%);
    }
    
    .section-title {
        font-size: 1.2em;
        font-weight: 600;
        margin: 0;
    }
    
    .negocio-card {
        background: rgba(255,255,255,0.03);
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        border-left: 4px solid #667eea;
    }
    
    .negocio-nombre {
        font-size: 1.1em;
        font-weight: 600;
        margin-bottom: 10px;
    }
    
    .negocio-valor {
        font-size: 1.8em;
        font-weight: 700;
        color: #eb3349;
    }
    
    .negocio-detalle {
        font-size: 0.85em;
        opacity: 0.7;
        margin-top: 8px;
    }
    
    .distribucion-bar {
        height: 30px;
        border-radius: 15px;
        overflow: hidden;
        background: rgba(255,255,255,0.1);
        margin: 15px 0;
    }
    
    .distribucion-segment {
        height: 100%;
        float: left;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.8em;
        font-weight: 600;
        color: white;
    }
    
    .resumen-tabla {
        background: rgba(255,255,255,0.03);
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    
    .resumen-row {
        display: flex;
        justify-content: space-between;
        padding: 10px 0;
        border-bottom: 1px solid rgba(255,255,255,0.1);
    }
    
    .resumen-row:last-child {
        border-bottom: none;
    }
    
    .resumen-row.total {
        font-weight: 700;
        font-size: 1.1em;
        border-top: 2px solid rgba(255,255,255,0.2);
        margin-top: 10px;
        padding-top: 15px;
    }
    
    .alerta-box {
        background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
        border-radius: 10px;
        padding: 15px 20px;
        color: white;
        margin: 10px 0;
    }
</style>
"""


def formato_moneda(valor):
    """Formatea un valor como moneda colombiana"""
    try:
        return f"${valor:,.0f}".replace(",", ".")
    except:
        return f"${0:,.0f}"


def render():
    """Renderiza el Dashboard Global"""
    st.markdown(CSS_STYLES, unsafe_allow_html=True)
    st.markdown(DASHBOARD_STYLES, unsafe_allow_html=True)
    
    # ==================== HEADER ====================
    st.markdown(f"""
    <div class="dashboard-hero">
        <div class="hero-title">📊 Dashboard Global - Kikes</div>
        <div class="hero-subtitle">Resumen financiero y operativo del negocio</div>
    </div>
    """, unsafe_allow_html=True)
    
    # ==================== MÉTRICAS PRINCIPALES ====================
    # Obtener datos
    deuda_super = get_dashboard_deuda_supermercado()
    resumen_nomina = get_dashboard_resumen_nomina_mes()
    resumen_general = get_dashboard_resumen_general()
    cuentas_pagar = get_dashboard_cuentas_pagar()
    
    # Fila de KPIs mega
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="mega-kpi">
            <div class="mega-kpi-icon">🏪</div>
            <div class="mega-kpi-valor">{formato_moneda(deuda_super['total_deuda'])}</div>
            <div class="mega-kpi-label">Deuda Supermercado</div>
            <div class="mega-kpi-sublabel">
                {deuda_super['cantidad_remisiones']} remisiones + {deuda_super['cantidad_facturas']} facturas
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        total_nomina_pendiente = resumen_nomina['pendientes']['estimado']
        color_nomina = "warning" if total_nomina_pendiente > 0 else "success"
        st.markdown(f"""
        <div class="mega-kpi {color_nomina}">
            <div class="mega-kpi-icon">👥</div>
            <div class="mega-kpi-valor">{formato_moneda(total_nomina_pendiente)}</div>
            <div class="mega-kpi-label">Nómina Pendiente</div>
            <div class="mega-kpi-sublabel">
                {resumen_nomina['pendientes']['turnos']} turnos sin pagar
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="mega-kpi info">
            <div class="mega-kpi-icon">💰</div>
            <div class="mega-kpi-valor">{formato_moneda(resumen_nomina['pagos_diarios']['neto'])}</div>
            <div class="mega-kpi-label">Pagado Este Mes</div>
            <div class="mega-kpi-sublabel">
                {resumen_nomina['pagos_diarios']['pagos']} pagos realizados
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # ==================== DEUDA POR NEGOCIO ====================
    st.markdown("""
    <div class="section-header danger">
        <div class="section-title">🏪 Deuda al Supermercado por Negocio</div>
    </div>
    """, unsafe_allow_html=True)
    
    deuda_negocios = get_dashboard_deuda_por_negocio()
    
    if deuda_negocios:
        # Crear barra de distribución
        total_deuda = sum(n['total_deuda'] for n in deuda_negocios)
        
        if total_deuda > 0:
            colores = ['#667eea', '#f5576c', '#11998e', '#f2994a', '#764ba2']
            bar_segments = ""
            for i, negocio in enumerate(deuda_negocios[:5]):
                porcentaje = (negocio['total_deuda'] / total_deuda * 100) if total_deuda > 0 else 0
                color = colores[i % len(colores)]
                if porcentaje > 5:
                    bar_segments += f'<div class="distribucion-segment" style="width: {porcentaje}%; background: {color};">{porcentaje:.0f}%</div>'
                else:
                    bar_segments += f'<div class="distribucion-segment" style="width: {porcentaje}%; background: {color};"></div>'
            
            st.markdown(f"""
            <div class="distribucion-bar">{bar_segments}</div>
            """, unsafe_allow_html=True)
        
        # Cards por negocio
        cols = st.columns(min(3, len(deuda_negocios)))
        for i, negocio in enumerate(deuda_negocios[:3]):
            with cols[i]:
                porcentaje = (negocio['total_deuda'] / total_deuda * 100) if total_deuda > 0 else 0
                st.markdown(f"""
                <div class="negocio-card">
                    <div class="negocio-nombre">🏪 {negocio['negocio']}</div>
                    <div class="negocio-valor">{formato_moneda(negocio['total_deuda'])}</div>
                    <div class="negocio-detalle">
                        📋 {negocio['remisiones_cantidad']} rem. ({formato_moneda(negocio['remisiones_total'])})<br>
                        🧾 {negocio['facturas_cantidad']} fact. ({formato_moneda(negocio['facturas_total'])})<br>
                        <strong>{porcentaje:.1f}% del total</strong>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Mostrar más negocios si hay
        if len(deuda_negocios) > 3:
            with st.expander(f"Ver {len(deuda_negocios) - 3} negocios más"):
                for negocio in deuda_negocios[3:]:
                    st.markdown(f"""
                    **{negocio['negocio']}**: {formato_moneda(negocio['total_deuda'])} 
                    ({negocio['remisiones_cantidad']} rem. + {negocio['facturas_cantidad']} fact.)
                    """)
    else:
        st.success("✅ No hay deudas pendientes con el supermercado")
    
    # ==================== RESUMEN DE NÓMINA ====================
    st.markdown("""
    <div class="section-header success">
        <div class="section-title">💵 Resumen de Nómina - Este Mes</div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="resumen-tabla">
            <h4 style="margin-bottom: 15px;">📊 Distribución del Gasto</h4>
            <div class="resumen-row">
                <span>💼 Salarios Brutos (pagados)</span>
                <span>{formato_moneda(resumen_nomina['pagos_diarios']['bruto'])}</span>
            </div>
            <div class="resumen-row">
                <span>➖ Descuentos Aplicados</span>
                <span style="color: #38ef7d;">-{formato_moneda(resumen_nomina['pagos_diarios']['descuentos'])}</span>
            </div>
            <div class="resumen-row">
                <span>🍽️ Consumos Descontados</span>
                <span>{formato_moneda(resumen_nomina['pagos_diarios']['consumos'])}</span>
            </div>
            <div class="resumen-row total">
                <span>💰 Total Neto Pagado</span>
                <span style="color: #667eea;">{formato_moneda(resumen_nomina['pagos_diarios']['neto'])}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="resumen-tabla">
            <h4 style="margin-bottom: 15px;">🎁 Subsidio de Comida ({resumen_nomina['porcentaje_subsidio']:.0f}%)</h4>
            <div class="resumen-row">
                <span>🍔 Total Consumo Alimentos</span>
                <span>{formato_moneda(resumen_nomina['total_consumo_alimentos'])}</span>
            </div>
            <div class="resumen-row">
                <span>📉 Porcentaje Subsidio</span>
                <span>{resumen_nomina['porcentaje_subsidio']:.0f}%</span>
            </div>
            <div class="resumen-row total">
                <span>💸 Gasto en Subsidio</span>
                <span style="color: #eb3349;">{formato_moneda(resumen_nomina['gasto_subsidio'])}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.caption("💡 El subsidio es lo que el negocio asume del consumo de los empleados")
    
    # ==================== GASTOS POR SEDE ====================
    st.markdown("""
    <div class="section-header">
        <div class="section-title">📍 Gastos de Nómina por Sede - Este Mes</div>
    </div>
    """, unsafe_allow_html=True)
    
    gastos_sede = get_dashboard_gastos_por_sede()
    
    if gastos_sede:
        cols = st.columns(len(gastos_sede))
        total_todas_sedes = sum(s['total_pagado'] for s in gastos_sede)
        
        for i, sede in enumerate(gastos_sede):
            with cols[i]:
                porcentaje = (sede['total_pagado'] / total_todas_sedes * 100) if total_todas_sedes > 0 else 0
                st.markdown(f"""
                <div class="kpi-card info">
                    <div class="kpi-icon">📍</div>
                    <div class="kpi-label">{sede['sede']}</div>
                    <div class="kpi-valor">{formato_moneda(sede['total_pagado'])}</div>
                    <div style="font-size: 0.8em; opacity: 0.7;">
                        {sede['pagos']} pagos | {porcentaje:.1f}% del total
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No hay pagos registrados este mes")
    
    # ==================== CUENTAS POR COBRAR A EMPLEADOS ====================
    if cuentas_pagar['total_cuentas'] > 0:
        st.markdown("""
        <div class="section-header warning">
            <div class="section-title">💳 Cuentas por Cobrar a Empleados (Consumos a Cuenta)</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="alerta-box">
            <strong>⚠️ Total por Cobrar: {formato_moneda(cuentas_pagar['total_cuentas'])}</strong><br>
            {len(cuentas_pagar['cuentas_empleados'])} empleado(s) con consumos a cuenta pendientes
        </div>
        """, unsafe_allow_html=True)
        
        if cuentas_pagar['cuentas_empleados']:
            df = pd.DataFrame(cuentas_pagar['cuentas_empleados'])
            df = df[['nombre', 'sede', 'cantidad', 'total']]
            df.columns = ['Empleado', 'Sede', 'Consumos', 'Deuda']
            df['Deuda'] = df['Deuda'].apply(formato_moneda)
            st.dataframe(df, use_container_width=True, hide_index=True)
    
    # ==================== EMPLEADOS Y OPERACIÓN ====================
    st.markdown("""
    <div class="section-header">
        <div class="section-title">👥 Estado de Empleados</div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="kpi-card info">
            <div class="kpi-icon">👥</div>
            <div class="kpi-valor">{resumen_general['total_empleados']}</div>
            <div class="kpi-label">Empleados Activos</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="kpi-card success">
            <div class="kpi-icon">🏃</div>
            <div class="kpi-valor">{resumen_general['empleados_trabajando']}</div>
            <div class="kpi-label">Trabajando Ahora</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        color = "warning" if resumen_general['turnos_pendientes_pago'] > 0 else "success"
        st.markdown(f"""
        <div class="kpi-card {color}">
            <div class="kpi-icon">⏳</div>
            <div class="kpi-valor">{resumen_general['turnos_pendientes_pago']}</div>
            <div class="kpi-label">Turnos Sin Pagar</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="kpi-card purple">
            <div class="kpi-icon">📅</div>
            <div class="kpi-valor">{resumen_nomina['pagos_diarios']['pagos']}</div>
            <div class="kpi-label">Pagos Este Mes</div>
        </div>
        """, unsafe_allow_html=True)
    
    # ==================== RESUMEN EJECUTIVO ====================
    st.markdown("""
    <div class="section-header">
        <div class="section-title">📋 Resumen Ejecutivo - Obligaciones Totales</div>
    </div>
    """, unsafe_allow_html=True)
    
    total_obligaciones = (
        deuda_super['total_deuda'] + 
        resumen_nomina['pendientes']['estimado']
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="resumen-tabla">
            <h4>💸 Por Pagar</h4>
            <div class="resumen-row">
                <span>🏪 Deuda Supermercado</span>
                <span>{formato_moneda(deuda_super['total_deuda'])}</span>
            </div>
            <div class="resumen-row">
                <span>👥 Nómina Pendiente</span>
                <span>{formato_moneda(resumen_nomina['pendientes']['estimado'])}</span>
            </div>
            <div class="resumen-row total">
                <span><strong>TOTAL OBLIGACIONES</strong></span>
                <span style="color: #eb3349;"><strong>{formato_moneda(total_obligaciones)}</strong></span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="resumen-tabla">
            <h4>💰 Este Mes</h4>
            <div class="resumen-row">
                <span>💵 Nómina Pagada</span>
                <span style="color: #38ef7d;">{formato_moneda(resumen_nomina['pagos_diarios']['neto'])}</span>
            </div>
            <div class="resumen-row">
                <span>🎁 Subsidio Comida</span>
                <span>{formato_moneda(resumen_nomina['gasto_subsidio'])}</span>
            </div>
            <div class="resumen-row">
                <span>💳 Por Cobrar a Empleados</span>
                <span style="color: #f2994a;">{formato_moneda(cuentas_pagar['total_cuentas'])}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.caption(f"📅 Dashboard actualizado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
