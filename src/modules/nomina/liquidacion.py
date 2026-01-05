"""
Módulo de Nómina - Liquidación de Nómina
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from decimal import Decimal
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from data_base.controler import (
    get_turnos_pendientes_pago,
    get_descuentos_pendientes_pago,
    get_horas_extra_pendientes_pago,
    get_configuracion_nomina,
    update_configuracion_nomina,
    crear_liquidacion,
    get_liquidaciones,
    get_detalle_liquidacion,
    actualizar_estado_liquidacion,
    anular_liquidacion,
    eliminar_liquidacion,
    actualizar_detalle_liquidacion,
    get_all_empleados_activos
)
from src.utils.ui_helpers import CSS_STYLES


# ==================== CONSTANTES ====================
VALOR_HORA_EXTRA_MULTIPLICADOR = 1.25  # Las horas extra valen 25% más


# ==================== ESTILOS ====================
LIQUIDACION_STYLES = """
<style>
    .liquidacion-header {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border-radius: 15px;
        padding: 25px;
        margin: 15px 0;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        padding: 20px;
        color: white;
        text-align: center;
        margin: 10px 0;
    }
    
    .metric-card.success {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    }
    
    .metric-card.danger {
        background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
    }
    
    .metric-card.warning {
        background: linear-gradient(135deg, #f2994a 0%, #f2c94c 100%);
    }
    
    .metric-value {
        font-size: 1.8em;
        font-weight: 700;
    }
    
    .metric-label {
        font-size: 0.85em;
        opacity: 0.9;
    }
    
    .empleado-card {
        background: rgba(255,255,255,0.05);
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
        border-left: 4px solid #667eea;
    }
    
    .empleado-card.modificado {
        border-left-color: #f2994a;
    }
    
    .empleado-nombre {
        font-size: 1.2em;
        font-weight: 600;
        color: #667eea;
    }
    
    .detalle-row {
        display: flex;
        justify-content: space-between;
        padding: 5px 0;
        border-bottom: 1px solid rgba(255,255,255,0.05);
    }
    
    .total-row {
        font-weight: 700;
        font-size: 1.1em;
        padding: 10px 0;
        border-top: 2px solid rgba(255,255,255,0.2);
        margin-top: 10px;
    }
    
    .config-card {
        background: linear-gradient(135deg, #434343 0%, #000000 100%);
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
    }
    
    .estado-badge {
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 0.85em;
        font-weight: 600;
    }
    
    .estado-pendiente {
        background: #f2994a;
        color: white;
    }
    
    .estado-pagado {
        background: #38ef7d;
        color: #1a1a2e;
    }
    
    .estado-anulado {
        background: #eb3349;
        color: white;
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
    """Renderiza la vista principal de Liquidación de Nómina"""
    st.markdown(CSS_STYLES, unsafe_allow_html=True)
    st.markdown(LIQUIDACION_STYLES, unsafe_allow_html=True)
    
    st.markdown("### 💰 Liquidación de Nómina")
    st.caption("Genera y administra las liquidaciones de nómina de tus empleados")
    
    # Tabs principales
    tab1, tab2, tab3, tab4 = st.tabs([
        "📝 Nueva Liquidación", 
        "📋 Historial",
        "✏️ Editar / Eliminar",
        "⚙️ Configuración"
    ])
    
    with tab1:
        render_nueva_liquidacion()
    
    with tab2:
        render_historial_liquidaciones()
    
    with tab3:
        render_editar_eliminar()
    
    with tab4:
        render_configuracion()


def render_configuracion():
    """Renderiza la configuración de nómina"""
    st.markdown("#### ⚙️ Configuración de Nómina")
    
    config = get_configuracion_nomina('descuento_comida_porcentaje')
    
    if config:
        st.markdown("""
        <div class="config-card">
            <h4>🍽️ Descuento en Consumos de Alimento</h4>
            <p style="opacity:0.7;">Este porcentaje se aplica como descuento a los consumos de alimento de los empleados</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            nuevo_porcentaje = st.slider(
                "Porcentaje de descuento (%)",
                min_value=0,
                max_value=100,
                value=int(config['valor_config']),
                step=5,
                help="Porcentaje que se descuenta del valor de los consumos de alimento"
            )
        
        with col2:
            st.metric(
                "Valor actual",
                f"{config['valor_config']:.0f}%",
                delta=f"{nuevo_porcentaje - config['valor_config']:.0f}%" if nuevo_porcentaje != config['valor_config'] else None
            )
        
        if nuevo_porcentaje != config['valor_config']:
            if st.button("💾 Guardar Configuración", type="primary"):
                success, error = update_configuracion_nomina('descuento_comida_porcentaje', nuevo_porcentaje)
                if success:
                    st.success("✅ Configuración actualizada correctamente")
                    st.rerun()
                else:
                    st.error(f"❌ Error: {error}")
    else:
        st.warning("⚠️ No se encontró la configuración. Contacta al administrador.")


def render_nueva_liquidacion():
    """Renderiza el formulario para crear una nueva liquidación"""
    st.markdown("#### 📝 Crear Nueva Liquidación")
    
    # Selector de rango de fechas
    col1, col2 = st.columns(2)
    
    with col1:
        fecha_inicio = st.date_input(
            "Fecha Inicio",
            value=datetime.now().date() - timedelta(days=7),
            help="Fecha de inicio del período a liquidar"
        )
    
    with col2:
        fecha_fin = st.date_input(
            "Fecha Fin",
            value=datetime.now().date(),
            help="Fecha de fin del período a liquidar"
        )
    
    if fecha_inicio > fecha_fin:
        st.error("❌ La fecha de inicio no puede ser mayor que la fecha de fin")
        return
    
    # Botón para cargar datos
    if st.button("🔄 Cargar Datos del Período", type="primary", use_container_width=True):
        st.session_state['liquidacion_fecha_inicio'] = fecha_inicio
        st.session_state['liquidacion_fecha_fin'] = fecha_fin
        st.session_state['liquidacion_cargada'] = True
    
    # Si hay datos cargados, mostrar preliquidación
    if st.session_state.get('liquidacion_cargada'):
        f_inicio = st.session_state.get('liquidacion_fecha_inicio', fecha_inicio)
        f_fin = st.session_state.get('liquidacion_fecha_fin', fecha_fin)
        
        render_preliquidacion(f_inicio, f_fin)


def render_preliquidacion(fecha_inicio, fecha_fin):
    """Renderiza la vista previa de la liquidación"""
    st.markdown("---")
    st.markdown(f"### 📊 Pre-liquidación: {fecha_inicio.strftime('%d/%m/%Y')} - {fecha_fin.strftime('%d/%m/%Y')}")
    
    # Obtener datos
    turnos = get_turnos_pendientes_pago(fecha_inicio, fecha_fin)
    descuentos = get_descuentos_pendientes_pago(fecha_inicio, fecha_fin)
    horas_extra = get_horas_extra_pendientes_pago(fecha_inicio, fecha_fin)
    config_descuento = get_configuracion_nomina('descuento_comida_porcentaje')
    porcentaje_descuento_comida = config_descuento['valor_config'] if config_descuento else 10
    
    if not turnos:
        st.warning("⚠️ No hay turnos pendientes de pago en este período")
        return
    
    # Agrupar por empleado
    empleados_data = {}
    
    for turno in turnos:
        id_emp = turno['id_empleado']
        if id_emp not in empleados_data:
            empleados_data[id_emp] = {
                'id_empleado': id_emp,
                'nombre_empleado': turno['nombre_empleado'],
                'cedula_empleado': turno['cedula_empleado'],
                'nombre_sede': turno['nombre_sede'],
                'salario_dia': turno['salario_dia'],
                'turnos': [],
                'turnos_ids': [],
                'dias_trabajados': 0,
                'horas_trabajadas': 0,
                'horas_extra': 0,
                'horas_extra_ids': [],
                'descuentos': [],
                'descuentos_ids': [],
                'descuento_comida_bruto': 0,
                'otros_descuentos': 0
            }
        
        empleados_data[id_emp]['turnos'].append(turno)
        empleados_data[id_emp]['turnos_ids'].append(turno['id_turno'])
        empleados_data[id_emp]['dias_trabajados'] += 1
        empleados_data[id_emp]['horas_trabajadas'] += turno['total_horas']
    
    # Agregar horas extra
    for he in horas_extra:
        id_emp = he['id_empleado']
        if id_emp in empleados_data:
            empleados_data[id_emp]['horas_extra'] += he['total_horas_extra']
            empleados_data[id_emp]['horas_extra_ids'].append(he['id'])
    
    # Agregar descuentos
    for desc in descuentos:
        id_emp = desc['id_empleado']
        if id_emp in empleados_data:
            empleados_data[id_emp]['descuentos'].append(desc)
            empleados_data[id_emp]['descuentos_ids'].append(desc['id_descuento'])
            
            if desc['tipo_descuento'] == 'Consumo Alimento':
                empleados_data[id_emp]['descuento_comida_bruto'] += desc['valor']
            else:
                empleados_data[id_emp]['otros_descuentos'] += desc['valor']
    
    # ==================== SELECTOR DE EMPLEADOS ====================
    st.markdown("#### 👥 Seleccionar Empleados a Liquidar")
    
    # Crear opciones para el multiselect
    opciones_empleados = []
    for id_emp, data in empleados_data.items():
        # Calcular valor neto estimado para mostrar
        salario_base = data['dias_trabajados'] * data['salario_dia']
        valor_hora = data['salario_dia'] / 8
        valor_horas_extra = data['horas_extra'] * valor_hora * VALOR_HORA_EXTRA_MULTIPLICADOR
        subtotal_bruto = salario_base + valor_horas_extra
        descuento_comida_neto = data['descuento_comida_bruto'] * (1 - porcentaje_descuento_comida / 100)
        total_descuentos = descuento_comida_neto + data['otros_descuentos']
        total_neto = subtotal_bruto - total_descuentos
        
        opciones_empleados.append({
            'id': id_emp,
            'label': f"{data['nombre_empleado']} ({data['nombre_sede']}) - {data['dias_trabajados']} días - {formato_moneda(total_neto)}",
            'nombre': data['nombre_empleado']
        })
    
    # Ordenar por nombre
    opciones_empleados.sort(key=lambda x: x['nombre'])
    
    # Inicializar empleados seleccionados en session_state
    if 'empleados_seleccionados_ids' not in st.session_state:
        st.session_state['empleados_seleccionados_ids'] = [e['id'] for e in opciones_empleados]
    
    # Botones para seleccionar/deseleccionar todos
    col_sel1, col_sel2, col_sel3 = st.columns([1, 1, 2])
    
    with col_sel1:
        if st.button("✅ Seleccionar Todos", use_container_width=True):
            st.session_state['empleados_seleccionados_ids'] = [e['id'] for e in opciones_empleados]
            st.rerun()
    
    with col_sel2:
        if st.button("❌ Deseleccionar Todos", use_container_width=True):
            st.session_state['empleados_seleccionados_ids'] = []
            st.rerun()
    
    with col_sel3:
        st.info(f"📊 {len(st.session_state['empleados_seleccionados_ids'])} de {len(opciones_empleados)} empleados seleccionados")
    
    # Multiselect de empleados
    labels_seleccionados = [e['label'] for e in opciones_empleados if e['id'] in st.session_state['empleados_seleccionados_ids']]
    
    empleados_seleccionados_labels = st.multiselect(
        "Empleados a incluir en la liquidación",
        options=[e['label'] for e in opciones_empleados],
        default=labels_seleccionados,
        help="Selecciona los empleados que deseas incluir en esta liquidación"
    )
    
    # Actualizar IDs seleccionados basado en labels
    st.session_state['empleados_seleccionados_ids'] = [
        e['id'] for e in opciones_empleados if e['label'] in empleados_seleccionados_labels
    ]
    
    if not st.session_state['empleados_seleccionados_ids']:
        st.warning("⚠️ Debes seleccionar al menos un empleado para crear la liquidación")
        return
    
    # Filtrar empleados_data solo con los seleccionados
    empleados_data_filtrado = {
        id_emp: data for id_emp, data in empleados_data.items() 
        if id_emp in st.session_state['empleados_seleccionados_ids']
    }
    
    st.markdown("---")
    
    # Calcular valores para cada empleado SELECCIONADO
    detalles_liquidacion = []
    total_bruto_general = 0
    total_descuentos_general = 0
    total_neto_general = 0
    
    # Inicializar ajustes manuales en session_state si no existen
    if 'ajustes_manuales' not in st.session_state:
        st.session_state['ajustes_manuales'] = {}
    
    for id_emp, data in empleados_data_filtrado.items():
        # Calcular salario base (días trabajados * salario día)
        salario_base = data['dias_trabajados'] * data['salario_dia']
        
        # Calcular valor horas extra (horas extra * (salario_dia/8) * multiplicador)
        valor_hora = data['salario_dia'] / 8
        valor_horas_extra = data['horas_extra'] * valor_hora * VALOR_HORA_EXTRA_MULTIPLICADOR
        
        # Subtotal bruto
        subtotal_bruto = salario_base + valor_horas_extra
        
        # Descuento de comida con porcentaje aplicado
        descuento_comida_neto = data['descuento_comida_bruto'] * (1 - porcentaje_descuento_comida / 100)
        
        # Total descuentos
        total_descuentos = descuento_comida_neto + data['otros_descuentos']
        
        # Ajuste manual (si existe)
        ajuste_manual = st.session_state['ajustes_manuales'].get(id_emp, 0)
        
        # Total neto
        total_neto = subtotal_bruto - total_descuentos + ajuste_manual
        
        detalle = {
            'id_empleado': id_emp,
            'nombre_empleado': data['nombre_empleado'],
            'cedula_empleado': data['cedula_empleado'],
            'nombre_sede': data['nombre_sede'],
            'dias_trabajados': data['dias_trabajados'],
            'horas_trabajadas': data['horas_trabajadas'],
            'horas_extra': data['horas_extra'],
            'salario_base': salario_base,
            'valor_horas_extra': valor_horas_extra,
            'subtotal_bruto': subtotal_bruto,
            'descuento_comida_bruto': data['descuento_comida_bruto'],
            'porcentaje_descuento_comida': porcentaje_descuento_comida,
            'descuento_comida_neto': descuento_comida_neto,
            'otros_descuentos': data['otros_descuentos'],
            'total_descuentos': total_descuentos,
            'total_neto': total_neto,
            'ajuste_manual': ajuste_manual,
            'turnos_ids': data['turnos_ids'],
            'descuentos_ids': data['descuentos_ids'],
            'horas_extra_ids': data['horas_extra_ids'],
            'observaciones': ''
        }
        
        detalles_liquidacion.append(detalle)
        total_bruto_general += subtotal_bruto
        total_descuentos_general += total_descuentos
        total_neto_general += total_neto
    
    # Métricas generales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">👥 Empleados</div>
            <div class="metric-value">{len(empleados_data_filtrado)}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card success">
            <div class="metric-label">💵 Total Bruto</div>
            <div class="metric-value">{formato_moneda(total_bruto_general)}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card danger">
            <div class="metric-label">📉 Descuentos</div>
            <div class="metric-value">{formato_moneda(total_descuentos_general)}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card warning">
            <div class="metric-label">💰 Total a Pagar</div>
            <div class="metric-value">{formato_moneda(total_neto_general)}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Info del descuento de comida
    st.info(f"🍽️ **Descuento en Alimentos:** {porcentaje_descuento_comida}% (Los empleados pagan el {100 - porcentaje_descuento_comida}% de sus consumos de comida)")
    
    # Detalle por empleado
    st.markdown("### 👥 Detalle por Empleado")
    
    for detalle in detalles_liquidacion:
        with st.expander(f"👤 {detalle['nombre_empleado']} - {detalle['nombre_sede']} | Neto: {formato_moneda(detalle['total_neto'])}", expanded=False):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"""
                **📋 Información del Empleado**
                - **Cédula:** {detalle['cedula_empleado']}
                - **Sede:** {detalle['nombre_sede']}
                - **Días trabajados:** {detalle['dias_trabajados']}
                - **Horas trabajadas:** {detalle['horas_trabajadas']:.2f}
                - **Horas extra:** {detalle['horas_extra']:.2f}
                """)
                
                st.markdown("---")
                
                st.markdown(f"""
                **💵 Ingresos**
                - Salario base ({detalle['dias_trabajados']} días): **{formato_moneda(detalle['salario_base'])}**
                - Valor horas extra ({detalle['horas_extra']:.2f} hrs): **{formato_moneda(detalle['valor_horas_extra'])}**
                - **Subtotal bruto:** **{formato_moneda(detalle['subtotal_bruto'])}**
                """)
                
                st.markdown("---")
                
                st.markdown(f"""
                **📉 Descuentos**
                - Consumo alimentos (bruto): {formato_moneda(detalle['descuento_comida_bruto'])}
                - Descuento empresa ({detalle['porcentaje_descuento_comida']}%): -{formato_moneda(detalle['descuento_comida_bruto'] * detalle['porcentaje_descuento_comida'] / 100)}
                - **Descuento comida (neto):** **{formato_moneda(detalle['descuento_comida_neto'])}**
                - Otros descuentos: **{formato_moneda(detalle['otros_descuentos'])}**
                - **Total descuentos:** **{formato_moneda(detalle['total_descuentos'])}**
                """)
            
            with col2:
                st.markdown("**🔧 Ajuste Manual**")
                ajuste = st.number_input(
                    "Ajuste (+/-)",
                    value=float(st.session_state['ajustes_manuales'].get(detalle['id_empleado'], 0)),
                    step=1000.0,
                    key=f"ajuste_{detalle['id_empleado']}",
                    help="Valor positivo suma, negativo resta al total"
                )
                
                if ajuste != st.session_state['ajustes_manuales'].get(detalle['id_empleado'], 0):
                    st.session_state['ajustes_manuales'][detalle['id_empleado']] = ajuste
                    st.rerun()
                
                st.markdown("---")
                
                st.markdown(f"""
                <div class="metric-card {'warning' if detalle['ajuste_manual'] != 0 else 'success'}">
                    <div class="metric-label">💰 Total a Pagar</div>
                    <div class="metric-value">{formato_moneda(detalle['total_neto'])}</div>
                </div>
                """, unsafe_allow_html=True)
                
                if detalle['ajuste_manual'] != 0:
                    st.caption(f"Incluye ajuste de {formato_moneda(detalle['ajuste_manual'])}")
    
    st.markdown("---")
    
    # Observaciones generales
    observaciones = st.text_area(
        "📝 Observaciones de la Liquidación",
        placeholder="Notas o comentarios sobre esta liquidación...",
        help="Estas observaciones quedarán registradas en la liquidación"
    )
    
    # Botón para crear liquidación
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("❌ Cancelar", use_container_width=True):
            st.session_state['liquidacion_cargada'] = False
            st.session_state['ajustes_manuales'] = {}
            st.session_state['empleados_seleccionados_ids'] = []
            st.rerun()
    
    with col2:
        if st.button("✅ Crear Liquidación", type="primary", use_container_width=True):
            # Actualizar ajustes manuales en los detalles
            for detalle in detalles_liquidacion:
                detalle['ajuste_manual'] = st.session_state['ajustes_manuales'].get(detalle['id_empleado'], 0)
                # Recalcular total neto con ajuste
                detalle['total_neto'] = detalle['subtotal_bruto'] - detalle['total_descuentos'] + detalle['ajuste_manual']
            
            id_liquidacion, error = crear_liquidacion(
                fecha_inicio,
                fecha_fin,
                detalles_liquidacion,
                observaciones
            )
            
            if error:
                st.error(f"❌ Error al crear la liquidación: {error}")
            else:
                st.success(f"✅ Liquidación #{id_liquidacion} creada exitosamente")
                st.session_state['liquidacion_cargada'] = False
                st.session_state['ajustes_manuales'] = {}
                st.session_state['empleados_seleccionados_ids'] = []
                st.rerun()


def render_historial_liquidaciones():
    """Renderiza el historial de liquidaciones"""
    st.markdown("#### 📋 Historial de Liquidaciones")
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    
    with col1:
        estado_filtro = st.selectbox(
            "Estado",
            options=["Todos", "pendiente", "pagado", "anulado"],
            index=0
        )
    
    with col2:
        fecha_desde = st.date_input(
            "Desde",
            value=datetime.now().date() - timedelta(days=30)
        )
    
    with col3:
        fecha_hasta = st.date_input(
            "Hasta",
            value=datetime.now().date()
        )
    
    # Obtener liquidaciones
    estado = estado_filtro if estado_filtro != "Todos" else None
    liquidaciones = get_liquidaciones(estado, fecha_desde, fecha_hasta)
    
    if not liquidaciones:
        st.info("📭 No hay liquidaciones en el período seleccionado")
        return
    
    # Mostrar liquidaciones
    for liq in liquidaciones:
        estado_class = f"estado-{liq['estado']}"
        estado_emoji = "⏳" if liq['estado'] == 'pendiente' else ("✅" if liq['estado'] == 'pagado' else "❌")
        
        with st.expander(
            f"{estado_emoji} Liquidación #{liq['id_liquidacion']} | {liq['fecha_liquidacion'].strftime('%d/%m/%Y')} | {formato_moneda(liq['total_neto'])} | {liq['num_empleados']} empleados",
            expanded=False
        ):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"""
                **📅 Período:** {liq['fecha_inicio'].strftime('%d/%m/%Y')} - {liq['fecha_fin'].strftime('%d/%m/%Y')}  
                **📊 Estado:** <span class="estado-badge {estado_class}">{liq['estado'].upper()}</span>
                """, unsafe_allow_html=True)
            
            with col2:
                st.metric("Total Bruto", formato_moneda(liq['total_bruto']))
            
            with col3:
                st.metric("Total Neto", formato_moneda(liq['total_neto']), delta=f"-{formato_moneda(liq['total_descuentos'])}")
            
            if liq['observaciones']:
                st.info(f"📝 {liq['observaciones']}")
            
            # Detalle por empleado
            st.markdown("##### 👥 Detalle por Empleado")
            detalles = get_detalle_liquidacion(liq['id_liquidacion'])
            
            if detalles:
                df_detalles = pd.DataFrame(detalles)
                df_display = df_detalles[[
                    'nombre_empleado', 'dias_trabajados', 'horas_trabajadas', 
                    'salario_base', 'valor_horas_extra', 'subtotal_bruto',
                    'descuento_comida_neto', 'otros_descuentos', 'total_descuentos',
                    'ajuste_manual', 'total_neto'
                ]].copy()
                
                df_display.columns = [
                    'Empleado', 'Días', 'Horas', 'Salario Base', 'Hrs Extra $',
                    'Bruto', 'Desc. Comida', 'Otros Desc.', 'Total Desc.',
                    'Ajuste', 'Neto'
                ]
                
                # Formatear columnas de dinero
                for col in ['Salario Base', 'Hrs Extra $', 'Bruto', 'Desc. Comida', 'Otros Desc.', 'Total Desc.', 'Ajuste', 'Neto']:
                    df_display[col] = df_display[col].apply(lambda x: formato_moneda(x))
                
                st.dataframe(df_display, use_container_width=True, hide_index=True)
            
            # Acciones
            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if liq['estado'] == 'pendiente':
                    if st.button("✅ Marcar como Pagado", key=f"pagar_{liq['id_liquidacion']}", use_container_width=True):
                        success, error = actualizar_estado_liquidacion(liq['id_liquidacion'], 'pagado')
                        if success:
                            st.success("Liquidación marcada como pagada")
                            st.rerun()
                        else:
                            st.error(f"Error: {error}")
            
            with col2:
                if liq['estado'] != 'anulado':
                    if st.button("🗑️ Anular Liquidación", key=f"anular_{liq['id_liquidacion']}", use_container_width=True):
                        success, error = anular_liquidacion(liq['id_liquidacion'])
                        if success:
                            st.warning("Liquidación anulada. Los turnos y descuentos han sido liberados.")
                            st.rerun()
                        else:
                            st.error(f"Error: {error}")
            
            with col3:
                # Exportar a CSV
                if detalles:
                    csv = pd.DataFrame(detalles).to_csv(index=False)
                    st.download_button(
                        "📥 Exportar CSV",
                        data=csv,
                        file_name=f"liquidacion_{liq['id_liquidacion']}_{liq['fecha_liquidacion'].strftime('%Y%m%d')}.csv",
                        mime="text/csv",
                        key=f"csv_{liq['id_liquidacion']}",
                        use_container_width=True
                    )


def render_editar_eliminar():
    """Renderiza la vista para editar y eliminar liquidaciones"""
    st.markdown("#### ✏️ Editar / Eliminar Liquidaciones")
    st.caption("Modifica los ajustes manuales de los empleados o elimina liquidaciones")
    
    # Obtener todas las liquidaciones no anuladas
    liquidaciones = get_liquidaciones()
    liquidaciones_editables = [l for l in liquidaciones if l['estado'] != 'anulado']
    
    if not liquidaciones_editables:
        st.info("📭 No hay liquidaciones disponibles para editar o eliminar")
        return
    
    # Selector de liquidación
    opciones_liq = {
        f"#{l['id_liquidacion']} | {l['fecha_liquidacion'].strftime('%d/%m/%Y')} | {l['estado'].upper()} | {formato_moneda(l['total_neto'])}": l['id_liquidacion']
        for l in liquidaciones_editables
    }
    
    liq_seleccionada = st.selectbox(
        "Selecciona una liquidación",
        options=list(opciones_liq.keys()),
        help="Selecciona la liquidación que deseas editar o eliminar"
    )
    
    if not liq_seleccionada:
        return
    
    id_liquidacion = opciones_liq[liq_seleccionada]
    
    # Obtener datos de la liquidación
    liq_data = next((l for l in liquidaciones_editables if l['id_liquidacion'] == id_liquidacion), None)
    detalles = get_detalle_liquidacion(id_liquidacion)
    
    if not liq_data:
        st.error("Error al cargar la liquidación")
        return
    
    st.markdown("---")
    
    # Información de la liquidación
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        estado_class = f"estado-{liq_data['estado']}"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">📊 Estado</div>
            <div class="metric-value"><span class="estado-badge {estado_class}">{liq_data['estado'].upper()}</span></div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card success">
            <div class="metric-label">💵 Total Bruto</div>
            <div class="metric-value">{formato_moneda(liq_data['total_bruto'])}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card danger">
            <div class="metric-label">📉 Descuentos</div>
            <div class="metric-value">{formato_moneda(liq_data['total_descuentos'])}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card warning">
            <div class="metric-label">💰 Total Neto</div>
            <div class="metric-value">{formato_moneda(liq_data['total_neto'])}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown(f"**📅 Período:** {liq_data['fecha_inicio'].strftime('%d/%m/%Y')} - {liq_data['fecha_fin'].strftime('%d/%m/%Y')}")
    
    st.markdown("---")
    
    # Tabs para editar y eliminar
    edit_tab, delete_tab = st.tabs(["✏️ Editar Detalles", "🗑️ Eliminar Liquidación"])
    
    with edit_tab:
        render_editar_detalles(id_liquidacion, detalles, liq_data)
    
    with delete_tab:
        render_eliminar_liquidacion(id_liquidacion, liq_data)


def render_editar_detalles(id_liquidacion, detalles, liq_data):
    """Renderiza la edición de detalles de una liquidación"""
    st.markdown("##### ✏️ Editar Ajustes por Empleado")
    
    if liq_data['estado'] == 'pagado':
        st.warning("⚠️ Esta liquidación ya está marcada como PAGADA. Los cambios afectarán el registro histórico.")
    
    if not detalles:
        st.info("No hay detalles para editar")
        return
    
    # Mostrar cada empleado con opción de editar
    for detalle in detalles:
        with st.expander(f"👤 {detalle['nombre_empleado']} | Neto actual: {formato_moneda(detalle['total_neto'])}", expanded=False):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"""
                **Información Actual:**
                - Subtotal Bruto: {formato_moneda(detalle['subtotal_bruto'])}
                - Total Descuentos: {formato_moneda(detalle['total_descuentos'])}
                - Ajuste Manual Actual: {formato_moneda(detalle['ajuste_manual'])}
                - **Total Neto:** {formato_moneda(detalle['total_neto'])}
                """)
                
                observaciones_actuales = detalle.get('observaciones', '') or ''
                st.text_area(
                    "Observaciones actuales",
                    value=observaciones_actuales,
                    disabled=True,
                    key=f"obs_actual_{detalle['id_detalle']}",
                    height=60
                )
            
            with col2:
                st.markdown("**Modificar:**")
                
                nuevo_ajuste = st.number_input(
                    "Nuevo Ajuste (+/-)",
                    value=float(detalle['ajuste_manual']),
                    step=1000.0,
                    key=f"edit_ajuste_{detalle['id_detalle']}",
                    help="Valor positivo suma, negativo resta al total"
                )
                
                nuevas_obs = st.text_area(
                    "Nuevas Observaciones",
                    value=observaciones_actuales,
                    key=f"edit_obs_{detalle['id_detalle']}",
                    height=60,
                    placeholder="Motivo del ajuste..."
                )
                
                # Calcular nuevo total
                nuevo_total = detalle['subtotal_bruto'] - detalle['total_descuentos'] + nuevo_ajuste
                diferencia = nuevo_total - detalle['total_neto']
                
                if diferencia != 0:
                    st.metric(
                        "Nuevo Total",
                        formato_moneda(nuevo_total),
                        delta=formato_moneda(diferencia)
                    )
                    
                    if st.button("💾 Guardar Cambios", key=f"save_{detalle['id_detalle']}", type="primary", use_container_width=True):
                        success, error = actualizar_detalle_liquidacion(
                            detalle['id_detalle'],
                            nuevo_ajuste,
                            nuevas_obs
                        )
                        if success:
                            st.success("✅ Cambios guardados correctamente")
                            st.rerun()
                        else:
                            st.error(f"❌ Error: {error}")


def render_eliminar_liquidacion(id_liquidacion, liq_data):
    """Renderiza la opción de eliminar una liquidación"""
    st.markdown("##### 🗑️ Eliminar Liquidación Permanentemente")
    
    st.error("""
    ⚠️ **ADVERTENCIA:** Esta acción es IRREVERSIBLE.
    
    Al eliminar la liquidación:
    - Se borrarán todos los registros de esta liquidación
    - Los turnos y descuentos quedarán LIBERADOS para futuras liquidaciones
    - No se podrá recuperar la información
    """)
    
    st.markdown(f"""
    **Liquidación a eliminar:**
    - **ID:** #{id_liquidacion}
    - **Fecha:** {liq_data['fecha_liquidacion'].strftime('%d/%m/%Y')}
    - **Período:** {liq_data['fecha_inicio'].strftime('%d/%m/%Y')} - {liq_data['fecha_fin'].strftime('%d/%m/%Y')}
    - **Total Neto:** {formato_moneda(liq_data['total_neto'])}
    - **Empleados:** {liq_data['num_empleados']}
    - **Estado:** {liq_data['estado'].upper()}
    """)
    
    st.markdown("---")
    
    # Confirmación con texto
    st.markdown("Para confirmar, escribe **ELIMINAR** en el campo de abajo:")
    confirmacion = st.text_input(
        "Confirmación",
        placeholder="Escribe ELIMINAR para confirmar",
        key=f"confirm_delete_{id_liquidacion}"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("❌ Cancelar", use_container_width=True):
            st.rerun()
    
    with col2:
        eliminar_disabled = confirmacion != "ELIMINAR"
        if st.button(
            "🗑️ Eliminar Permanentemente",
            type="primary",
            use_container_width=True,
            disabled=eliminar_disabled
        ):
            if confirmacion == "ELIMINAR":
                success, error = eliminar_liquidacion(id_liquidacion)
                if success:
                    st.success("✅ Liquidación eliminada permanentemente. Los turnos y descuentos han sido liberados.")
                    st.rerun()
                else:
                    st.error(f"❌ Error al eliminar: {error}")
            else:
                st.warning("⚠️ Debes escribir ELIMINAR para confirmar")
