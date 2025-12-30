"""
Módulo de base de datos - Conexión y operaciones
"""
from data_base.connection import get_connection
from data_base.controler import (
    # Clientes
    insert_cliente,
    # Negocios
    insert_negocio,
    # Remisiones
    get_last_remission_number,
    insert_remision,
    get_all_remisiones_open,
    get_all_remisiones_open_with_value,
    update_remision_estado,
    update_remision_valor,
    reset_all_remisiones_to_closed,
    upsert_remision,
    # Facturas
    get_last_invoice_number,
    insert_factura,
    get_all_facturas_open,
    get_all_facturas_open_with_value,
    update_factura_estado,
    update_factura_valor,
    reset_all_facturas_to_closed,
    upsert_factura,
    # Empleados
    insert_empleado,
    check_cedula_exists,
    get_all_empleados,
)

__all__ = [
    'get_connection',
    'insert_cliente',
    'insert_negocio',
    'get_last_remission_number',
    'insert_remision',
    'get_all_remisiones_open',
    'get_all_remisiones_open_with_value',
    'update_remision_estado',
    'update_remision_valor',
    'reset_all_remisiones_to_closed',
    'upsert_remision',
    'get_last_invoice_number',
    'insert_factura',
    'get_all_facturas_open',
    'get_all_facturas_open_with_value',
    'update_factura_estado',
    'update_factura_valor',
    'reset_all_facturas_to_closed',
    'upsert_factura',
    'insert_empleado',
    'check_cedula_exists',
    'get_all_empleados',
]
