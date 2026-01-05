"""
Módulo de Empleados - Gestión de Turnos Simple
"""
import streamlit as st
from datetime import datetime
import pytz
import sys
import os
import base64

# Zona horaria Colombia
TZ_COLOMBIA = pytz.timezone('America/Bogota')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from data_base.controler import (
    get_empleado_by_cedula,
    insert_turno_con_foto,
    cerrar_turno_con_foto,
    get_turno_abierto_empleado,
    get_all_sedes
)

# ==================== ESTILOS ====================
STYLES = """
<style>
    .empleado-card {
        background: rgba(79, 209, 197, 0.1);
        border: 1px solid #4fd1c5;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    
    .empleado-card-entrada {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        border: none;
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        color: white;
    }
    
    .empleado-card-salida {
        background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
        border: none;
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        color: white;
    }
    
    .empleado-nombre {
        font-size: 1.4em;
        font-weight: 700;
        margin-bottom: 8px;
    }
    
    .empleado-info {
        font-size: 0.95em;
        margin: 4px 0;
        opacity: 0.95;
    }
    
    .empleado-badge {
        display: inline-block;
        background: rgba(255,255,255,0.2);
        padding: 4px 12px;
        border-radius: 15px;
        font-size: 0.85em;
        margin: 3px 5px 3px 0;
    }
    
    .registro-exitoso {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        border-radius: 12px;
        padding: 20px;
        color: white;
        margin: 15px 0;
        display: flex;
        align-items: center;
        gap: 20px;
    }
    
    .registro-salida {
        background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
        border-radius: 12px;
        padding: 20px;
        color: white;
        margin: 15px 0;
        display: flex;
        align-items: center;
        gap: 20px;
    }
    
    .registro-foto {
        width: 100px;
        height: 100px;
        border-radius: 50%;
        object-fit: cover;
        border: 3px solid rgba(255,255,255,0.5);
    }
    
    .registro-info {
        flex: 1;
    }
    
    .registro-titulo {
        font-size: 1.3em;
        font-weight: 600;
        margin-bottom: 5px;
    }
    
    .registro-nombre {
        font-size: 1.1em;
        margin-bottom: 5px;
    }
    
    .registro-hora {
        font-size: 1.2em;
        font-weight: 500;
    }
    
    .registro-detalle {
        font-size: 0.9em;
        opacity: 0.9;
        margin-top: 5px;
    }
    
    /* Contenedor de cámara con mejor diseño */
    [data-testid="stCameraInput"] {
        max-width: 250px !important;
        margin: 0 auto !important;
        display: block !important;
    }
    
    [data-testid="stCameraInput"] > div {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%) !important;
        border-radius: 12px !important;
        padding: 8px !important;
        border: 2px solid #4fd1c5 !important;
        box-shadow: 0 4px 15px rgba(79, 209, 197, 0.2) !important;
        margin: 0 auto !important;
    }
    
    [data-testid="stCameraInput"] video,
    [data-testid="stCameraInput"] img {
        border-radius: 8px !important;
        max-width: 230px !important;
        max-height: 170px !important;
    }
    
    /* Estilizar el botón de la cámara */
    [data-testid="stCameraInput"] button {
        background: linear-gradient(135deg, #4fd1c5 0%, #38ef7d 100%) !important;
        color: #1a1a2e !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 6px 12px !important;
        margin-top: 6px !important;
        font-size: 0 !important;
    }
    
    [data-testid="stCameraInput"] button::after {
        content: "Tomar Foto" !important;
        font-size: 13px !important;
    }
    
    [data-testid="stCameraInput"] button:hover {
        background: linear-gradient(135deg, #38ef7d 0%, #4fd1c5 100%) !important;
    }
    
    /* Centrar contenido de la columna */
    [data-testid="column"] {
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
    }
    
    /* Contenedor para centrar cámara y botón */
    .camera-container {
        display: flex;
        flex-direction: row;
        align-items: center;
        justify-content: center;
        gap: 20px;
    }
</style>
"""


def render():
    """Renderiza el módulo simplificado de gestión de turnos"""
    st.markdown(STYLES, unsafe_allow_html=True)
    
    st.title("⏱️ Control de Turnos")
    st.markdown("---")
    
    # Verificar si es admin_negocio para usar su sede automáticamente
    user = st.session_state.get('user') or {}
    es_admin_negocio = user.get('rol') == 'admin_negocio' if user else False
    
    # Inicializar estados
    if 'registro_exitoso' not in st.session_state:
        st.session_state.registro_exitoso = None
    if 'sede_seleccionada_turno' not in st.session_state:
        st.session_state.sede_seleccionada_turno = None
    
    # Si hay un registro exitoso (debe ser un diccionario), mostrar solo la tarjeta de confirmación
    if st.session_state.registro_exitoso and isinstance(st.session_state.registro_exitoso, dict):
        mostrar_confirmacion(st.session_state.registro_exitoso)
        return
    elif st.session_state.registro_exitoso:
        # Si no es un diccionario pero es truthy, resetear
        st.session_state.registro_exitoso = None
    
    # ==================== SELECCIÓN DE SEDE ====================
    # Si es admin_negocio, usar su sede automáticamente
    if es_admin_negocio:
        id_sede_filtro = user.get('id_sede')
        nombre_sede_filtro = user.get('nombre_sede', 'Tu sede')
        st.info(f"📍 Registrando turnos para: **{nombre_sede_filtro}**")
    else:
        # Mostrar selector de sede
        sedes = get_all_sedes()
        if not sedes:
            st.error("No hay sedes configuradas en el sistema")
            return
        
        # Crear opciones de sede
        sedes_opciones = {s['nombre_sede']: s['id_sede'] for s in sedes}
        
        # Si no hay sede seleccionada, mostrar selector
        if not st.session_state.sede_seleccionada_turno:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        border-radius: 15px; padding: 25px; text-align: center; color: white; margin: 20px 0;">
                <div style="font-size: 3em; margin-bottom: 10px;">🏪</div>
                <div style="font-size: 1.3em; font-weight: 600; margin-bottom: 15px;">Selecciona la Sede</div>
                <div style="opacity: 0.9;">Para registrar turnos, primero selecciona la sede</div>
            </div>
            """, unsafe_allow_html=True)
            
            sede_nombre = st.selectbox(
                "📍 Sede",
                options=list(sedes_opciones.keys()),
                key="select_sede_turno",
                label_visibility="collapsed"
            )
            
            if st.button("✅ Confirmar Sede", use_container_width=True, type="primary"):
                st.session_state.sede_seleccionada_turno = {
                    'id': sedes_opciones[sede_nombre],
                    'nombre': sede_nombre
                }
                st.rerun()
            return
        
        # Ya hay sede seleccionada
        id_sede_filtro = st.session_state.sede_seleccionada_turno['id']
        nombre_sede_filtro = st.session_state.sede_seleccionada_turno['nombre']
        
        # Mostrar sede actual con opción de cambiar
        col_sede, col_cambiar = st.columns([3, 1])
        with col_sede:
            st.info(f"📍 Sede: **{nombre_sede_filtro}**")
        with col_cambiar:
            if st.button("🔄 Cambiar", key="cambiar_sede"):
                st.session_state.sede_seleccionada_turno = None
                if 'empleado_encontrado' in st.session_state:
                    del st.session_state.empleado_encontrado
                st.rerun()
    
    st.markdown("---")
    
    # ==================== BÚSQUEDA DE EMPLEADO ====================
    # Input de cédula
    col1, col2 = st.columns([3, 1])
    with col1:
        cedula = st.text_input(
            "Cédula",
            placeholder="Ingresa la cédula del empleado",
            key="cedula_turno",
            label_visibility="collapsed"
        )
    with col2:
        buscar = st.button("Buscar", use_container_width=True, type="primary")
    
    # Si hay cédula y se presionó buscar
    if cedula and buscar:
        # Buscar empleado filtrando por sede
        empleado = get_empleado_by_cedula(cedula.strip(), id_sede_filtro)
        if not empleado:
            # Verificar si existe en otra sede
            empleado_otra_sede = get_empleado_by_cedula(cedula.strip())
            if empleado_otra_sede:
                st.error(f"⚠️ El empleado **{empleado_otra_sede['nombre_empleado']}** pertenece a **{empleado_otra_sede['nombre_sede']}**, no a **{nombre_sede_filtro}**")
            else:
                st.error("❌ No se encontró ningún empleado con esa cédula")
            return
        st.session_state.empleado_encontrado = empleado
    
    # Si ya se encontró un empleado
    if 'empleado_encontrado' in st.session_state:
        empleado = st.session_state.empleado_encontrado
        
        # Verificar si tiene turno abierto para determinar el color de la tarjeta
        turno_abierto = get_turno_abierto_empleado(empleado['id_empleado'])
        
        # Tarjeta del empleado con color según tipo de acción
        if turno_abierto:
            # SALIDA - Tarjeta roja
            card_class = "empleado-card-salida"
            accion_texto = "🔴 REGISTRAR SALIDA"
        else:
            # ENTRADA - Tarjeta verde
            card_class = "empleado-card-entrada"
            accion_texto = "🟢 REGISTRAR ENTRADA"
        
        st.markdown(f"""
        <div class="{card_class}">
            <div class="empleado-nombre">👤 {empleado['nombre_empleado']}</div>
            <div class="empleado-info">📄 CC: {empleado['cedula_empleado']}</div>
            <div style="margin-top: 10px;">
                <span class="empleado-badge">🏪 {empleado['nombre_sede']}</span>
                <span class="empleado-badge">🏷️ {empleado['nombre_rol']}</span>
            </div>
            <div style="margin-top: 12px; font-size: 1.1em; font-weight: 600;">{accion_texto}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Botón cambiar empleado
        if st.button("🔄 Cambiar empleado", key="cambiar_emp"):
            del st.session_state.empleado_encontrado
            st.rerun()
        
        st.markdown("---")
        
        if turno_abierto:
            # SALIDA - Tiene turno abierto
            hora_entrada = turno_abierto['hora_inicio'].astimezone(TZ_COLOMBIA)
            st.markdown(f"**Turno iniciado:** {hora_entrada.strftime('%I:%M %p')}")
            
            # Centrar cámara y botón
            col_left, col_center, col_right = st.columns([1, 2, 1])
            with col_center:
                foto = st.camera_input("foto", key="foto_salida", label_visibility="collapsed")
                if st.button("Registrar Salida", use_container_width=True, type="primary", disabled=foto is None):
                    if foto:
                        hora_salida = datetime.now(TZ_COLOMBIA)
                        success, error = cerrar_turno_con_foto(
                            turno_abierto['id_turno'],
                            hora_salida,
                            foto.getvalue()
                        )
                        if success:
                            st.session_state.registro_exitoso = {
                                "tipo": "salida",
                                "nombre": empleado['nombre_empleado'],
                                "cedula": empleado['cedula_empleado'],
                                "sede": empleado['nombre_sede'],
                                "rol": empleado['nombre_rol'],
                                "hora": hora_salida.strftime('%I:%M %p'),
                                "hora_entrada": hora_entrada.strftime('%I:%M %p'),
                                "foto": base64.b64encode(foto.getvalue()).decode('utf-8')
                            }
                            del st.session_state.empleado_encontrado
                            st.rerun()
                        else:
                            st.error(f"Error: {error}")
        else:
            # ENTRADA - No tiene turno
            col_left, col_center, col_right = st.columns([1, 2, 1])
            with col_center:
                foto = st.camera_input("foto", key="foto_entrada", label_visibility="collapsed")
                if st.button("Registrar Entrada", use_container_width=True, type="primary", disabled=foto is None):
                    if foto:
                        hora_entrada = datetime.now(TZ_COLOMBIA)
                        id_turno, error = insert_turno_con_foto(
                            empleado['id_empleado'],
                            hora_entrada,
                            foto.getvalue()
                        )
                        if id_turno:
                            st.session_state.registro_exitoso = {
                                "tipo": "entrada",
                                "nombre": empleado['nombre_empleado'],
                                "cedula": empleado['cedula_empleado'],
                                "sede": empleado['nombre_sede'],
                                "rol": empleado['nombre_rol'],
                                "hora": hora_entrada.strftime('%I:%M %p'),
                                "foto": base64.b64encode(foto.getvalue()).decode('utf-8')
                            }
                            del st.session_state.empleado_encontrado
                            st.rerun()
                        else:
                            st.error(f"Error: {error}")


def mostrar_confirmacion(registro):
    """Muestra la tarjeta de confirmación después de registrar"""
    foto_b64 = registro['foto']
    
    # Obtener datos con valores por defecto para compatibilidad
    cedula = registro.get('cedula', '')
    sede = registro.get('sede', '')
    rol = registro.get('rol', '')
    
    # Construir línea de detalle solo si hay datos
    detalle_cedula = f'<div class="registro-detalle">📄 CC: {cedula}</div>' if cedula else ''
    detalle_sede_rol = f'<div class="registro-detalle">🏪 {sede} | 🏷️ {rol}</div>' if sede or rol else ''
    
    if registro["tipo"] == "entrada":
        st.markdown(f"""
        <div class="registro-exitoso">
            <img src="data:image/jpeg;base64,{foto_b64}" class="registro-foto" />
            <div class="registro-info">
                <div class="registro-titulo">✅ Entrada Registrada</div>
                <div class="registro-nombre">{registro['nombre']}</div>
                {detalle_cedula}
                {detalle_sede_rol}
                <div class="registro-hora">🕐 {registro['hora']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="registro-salida">
            <img src="data:image/jpeg;base64,{foto_b64}" class="registro-foto" />
            <div class="registro-info">
                <div class="registro-titulo">✅ Salida Registrada</div>
                <div class="registro-nombre">{registro['nombre']}</div>
                {detalle_cedula}
                {detalle_sede_rol}
                <div class="registro-hora">🕐 {registro['hora_entrada']} → {registro['hora']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Botón para nuevo registro
    if st.button("➕ Nuevo registro", use_container_width=True, type="primary"):
        st.session_state.registro_exitoso = None
        st.rerun()

