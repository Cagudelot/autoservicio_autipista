"""
Módulo de Cartera - Kikes (Negocios específicos)
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.utils.ui_helpers import get_db_connection, format_currency, create_metric_card, CSS_STYLES


# ==================== FUNCIONES DE DATOS ====================

@st.cache_data(ttl=60)
def get_negocios_kikes():
    """Obtiene los negocios relacionados con Kikes"""
    return ['COMIDAS RAPIDAS KIKE', 'COMIDAS RAPIDAS KIKE 2', 'KIKES PIZZA']


@st.cache_data(ttl=60)
def get_resumen_kikes():
    """Obtiene resumen de deudas de Kikes separado por negocio"""
    conn = get_db_connection()
    negocios = get_negocios_kikes()
    
    resultados = {}
    
    for negocio in negocios:
        # Remisiones
        query_rem = """
            SELECT COUNT(*) as cantidad, COALESCE(SUM(valor_remsion), 0) as total
            FROM remisiones
            WHERE nombre_negocio = %s AND estado_remision = 'open'
        """
        df_rem = pd.read_sql(query_rem, conn, params=(negocio,))
        
        # Facturas
        query_fact = """
            SELECT COUNT(*) as cantidad, COALESCE(SUM(balance_factura), 0) as total
            FROM facturas
            WHERE nombre_negocio = %s AND estado_factura = 'open'
        """
        df_fact = pd.read_sql(query_fact, conn, params=(negocio,))
        
        resultados[negocio] = {
            'remisiones_cantidad': int(df_rem['cantidad'].iloc[0]),
            'remisiones_total': float(df_rem['total'].iloc[0]),
            'facturas_cantidad': int(df_fact['cantidad'].iloc[0]),
            'facturas_total': float(df_fact['total'].iloc[0]),
            'total_deuda': float(df_rem['total'].iloc[0]) + float(df_fact['total'].iloc[0])
        }
    
    return resultados


@st.cache_data(ttl=60)
def get_remisiones_negocio(nombre_negocio):
    """Obtiene remisiones abiertas de un negocio específico"""
    conn = get_db_connection()
    query = """
        SELECT numero_remision, fecha, valor_remsion, estado_remision
        FROM remisiones
        WHERE nombre_negocio = %s AND estado_remision = 'open'
        ORDER BY fecha DESC
    """
    df = pd.read_sql(query, conn, params=(nombre_negocio,))
    return df


@st.cache_data(ttl=60)
def get_facturas_negocio(nombre_negocio):
    """Obtiene facturas abiertas de un negocio específico"""
    conn = get_db_connection()
    query = """
        SELECT numero_factura, fecha, balance_factura as valor_factura, estado_factura
        FROM facturas
        WHERE nombre_negocio = %s AND estado_factura = 'open'
        ORDER BY fecha DESC
    """
    df = pd.read_sql(query, conn, params=(nombre_negocio,))
    return df


@st.cache_data(ttl=60)
def get_evolucion_kikes():
    """Obtiene evolución de deudas por negocio por día"""
    conn = get_db_connection()
    negocios = get_negocios_kikes()
    
    query = """
        SELECT 
            fecha::date as dia,
            nombre_negocio,
            COUNT(*) as cantidad_remisiones,
            SUM(valor_remsion) as total_remisiones
        FROM remisiones
        WHERE nombre_negocio IN %s AND estado_remision = 'open'
        GROUP BY fecha::date, nombre_negocio
        ORDER BY dia, nombre_negocio
    """
    df = pd.read_sql(query, conn, params=(tuple(negocios),))
    return df


@st.cache_data(ttl=60)
def get_evolucion_acumulada_kikes():
    """Obtiene evolución acumulada de remisiones por negocio"""
    conn = get_db_connection()
    negocios = get_negocios_kikes()
    
    query = """
        SELECT 
            fecha::date as dia,
            nombre_negocio,
            valor_remsion,
            numero_remision
        FROM remisiones
        WHERE nombre_negocio IN %s AND estado_remision = 'open'
        ORDER BY fecha
    """
    df = pd.read_sql(query, conn, params=(tuple(negocios),))
    
    if df.empty:
        return df
    
    df['dia'] = pd.to_datetime(df['dia'])
    
    df_grouped = df.groupby(['dia', 'nombre_negocio']).agg({
        'valor_remsion': 'sum',
        'numero_remision': 'count'
    }).reset_index()
    df_grouped.columns = ['dia', 'nombre_negocio', 'valor_dia', 'cantidad']
    
    df_grouped = df_grouped.sort_values(['nombre_negocio', 'dia'])
    df_grouped['valor_acumulado'] = df_grouped.groupby('nombre_negocio')['valor_dia'].cumsum()
    
    return df_grouped


# ==================== COMPONENTES ====================

def render_negocio_card(nombre_negocio, datos, color_class="", icon="🏪"):
    """Renderiza una tarjeta de negocio con métricas"""
    return f"""
    <div class="kikes-card {color_class}">
        <div class="kikes-card-header">
            <span class="kikes-icon">{icon}</span>
            <span class="kikes-title">{nombre_negocio}</span>
        </div>
        <div class="kikes-total">{format_currency(datos['total_deuda'])}</div>
        <div class="kikes-details">
            <div class="kikes-detail-row">
                <span>📋 Remisiones ({datos['remisiones_cantidad']})</span>
                <span>{format_currency(datos['remisiones_total'])}</span>
            </div>
            <div class="kikes-detail-row">
                <span>🧾 Facturas ({datos['facturas_cantidad']})</span>
                <span>{format_currency(datos['facturas_total'])}</span>
            </div>
        </div>
    </div>
    """


def render_detalle_negocio(nombre_negocio, datos):
    """Renderiza el detalle expandido de un negocio"""
    with st.expander(f"📋 Ver detalle de {nombre_negocio}", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📋 Remisiones Pendientes")
            remisiones = get_remisiones_negocio(nombre_negocio)
            if not remisiones.empty:
                rem_display = remisiones.copy()
                rem_display.columns = ['N° Remisión', 'Fecha', 'Valor', 'Estado']
                rem_display['Valor'] = rem_display['Valor'].apply(lambda x: f"${x:,.0f}")
                st.dataframe(rem_display, hide_index=True, height=250)
            else:
                st.success("✅ Sin remisiones pendientes")
        
        with col2:
            st.markdown("#### 🧾 Facturas Pendientes")
            facturas = get_facturas_negocio(nombre_negocio)
            if not facturas.empty:
                fact_display = facturas.copy()
                fact_display.columns = ['N° Factura', 'Fecha', 'Valor', 'Estado']
                fact_display['Valor'] = fact_display['Valor'].apply(lambda x: f"${x:,.0f}")
                st.dataframe(fact_display, hide_index=True, height=250)
            else:
                st.success("✅ Sin facturas pendientes")


# ==================== ESTILOS ADICIONALES ====================

KIKES_STYLES = """
<style>
    .kikes-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        padding: 25px;
        margin: 10px 0;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .kikes-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(102, 126, 234, 0.4);
    }
    
    .kikes-card.card-orange {
        background: linear-gradient(135deg, #f5576c 0%, #f093fb 100%);
        box-shadow: 0 10px 30px rgba(245, 87, 108, 0.3);
    }
    
    .kikes-card.card-green {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        box-shadow: 0 10px 30px rgba(17, 153, 142, 0.3);
    }
    
    .kikes-card-header {
        display: flex;
        align-items: center;
        margin-bottom: 15px;
    }
    
    .kikes-icon {
        font-size: 2em;
        margin-right: 15px;
    }
    
    .kikes-title {
        font-size: 1.2em;
        font-weight: 600;
        color: white;
    }
    
    .kikes-total {
        font-size: 2.5em;
        font-weight: 700;
        color: white;
        margin: 15px 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .kikes-details {
        background: rgba(255,255,255,0.15);
        border-radius: 10px;
        padding: 15px;
        margin-top: 15px;
    }
    
    .kikes-detail-row {
        display: flex;
        justify-content: space-between;
        color: white;
        padding: 8px 0;
        border-bottom: 1px solid rgba(255,255,255,0.1);
    }
    
    .kikes-detail-row:last-child {
        border-bottom: none;
    }
    
    .total-general-card {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        border-radius: 20px;
        padding: 30px;
        text-align: center;
        box-shadow: 0 15px 40px rgba(30, 60, 114, 0.4);
        margin-bottom: 30px;
    }
    
    .total-general-title {
        color: rgba(255,255,255,0.8);
        font-size: 1em;
        font-weight: 500;
        letter-spacing: 2px;
        margin-bottom: 10px;
    }
    
    .total-general-value {
        color: white;
        font-size: 3em;
        font-weight: 700;
        text-shadow: 2px 2px 8px rgba(0,0,0,0.3);
    }
</style>
"""


# ==================== PÁGINA PRINCIPAL ====================

def render():
    """Renderiza la página de Kikes"""
    st.markdown(CSS_STYLES, unsafe_allow_html=True)
    st.markdown(KIKES_STYLES, unsafe_allow_html=True)
    
    # Header con botones
    col_titulo, col_btn1, col_btn2 = st.columns([4, 1, 1])
    
    with col_titulo:
        st.markdown('<p class="main-header">🍕 Dashboard Kikes</p>', unsafe_allow_html=True)
        st.markdown('<p class="sub-header">Control de deudas por negocio</p>', unsafe_allow_html=True)
    
    with col_btn1:
        st.write("")  # Espaciado
        if st.button("🔄 Sincronizar Alegra", key="sync_kikes", help="Actualizar datos desde Alegra"):
            with st.spinner("Sincronizando datos desde Alegra..."):
                try:
                    import sys
                    import os
                    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
                    from services.alegra_api import full_sync_all
                    full_sync_all()
                    st.cache_data.clear()
                    st.success("✅ Sincronización completada")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    with col_btn2:
        st.write("")  # Espaciado
        if st.button("🔃 Refrescar", key="kikes_refresh"):
            st.cache_data.clear()
            st.rerun()
    
    st.markdown("---")
    
    resumen = get_resumen_kikes()
    
    total_general = sum(datos['total_deuda'] for datos in resumen.values())
    total_remisiones = sum(datos['remisiones_cantidad'] for datos in resumen.values())
    total_facturas = sum(datos['facturas_cantidad'] for datos in resumen.values())
    
    st.markdown(f"""
    <div class="total-general-card">
        <div class="total-general-title">💰 DEUDA TOTAL KIKES</div>
        <div class="total-general-value">{format_currency(total_general)}</div>
        <div style="color: rgba(255,255,255,0.7); margin-top: 10px;">
            📋 {total_remisiones} remisiones | 🧾 {total_facturas} facturas
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Cards de negocios
    icons = ['🍔', '🍟', '🍕']
    colors = ['', 'card-orange', 'card-green']
    negocios = get_negocios_kikes()
    
    cols = st.columns(3)
    
    for i, negocio in enumerate(negocios):
        with cols[i]:
            datos = resumen.get(negocio, {
                'remisiones_cantidad': 0, 'remisiones_total': 0,
                'facturas_cantidad': 0, 'facturas_total': 0, 'total_deuda': 0
            })
            st.markdown(render_negocio_card(negocio, datos, colors[i], icons[i]), unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Gráficos comparativos
    st.markdown("### 📊 Análisis Comparativo")
    
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        df_comparativo = pd.DataFrame([
            {'Negocio': n, 'Remisiones': resumen[n]['remisiones_total'], 'Facturas': resumen[n]['facturas_total']}
            for n in negocios
        ])
        
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            name='Remisiones',
            x=df_comparativo['Negocio'],
            y=df_comparativo['Remisiones'],
            marker_color='#f5576c'
        ))
        fig_bar.add_trace(go.Bar(
            name='Facturas',
            x=df_comparativo['Negocio'],
            y=df_comparativo['Facturas'],
            marker_color='#4facfe'
        ))
        
        fig_bar.update_layout(
            title='Deuda por Negocio',
            barmode='group',
            height=350,
            margin=dict(t=40, b=20, l=20, r=20),
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
        )
        st.plotly_chart(fig_bar, key="kikes_bar")
    
    with col_chart2:
        df_dona = pd.DataFrame([
            {'Negocio': n, 'Total': resumen[n]['total_deuda']}
            for n in negocios
        ])
        
        fig_dona = go.Figure(data=[go.Pie(
            labels=df_dona['Negocio'],
            values=df_dona['Total'],
            hole=.5,
            marker_colors=['#667eea', '#f5576c', '#11998e'],
            textinfo='label+percent',
            textposition='outside'
        )])
        
        fig_dona.update_layout(
            title='Distribución de Deuda',
            height=350,
            margin=dict(t=40, b=20, l=20, r=20),
            showlegend=False
        )
        st.plotly_chart(fig_dona, key="kikes_dona")
    
    # Evolución temporal
    st.markdown("### 📈 Comportamiento de Remisiones Pendientes por Día")
    
    evolucion = get_evolucion_kikes()
    evolucion_acum = get_evolucion_acumulada_kikes()
    
    if not evolucion.empty:
        tipo_grafico = st.radio(
            "Tipo de visualización:",
            ["📊 Por día", "📈 Acumulado"],
            horizontal=True,
            key="tipo_grafico_kikes"
        )
        
        if tipo_grafico == "📊 Por día":
            fig_evol = px.bar(
                evolucion,
                x='dia',
                y='total_remisiones',
                color='nombre_negocio',
                barmode='group',
                color_discrete_map={
                    'COMIDAS RAPIDAS KIKE': '#667eea',
                    'COMIDAS RAPIDAS KIKE 2': '#f5576c',
                    'KIKES PIZZA': '#11998e'
                },
                labels={
                    'dia': 'Fecha',
                    'total_remisiones': 'Valor ($)',
                    'nombre_negocio': 'Negocio'
                }
            )
            fig_evol.update_layout(
                xaxis_title="Fecha",
                yaxis_title="Valor de Remisiones ($)",
                margin=dict(t=20, b=20, l=20, r=20),
                height=400,
                legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
                xaxis=dict(tickformat='%d %b %Y', tickangle=-45)
            )
            st.plotly_chart(fig_evol, key="kikes_evol_dia")
            
            with st.expander("📋 Ver detalle por día"):
                pivot_df = evolucion.pivot_table(
                    index='dia', 
                    columns='nombre_negocio', 
                    values='total_remisiones', 
                    fill_value=0,
                    aggfunc='sum'
                ).reset_index()
                pivot_df['dia'] = pd.to_datetime(pivot_df['dia']).dt.strftime('%d/%m/%Y')
                for col in pivot_df.columns[1:]:
                    pivot_df[col] = pivot_df[col].apply(lambda x: f"${x:,.0f}")
                st.dataframe(pivot_df, hide_index=True)
        else:
            if not evolucion_acum.empty:
                fig_acum = px.line(
                    evolucion_acum,
                    x='dia',
                    y='valor_acumulado',
                    color='nombre_negocio',
                    markers=True,
                    color_discrete_map={
                        'COMIDAS RAPIDAS KIKE': '#667eea',
                        'COMIDAS RAPIDAS KIKE 2': '#f5576c',
                        'KIKES PIZZA': '#11998e'
                    },
                    labels={
                        'dia': 'Fecha',
                        'valor_acumulado': 'Valor Acumulado ($)',
                        'nombre_negocio': 'Negocio'
                    }
                )
                fig_acum.update_layout(
                    xaxis_title="Fecha",
                    yaxis_title="Valor Acumulado ($)",
                    margin=dict(t=20, b=20, l=20, r=20),
                    height=400,
                    legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
                    xaxis=dict(tickformat='%d %b %Y', tickangle=-45)
                )
                st.plotly_chart(fig_acum, key="kikes_evol_acum")
            else:
                st.info("No hay datos acumulados disponibles")
    else:
        st.info("No hay datos de evolución disponibles")
    
    # Detalles expandibles por negocio
    st.markdown("### 📋 Detalle por Negocio")
    
    for negocio in negocios:
        render_detalle_negocio(negocio, resumen.get(negocio, {}))
