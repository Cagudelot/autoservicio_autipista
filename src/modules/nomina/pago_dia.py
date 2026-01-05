"""
Módulo de Nómina - Pago por Día
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO
import base64
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from data_base.controler import (
    get_empleados_turno_cerrado_hoy,
    get_consumos_hoy_empleado,
    get_consumos_cuenta_empleado,
    get_configuracion_nomina,
    agregar_consumo_cuenta,
    crear_pago_diario,
    get_pagos_diarios,
    eliminar_pago_diario,
    actualizar_pago_diario,
    get_pago_diario_detalle
)
from src.utils.ui_helpers import CSS_STYLES

# Importar canvas para firma
try:
    from streamlit_drawable_canvas import st_canvas
    CANVAS_DISPONIBLE = True
except ImportError:
    CANVAS_DISPONIBLE = False


# ==================== CONSTANTES ====================
VALOR_HORA_EXTRA_MULTIPLICADOR = 1.25


# ==================== ESTILOS ====================
PAGO_DIA_STYLES = """
<style>
    .pago-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border-radius: 15px;
        padding: 25px;
        margin: 15px 0;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    .empleado-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        padding: 20px;
        color: white;
        margin-bottom: 20px;
    }
    
    .empleado-nombre-grande {
        font-size: 1.5em;
        font-weight: 700;
        margin-bottom: 5px;
    }
    
    .empleado-info {
        opacity: 0.9;
        font-size: 0.95em;
    }
    
    .metric-pago {
        background: rgba(255,255,255,0.05);
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        margin: 5px;
    }
    
    .metric-pago.bruto {
        border-left: 4px solid #38ef7d;
    }
    
    .metric-pago.descuento {
        border-left: 4px solid #f45c43;
    }
    
    .metric-pago.neto {
        border-left: 4px solid #667eea;
        background: rgba(102, 126, 234, 0.1);
    }
    
    .metric-valor {
        font-size: 1.4em;
        font-weight: 700;
    }
    
    .metric-label {
        font-size: 0.85em;
        opacity: 0.8;
    }
    
    .consumo-item {
        background: rgba(255,255,255,0.03);
        border-radius: 8px;
        padding: 12px;
        margin: 8px 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-left: 3px solid #f2994a;
    }
    
    .consumo-cuenta {
        border-left-color: #eb3349;
    }
    
    .firma-container {
        background: white;
        border-radius: 10px;
        padding: 10px;
        margin: 15px 0;
    }
    
    .firma-label {
        text-align: center;
        color: #666;
        font-size: 0.9em;
        margin-top: 5px;
    }
    
    .total-pagar {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        border-radius: 15px;
        padding: 25px;
        text-align: center;
        color: white;
        margin: 20px 0;
    }
    
    .total-pagar-valor {
        font-size: 2.5em;
        font-weight: 700;
    }
    
    .total-pagar-label {
        font-size: 1em;
        opacity: 0.9;
    }
</style>
"""


def formato_moneda(valor):
    """Formatea un valor como moneda colombiana"""
    try:
        return f"${valor:,.0f}".replace(",", ".")
    except:
        return f"${0:,.0f}"


def formato_hora(dt):
    """Formatea datetime a hora 12h"""
    if dt:
        return dt.strftime("%I:%M %p")
    return "-"


def render():
    """Renderiza la vista principal de Pago por Día"""
    st.markdown(CSS_STYLES, unsafe_allow_html=True)
    st.markdown(PAGO_DIA_STYLES, unsafe_allow_html=True)
    
    # Verificar si es admin_negocio para limitar funcionalidades
    user = st.session_state.get('user', {})
    es_admin_negocio = user.get('rol') == 'admin_negocio'
    id_sede_filtro = user.get('id_sede') if es_admin_negocio else None
    nombre_sede = user.get('nombre_sede', 'Tu sede') if es_admin_negocio else None
    
    st.markdown("### 💵 Pago por Día")
    st.caption("Realiza pagos diarios a empleados con firma de recibido")
    
    # Mostrar sede si es admin_negocio
    if id_sede_filtro:
        st.info(f"📍 Mostrando datos de: **{nombre_sede}**")
    
    # Admin negocio solo puede realizar pagos (no ver historial ni editar/eliminar)
    if es_admin_negocio:
        # Solo mostrar tab de realizar pago
        render_realizar_pago(id_sede_filtro)
    else:
        # Tabs completos para otros usuarios
        tab1, tab2, tab3 = st.tabs(["💰 Realizar Pago", "📋 Historial de Pagos", "✏️ Editar / Eliminar"])
        
        with tab1:
            render_realizar_pago(id_sede_filtro)
        
        with tab2:
            render_historial_pagos()
        
        with tab3:
            render_editar_eliminar_pagos()


def render_realizar_pago(id_sede_filtro=None):
    """Renderiza la interfaz para realizar un pago diario"""
    
    # Obtener empleados con turno cerrado hoy (filtrado por sede si es admin_negocio)
    empleados = get_empleados_turno_cerrado_hoy(id_sede_filtro)
    
    if not empleados:
        st.info("📭 No hay empleados con turno cerrado hoy pendientes de pago")
        st.caption("Los empleados deben tener un turno registrado y cerrado (con hora de salida) para poder recibir el pago del día")
        return
    
    st.success(f"✅ {len(empleados)} empleado(s) con turno cerrado hoy")
    
    # Selector de empleado
    opciones_empleados = {
        f"{e['nombre_empleado']} ({e['nombre_sede']}) - {e['total_horas']:.1f} hrs": e
        for e in empleados
    }
    
    empleado_seleccionado_label = st.selectbox(
        "Selecciona el empleado a pagar",
        options=list(opciones_empleados.keys())
    )
    
    if not empleado_seleccionado_label:
        return
    
    empleado = opciones_empleados[empleado_seleccionado_label]
    
    st.markdown("---")
    
    # Renderizar detalle del pago
    render_detalle_pago(empleado)


def render_detalle_pago(empleado):
    """Renderiza el detalle del pago para un empleado"""
    
    # Header del empleado
    st.markdown(f"""
    <div class="empleado-header">
        <div class="empleado-nombre-grande">👤 {empleado['nombre_empleado']}</div>
        <div class="empleado-info">
            📍 {empleado['nombre_sede']} | 🪪 {empleado['cedula_empleado']} | 
            ⏰ {formato_hora(empleado['hora_inicio'])} - {formato_hora(empleado['hora_salida'])}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Obtener configuración de descuento
    config_descuento = get_configuracion_nomina('descuento_comida_porcentaje')
    porcentaje_descuento_comida = config_descuento['valor_config'] if config_descuento else 10
    
    # Obtener consumos de hoy
    consumos_hoy = get_consumos_hoy_empleado(empleado['id_empleado'])
    
    # Obtener consumos a cuenta pendientes
    consumos_cuenta = get_consumos_cuenta_empleado(empleado['id_empleado'])
    
    # Calcular valores
    salario_dia = empleado['salario_dia']
    horas_trabajadas = empleado['total_horas']
    
    # Calcular horas extra (más de 8 horas)
    horas_extra = max(0, horas_trabajadas - 8)
    valor_hora = salario_dia / 8
    valor_horas_extra = horas_extra * valor_hora * VALOR_HORA_EXTRA_MULTIPLICADOR
    
    subtotal_bruto = salario_dia + valor_horas_extra
    
    # Separar consumos de comida y otros
    consumos_comida = [c for c in consumos_hoy if c['tipo_descuento'] == 'Consumo Alimento']
    otros_consumos = [c for c in consumos_hoy if c['tipo_descuento'] != 'Consumo Alimento']
    
    total_comida_bruto = sum(c['valor'] for c in consumos_comida)
    total_otros = sum(c['valor'] for c in otros_consumos)
    total_cuenta_pendiente = sum(c['valor'] for c in consumos_cuenta)
    
    # Métricas de ingresos
    st.markdown("#### 💵 Ingresos del Día")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="metric-pago bruto">
            <div class="metric-label">Salario del Día</div>
            <div class="metric-valor">{formato_moneda(salario_dia)}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-pago bruto">
            <div class="metric-label">Horas Extra ({horas_extra:.1f} hrs)</div>
            <div class="metric-valor">{formato_moneda(valor_horas_extra)}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-pago bruto">
            <div class="metric-label">Subtotal Bruto</div>
            <div class="metric-valor">{formato_moneda(subtotal_bruto)}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ==================== CONSUMOS ====================
    st.markdown("#### 🍽️ Consumos de Hoy")
    
    # Inicializar estado para consumos
    if 'consumos_a_descontar' not in st.session_state:
        st.session_state['consumos_a_descontar'] = {}
    if 'consumos_a_cuenta_hoy' not in st.session_state:
        st.session_state['consumos_a_cuenta_hoy'] = []
    
    descuentos_ids = []
    consumos_descontar_total = 0
    consumos_cuenta_hoy_total = 0
    
    if consumos_comida or otros_consumos:
        st.info(f"🍽️ Descuento empresa en alimentos: {porcentaje_descuento_comida}%")
        
        for consumo in consumos_comida + otros_consumos:
            id_c = consumo['id_descuento']
            
            # Calcular valor con descuento si es comida
            if consumo['tipo_descuento'] == 'Consumo Alimento':
                valor_final = consumo['valor'] * (1 - porcentaje_descuento_comida / 100)
                descuento_texto = f" (con {porcentaje_descuento_comida}% desc.)"
            else:
                valor_final = consumo['valor']
                descuento_texto = ""
            
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.markdown(f"""
                <div class="consumo-item">
                    <div>
                        <strong>{consumo['tipo_descuento']}</strong>{descuento_texto}<br>
                        <small>{consumo['detalle'] or 'Sin detalle'}</small>
                    </div>
                    <div style="text-align: right;">
                        <strong>{formato_moneda(valor_final)}</strong>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                descontar = st.checkbox(
                    "Descontar",
                    value=True,
                    key=f"desc_{id_c}",
                    help="Descontar del pago de hoy"
                )
            
            with col3:
                a_cuenta = st.checkbox(
                    "A cuenta",
                    value=False,
                    key=f"cuenta_{id_c}",
                    help="Cargar a la cuenta del empleado (no descuenta hoy)"
                )
            
            # Lógica de exclusión mutua
            if descontar and not a_cuenta:
                consumos_descontar_total += valor_final
                descuentos_ids.append(id_c)
            elif a_cuenta and not descontar:
                consumos_cuenta_hoy_total += valor_final
                st.session_state['consumos_a_cuenta_hoy'].append({
                    'id_descuento': id_c,
                    'valor': valor_final,
                    'descripcion': f"{consumo['tipo_descuento']}: {consumo['detalle'] or 'Sin detalle'}"
                })
    else:
        st.caption("No hay consumos registrados hoy")
    
    st.markdown("---")
    
    # ==================== CONSUMOS A CUENTA PENDIENTES ====================
    st.markdown("#### 📋 Consumos a Cuenta Pendientes")
    
    consumos_cuenta_ids = []
    total_cuenta_descontar = 0
    
    if consumos_cuenta:
        st.warning(f"⚠️ Este empleado tiene {len(consumos_cuenta)} consumo(s) a cuenta pendiente(s)")
        
        for cc in consumos_cuenta:
            col1, col2 = st.columns([4, 1])
            
            with col1:
                st.markdown(f"""
                <div class="consumo-item consumo-cuenta">
                    <div>
                        <strong>Consumo a cuenta</strong> - {cc['fecha_registro'].strftime('%d/%m/%Y')}<br>
                        <small>{cc['descripcion'] or 'Sin descripción'}</small>
                    </div>
                    <div style="text-align: right;">
                        <strong>{formato_moneda(cc['valor'])}</strong>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                descontar_cc = st.checkbox(
                    "Descontar ahora",
                    value=False,
                    key=f"cc_{cc['id_consumo_cuenta']}",
                    help="Descontar este consumo a cuenta del pago de hoy"
                )
                
                if descontar_cc:
                    total_cuenta_descontar += cc['valor']
                    consumos_cuenta_ids.append(cc['id_consumo_cuenta'])
    else:
        st.caption("No hay consumos a cuenta pendientes")
    
    st.markdown("---")
    
    # ==================== RESUMEN Y TOTAL ====================
    total_descuentos = consumos_descontar_total + total_cuenta_descontar
    total_neto = subtotal_bruto - total_descuentos
    
    st.markdown("#### 📊 Resumen del Pago")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        **Ingresos:**
        - Salario día: {formato_moneda(salario_dia)}
        - Horas extra: {formato_moneda(valor_horas_extra)}
        - **Subtotal:** {formato_moneda(subtotal_bruto)}
        """)
    
    with col2:
        st.markdown(f"""
        **Descuentos:**
        - Consumos hoy: {formato_moneda(consumos_descontar_total)}
        - Consumos a cuenta: {formato_moneda(total_cuenta_descontar)}
        - **Total descuentos:** {formato_moneda(total_descuentos)}
        """)
    
    if consumos_cuenta_hoy_total > 0:
        st.info(f"💳 Se cargarán {formato_moneda(consumos_cuenta_hoy_total)} a la cuenta del empleado (no descontados hoy)")
    
    # Total a pagar
    st.markdown(f"""
    <div class="total-pagar">
        <div class="total-pagar-label">💰 TOTAL A PAGAR</div>
        <div class="total-pagar-valor">{formato_moneda(total_neto)}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ==================== FOTO DEL EMPLEADO ====================
    st.markdown("#### 📸 Foto del Empleado")
    st.caption("Toma una foto del empleado al momento de recibir el pago")
    
    foto_bytes = None
    col_foto_izq, col_foto_centro, col_foto_der = st.columns([1, 2, 1])
    
    with col_foto_centro:
        foto = st.camera_input("Toma la foto del empleado", key="foto_pago_dia", label_visibility="collapsed")
        
        if foto:
            foto_bytes = foto.getvalue()
            st.success("✅ Foto capturada correctamente")
    
    st.markdown("---")
    
    # ==================== FIRMA ====================
    st.markdown("#### ✍️ Firma del Empleado")
    st.caption("El empleado debe firmar en el recuadro blanco para confirmar el recibo del pago")
    
    firma_bytes = None
    
    # Importar directamente aquí para asegurar disponibilidad
    try:
        from streamlit_drawable_canvas import st_canvas
        import numpy as np
        from PIL import Image
        
        # Centrar el canvas con columnas
        col_izq, col_canvas, col_der = st.columns([1, 2, 1])
        
        with col_canvas:
            st.markdown("""
            <div style="text-align: center; margin-bottom: 10px;">
                <span style="background: #667eea; color: white; padding: 5px 15px; border-radius: 20px; font-size: 0.9em;">
                    Firme aquí ↓
                </span>
            </div>
            """, unsafe_allow_html=True)
            
            # Canvas para firma centrado
            canvas_result = st_canvas(
                fill_color="rgba(255, 255, 255, 1)",
                stroke_width=3,
                stroke_color="#000000",
                background_color="#FFFFFF",
                height=200,
                width=400,
                drawing_mode="freedraw",
                key="firma_canvas",
                display_toolbar=True,
            )
            
            st.caption("Use el borrador de la barra de herramientas para limpiar")
        
        # Convertir a bytes si hay dibujo
        if canvas_result is not None and canvas_result.image_data is not None:
            img_array = canvas_result.image_data.astype(np.uint8)
            
            # Verificar si hay algo dibujado (no solo blanco)
            if np.any(img_array[:, :, :3] != 255):
                img = Image.fromarray(img_array)
                buffer = BytesIO()
                img.save(buffer, format='PNG')
                firma_bytes = buffer.getvalue()
                st.success("✅ Firma capturada correctamente")
                
    except ImportError as e:
        st.error(f"⚠️ Error al cargar el componente de firma: {e}")
        st.info("Instala: `pip install streamlit-drawable-canvas`")
    except Exception as e:
        st.error(f"⚠️ Error con el canvas de firma: {e}")
    
    # Observaciones
    observaciones = st.text_area(
        "📝 Observaciones (opcional)",
        placeholder="Notas adicionales sobre este pago...",
        height=80
    )
    
    st.markdown("---")
    
    # Botón de pago
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("❌ Cancelar", use_container_width=True):
            st.session_state['consumos_a_cuenta_hoy'] = []
            st.rerun()
    
    with col2:
        # Validar que haya firma y foto obligatorias
        pagar_disabled = total_neto < 0 or firma_bytes is None or foto_bytes is None
        
        if firma_bytes is None:
            st.warning("⚠️ La firma del empleado es obligatoria para realizar el pago")
        if foto_bytes is None:
            st.warning("⚠️ La foto del empleado es obligatoria para realizar el pago")
        
        if st.button(
            "✅ Confirmar Pago",
            type="primary",
            use_container_width=True,
            disabled=pagar_disabled
        ):
            # Preparar datos del pago
            datos_pago = {
                'salario_dia': salario_dia,
                'horas_trabajadas': horas_trabajadas,
                'horas_extra': horas_extra,
                'valor_horas_extra': valor_horas_extra,
                'subtotal_bruto': subtotal_bruto,
                'consumos_descontados': consumos_descontar_total,
                'consumos_a_cuenta': consumos_cuenta_hoy_total,
                'otros_descuentos': total_cuenta_descontar,
                'total_descuentos': total_descuentos,
                'total_neto': total_neto,
                'observaciones': observaciones,
                'descuentos_ids': descuentos_ids,
                'consumos_cuenta_ids': consumos_cuenta_ids
            }
            
            # Crear consumos a cuenta si hay
            for cc_nuevo in st.session_state.get('consumos_a_cuenta_hoy', []):
                agregar_consumo_cuenta(
                    empleado['id_empleado'],
                    cc_nuevo['id_descuento'],
                    cc_nuevo['valor'],
                    cc_nuevo['descripcion']
                )
            
            # Crear el pago con firma y foto
            id_pago, error = crear_pago_diario(
                empleado['id_empleado'],
                empleado['id_turno'],
                datos_pago,
                firma_bytes,
                foto_bytes
            )
            
            if error:
                st.error(f"❌ Error al procesar el pago: {error}")
            else:
                st.success(f"✅ Pago #{id_pago} registrado exitosamente")
                st.session_state['consumos_a_cuenta_hoy'] = []
                st.rerun()


def render_historial_pagos():
    """Renderiza el historial de pagos diarios"""
    st.markdown("#### 📋 Historial de Pagos Diarios")
    
    # Verificar si es usuario master
    user = st.session_state.get('user') or {}
    es_master = user.get('es_master', False)
    
    # Filtros
    col1, col2 = st.columns(2)
    
    with col1:
        fecha_desde = st.date_input(
            "Desde",
            value=datetime.now().date()
        )
    
    with col2:
        fecha_hasta = st.date_input(
            "Hasta",
            value=datetime.now().date()
        )
    
    # Obtener pagos
    pagos = get_pagos_diarios(fecha_inicio=fecha_desde, fecha_fin=fecha_hasta)
    
    if not pagos:
        st.info("📭 No hay pagos en el período seleccionado")
        return
    
    # Métricas
    total_pagado = sum(p['total_neto'] for p in pagos)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Pagos", len(pagos))
    with col2:
        st.metric("Total Pagado", formato_moneda(total_pagado))
    with col3:
        con_firma = sum(1 for p in pagos if p['tiene_firma'])
        st.metric("Con Firma", f"{con_firma}/{len(pagos)}")
    
    st.markdown("---")
    
    # Lista de pagos
    for pago in pagos:
        firma_icon = "✍️" if pago['tiene_firma'] else "⚠️"
        
        with st.expander(
            f"{firma_icon} {pago['nombre_empleado']} | {pago['fecha_pago'].strftime('%d/%m/%Y')} | {formato_moneda(pago['total_neto'])}",
            expanded=False
        ):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"""
                **Empleado:** {pago['nombre_empleado']}  
                **Cédula:** {pago['cedula_empleado']}  
                **Sede:** {pago['nombre_sede']}  
                **Fecha:** {pago['fecha_pago'].strftime('%d/%m/%Y')}
                """)
            
            with col2:
                st.markdown(f"""
                **Salario Día:** {formato_moneda(pago['salario_dia'])}  
                **Horas:** {pago['horas_trabajadas']:.1f} hrs  
                **Bruto:** {formato_moneda(pago['subtotal_bruto'])}  
                **Descuentos:** {formato_moneda(pago['total_descuentos'])}  
                **Neto:** {formato_moneda(pago['total_neto'])}
                """)
            
            if pago['tiene_firma']:
                st.success("✅ Pago firmado por el empleado")
            else:
                st.warning("⚠️ Pago sin firma")
            
            if pago['observaciones']:
                st.info(f"📝 {pago['observaciones']}")
            
            # Si es master, mostrar firma y foto ampliadas
            if es_master:
                st.markdown("---")
                st.markdown("##### 👑 Vista Master - Evidencias del Pago")
                
                # Obtener detalle completo del pago con firma y foto
                pago_detalle = get_pago_diario_detalle(pago['id_pago'])
                
                if pago_detalle:
                    col_firma, col_foto = st.columns(2)
                    
                    with col_firma:
                        st.markdown("**✍️ Firma del Empleado:**")
                        if pago_detalle.get('firma_empleado'):
                            firma_b64 = base64.b64encode(bytes(pago_detalle['firma_empleado'])).decode()
                            st.markdown(f"""
                            <div style="background: white; padding: 15px; border-radius: 10px; text-align: center; border: 2px solid #667eea;">
                                <img src="data:image/png;base64,{firma_b64}" style="max-width: 100%; height: auto; max-height: 300px;">
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.warning("Sin firma registrada")
                    
                    with col_foto:
                        st.markdown("**📸 Foto del Empleado:**")
                        if pago_detalle.get('foto_pago'):
                            foto_b64 = base64.b64encode(bytes(pago_detalle['foto_pago'])).decode()
                            st.markdown(f"""
                            <div style="background: #1a1a2e; padding: 15px; border-radius: 10px; text-align: center; border: 2px solid #38ef7d;">
                                <img src="data:image/jpeg;base64,{foto_b64}" style="max-width: 100%; height: auto; max-height: 300px; border-radius: 8px;">
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.warning("Sin foto registrada")


def render_editar_eliminar_pagos():
    """Renderiza la interfaz para editar o eliminar pagos diarios"""
    st.markdown("#### ✏️ Editar / Eliminar Pagos Diarios")
    st.caption("Modifica o elimina pagos realizados")
    
    # Filtros
    col1, col2 = st.columns(2)
    
    with col1:
        fecha_desde = st.date_input(
            "Desde",
            value=datetime.now().date(),
            key="edit_fecha_desde"
        )
    
    with col2:
        fecha_hasta = st.date_input(
            "Hasta",
            value=datetime.now().date(),
            key="edit_fecha_hasta"
        )
    
    # Obtener pagos
    pagos = get_pagos_diarios(fecha_inicio=fecha_desde, fecha_fin=fecha_hasta)
    
    if not pagos:
        st.info("📭 No hay pagos en el período seleccionado")
        return
    
    st.markdown("---")
    
    # Selector de pago
    opciones_pagos = {
        f"#{p['id_pago']} - {p['nombre_empleado']} ({p['fecha_pago'].strftime('%d/%m/%Y')}) - {formato_moneda(p['total_neto'])}": p
        for p in pagos
    }
    
    pago_seleccionado_label = st.selectbox(
        "Selecciona el pago a modificar",
        options=list(opciones_pagos.keys()),
        key="select_pago_editar"
    )
    
    if not pago_seleccionado_label:
        return
    
    pago = opciones_pagos[pago_seleccionado_label]
    
    # Obtener detalle completo
    detalle = get_pago_diario_detalle(pago['id_pago'])
    
    if not detalle:
        st.error("No se pudo cargar el detalle del pago")
        return
    
    st.markdown("---")
    
    # Mostrar información del pago
    st.markdown(f"""
    <div class="empleado-header">
        <div class="empleado-nombre-grande">💰 Pago #{detalle['id_pago']}</div>
        <div class="empleado-info">
            👤 {detalle['nombre_empleado']} | 🪪 {detalle['cedula_empleado']} | 
            📍 {detalle['nombre_sede']} | 📅 {detalle['fecha_pago'].strftime('%d/%m/%Y')}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Tabs para editar o eliminar
    tab_editar, tab_eliminar = st.tabs(["✏️ Editar", "🗑️ Eliminar"])
    
    with tab_editar:
        render_editar_pago(detalle)
    
    with tab_eliminar:
        render_eliminar_pago(detalle)


def render_editar_pago(detalle):
    """Renderiza el formulario para editar un pago"""
    st.markdown("##### ✏️ Modificar Pago")
    
    # Mostrar detalles actuales (solo lectura)
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        **Detalles del Turno:**
        - Salario Día: {formato_moneda(detalle['salario_dia'])}
        - Horas Trabajadas: {detalle['horas_trabajadas']:.1f} hrs
        - Horas Extra: {detalle['horas_extra']:.1f} hrs
        - Valor Horas Extra: {formato_moneda(detalle['valor_horas_extra'])}
        """)
    
    with col2:
        st.markdown(f"""
        **Descuentos Aplicados:**
        - Consumos descontados: {formato_moneda(detalle['consumos_descontados'])}
        - Consumos a cuenta: {formato_moneda(detalle['consumos_a_cuenta'])}
        - Otros descuentos: {formato_moneda(detalle['otros_descuentos'])}
        - **Total descuentos:** {formato_moneda(detalle['total_descuentos'])}
        """)
    
    st.markdown("---")
    
    # Campos editables
    st.markdown("**Campos editables:**")
    
    nuevo_total = st.number_input(
        "Total Neto a Pagar",
        value=float(detalle['total_neto']),
        min_value=0.0,
        step=1000.0,
        format="%.0f",
        key="edit_total_neto",
        help="Modifica el total neto pagado al empleado"
    )
    
    nuevas_observaciones = st.text_area(
        "Observaciones",
        value=detalle['observaciones'] or "",
        height=80,
        key="edit_observaciones"
    )
    
    # Mostrar firma si existe
    if detalle['firma_empleado']:
        st.markdown("##### ✍️ Firma del Empleado")
        try:
            from PIL import Image
            img = Image.open(BytesIO(detalle['firma_empleado']))
            st.image(img, width=300, caption="Firma registrada")
        except Exception as e:
            st.info("✅ Este pago tiene firma registrada")
    else:
        st.warning("⚠️ Este pago no tiene firma registrada")
    
    st.markdown("---")
    
    # Botón guardar
    if st.button("💾 Guardar Cambios", type="primary", use_container_width=True, key="btn_guardar_pago"):
        datos_actualizados = {
            'total_neto': nuevo_total,
            'observaciones': nuevas_observaciones
        }
        
        success, error = actualizar_pago_diario(detalle['id_pago'], datos_actualizados)
        
        if success:
            st.success("✅ Pago actualizado correctamente")
            st.rerun()
        else:
            st.error(f"❌ Error al actualizar: {error}")


def render_eliminar_pago(detalle):
    """Renderiza la confirmación para eliminar un pago"""
    st.markdown("##### 🗑️ Eliminar Pago")
    
    st.warning(f"""
    ⚠️ **¿Estás seguro de eliminar este pago?**
    
    - **ID Pago:** #{detalle['id_pago']}
    - **Empleado:** {detalle['nombre_empleado']}
    - **Fecha:** {detalle['fecha_pago'].strftime('%d/%m/%Y')}
    - **Total Pagado:** {formato_moneda(detalle['total_neto'])}
    
    **Esta acción:**
    - Eliminará el registro del pago
    - Marcará el turno asociado como "No Pagado" (podrá volver a pagarse)
    - Revertirá los consumos a cuenta asociados a estado "Pendiente"
    """)
    
    # Confirmación con checkbox
    confirmar = st.checkbox(
        "Confirmo que deseo eliminar este pago",
        value=False,
        key=f"confirmar_eliminar_{detalle['id_pago']}"
    )
    
    # Botón eliminar
    if st.button(
        "🗑️ Eliminar Pago",
        type="primary",
        use_container_width=True,
        disabled=not confirmar,
        key="btn_eliminar_pago"
    ):
        success, error = eliminar_pago_diario(detalle['id_pago'])
        
        if success:
            st.success("✅ Pago eliminado correctamente")
            st.rerun()
        else:
            st.error(f"❌ Error al eliminar: {error}")
