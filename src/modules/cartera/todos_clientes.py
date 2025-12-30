"""
Módulo de Cartera - Todos los Clientes
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
def get_clientes():
    """Obtiene lista de clientes"""
    conn = get_db_connection()
    query = """
        SELECT DISTINCT c.id_cliente, c.nombre_cliente, c.nit_cliente
        FROM clientes c
        ORDER BY c.nombre_cliente
    """
    df = pd.read_sql(query, conn)
    return df


@st.cache_data(ttl=60)
def get_negocios_cliente(id_cliente):
    """Obtiene negocios de un cliente"""
    conn = get_db_connection()
    query = """
        SELECT id_negocio, nombre_negocio
        FROM negocios
        WHERE id_cliente = %s
        ORDER BY nombre_negocio
    """
    df = pd.read_sql(query, conn, params=(int(id_cliente),))
    return df


@st.cache_data(ttl=60)
def get_resumen_global():
    """Obtiene resumen global de deudas"""
    conn = get_db_connection()
    
    query_rem = """
        SELECT COUNT(*) as cantidad, COALESCE(SUM(valor_remsion), 0) as total
        FROM remisiones
        WHERE estado_remision = 'open'
    """
    df_rem = pd.read_sql(query_rem, conn)
    
    query_fact = """
        SELECT COUNT(*) as cantidad, COALESCE(SUM(balance_factura), 0) as total
        FROM facturas
        WHERE estado_factura = 'open'
    """
    df_fact = pd.read_sql(query_fact, conn)
    
    return {
        'remisiones_cantidad': int(df_rem['cantidad'].iloc[0]),
        'remisiones_total': float(df_rem['total'].iloc[0]),
        'facturas_cantidad': int(df_fact['cantidad'].iloc[0]),
        'facturas_total': float(df_fact['total'].iloc[0])
    }


@st.cache_data(ttl=60)
def get_deudas_por_cliente(id_cliente=None):
    """Obtiene deudas agrupadas por cliente"""
    conn = get_db_connection()
    
    where_clause = ""
    params = ()
    if id_cliente:
        where_clause = "AND c.id_cliente = %s"
        params = (int(id_cliente),)
    
    query = f"""
        SELECT 
            c.id_cliente,
            c.nombre_cliente,
            c.nit_cliente,
            COALESCE(rem.cantidad_remisiones, 0) as cantidad_remisiones,
            COALESCE(rem.total_remisiones, 0) as total_remisiones,
            COALESCE(fact.cantidad_facturas, 0) as cantidad_facturas,
            COALESCE(fact.total_facturas, 0) as total_facturas
        FROM clientes c
        LEFT JOIN (
            SELECT id_cliente, COUNT(*) as cantidad_remisiones, SUM(valor_remsion) as total_remisiones
            FROM remisiones
            WHERE estado_remision = 'open'
            GROUP BY id_cliente
        ) rem ON c.id_cliente = rem.id_cliente
        LEFT JOIN (
            SELECT id_cliente, COUNT(*) as cantidad_facturas, SUM(balance_factura) as total_facturas
            FROM facturas
            WHERE estado_factura = 'open'
            GROUP BY id_cliente
        ) fact ON c.id_cliente = fact.id_cliente
        WHERE (rem.cantidad_remisiones > 0 OR fact.cantidad_facturas > 0)
        {where_clause}
        ORDER BY (COALESCE(rem.total_remisiones, 0) + COALESCE(fact.total_facturas, 0)) DESC
    """
    df = pd.read_sql(query, conn, params=params if params else None)
    return df


@st.cache_data(ttl=60)
def get_deudas_por_negocio(id_cliente=None):
    """Obtiene deudas agrupadas por negocio"""
    conn = get_db_connection()
    
    where_rem = "WHERE estado_remision = 'open'"
    where_fact = "WHERE estado_factura = 'open'"
    
    if id_cliente:
        where_rem += f" AND id_cliente = {int(id_cliente)}"
        where_fact += f" AND id_cliente = {int(id_cliente)}"
    
    query = f"""
        WITH remisiones_negocio AS (
            SELECT nombre_negocio, COUNT(*) as cantidad, SUM(valor_remsion) as total
            FROM remisiones
            {where_rem}
            GROUP BY nombre_negocio
        ),
        facturas_negocio AS (
            SELECT nombre_negocio, COUNT(*) as cantidad, SUM(balance_factura) as total
            FROM facturas
            {where_fact}
            GROUP BY nombre_negocio
        )
        SELECT 
            COALESCE(r.nombre_negocio, f.nombre_negocio) as nombre_negocio,
            COALESCE(r.cantidad, 0) as cantidad_remisiones,
            COALESCE(r.total, 0) as total_remisiones,
            COALESCE(f.cantidad, 0) as cantidad_facturas,
            COALESCE(f.total, 0) as total_facturas
        FROM remisiones_negocio r
        FULL OUTER JOIN facturas_negocio f ON r.nombre_negocio = f.nombre_negocio
        ORDER BY (COALESCE(r.total, 0) + COALESCE(f.total, 0)) DESC
    """
    df = pd.read_sql(query, conn)
    return df


@st.cache_data(ttl=60)
def get_remisiones_detalle(nombre_negocio=None, id_cliente=None):
    """Obtiene detalle de remisiones"""
    conn = get_db_connection()
    
    conditions = ["estado_remision = 'open'"]
    params = []
    
    if nombre_negocio:
        conditions.append("nombre_negocio = %s")
        params.append(nombre_negocio)
    if id_cliente:
        conditions.append("id_cliente = %s")
        params.append(int(id_cliente))
    
    where_clause = " AND ".join(conditions)
    
    query = f"""
        SELECT numero_remision, fecha, nombre_negocio, valor_remsion as valor, estado_remision
        FROM remisiones
        WHERE {where_clause}
        ORDER BY fecha DESC
    """
    df = pd.read_sql(query, conn, params=params if params else None)
    return df


@st.cache_data(ttl=60)
def get_facturas_detalle(nombre_negocio=None, id_cliente=None):
    """Obtiene detalle de facturas"""
    conn = get_db_connection()
    
    conditions = ["estado_factura = 'open'"]
    params = []
    
    if nombre_negocio:
        conditions.append("nombre_negocio = %s")
        params.append(nombre_negocio)
    if id_cliente:
        conditions.append("id_cliente = %s")
        params.append(int(id_cliente))
    
    where_clause = " AND ".join(conditions)
    
    query = f"""
        SELECT numero_factura, fecha, nombre_negocio, balance_factura as valor, estado_factura
        FROM facturas
        WHERE {where_clause}
        ORDER BY fecha DESC
    """
    df = pd.read_sql(query, conn, params=params if params else None)
    return df


# ==================== INTERFAZ ====================

def render():
    """Renderiza la página de todos los clientes"""
    st.markdown(CSS_STYLES, unsafe_allow_html=True)
    
    st.markdown('<h1 class="main-header">📊 Cartera - Todos los Clientes</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Resumen de deudas de todos los clientes</p>', unsafe_allow_html=True)
    
    # Resumen global
    resumen = get_resumen_global()
    total_deuda = resumen['remisiones_total'] + resumen['facturas_total']
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(
            create_metric_card("Total Deuda", format_currency(total_deuda), "💰", "metric-card-red"),
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            create_metric_card(
                f"Remisiones ({resumen['remisiones_cantidad']})",
                format_currency(resumen['remisiones_total']),
                "📋",
                "metric-card-orange"
            ),
            unsafe_allow_html=True
        )
    
    with col3:
        st.markdown(
            create_metric_card(
                f"Facturas ({resumen['facturas_cantidad']})",
                format_currency(resumen['facturas_total']),
                "📄",
                "metric-card-blue"
            ),
            unsafe_allow_html=True
        )
    
    st.markdown("---")
    
    # Filtros
    col_filtro1, col_filtro2 = st.columns(2)
    
    with col_filtro1:
        clientes = get_clientes()
        cliente_options = ["Todos los clientes"] + clientes['nombre_cliente'].tolist()
        cliente_seleccionado = st.selectbox("🔍 Filtrar por cliente:", cliente_options)
    
    id_cliente_filtro = None
    if cliente_seleccionado != "Todos los clientes":
        id_cliente_filtro = clientes[clientes['nombre_cliente'] == cliente_seleccionado]['id_cliente'].iloc[0]
    
    # Tabs para diferentes vistas
    tab1, tab2, tab3 = st.tabs(["📊 Por Cliente", "🏪 Por Negocio", "📋 Detalle"])
    
    with tab1:
        df_clientes = get_deudas_por_cliente(id_cliente_filtro)
        if not df_clientes.empty:
            df_clientes['total_deuda'] = df_clientes['total_remisiones'] + df_clientes['total_facturas']
            
            # Gráfico
            fig = px.bar(
                df_clientes.head(10),
                x='nombre_cliente',
                y='total_deuda',
                title='Top 10 Clientes con Mayor Deuda',
                color='total_deuda',
                color_continuous_scale='Reds'
            )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
            
            # Tabla
            st.dataframe(
                df_clientes[['nombre_cliente', 'cantidad_remisiones', 'total_remisiones', 
                            'cantidad_facturas', 'total_facturas', 'total_deuda']].style.format({
                    'total_remisiones': '${:,.0f}',
                    'total_facturas': '${:,.0f}',
                    'total_deuda': '${:,.0f}'
                }),
                use_container_width=True
            )
        else:
            st.info("No hay deudas registradas")
    
    with tab2:
        df_negocios = get_deudas_por_negocio(id_cliente_filtro)
        if not df_negocios.empty:
            df_negocios['total_deuda'] = df_negocios['total_remisiones'] + df_negocios['total_facturas']
            
            # Gráfico de pie
            fig = px.pie(
                df_negocios,
                values='total_deuda',
                names='nombre_negocio',
                title='Distribución de Deuda por Negocio'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Tabla
            st.dataframe(
                df_negocios.style.format({
                    'total_remisiones': '${:,.0f}',
                    'total_facturas': '${:,.0f}',
                    'total_deuda': '${:,.0f}'
                }),
                use_container_width=True
            )
        else:
            st.info("No hay deudas por negocio")
    
    with tab3:
        col_det1, col_det2 = st.columns(2)
        
        with col_det1:
            st.subheader("📋 Remisiones Abiertas")
            df_rem = get_remisiones_detalle(id_cliente=id_cliente_filtro)
            if not df_rem.empty:
                st.dataframe(
                    df_rem.style.format({'valor': '${:,.0f}'}),
                    use_container_width=True
                )
            else:
                st.info("No hay remisiones abiertas")
        
        with col_det2:
            st.subheader("📄 Facturas Abiertas")
            df_fact = get_facturas_detalle(id_cliente=id_cliente_filtro)
            if not df_fact.empty:
                st.dataframe(
                    df_fact.style.format({'valor': '${:,.0f}'}),
                    use_container_width=True
                )
            else:
                st.info("No hay facturas abiertas")
