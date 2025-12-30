"""
Módulo de Empleados - Registro de empleados
"""
import streamlit as st
import time
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.settings import TIPOS_DOCUMENTO
from data_base.controler import insert_empleado, check_cedula_exists
from src.utils.ui_helpers import CSS_STYLES


def render():
    """Renderiza el formulario de registro de empleados"""
    st.markdown(CSS_STYLES, unsafe_allow_html=True)
    
    st.title("👤 Registro de Empleado")
    st.markdown("---")

    # Inicializar estado del formulario
    if 'registro_exitoso' not in st.session_state:
        st.session_state.registro_exitoso = False
    if 'mensaje_registro' not in st.session_state:
        st.session_state.mensaje_registro = ""
    if 'tiempo_mensaje' not in st.session_state:
        st.session_state.tiempo_mensaje = 0

    # Placeholder para el mensaje de éxito
    mensaje_placeholder = st.empty()

    # Mostrar mensaje si existe y no han pasado 10 segundos
    if st.session_state.registro_exitoso and st.session_state.tiempo_mensaje > 0:
        tiempo_restante = 10 - (time.time() - st.session_state.tiempo_mensaje)
        if tiempo_restante > 0:
            mensaje_placeholder.success(st.session_state.mensaje_registro)
        else:
            st.session_state.registro_exitoso = False
            st.session_state.mensaje_registro = ""
            st.session_state.tiempo_mensaje = 0

    # Formulario de registro
    with st.form(key="form_registro_empleado", clear_on_submit=True):
        st.subheader("📋 Información del Empleado")
        
        col1, col2 = st.columns(2)
        
        with col1:
            nombre = st.text_input(
                "Nombre Completo *",
                placeholder="Ingrese el nombre completo",
                help="Nombre completo del empleado"
            )
        
        with col2:
            tipo_documento = st.selectbox(
                "Tipo de Documento *",
                options=TIPOS_DOCUMENTO,
                help="Seleccione el tipo de documento de identidad"
            )
        
        col3, col4 = st.columns(2)
        
        with col3:
            numero_documento = st.text_input(
                "Número de Documento *",
                placeholder="Ingrese el número de documento",
                help="Número de identificación del empleado"
            )
        
        with col4:
            salario_dia = st.number_input(
                "Salario por Día *",
                min_value=0,
                step=1000,
                format="%d",
                help="Salario diario del empleado en pesos"
            )
        
        st.markdown("---")
        
        # Botón de registro
        submit_button = st.form_submit_button(
            label="📝 Registrar Empleado",
            use_container_width=True,
            type="primary"
        )
        
        if submit_button:
            # Validaciones
            errores = []
            
            if not nombre or nombre.strip() == "":
                errores.append("El nombre es obligatorio")
            
            if not numero_documento or numero_documento.strip() == "":
                errores.append("El número de documento es obligatorio")
            
            if salario_dia <= 0:
                errores.append("El salario debe ser mayor a 0")
            
            # Verificar si la cédula ya existe
            if numero_documento and check_cedula_exists(numero_documento.strip()):
                errores.append("Ya existe un empleado con ese número de documento")
            
            if errores:
                for error in errores:
                    st.error(f"❌ {error}")
            else:
                # Insertar empleado
                id_empleado, error = insert_empleado(
                    nombre_empleado=nombre.strip(),
                    tipo_documento=tipo_documento,
                    cedula_empleado=numero_documento.strip(),
                    salario_dia=int(salario_dia)
                )
                
                if error:
                    st.error(f"❌ Error al registrar: {error}")
                else:
                    st.session_state.registro_exitoso = True
                    st.session_state.mensaje_registro = f"✅ Empleado '{nombre.strip()}' registrado exitosamente con ID: {id_empleado}"
                    st.session_state.tiempo_mensaje = time.time()
                    st.rerun()

    # Información adicional
    st.markdown("---")
    st.caption("* Campos obligatorios")
    st.caption("Los datos se guardarán en la base de datos automáticamente al presionar 'Registrar Empleado'")
