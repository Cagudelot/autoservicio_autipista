"""
Módulo de Nómina - Descuentos de Nómina
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from data_base.controler import (
    get_empleados_con_turno_abierto,
    get_all_empleados_activos,
    get_all_sedes,
    insert_descuento_nomina,
    get_descuentos_nomina,
    get_resumen_descuentos_por_empleado,
    delete_descuento_nomina
)
from src.utils.ui_helpers import CSS_STYLES


# ==================== TIPOS DE DESCUENTO ====================
TIPOS_DESCUENTO = [
    "Consumo Alimento",
    "Pérdidas Asumidas",
    "Préstamo",
    "Adelanto",
    "Otro"
]


# ==================== ESTILOS ====================
DESCUENTOS_STYLES = """
<style>
    .descuento-card {
        background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
        border-radius: 15px;
        padding: 20px;
        color: white;
        text-align: center;
        margin: 10px 0;
        box-shadow: 0 10px 30px rgba(235, 51, 73, 0.3);
    }
    
    .descuento-card.cantidad {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .descuento-card.promedio {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    }
    
    .descuento-valor {
        font-size: 2.2em;
        font-weight: 700;
        margin: 10px 0;
    }
    
    .descuento-label {
        font-size: 0.9em;
        opacity: 0.9;
    }
    
    .form-container {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border-radius: 15px;
        padding: 25px;
        margin: 15px 0;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    .empleado-turno-badge {
        background: linear-gradient(90deg, #11998e, #38ef7d);
        padding: 8px 15px;
        border-radius: 20px;
        font-size: 0.9em;
        display: inline-block;
        margin: 5px;
        color: white;
    }
    
    .descuento-item {
        background: rgba(255,255,255,0.05);
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border-left: 4px solid #f45c43;
    }
</style>
"""


def render():
    """Renderiza la vista de Descuentos de Nómina"""
    st.markdown(CSS_STYLES, unsafe_allow_html=True)
    st.markdown(DESCUENTOS_STYLES, unsafe_allow_html=True)
    
    # Verificar si es admin_negocio para limitar funcionalidades
    user = st.session_state.get('user', {})
    es_admin_negocio = user.get('rol') == 'admin_negocio'
    id_sede_filtro = user.get('id_sede') if es_admin_negocio else None
    nombre_sede = user.get('nombre_sede', 'Tu sede') if es_admin_negocio else None
    
    st.markdown("### 💸 Descuentos de Nómina")
    st.caption("Registra y visualiza los descuentos aplicados a los empleados")
    
    # Mostrar sede si es admin_negocio
    if id_sede_filtro:
        st.info(f"📍 Mostrando datos de: **{nombre_sede}**")
    
    # Admin negocio solo puede registrar descuentos (no ver historial)
    if es_admin_negocio:
        render_formulario_descuento(id_sede_filtro)
    else:
        # Tabs para separar registro y visualización
        tab1, tab2 = st.tabs(["📝 Registrar Descuento", "📋 Ver Descuentos"])
        
        with tab1:
            render_formulario_descuento(id_sede_filtro)
        
        with tab2:
            render_lista_descuentos()


def render_formulario_descuento(id_sede_filtro=None):
    """Renderiza el formulario para registrar un descuento"""
    st.markdown("#### 📝 Nuevo Descuento")
    
    # Obtener empleados con turno abierto (sin hora de salida), filtrados por sede si aplica
    empleados_turno_abierto = get_empleados_con_turno_abierto(id_sede_filtro)
    
    if not empleados_turno_abierto:
        st.warning("⚠️ No hay empleados con turno abierto actualmente")
        st.info("💡 Solo puedes registrar descuentos a empleados que tengan un turno activo (sin hora de salida)")
        return
    
    st.success(f"✅ {len(empleados_turno_abierto)} empleado(s) con turno abierto")
    
    st.markdown("---")
    
    # Formulario
    with st.form(key="form_descuento", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            # Selector de empleado - Solo los que tienen turno abierto
            opciones_empleados = {}
            for emp in empleados_turno_abierto:
                opciones_empleados[f"{emp['nombre_empleado']} ({emp['nombre_sede']})"] = emp['id_empleado']
            
            empleado_seleccionado = st.selectbox(
                "Empleado *",
                options=list(opciones_empleados.keys()),
                help="Solo se muestran empleados con turno abierto"
            )
        
        with col2:
            tipo_descuento = st.selectbox(
                "Tipo de Descuento *",
                options=TIPOS_DESCUENTO,
                help="Selecciona el tipo de descuento a aplicar"
            )
        
        col3, col4 = st.columns(2)
        
        with col3:
            detalle = st.text_area(
                "Detalle",
                placeholder="Describe el motivo del descuento...",
                help="Descripción detallada del descuento",
                height=100
            )
        
        with col4:
            valor = st.number_input(
                "Valor ($) *",
                min_value=0,
                step=1000,
                format="%d",
                help="Valor del descuento en pesos"
            )
            
            fecha = st.date_input(
                "Fecha",
                value=datetime.now().date(),
                help="Fecha del descuento"
            )
        
        st.markdown("---")
        
        submitted = st.form_submit_button(
            "💾 Guardar Descuento",
            use_container_width=True,
            type="primary"
        )
        
        if submitted:
            # Validaciones
            errores = []
            
            if not empleado_seleccionado:
                errores.append("Debes seleccionar un empleado")
            
            if valor <= 0:
                errores.append("El valor debe ser mayor a 0")
            
            if errores:
                for error in errores:
                    st.error(f"❌ {error}")
            else:
                id_empleado = opciones_empleados[empleado_seleccionado]
                
                id_descuento, error = insert_descuento_nomina(
                    id_empleado=id_empleado,
                    tipo_descuento=tipo_descuento,
                    detalle=detalle.strip() if detalle else None,
                    valor=valor,
                    fecha=fecha
                )
                
                if error:
                    st.error(f"❌ Error al guardar: {error}")
                else:
                    st.success(f"✅ Descuento registrado correctamente (ID: {id_descuento})")


def render_lista_descuentos():
    """Renderiza la lista de descuentos con filtros"""
    st.markdown("#### 📋 Historial de Descuentos")
    
    # ==================== FILTROS ====================
    with st.expander("🔍 Filtros", expanded=True):
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            fecha_inicio = st.date_input(
                "Fecha inicio",
                value=datetime.now().date() - timedelta(days=30),
                key="fecha_inicio_descuentos"
            )
        
        with col2:
            fecha_fin = st.date_input(
                "Fecha fin",
                value=datetime.now().date(),
                key="fecha_fin_descuentos"
            )
        
        with col3:
            sedes = get_all_sedes()
            opciones_sedes = {"Todas": None}
            for sede in sedes:
                opciones_sedes[sede['nombre_sede']] = sede['id_sede']
            
            sede_seleccionada = st.selectbox(
                "Sede",
                options=list(opciones_sedes.keys()),
                key="sede_filtro_descuentos"
            )
            id_sede = opciones_sedes[sede_seleccionada]
        
        with col4:
            empleados = get_all_empleados_activos()
            opciones_empleados = {"Todos": None}
            for emp in empleados:
                opciones_empleados[emp['nombre_empleado']] = emp['id_empleado']
            
            empleado_filtro = st.selectbox(
                "Empleado",
                options=list(opciones_empleados.keys()),
                key="empleado_filtro_descuentos"
            )
            id_empleado = opciones_empleados[empleado_filtro]
    
    # ==================== OBTENER DATOS ====================
    descuentos = get_descuentos_nomina(
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        id_empleado=id_empleado,
        id_sede=id_sede
    )
    
    if not descuentos:
        st.info("📭 No se encontraron descuentos para los filtros seleccionados.")
        return
    
    # ==================== MÉTRICAS ====================
    total_valor = sum(d['valor'] for d in descuentos)
    total_descuentos = len(descuentos)
    promedio = total_valor / total_descuentos if total_descuentos > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="descuento-card">
            <div class="descuento-label">💰 Total Descuentos</div>
            <div class="descuento-valor">${total_valor:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="descuento-card cantidad">
            <div class="descuento-label">📋 Cantidad</div>
            <div class="descuento-valor">{total_descuentos}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="descuento-card promedio">
            <div class="descuento-label">📊 Promedio</div>
            <div class="descuento-valor">${promedio:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ==================== TABLA DE DESCUENTOS ====================
    df = pd.DataFrame(descuentos)
    
    # Formatear columnas
    df['fecha'] = pd.to_datetime(df['fecha']).dt.strftime('%Y-%m-%d')
    df['valor_fmt'] = df['valor'].apply(lambda x: f"${x:,.0f}")
    
    df_display = df.rename(columns={
        'nombre_empleado': 'Empleado',
        'nombre_sede': 'Sede',
        'tipo_descuento': 'Tipo',
        'detalle': 'Detalle',
        'valor_fmt': 'Valor',
        'fecha': 'Fecha'
    })
    
    columnas_mostrar = ['Empleado', 'Sede', 'Tipo', 'Detalle', 'Valor', 'Fecha']
    
    st.dataframe(
        df_display[columnas_mostrar],
        use_container_width=True,
        hide_index=True
    )
    
    # ==================== RESUMEN POR EMPLEADO ====================
    if id_empleado is None:
        st.markdown("---")
        st.markdown("#### 👥 Resumen por Empleado")
        
        resumen = get_resumen_descuentos_por_empleado(
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            id_sede=id_sede
        )
        
        if resumen:
            df_resumen = pd.DataFrame(resumen)
            df_resumen['total_valor_fmt'] = df_resumen['total_valor'].apply(lambda x: f"${x:,.0f}")
            
            df_resumen_display = df_resumen.rename(columns={
                'nombre_empleado': 'Empleado',
                'nombre_sede': 'Sede',
                'total_descuentos': 'Cant. Descuentos',
                'total_valor_fmt': 'Total Descuentos'
            })
            
            st.dataframe(
                df_resumen_display[['Empleado', 'Sede', 'Cant. Descuentos', 'Total Descuentos']],
                use_container_width=True,
                hide_index=True
            )
    
    # ==================== ELIMINAR DESCUENTO ====================
    st.markdown("---")
    st.markdown("#### 🗑️ Eliminar Descuento")
    
    with st.expander("Eliminar un descuento", expanded=False):
        opciones_eliminar = {f"ID {d['id_descuento']} - {d['nombre_empleado']} - {d['tipo_descuento']} - ${d['valor']:,.0f} ({d['fecha']})": d['id_descuento'] for d in descuentos}
        
        descuento_a_eliminar = st.selectbox(
            "Selecciona el descuento a eliminar",
            options=list(opciones_eliminar.keys()),
            key="descuento_eliminar"
        )
        
        col_del1, col_del2 = st.columns([1, 3])
        
        with col_del1:
            if st.button("🗑️ Eliminar", type="secondary", use_container_width=True):
                id_del = opciones_eliminar[descuento_a_eliminar]
                exito, error = delete_descuento_nomina(id_del)
                if exito:
                    st.success("✅ Descuento eliminado")
                    st.rerun()
                else:
                    st.error(f"❌ Error: {error}")
    
    # ==================== EXPORTAR ====================
    st.markdown("---")
    col_export1, col_export2 = st.columns([1, 4])
    
    with col_export1:
        df_export = df_display[columnas_mostrar].copy()
        csv = df_export.to_csv(index=False).encode('utf-8')
        
        st.download_button(
            label="📥 Exportar CSV",
            data=csv,
            file_name=f"descuentos_nomina_{fecha_inicio}_{fecha_fin}.csv",
            mime="text/csv"
        )
