"""
Controlador de operaciones de base de datos
"""
import psycopg2
from psycopg2 import sql
from data_base.connection import get_connection


def get_last_remission_number():
    """Obtiene el número de la última remisión guardada"""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT MAX(numero_remision) FROM remisiones")
    result = cur.fetchone()[0]
    
    cur.close()
    conn.close()
    
    return result or 0


def insert_cliente(nit, nombre):
    """Inserta un cliente si no existe y retorna su id"""
    conn = get_connection()
    cur = conn.cursor()
    
    # Verificar si el cliente ya existe
    cur.execute("SELECT id_cliente FROM clientes WHERE nit_cliente = %s", (nit,))
    result = cur.fetchone()
    
    if result:
        id_cliente = result[0]
    else:
        cur.execute(
            "INSERT INTO clientes (nit_cliente, nombre_cliente) VALUES (%s, %s) RETURNING id_cliente",
            (nit, nombre)
        )
        id_cliente = cur.fetchone()[0]
        conn.commit()
    
    cur.close()
    conn.close()
    
    return id_cliente


def insert_negocio(id_cliente, nombre_negocio):
    """Inserta un negocio si no existe"""
    conn = get_connection()
    cur = conn.cursor()
    
    # Verificar si el negocio ya existe
    cur.execute(
        "SELECT id_negocio FROM negocios WHERE id_cliente = %s AND nombre_negocio = %s",
        (id_cliente, nombre_negocio)
    )
    result = cur.fetchone()
    
    if not result:
        cur.execute(
            "INSERT INTO negocios (id_cliente, nombre_negocio) VALUES (%s, %s)",
            (id_cliente, nombre_negocio)
        )
        conn.commit()
    
    cur.close()
    conn.close()


def insert_remision(numero_remision, id_cliente, fecha, estado, valor):
    """Inserta una remisión si no existe"""
    conn = get_connection()
    cur = conn.cursor()
    
    # Verificar si la remisión ya existe
    cur.execute("SELECT remision_id FROM remisiones WHERE numero_remision = %s", (numero_remision,))
    result = cur.fetchone()
    
    if not result:
        cur.execute(
            """INSERT INTO remisiones (numero_remision, id_cliente, fecha, estado_remision, valor_remsion) 
               VALUES (%s, %s, %s, %s, %s)""",
            (numero_remision, id_cliente, fecha, estado, valor)
        )
        conn.commit()
    
    cur.close()
    conn.close()


def get_last_invoice_number():
    """Obtiene el número de la última factura guardada"""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT MAX(numero_factura) FROM facturas")
    result = cur.fetchone()[0]
    
    cur.close()
    conn.close()
    
    return result or ""


def insert_factura(numero_factura, id_cliente, fecha, estado, valor):
    """Inserta una factura si no existe"""
    conn = get_connection()
    cur = conn.cursor()
    
    # Verificar si la factura ya existe
    cur.execute("SELECT factura_id FROM facturas WHERE numero_factura = %s", (numero_factura,))
    result = cur.fetchone()
    
    if not result:
        cur.execute(
            """INSERT INTO facturas (numero_factura, id_cliente, fecha, estado_factura, valor_factura) 
               VALUES (%s, %s, %s, %s, %s)""",
            (numero_factura, id_cliente, fecha, estado, valor)
        )
        conn.commit()
    
    cur.close()
    conn.close()


# ==================== FUNCIONES DE ACTUALIZACIÓN ====================

def get_all_remisiones_open():
    """Obtiene todas las remisiones con estado 'open'"""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT numero_remision, estado_remision FROM remisiones WHERE estado_remision = 'open'")
    result = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return result


def update_remision_estado(numero_remision, nuevo_estado):
    """Actualiza el estado de una remisión"""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute(
        "UPDATE remisiones SET estado_remision = %s WHERE numero_remision = %s",
        (nuevo_estado, numero_remision)
    )
    conn.commit()
    
    cur.close()
    conn.close()


def get_all_facturas_open():
    """Obtiene todas las facturas con estado 'open'"""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT numero_factura, estado_factura FROM facturas WHERE estado_factura = 'open'")
    result = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return result


def update_factura_estado(numero_factura, nuevo_estado):
    """Actualiza el estado de una factura"""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute(
        "UPDATE facturas SET estado_factura = %s WHERE numero_factura = %s",
        (nuevo_estado, numero_factura)
    )
    conn.commit()
    
    cur.close()
    conn.close()


def update_remision_valor(numero_remision, nuevo_valor):
    """Actualiza el valor de una remisión"""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute(
        "UPDATE remisiones SET valor_remsion = %s WHERE numero_remision = %s",
        (nuevo_valor, numero_remision)
    )
    conn.commit()
    
    cur.close()
    conn.close()


def update_factura_valor(numero_factura, nuevo_valor):
    """Actualiza el valor de una factura"""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute(
        "UPDATE facturas SET valor_factura = %s WHERE numero_factura = %s",
        (nuevo_valor, numero_factura)
    )
    conn.commit()
    
    cur.close()
    conn.close()


def get_all_remisiones_open_with_value():
    """Obtiene todas las remisiones abiertas con su valor actual"""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT numero_remision, estado_remision, valor_remsion FROM remisiones WHERE estado_remision = 'open'")
    result = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return result


def get_all_facturas_open_with_value():
    """Obtiene todas las facturas abiertas con su valor actual"""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT numero_factura, estado_factura, valor_factura FROM facturas WHERE estado_factura = 'open'")
    result = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return result


def reset_all_remisiones_to_closed(excluidas=None):
    """Marca todas las remisiones abiertas como cerradas (para sincronización completa)
    
    Args:
        excluidas: Lista de números de remisión que NO deben ser tocadas (cerradas manualmente)
    """
    conn = get_connection()
    cur = conn.cursor()
    
    if excluidas:
        # Cerrar todas EXCEPTO las excluidas
        cur.execute("""
            UPDATE remisiones 
            SET estado_remision = 'closed' 
            WHERE estado_remision = 'open' 
            AND numero_remision NOT IN %s
        """, (tuple(excluidas),))
    else:
        cur.execute("UPDATE remisiones SET estado_remision = 'closed' WHERE estado_remision = 'open'")
    
    count = cur.rowcount
    conn.commit()
    
    cur.close()
    conn.close()
    
    return count


def reset_all_facturas_to_closed():
    """Marca todas las facturas abiertas como cerradas (para sincronización completa)"""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("UPDATE facturas SET estado_factura = 'closed' WHERE estado_factura = 'open'")
    count = cur.rowcount
    conn.commit()
    
    cur.close()
    conn.close()
    
    return count


def upsert_remision(numero_remision, id_cliente, fecha, estado, valor, nombre_negocio):
    """Inserta o actualiza una remisión (respeta exclusiones)"""
    conn = get_connection()
    cur = conn.cursor()
    
    # Verificar si está excluida (cerrada manualmente)
    cur.execute("SELECT 1 FROM remisiones_excluidas WHERE numero_remision = %s", (numero_remision,))
    if cur.fetchone():
        # No actualizar remisiones excluidas
        cur.close()
        conn.close()
        return False  # No fue insertada ni actualizada
    
    # Verificar si existe
    cur.execute("SELECT remision_id FROM remisiones WHERE numero_remision = %s", (numero_remision,))
    result = cur.fetchone()
    
    if result:
        # Actualizar
        cur.execute("""
            UPDATE remisiones 
            SET estado_remision = %s, valor_remsion = %s, nombre_negocio = %s
            WHERE numero_remision = %s
        """, (estado, valor, nombre_negocio, numero_remision))
    else:
        # Insertar
        cur.execute("""
            INSERT INTO remisiones (numero_remision, id_cliente, fecha, estado_remision, valor_remsion, nombre_negocio)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (numero_remision, id_cliente, fecha, estado, valor, nombre_negocio))
    
    conn.commit()
    cur.close()
    conn.close()
    
    return result is None  # True si fue insertado, False si fue actualizado


def upsert_factura(numero_factura, id_cliente, fecha, estado, valor, balance, nombre_negocio):
    """Inserta o actualiza una factura"""
    conn = get_connection()
    cur = conn.cursor()
    
    # Verificar si existe
    cur.execute("SELECT factura_id FROM facturas WHERE numero_factura = %s", (numero_factura,))
    result = cur.fetchone()
    
    if result:
        # Actualizar
        cur.execute("""
            UPDATE facturas 
            SET estado_factura = %s, valor_factura = %s, balance_factura = %s, nombre_negocio = %s
            WHERE numero_factura = %s
        """, (estado, valor, balance, nombre_negocio, numero_factura))
    else:
        # Insertar
        cur.execute("""
            INSERT INTO facturas (numero_factura, id_cliente, fecha, estado_factura, valor_factura, balance_factura, nombre_negocio)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (numero_factura, id_cliente, fecha, estado, valor, balance, nombre_negocio))
    
    conn.commit()
    cur.close()
    conn.close()
    
    return result is None  # True si fue insertado, False si fue actualizado


# ==================== FUNCIONES DE SEDES ====================

def get_all_sedes():
    """Obtiene todas las sedes activas"""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT id_sede, nombre_sede FROM sedes WHERE activo = TRUE ORDER BY nombre_sede")
    result = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return [{'id_sede': r[0], 'nombre_sede': r[1]} for r in result]


def get_sede_by_id(id_sede):
    """Obtiene una sede por su ID"""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT id_sede, nombre_sede FROM sedes WHERE id_sede = %s", (id_sede,))
    result = cur.fetchone()
    
    cur.close()
    conn.close()
    
    if result:
        return {'id_sede': result[0], 'nombre_sede': result[1]}
    return None


# ==================== FUNCIONES DE ROLES ====================

def get_all_roles():
    """Obtiene todos los roles activos"""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT id_rol, nombre_rol FROM roles WHERE activo = TRUE ORDER BY nombre_rol")
    result = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return [{'id_rol': r[0], 'nombre_rol': r[1]} for r in result]


def get_rol_by_id(id_rol):
    """Obtiene un rol por su ID"""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT id_rol, nombre_rol FROM roles WHERE id_rol = %s", (id_rol,))
    result = cur.fetchone()
    
    cur.close()
    conn.close()
    
    if result:
        return {'id_rol': result[0], 'nombre_rol': result[1]}
    return None


def insert_rol(nombre_rol):
    """Inserta un nuevo rol"""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute(
            "INSERT INTO roles (nombre_rol) VALUES (%s) RETURNING id_rol",
            (nombre_rol,)
        )
        id_rol = cur.fetchone()[0]
        conn.commit()
        return id_rol, None
    except Exception as e:
        conn.rollback()
        return None, str(e)
    finally:
        cur.close()
        conn.close()


def update_rol(id_rol, nombre_rol):
    """Actualiza un rol existente"""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute(
            "UPDATE roles SET nombre_rol = %s WHERE id_rol = %s",
            (nombre_rol, id_rol)
        )
        conn.commit()
        return True, None
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        cur.close()
        conn.close()


def delete_rol(id_rol):
    """Desactiva un rol (soft delete)"""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute(
            "UPDATE roles SET activo = FALSE WHERE id_rol = %s",
            (id_rol,)
        )
        conn.commit()
        return True, None
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        cur.close()
        conn.close()


# ==================== FUNCIONES DE EMPLEADOS ====================

def insert_empleado(nombre_empleado, tipo_documento, cedula_empleado, salario_dia, id_sede=None, id_rol=None, celular=None, tipo_empleado='no_asegurado'):
    """Inserta un nuevo empleado en la base de datos"""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute(
            """INSERT INTO empleados (nombre_empleado, tipo_documento, cedula_empleado, salario_dia, id_sede, id_rol, celular, tipo_empleado)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id_empleado""",
            (nombre_empleado, tipo_documento, cedula_empleado, salario_dia, id_sede, id_rol, celular, tipo_empleado)
        )
        id_empleado = cur.fetchone()[0]
        conn.commit()
        return id_empleado, None
    except Exception as e:
        conn.rollback()
        return None, str(e)
    finally:
        cur.close()
        conn.close()


def check_cedula_exists(cedula_empleado):
    """Verifica si ya existe un empleado con esa cédula"""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT id_empleado FROM empleados WHERE cedula_empleado = %s", (cedula_empleado,))
    result = cur.fetchone()
    
    cur.close()
    conn.close()
    
    return result is not None


def get_all_empleados():
    """Obtiene todos los empleados"""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT id_empleado, nombre_empleado, tipo_documento, cedula_empleado, salario_dia, create_at FROM empleados ORDER BY nombre_empleado")
    result = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return result


def get_all_empleados_completo():
    """Obtiene todos los empleados con sede y rol"""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT e.id_empleado, e.nombre_empleado, e.tipo_documento, e.cedula_empleado, 
               e.salario_dia, e.celular, e.id_sede, e.id_rol, e.tipo_empleado,
               COALESCE(s.nombre_sede, 'Sin Sede') as nombre_sede,
               COALESCE(r.nombre_rol, 'Sin Rol') as nombre_rol,
               e.create_at
        FROM empleados e
        LEFT JOIN sedes s ON e.id_sede = s.id_sede
        LEFT JOIN roles r ON e.id_rol = r.id_rol
        ORDER BY e.nombre_empleado
    """)
    result = cur.fetchall()
    
    cur.close()
    conn.close()
    
    empleados = []
    for row in result:
        empleados.append({
            'id_empleado': row[0],
            'nombre_empleado': row[1],
            'tipo_documento': row[2],
            'cedula_empleado': row[3],
            'salario_dia': row[4],
            'celular': row[5],
            'id_sede': row[6],
            'id_rol': row[7],
            'tipo_empleado': row[8] or 'no_asegurado',
            'nombre_sede': row[9],
            'nombre_rol': row[10],
            'create_at': row[11]
        })
    
    return empleados


def get_empleado_by_id(id_empleado):
    """Obtiene un empleado por su ID con todos sus datos"""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT e.id_empleado, e.nombre_empleado, e.tipo_documento, e.cedula_empleado, 
               e.salario_dia, e.celular, e.id_sede, e.id_rol, e.tipo_empleado,
               COALESCE(s.nombre_sede, 'Sin Sede') as nombre_sede,
               COALESCE(r.nombre_rol, 'Sin Rol') as nombre_rol
        FROM empleados e
        LEFT JOIN sedes s ON e.id_sede = s.id_sede
        LEFT JOIN roles r ON e.id_rol = r.id_rol
        WHERE e.id_empleado = %s
    """, (id_empleado,))
    result = cur.fetchone()
    
    cur.close()
    conn.close()
    
    if result:
        return {
            'id_empleado': result[0],
            'nombre_empleado': result[1],
            'tipo_documento': result[2],
            'cedula_empleado': result[3],
            'salario_dia': result[4],
            'celular': result[5],
            'id_sede': result[6],
            'id_rol': result[7],
            'tipo_empleado': result[8] or 'no_asegurado',
            'nombre_sede': result[9],
            'nombre_rol': result[10]
        }
    return None


def update_empleado(id_empleado, nombre_empleado, tipo_documento, cedula_empleado, salario_dia, id_sede, id_rol, celular, tipo_empleado):
    """Actualiza los datos de un empleado"""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            UPDATE empleados 
            SET nombre_empleado = %s, tipo_documento = %s, cedula_empleado = %s, 
                salario_dia = %s, id_sede = %s, id_rol = %s, celular = %s, tipo_empleado = %s
            WHERE id_empleado = %s
        """, (nombre_empleado, tipo_documento, cedula_empleado, salario_dia, id_sede, id_rol, celular, tipo_empleado, id_empleado))
        conn.commit()
        return True, None
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        cur.close()
        conn.close()


def delete_empleado(id_empleado):
    """Elimina un empleado de la base de datos"""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # Primero eliminar turnos relacionados
        cur.execute("DELETE FROM turnos WHERE id_empleado = %s", (id_empleado,))
        # Luego eliminar el empleado
        cur.execute("DELETE FROM empleados WHERE id_empleado = %s", (id_empleado,))
        conn.commit()
        return True, None
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        cur.close()
        conn.close()


def check_cedula_exists_excluding(cedula_empleado, id_empleado):
    """Verifica si ya existe un empleado con esa cédula, excluyendo el empleado actual"""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT id_empleado FROM empleados WHERE cedula_empleado = %s AND id_empleado != %s", (cedula_empleado, id_empleado))
    result = cur.fetchone()
    
    cur.close()
    conn.close()
    
    return result is not None


# ==================== FUNCIONES DE TURNOS ====================

def get_empleado_by_cedula(cedula, id_sede=None):
    """Obtiene un empleado por su número de cédula con sede y rol
    
    Args:
        cedula: Número de cédula del empleado
        id_sede: Si se proporciona, solo retorna el empleado si pertenece a esa sede
    """
    conn = get_connection()
    cur = conn.cursor()
    
    if id_sede:
        cur.execute(
            """SELECT e.id_empleado, e.nombre_empleado, e.tipo_documento, e.cedula_empleado, e.salario_dia,
                      COALESCE(s.nombre_sede, 'Sin Sede') as nombre_sede,
                      COALESCE(r.nombre_rol, 'Sin Rol') as nombre_rol,
                      e.id_sede
               FROM empleados e
               LEFT JOIN sedes s ON e.id_sede = s.id_sede
               LEFT JOIN roles r ON e.id_rol = r.id_rol
               WHERE e.cedula_empleado = %s AND e.id_sede = %s""",
            (cedula, id_sede)
        )
    else:
        cur.execute(
            """SELECT e.id_empleado, e.nombre_empleado, e.tipo_documento, e.cedula_empleado, e.salario_dia,
                      COALESCE(s.nombre_sede, 'Sin Sede') as nombre_sede,
                      COALESCE(r.nombre_rol, 'Sin Rol') as nombre_rol,
                      e.id_sede
               FROM empleados e
               LEFT JOIN sedes s ON e.id_sede = s.id_sede
               LEFT JOIN roles r ON e.id_rol = r.id_rol
               WHERE e.cedula_empleado = %s""",
            (cedula,)
        )
    result = cur.fetchone()
    
    cur.close()
    conn.close()
    
    if result:
        return {
            'id_empleado': result[0],
            'nombre_empleado': result[1],
            'tipo_documento': result[2],
            'cedula_empleado': result[3],
            'salario_dia': result[4],
            'nombre_sede': result[5],
            'nombre_rol': result[6],
            'id_sede': result[7]
        }
    return None


def get_turno_abierto_hoy(id_empleado):
    """Verifica si el empleado tiene un turno abierto hoy (sin hora_salida) - Usando zona horaria Colombia"""
    conn = get_connection()
    cur = conn.cursor()
    
    # Usar zona horaria de Colombia para comparar fechas
    cur.execute("""
        SELECT id_turno, hora_inicio, hora_salida 
        FROM turnos 
        WHERE id_empleado = %s 
          AND DATE(hora_inicio AT TIME ZONE 'America/Bogota') = (CURRENT_TIMESTAMP AT TIME ZONE 'America/Bogota')::DATE
          AND hora_salida IS NULL
        ORDER BY hora_inicio DESC
        LIMIT 1
    """, (id_empleado,))
    result = cur.fetchone()
    
    cur.close()
    conn.close()
    
    if result:
        return {
            'id_turno': result[0],
            'hora_inicio': result[1],
            'hora_salida': result[2]
        }
    return None


def get_turno_completo_hoy(id_empleado):
    """Obtiene todos los turnos completados hoy (con entrada y salida) - Ya no se usa para bloquear"""
    conn = get_connection()
    cur = conn.cursor()
    
    # Usar zona horaria de Colombia para comparar fechas
    cur.execute("""
        SELECT id_turno, hora_inicio, hora_salida 
        FROM turnos 
        WHERE id_empleado = %s 
          AND DATE(hora_inicio AT TIME ZONE 'America/Bogota') = (CURRENT_TIMESTAMP AT TIME ZONE 'America/Bogota')::DATE
          AND hora_salida IS NOT NULL
        ORDER BY hora_inicio DESC
        LIMIT 1
    """, (id_empleado,))
    result = cur.fetchone()
    
    cur.close()
    conn.close()
    
    if result:
        return {
            'id_turno': result[0],
            'hora_inicio': result[1],
            'hora_salida': result[2]
        }
    return None


def registrar_entrada(id_empleado):
    """Registra la entrada de un empleado (crea un nuevo turno) - Usando zona horaria Colombia"""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # Guardar timestamp con zona horaria de Colombia
        cur.execute(
            "INSERT INTO turnos (id_empleado, hora_inicio) VALUES (%s, NOW()) RETURNING id_turno, hora_inicio",
            (id_empleado,)
        )
        result = cur.fetchone()
        conn.commit()
        return {'id_turno': result[0], 'hora_inicio': result[1]}, None
    except Exception as e:
        conn.rollback()
        return None, str(e)
    finally:
        cur.close()
        conn.close()


def registrar_salida(id_turno):
    """Registra la salida de un empleado (actualiza hora_salida del turno)"""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute(
            "UPDATE turnos SET hora_salida = NOW() WHERE id_turno = %s RETURNING hora_salida",
            (id_turno,)
        )
        result = cur.fetchone()
        conn.commit()
        return {'hora_salida': result[0]}, None
    except Exception as e:
        conn.rollback()
        return None, str(e)
    finally:
        cur.close()
        conn.close()


def get_turnos_empleado_hoy(id_empleado):
    """Obtiene todos los turnos del empleado del día de hoy - Usando zona horaria Colombia"""
    conn = get_connection()
    cur = conn.cursor()
    
    # Usar zona horaria de Colombia para comparar fechas
    cur.execute("""
        SELECT id_turno, hora_inicio, hora_salida 
        FROM turnos 
        WHERE id_empleado = %s 
          AND DATE(hora_inicio AT TIME ZONE 'America/Bogota') = (CURRENT_TIMESTAMP AT TIME ZONE 'America/Bogota')::DATE
        ORDER BY hora_inicio DESC
    """, (id_empleado,))
    results = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return [{'id_turno': r[0], 'hora_inicio': r[1], 'hora_salida': r[2]} for r in results]


# ==================== FUNCIONES DE DIRECCIONES IP ====================

def get_all_direcciones_ip():
    """Obtiene todas las direcciones IP registradas"""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT id_direccion, direccion_ip, nombre_equipo, activo, create_at 
        FROM direcciones_ip 
        ORDER BY nombre_equipo
    """)
    results = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return [{
        'id_direccion': r[0],
        'direccion_ip': r[1],
        'nombre_equipo': r[2],
        'activo': r[3],
        'create_at': r[4]
    } for r in results]


def insert_direccion_ip(direccion_ip, nombre_equipo):
    """Inserta una nueva dirección IP"""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute(
            "INSERT INTO direcciones_ip (direccion_ip, nombre_equipo) VALUES (%s, %s) RETURNING id_direccion",
            (direccion_ip, nombre_equipo)
        )
        id_direccion = cur.fetchone()[0]
        conn.commit()
        return id_direccion, None
    except Exception as e:
        conn.rollback()
        return None, str(e)
    finally:
        cur.close()
        conn.close()


def update_direccion_ip_estado(id_direccion, activo):
    """Activa o desactiva una dirección IP"""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute(
            "UPDATE direcciones_ip SET activo = %s WHERE id_direccion = %s",
            (activo, id_direccion)
        )
        conn.commit()
        return True, None
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        cur.close()
        conn.close()


def delete_direccion_ip(id_direccion):
    """Elimina una dirección IP"""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("DELETE FROM direcciones_ip WHERE id_direccion = %s", (id_direccion,))
        conn.commit()
        return True, None
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        cur.close()
        conn.close()


def check_ip_autorizada(ip):
    """Verifica si una IP está autorizada (activa)"""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute(
        "SELECT id_direccion, nombre_equipo FROM direcciones_ip WHERE direccion_ip = %s AND activo = true",
        (ip,)
    )
    result = cur.fetchone()
    
    cur.close()
    conn.close()
    
    if result:
        return {'id_direccion': result[0], 'nombre_equipo': result[1]}
    return None


def check_ip_exists(direccion_ip):
    """Verifica si una dirección IP ya existe"""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT id_direccion FROM direcciones_ip WHERE direccion_ip = %s", (direccion_ip,))
    result = cur.fetchone()
    
    cur.close()
    conn.close()
    
    return result is not None


# ==================== FUNCIONES DE GESTIÓN DE TURNOS ====================

def get_all_empleados_activos(id_sede=None):
    """Obtiene todos los empleados activos para selección, opcionalmente filtrados por sede"""
    conn = get_connection()
    cur = conn.cursor()
    
    if id_sede:
        cur.execute("""
            SELECT id_empleado, nombre_empleado, cedula_empleado 
            FROM empleados 
            WHERE id_sede = %s
            ORDER BY nombre_empleado
        """, (id_sede,))
    else:
        cur.execute("""
            SELECT id_empleado, nombre_empleado, cedula_empleado 
            FROM empleados 
            ORDER BY nombre_empleado
        """)
    results = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return [{
        'id_empleado': r[0],
        'nombre_empleado': r[1],
        'cedula_empleado': r[2]
    } for r in results]


def insert_turno_manual(id_empleado, hora_inicio, hora_salida=None):
    """Inserta un turno de forma manual con fecha/hora específica (convierte hora Colombia a UTC)"""
    import pytz
    
    # Zona horaria Colombia
    tz_colombia = pytz.timezone('America/Bogota')
    
    # Si hora_inicio no tiene zona horaria, asumimos que es hora Colombia y la convertimos a UTC
    if hora_inicio.tzinfo is None:
        hora_inicio = tz_colombia.localize(hora_inicio).astimezone(pytz.UTC)
    
    if hora_salida and hora_salida.tzinfo is None:
        hora_salida = tz_colombia.localize(hora_salida).astimezone(pytz.UTC)
    
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        if hora_salida:
            cur.execute(
                """INSERT INTO turnos (id_empleado, hora_inicio, hora_salida) 
                   VALUES (%s, %s, %s) RETURNING id_turno""",
                (id_empleado, hora_inicio, hora_salida)
            )
        else:
            cur.execute(
                """INSERT INTO turnos (id_empleado, hora_inicio) 
                   VALUES (%s, %s) RETURNING id_turno""",
                (id_empleado, hora_inicio)
            )
        id_turno = cur.fetchone()[0]
        conn.commit()
        return id_turno, None
    except Exception as e:
        conn.rollback()
        return None, str(e)
    finally:
        cur.close()
        conn.close()


def update_turno(id_turno, hora_inicio=None, hora_salida=None):
    """Actualiza un turno existente (convierte hora Colombia a UTC)"""
    import pytz
    
    # Zona horaria Colombia
    tz_colombia = pytz.timezone('America/Bogota')
    
    # Convertir horas locales a UTC si no tienen zona horaria
    if hora_inicio and hora_inicio.tzinfo is None:
        hora_inicio = tz_colombia.localize(hora_inicio).astimezone(pytz.UTC)
    
    if hora_salida and hora_salida.tzinfo is None:
        hora_salida = tz_colombia.localize(hora_salida).astimezone(pytz.UTC)
    
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        if hora_inicio and hora_salida:
            cur.execute(
                "UPDATE turnos SET hora_inicio = %s, hora_salida = %s WHERE id_turno = %s",
                (hora_inicio, hora_salida, id_turno)
            )
        elif hora_inicio:
            cur.execute(
                "UPDATE turnos SET hora_inicio = %s WHERE id_turno = %s",
                (hora_inicio, id_turno)
            )
        elif hora_salida:
            cur.execute(
                "UPDATE turnos SET hora_salida = %s WHERE id_turno = %s",
                (hora_salida, id_turno)
            )
        conn.commit()
        return True, None
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        cur.close()
        conn.close()


def cerrar_turno_abierto(id_turno, hora_salida):
    """Cierra un turno abierto con hora de salida específica (convierte hora Colombia a UTC)"""
    import pytz
    
    # Zona horaria Colombia
    tz_colombia = pytz.timezone('America/Bogota')
    
    # Convertir hora local a UTC si no tiene zona horaria
    if hora_salida and hora_salida.tzinfo is None:
        hora_salida = tz_colombia.localize(hora_salida).astimezone(pytz.UTC)
    
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute(
            "UPDATE turnos SET hora_salida = %s WHERE id_turno = %s AND hora_salida IS NULL",
            (hora_salida, id_turno)
        )
        affected = cur.rowcount
        conn.commit()
        return affected > 0, None
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        cur.close()
        conn.close()


def delete_turno(id_turno):
    """Elimina un turno"""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("DELETE FROM turnos WHERE id_turno = %s", (id_turno,))
        conn.commit()
        return True, None
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        cur.close()
        conn.close()


def get_turnos_abiertos(id_sede=None):
    """Obtiene todos los turnos abiertos (sin hora de salida), opcionalmente filtrados por sede"""
    conn = get_connection()
    cur = conn.cursor()
    
    if id_sede:
        cur.execute("""
            SELECT t.id_turno, e.nombre_empleado, e.cedula_empleado, t.hora_inicio
            FROM turnos t
            INNER JOIN empleados e ON t.id_empleado = e.id_empleado
            WHERE t.hora_salida IS NULL AND e.id_sede = %s
            ORDER BY t.hora_inicio DESC
        """, (id_sede,))
    else:
        cur.execute("""
            SELECT t.id_turno, e.nombre_empleado, e.cedula_empleado, t.hora_inicio
            FROM turnos t
            INNER JOIN empleados e ON t.id_empleado = e.id_empleado
            WHERE t.hora_salida IS NULL
            ORDER BY t.hora_inicio DESC
        """)
    results = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return [{
        'id_turno': r[0],
        'nombre_empleado': r[1],
        'cedula_empleado': r[2],
        'hora_inicio': r[3]
    } for r in results]


def get_historial_turnos(fecha_inicio=None, fecha_fin=None, id_empleado=None, limit=100, id_sede=None):
    """Obtiene el historial de turnos con filtros, opcionalmente filtrados por sede"""
    conn = get_connection()
    cur = conn.cursor()
    
    query = """
        SELECT t.id_turno, e.id_empleado, e.nombre_empleado, e.cedula_empleado, 
               t.hora_inicio, t.hora_salida,
               CASE WHEN t.hora_salida IS NULL THEN 'Abierto' ELSE 'Cerrado' END as estado
        FROM turnos t
        INNER JOIN empleados e ON t.id_empleado = e.id_empleado
        WHERE 1=1
    """
    params = []
    
    if id_sede:
        query += " AND e.id_sede = %s"
        params.append(id_sede)
    
    if fecha_inicio:
        query += " AND DATE(t.hora_inicio) >= %s"
        params.append(fecha_inicio)
    
    if fecha_fin:
        query += " AND DATE(t.hora_inicio) <= %s"
        params.append(fecha_fin)
    
    if id_empleado:
        query += " AND t.id_empleado = %s"
        params.append(id_empleado)
    
    query += " ORDER BY t.hora_inicio DESC LIMIT %s"
    params.append(limit)
    
    cur.execute(query, params)
    results = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return [{
        'id_turno': r[0],
        'id_empleado': r[1],
        'nombre_empleado': r[2],
        'cedula_empleado': r[3],
        'hora_inicio': r[4],
        'hora_salida': r[5],
        'estado': r[6]
    } for r in results]


def get_turno_by_id(id_turno):
    """Obtiene un turno por su ID"""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT t.id_turno, t.id_empleado, e.nombre_empleado, e.cedula_empleado,
               t.hora_inicio, t.hora_salida
        FROM turnos t
        INNER JOIN empleados e ON t.id_empleado = e.id_empleado
        WHERE t.id_turno = %s
    """, (id_turno,))
    result = cur.fetchone()
    
    cur.close()
    conn.close()
    
    if result:
        return {
            'id_turno': result[0],
            'id_empleado': result[1],
            'nombre_empleado': result[2],
            'cedula_empleado': result[3],
            'hora_inicio': result[4],
            'hora_salida': result[5]
        }
    return None


# ==================== FUNCIONES DE AUTENTICACIÓN Y USUARIOS ====================

import hashlib

def hash_password(password):
    """Genera hash SHA256 de una contraseña"""
    return hashlib.sha256(password.encode()).hexdigest()


def autenticar_usuario(username, password):
    """Autentica un usuario y retorna sus datos si es válido"""
    conn = get_connection()
    cur = conn.cursor()
    
    password_hash = hash_password(password)
    
    cur.execute("""
        SELECT u.id_usuario, u.username, u.nombre_completo, u.es_master, u.es_empleado, u.es_admin, 
               u.activo
        FROM usuarios u
        WHERE u.username = %s AND u.password_hash = %s AND u.activo = TRUE
    """, (username, password_hash))
    result = cur.fetchone()
    
    cur.close()
    conn.close()
    
    if result:
        return {
            'id_usuario': result[0],
            'username': result[1],
            'nombre_completo': result[2],
            'es_master': result[3],
            'es_empleado': result[4],
            'es_admin': result[5],
            'activo': result[6]
        }
    return None


def get_modulos_usuario(id_usuario):
    """Obtiene los módulos a los que tiene acceso un usuario"""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT m.id_modulo, m.nombre_modulo, m.descripcion, m.icono, um.puede_ver, um.puede_editar
        FROM usuarios_modulos um
        INNER JOIN modulos_sistema m ON um.id_modulo = m.id_modulo
        WHERE um.id_usuario = %s AND um.puede_ver = TRUE
        ORDER BY m.orden
    """, (id_usuario,))
    results = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return [{
        'id_modulo': r[0],
        'nombre_modulo': r[1],
        'descripcion': r[2],
        'icono': r[3],
        'puede_ver': r[4],
        'puede_editar': r[5]
    } for r in results]


def get_all_usuarios():
    """Obtiene todos los usuarios"""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT u.id_usuario, u.username, u.nombre_completo, u.es_master, u.es_empleado, u.es_admin, 
               u.activo, u.create_at, u.rol, u.id_sede, s.nombre_sede
        FROM usuarios u
        LEFT JOIN sedes s ON u.id_sede = s.id_sede
        ORDER BY u.es_master DESC, u.es_admin DESC, u.nombre_completo
    """)
    results = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return [{
        'id_usuario': r[0],
        'username': r[1],
        'nombre_completo': r[2],
        'es_master': r[3],
        'es_empleado': r[4],
        'es_admin': r[5],
        'activo': r[6],
        'create_at': r[7],
        'rol': r[8],
        'id_sede': r[9],
        'nombre_sede': r[10]
    } for r in results]


def get_usuario_by_id(id_usuario):
    """Obtiene un usuario por su ID"""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT u.id_usuario, u.username, u.nombre_completo, u.es_master, u.es_empleado, u.es_admin, 
               u.activo, u.rol, u.id_sede, s.nombre_sede
        FROM usuarios u
        LEFT JOIN sedes s ON u.id_sede = s.id_sede
        WHERE u.id_usuario = %s
    """, (id_usuario,))
    result = cur.fetchone()
    
    cur.close()
    conn.close()
    
    if result:
        return {
            'id_usuario': result[0],
            'username': result[1],
            'nombre_completo': result[2],
            'es_master': result[3],
            'es_empleado': result[4],
            'es_admin': result[5],
            'activo': result[6],
            'rol': result[7],
            'id_sede': result[8],
            'nombre_sede': result[9]
        }
    return None
    
    cur.close()
    conn.close()
    
    if result:
        return {
            'id_usuario': result[0],
            'username': result[1],
            'nombre_completo': result[2],
            'es_master': result[3],
            'es_empleado': result[4],
            'es_admin': result[5],
            'activo': result[6]
        }
    return None


def insert_usuario(username, password, nombre_completo, es_master=False, es_empleado=False, es_admin=False, rol='normal', id_sede=None):
    """Inserta un nuevo usuario"""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        password_hash = hash_password(password)
        cur.execute(
            """INSERT INTO usuarios (username, password_hash, nombre_completo, es_master, es_empleado, es_admin, rol, id_sede)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id_usuario""",
            (username, password_hash, nombre_completo, es_master, es_empleado, es_admin, rol, id_sede)
        )
        id_usuario = cur.fetchone()[0]
        conn.commit()
        return id_usuario, None
    except Exception as e:
        conn.rollback()
        return None, str(e)
    finally:
        cur.close()
        conn.close()


def update_usuario(id_usuario, username=None, nombre_completo=None, es_master=None, es_empleado=None, es_admin=None, activo=None, rol=None, id_sede=None):
    """Actualiza un usuario existente"""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        updates = []
        params = []
        
        if username is not None:
            updates.append("username = %s")
            params.append(username)
        if nombre_completo is not None:
            updates.append("nombre_completo = %s")
            params.append(nombre_completo)
        if es_master is not None:
            updates.append("es_master = %s")
            params.append(es_master)
        if es_empleado is not None:
            updates.append("es_empleado = %s")
            params.append(es_empleado)
        if es_admin is not None:
            updates.append("es_admin = %s")
            params.append(es_admin)
        if activo is not None:
            updates.append("activo = %s")
            params.append(activo)
        if rol is not None:
            updates.append("rol = %s")
            params.append(rol)
        if id_sede is not None:
            updates.append("id_sede = %s")
            params.append(id_sede if id_sede != 0 else None)
        
        if updates:
            params.append(id_usuario)
            query = f"UPDATE usuarios SET {', '.join(updates)} WHERE id_usuario = %s"
            cur.execute(query, params)
            conn.commit()
        
        return True, None
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        cur.close()
        conn.close()


def update_usuario_password(id_usuario, new_password):
    """Actualiza la contraseña de un usuario"""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        password_hash = hash_password(new_password)
        cur.execute(
            "UPDATE usuarios SET password_hash = %s WHERE id_usuario = %s",
            (password_hash, id_usuario)
        )
        conn.commit()
        return True, None
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        cur.close()
        conn.close()


def delete_usuario(id_usuario):
    """Elimina un usuario"""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("DELETE FROM usuarios WHERE id_usuario = %s AND es_master = FALSE", (id_usuario,))
        affected = cur.rowcount
        conn.commit()
        return affected > 0, None
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        cur.close()
        conn.close()


def check_username_exists(username, exclude_id=None):
    """Verifica si un nombre de usuario ya existe"""
    conn = get_connection()
    cur = conn.cursor()
    
    if exclude_id:
        cur.execute("SELECT id_usuario FROM usuarios WHERE username = %s AND id_usuario != %s", (username, exclude_id))
    else:
        cur.execute("SELECT id_usuario FROM usuarios WHERE username = %s", (username,))
    result = cur.fetchone()
    
    cur.close()
    conn.close()
    
    return result is not None


def get_all_modulos():
    """Obtiene todos los módulos del sistema"""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT id_modulo, nombre_modulo, descripcion, icono, orden FROM modulos_sistema ORDER BY orden")
    results = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return [{
        'id_modulo': r[0],
        'nombre_modulo': r[1],
        'descripcion': r[2],
        'icono': r[3],
        'orden': r[4]
    } for r in results]


def get_permisos_usuario(id_usuario):
    """Obtiene los permisos de módulos de un usuario"""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT m.id_modulo, m.nombre_modulo, 
               COALESCE(um.puede_ver, FALSE) as puede_ver, 
               COALESCE(um.puede_editar, FALSE) as puede_editar
        FROM modulos_sistema m
        LEFT JOIN usuarios_modulos um ON m.id_modulo = um.id_modulo AND um.id_usuario = %s
        ORDER BY m.orden
    """, (id_usuario,))
    results = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return [{
        'id_modulo': r[0],
        'nombre_modulo': r[1],
        'puede_ver': r[2],
        'puede_editar': r[3]
    } for r in results]


def set_permisos_usuario(id_usuario, permisos):
    """Establece los permisos de módulos para un usuario
    permisos: lista de dict con {id_modulo, puede_ver, puede_editar}
    """
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # Eliminar permisos existentes
        cur.execute("DELETE FROM usuarios_modulos WHERE id_usuario = %s", (id_usuario,))
        
        # Insertar nuevos permisos
        for perm in permisos:
            if perm.get('puede_ver', False):
                cur.execute(
                    """INSERT INTO usuarios_modulos (id_usuario, id_modulo, puede_ver, puede_editar)
                       VALUES (%s, %s, %s, %s)""",
                    (id_usuario, perm['id_modulo'], perm['puede_ver'], perm.get('puede_editar', False))
                )
        
        conn.commit()
        return True, None
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        cur.close()
        conn.close()


# ==================== FUNCIONES DE TOTAL HORAS (NÓMINA) ====================

def get_total_horas_por_fecha(fecha_inicio=None, fecha_fin=None, id_empleado=None, id_sede=None):
    """
    Obtiene los turnos con cálculo de horas trabajadas.
    Solo incluye turnos completados (con hora_salida).
    
    Args:
        fecha_inicio: Fecha inicial del filtro (opcional)
        fecha_fin: Fecha final del filtro (opcional)
        id_empleado: ID del empleado para filtrar (opcional)
        id_sede: ID de la sede para filtrar (opcional)
    
    Returns:
        Lista de diccionarios con información de turnos y horas trabajadas
    """
    conn = get_connection()
    cur = conn.cursor()
    
    query = """
        SELECT 
            t.id_turno,
            e.id_empleado,
            e.nombre_empleado,
            e.cedula_empleado,
            DATE(t.hora_inicio AT TIME ZONE 'America/Bogota') as fecha,
            t.hora_inicio AT TIME ZONE 'America/Bogota' as hora_entrada,
            t.hora_salida AT TIME ZONE 'America/Bogota' as hora_salida,
            EXTRACT(EPOCH FROM (t.hora_salida - t.hora_inicio)) / 3600 as total_horas,
            COALESCE(s.nombre_sede, 'Sin Sede') as nombre_sede
        FROM turnos t
        INNER JOIN empleados e ON t.id_empleado = e.id_empleado
        LEFT JOIN sedes s ON e.id_sede = s.id_sede
        WHERE t.hora_salida IS NOT NULL
    """
    
    params = []
    
    if fecha_inicio:
        query += " AND DATE(t.hora_inicio AT TIME ZONE 'America/Bogota') >= %s"
        params.append(fecha_inicio)
    
    if fecha_fin:
        query += " AND DATE(t.hora_inicio AT TIME ZONE 'America/Bogota') <= %s"
        params.append(fecha_fin)
    
    if id_empleado:
        query += " AND t.id_empleado = %s"
        params.append(id_empleado)
    
    if id_sede:
        query += " AND e.id_sede = %s"
        params.append(id_sede)
    
    query += " ORDER BY t.hora_inicio DESC"
    
    cur.execute(query, params)
    results = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return [{
        'id_turno': r[0],
        'id_empleado': r[1],
        'nombre_empleado': r[2],
        'cedula_empleado': r[3],
        'fecha': r[4],
        'hora_entrada': r[5],
        'hora_salida': r[6],
        'total_horas': round(r[7], 2) if r[7] else 0,
        'nombre_sede': r[8]
    } for r in results]


def get_resumen_horas_por_empleado(fecha_inicio=None, fecha_fin=None):
    """
    Obtiene el resumen de horas trabajadas por empleado.
    
    Args:
        fecha_inicio: Fecha inicial del filtro (opcional)
        fecha_fin: Fecha final del filtro (opcional)
    
    Returns:
        Lista de diccionarios con resumen por empleado
    """
    conn = get_connection()
    cur = conn.cursor()
    
    query = """
        SELECT 
            e.id_empleado,
            e.nombre_empleado,
            e.cedula_empleado,
            COUNT(t.id_turno) as total_turnos,
            SUM(EXTRACT(EPOCH FROM (t.hora_salida - t.hora_inicio)) / 3600) as total_horas
        FROM empleados e
        LEFT JOIN turnos t ON e.id_empleado = t.id_empleado 
            AND t.hora_salida IS NOT NULL
    """
    
    params = []
    conditions = []
    
    if fecha_inicio:
        conditions.append("DATE(t.hora_inicio AT TIME ZONE 'America/Bogota') >= %s")
        params.append(fecha_inicio)
    
    if fecha_fin:
        conditions.append("DATE(t.hora_inicio AT TIME ZONE 'America/Bogota') <= %s")
        params.append(fecha_fin)
    
    if conditions:
        query += " AND " + " AND ".join(conditions)
    
    query += """
        GROUP BY e.id_empleado, e.nombre_empleado, e.cedula_empleado
        ORDER BY e.nombre_empleado
    """
    
    cur.execute(query, params)
    results = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return [{
        'id_empleado': r[0],
        'nombre_empleado': r[1],
        'cedula_empleado': r[2],
        'total_turnos': r[3] or 0,
        'total_horas': round(r[4], 2) if r[4] else 0
    } for r in results]


def insertar_total_horas(id_turno, fecha, total_horas):
    """
    Inserta o actualiza el registro de total de horas para un turno.
    
    Args:
        id_turno: ID del turno
        fecha: Fecha del turno
        total_horas: Total de horas trabajadas
    
    Returns:
        Tupla (id_registro, error)
    """
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # Verificar si ya existe un registro para este turno
        cur.execute("SELECT id FROM total_horas WHERE id_turno = %s", (id_turno,))
        result = cur.fetchone()
        
        if result:
            # Actualizar registro existente
            cur.execute(
                "UPDATE total_horas SET fecha = %s, total_horas = %s WHERE id_turno = %s RETURNING id",
                (fecha, total_horas, id_turno)
            )
        else:
            # Insertar nuevo registro
            cur.execute(
                "INSERT INTO total_horas (id_turno, fecha, total_horas) VALUES (%s, %s, %s) RETURNING id",
                (id_turno, fecha, total_horas)
            )
        
        id_registro = cur.fetchone()[0]
        conn.commit()
        return id_registro, None
    except Exception as e:
        conn.rollback()
        return None, str(e)
    finally:
        cur.close()
        conn.close()


def sincronizar_total_horas():
    """
    Sincroniza la tabla total_horas con los turnos completados.
    Calcula y guarda las horas trabajadas de todos los turnos con hora_salida.
    
    Returns:
        Tupla (cantidad_sincronizados, error)
    """
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # Obtener todos los turnos completados que no estén en total_horas
        cur.execute("""
            INSERT INTO total_horas (id_turno, fecha, total_horas)
            SELECT 
                t.id_turno,
                DATE(t.hora_inicio AT TIME ZONE 'America/Bogota'),
                EXTRACT(EPOCH FROM (t.hora_salida - t.hora_inicio)) / 3600
            FROM turnos t
            WHERE t.hora_salida IS NOT NULL
              AND NOT EXISTS (
                  SELECT 1 FROM total_horas th WHERE th.id_turno = t.id_turno
              )
            RETURNING id
        """)
        
        insertados = len(cur.fetchall())
        conn.commit()
        return insertados, None
    except Exception as e:
        conn.rollback()
        return 0, str(e)
    finally:
        cur.close()
        conn.close()


# ==================== FUNCIONES DE HORAS EXTRA ====================

def get_horas_extra(fecha_inicio=None, fecha_fin=None, id_empleado=None, id_sede=None):
    """
    Obtiene los turnos con horas extra (más de 8 horas trabajadas).
    
    Args:
        fecha_inicio: Fecha inicial del filtro (opcional)
        fecha_fin: Fecha final del filtro (opcional)
        id_empleado: ID del empleado para filtrar (opcional)
        id_sede: ID de la sede para filtrar (opcional)
    
    Returns:
        Lista de diccionarios con información de turnos y horas extra
    """
    conn = get_connection()
    cur = conn.cursor()
    
    query = """
        SELECT 
            t.id_turno,
            th.id as id_hora,
            e.id_empleado,
            e.nombre_empleado,
            DATE(t.hora_inicio AT TIME ZONE 'America/Bogota') as fecha,
            t.hora_inicio AT TIME ZONE 'America/Bogota' as hora_entrada,
            t.hora_salida AT TIME ZONE 'America/Bogota' as hora_salida,
            EXTRACT(EPOCH FROM (t.hora_salida - t.hora_inicio)) / 3600 as total_horas,
            CASE 
                WHEN EXTRACT(EPOCH FROM (t.hora_salida - t.hora_inicio)) / 3600 > 8 
                THEN EXTRACT(EPOCH FROM (t.hora_salida - t.hora_inicio)) / 3600 - 8
                ELSE 0
            END as horas_extra,
            COALESCE(s.nombre_sede, 'Sin Sede') as nombre_sede
        FROM turnos t
        INNER JOIN empleados e ON t.id_empleado = e.id_empleado
        LEFT JOIN total_horas th ON t.id_turno = th.id_turno
        LEFT JOIN sedes s ON e.id_sede = s.id_sede
        WHERE t.hora_salida IS NOT NULL
          AND EXTRACT(EPOCH FROM (t.hora_salida - t.hora_inicio)) / 3600 > 8
    """
    
    params = []
    
    if fecha_inicio:
        query += " AND DATE(t.hora_inicio AT TIME ZONE 'America/Bogota') >= %s"
        params.append(fecha_inicio)
    
    if fecha_fin:
        query += " AND DATE(t.hora_inicio AT TIME ZONE 'America/Bogota') <= %s"
        params.append(fecha_fin)
    
    if id_empleado:
        query += " AND t.id_empleado = %s"
        params.append(id_empleado)
    
    if id_sede:
        query += " AND e.id_sede = %s"
        params.append(id_sede)
    
    query += " ORDER BY t.hora_inicio DESC"
    
    cur.execute(query, params)
    results = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return [{
        'id_turno': r[0],
        'id_hora': r[1],
        'id_empleado': r[2],
        'nombre_empleado': r[3],
        'fecha': r[4],
        'hora_entrada': r[5],
        'hora_salida': r[6],
        'total_horas': round(r[7], 2) if r[7] else 0,
        'horas_extra': round(r[8], 2) if r[8] else 0,
        'nombre_sede': r[9]
    } for r in results]


def sincronizar_horas_extra():
    """
    Sincroniza la tabla horas_extra con los turnos que tienen más de 8 horas.
    
    Returns:
        Tupla (cantidad_sincronizados, error)
    """
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # Insertar horas extra para turnos que trabajaron más de 8 horas
        cur.execute("""
            INSERT INTO horas_extra (id_turno, id_hora, total_horas_extra)
            SELECT 
                t.id_turno,
                th.id,
                EXTRACT(EPOCH FROM (t.hora_salida - t.hora_inicio)) / 3600 - 8
            FROM turnos t
            INNER JOIN total_horas th ON t.id_turno = th.id_turno
            WHERE t.hora_salida IS NOT NULL
              AND EXTRACT(EPOCH FROM (t.hora_salida - t.hora_inicio)) / 3600 > 8
              AND NOT EXISTS (
                  SELECT 1 FROM horas_extra he WHERE he.id_turno = t.id_turno
              )
            RETURNING id
        """)
        
        insertados = len(cur.fetchall())
        conn.commit()
        return insertados, None
    except Exception as e:
        conn.rollback()
        return 0, str(e)
    finally:
        cur.close()
        conn.close()


def get_resumen_horas_extra_por_empleado(fecha_inicio=None, fecha_fin=None):
    """
    Obtiene el resumen de horas extra por empleado.
    
    Args:
        fecha_inicio: Fecha inicial del filtro (opcional)
        fecha_fin: Fecha final del filtro (opcional)
    
    Returns:
        Lista de diccionarios con resumen por empleado
    """
    conn = get_connection()
    cur = conn.cursor()
    
    query = """
        SELECT 
            e.id_empleado,
            e.nombre_empleado,
            COUNT(t.id_turno) as total_turnos_extra,
            SUM(
                CASE 
                    WHEN EXTRACT(EPOCH FROM (t.hora_salida - t.hora_inicio)) / 3600 > 8 
                    THEN EXTRACT(EPOCH FROM (t.hora_salida - t.hora_inicio)) / 3600 - 8
                    ELSE 0
                END
            ) as total_horas_extra
        FROM empleados e
        INNER JOIN turnos t ON e.id_empleado = t.id_empleado
        WHERE t.hora_salida IS NOT NULL
          AND EXTRACT(EPOCH FROM (t.hora_salida - t.hora_inicio)) / 3600 > 8
    """
    
    params = []
    
    if fecha_inicio:
        query += " AND DATE(t.hora_inicio AT TIME ZONE 'America/Bogota') >= %s"
        params.append(fecha_inicio)
    
    if fecha_fin:
        query += " AND DATE(t.hora_inicio AT TIME ZONE 'America/Bogota') <= %s"
        params.append(fecha_fin)
    
    query += """
        GROUP BY e.id_empleado, e.nombre_empleado
        HAVING SUM(
            CASE 
                WHEN EXTRACT(EPOCH FROM (t.hora_salida - t.hora_inicio)) / 3600 > 8 
                THEN EXTRACT(EPOCH FROM (t.hora_salida - t.hora_inicio)) / 3600 - 8
                ELSE 0
            END
        ) > 0
        ORDER BY total_horas_extra DESC
    """
    
    cur.execute(query, params)
    results = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return [{
        'id_empleado': r[0],
        'nombre_empleado': r[1],
        'total_turnos_extra': r[2] or 0,
        'total_horas_extra': round(r[3], 2) if r[3] else 0
    } for r in results]


# ==================== FUNCIONES PARA CONTROL DE TURNOS SIMPLIFICADO ====================

def get_turno_abierto_empleado(id_empleado):
    """Obtiene el turno abierto (sin hora_salida) de un empleado, sin importar la fecha"""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT id_turno, hora_inicio, hora_salida 
        FROM turnos 
        WHERE id_empleado = %s 
          AND hora_salida IS NULL
        ORDER BY hora_inicio DESC
        LIMIT 1
    """, (id_empleado,))
    result = cur.fetchone()
    
    cur.close()
    conn.close()
    
    if result:
        return {
            'id_turno': result[0],
            'hora_inicio': result[1],
            'hora_salida': result[2]
        }
    return None


def insert_turno_con_foto(id_empleado, hora_inicio, foto_bytes=None):
    """Inserta un nuevo turno con foto de entrada - convierte hora Colombia a UTC"""
    import pytz
    
    tz_colombia = pytz.timezone('America/Bogota')
    
    # Convertir a UTC si no tiene zona horaria
    if hora_inicio.tzinfo is None:
        hora_inicio = tz_colombia.localize(hora_inicio).astimezone(pytz.UTC)
    elif str(hora_inicio.tzinfo) != 'UTC':
        hora_inicio = hora_inicio.astimezone(pytz.UTC)
    
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute(
            """INSERT INTO turnos (id_empleado, hora_inicio, foto_entrada) 
               VALUES (%s, %s, %s) RETURNING id_turno""",
            (id_empleado, hora_inicio, psycopg2.Binary(foto_bytes) if foto_bytes else None)
        )
        id_turno = cur.fetchone()[0]
        conn.commit()
        return id_turno, None
    except Exception as e:
        conn.rollback()
        return None, str(e)
    finally:
        cur.close()
        conn.close()


def cerrar_turno_con_foto(id_turno, hora_salida, foto_bytes=None):
    """Cierra un turno con foto de salida - convierte hora Colombia a UTC"""
    import pytz
    
    tz_colombia = pytz.timezone('America/Bogota')
    
    # Convertir a UTC si no tiene zona horaria
    if hora_salida.tzinfo is None:
        hora_salida = tz_colombia.localize(hora_salida).astimezone(pytz.UTC)
    elif str(hora_salida.tzinfo) != 'UTC':
        hora_salida = hora_salida.astimezone(pytz.UTC)
    
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute(
            """UPDATE turnos SET hora_salida = %s, foto_salida = %s WHERE id_turno = %s""",
            (hora_salida, psycopg2.Binary(foto_bytes) if foto_bytes else None, id_turno)
        )
        conn.commit()
        return True, None
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        cur.close()
        conn.close()


# ==================== FUNCIONES DE DESCUENTOS DE NÓMINA ====================

def insert_descuento_nomina(id_empleado, tipo_descuento, detalle, valor, fecha=None):
    """Inserta un nuevo descuento de nómina"""
    from datetime import date
    
    conn = get_connection()
    cur = conn.cursor()
    
    if fecha is None:
        fecha = date.today()
    
    try:
        cur.execute(
            """INSERT INTO descuentos_nomina (id_empleado, tipo_descuento, detalle, valor, fecha)
               VALUES (%s, %s, %s, %s, %s) RETURNING id_descuento""",
            (id_empleado, tipo_descuento, detalle, valor, fecha)
        )
        id_descuento = cur.fetchone()[0]
        conn.commit()
        return id_descuento, None
    except Exception as e:
        conn.rollback()
        return None, str(e)
    finally:
        cur.close()
        conn.close()


def get_descuentos_nomina(fecha_inicio=None, fecha_fin=None, id_empleado=None, id_sede=None):
    """Obtiene los descuentos de nómina con filtros"""
    conn = get_connection()
    cur = conn.cursor()
    
    query = """
        SELECT 
            d.id_descuento,
            d.id_empleado,
            e.nombre_empleado,
            e.cedula_empleado,
            COALESCE(s.nombre_sede, 'Sin Sede') as nombre_sede,
            d.tipo_descuento,
            d.detalle,
            d.valor,
            d.fecha,
            d.create_at
        FROM descuentos_nomina d
        INNER JOIN empleados e ON d.id_empleado = e.id_empleado
        LEFT JOIN sedes s ON e.id_sede = s.id_sede
        WHERE 1=1
    """
    
    params = []
    
    if fecha_inicio:
        query += " AND d.fecha >= %s"
        params.append(fecha_inicio)
    
    if fecha_fin:
        query += " AND d.fecha <= %s"
        params.append(fecha_fin)
    
    if id_empleado:
        query += " AND d.id_empleado = %s"
        params.append(id_empleado)
    
    if id_sede:
        query += " AND e.id_sede = %s"
        params.append(id_sede)
    
    query += " ORDER BY d.fecha DESC, d.create_at DESC"
    
    cur.execute(query, params)
    results = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return [{
        'id_descuento': r[0],
        'id_empleado': r[1],
        'nombre_empleado': r[2],
        'cedula_empleado': r[3],
        'nombre_sede': r[4],
        'tipo_descuento': r[5],
        'detalle': r[6],
        'valor': float(r[7]) if r[7] else 0,
        'fecha': r[8],
        'create_at': r[9]
    } for r in results]


def get_resumen_descuentos_por_empleado(fecha_inicio=None, fecha_fin=None, id_sede=None):
    """Obtiene el resumen de descuentos por empleado"""
    conn = get_connection()
    cur = conn.cursor()
    
    query = """
        SELECT 
            e.id_empleado,
            e.nombre_empleado,
            COALESCE(s.nombre_sede, 'Sin Sede') as nombre_sede,
            COUNT(d.id_descuento) as total_descuentos,
            SUM(d.valor) as total_valor
        FROM empleados e
        INNER JOIN descuentos_nomina d ON e.id_empleado = d.id_empleado
        LEFT JOIN sedes s ON e.id_sede = s.id_sede
        WHERE 1=1
    """
    
    params = []
    
    if fecha_inicio:
        query += " AND d.fecha >= %s"
        params.append(fecha_inicio)
    
    if fecha_fin:
        query += " AND d.fecha <= %s"
        params.append(fecha_fin)
    
    if id_sede:
        query += " AND e.id_sede = %s"
        params.append(id_sede)
    
    query += """
        GROUP BY e.id_empleado, e.nombre_empleado, s.nombre_sede
        HAVING SUM(d.valor) > 0
        ORDER BY total_valor DESC
    """
    
    cur.execute(query, params)
    results = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return [{
        'id_empleado': r[0],
        'nombre_empleado': r[1],
        'nombre_sede': r[2],
        'total_descuentos': r[3] or 0,
        'total_valor': float(r[4]) if r[4] else 0
    } for r in results]


def delete_descuento_nomina(id_descuento):
    """Elimina un descuento de nómina"""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("DELETE FROM descuentos_nomina WHERE id_descuento = %s", (id_descuento,))
        conn.commit()
        return True, None
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        cur.close()
        conn.close()


def get_empleados_con_turno_abierto(id_sede=None):
    """Obtiene los empleados que tienen turno abierto (sin hora de salida)
    
    Args:
        id_sede: Si se proporciona, filtra solo los empleados de esa sede
    """
    conn = get_connection()
    cur = conn.cursor()
    
    if id_sede:
        cur.execute("""
            SELECT DISTINCT
                e.id_empleado,
                e.nombre_empleado,
                e.cedula_empleado,
                COALESCE(s.nombre_sede, 'Sin Sede') as nombre_sede
            FROM empleados e
            INNER JOIN turnos t ON e.id_empleado = t.id_empleado
            LEFT JOIN sedes s ON e.id_sede = s.id_sede
            WHERE t.hora_salida IS NULL
              AND e.id_sede = %s
            ORDER BY e.nombre_empleado
        """, (id_sede,))
    else:
        cur.execute("""
            SELECT DISTINCT
                e.id_empleado,
                e.nombre_empleado,
                e.cedula_empleado,
                COALESCE(s.nombre_sede, 'Sin Sede') as nombre_sede
            FROM empleados e
            INNER JOIN turnos t ON e.id_empleado = t.id_empleado
            LEFT JOIN sedes s ON e.id_sede = s.id_sede
            WHERE t.hora_salida IS NULL
            ORDER BY e.nombre_empleado
        """)
    results = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return [{
        'id_empleado': r[0],
        'nombre_empleado': r[1],
        'cedula_empleado': r[2],
        'nombre_sede': r[3]
    } for r in results]


# ==================== FUNCIONES DE CONFIGURACIÓN NÓMINA ====================

def get_configuracion_nomina(nombre_config=None):
    """Obtiene la configuración de nómina"""
    conn = get_connection()
    cur = conn.cursor()
    
    if nombre_config:
        cur.execute("""
            SELECT id_config, nombre_config, valor_config, descripcion, activo
            FROM configuracion_nomina
            WHERE nombre_config = %s AND activo = TRUE
        """, (nombre_config,))
        result = cur.fetchone()
        cur.close()
        conn.close()
        
        if result:
            return {
                'id_config': result[0],
                'nombre_config': result[1],
                'valor_config': float(result[2]),
                'descripcion': result[3],
                'activo': result[4]
            }
        return None
    else:
        cur.execute("""
            SELECT id_config, nombre_config, valor_config, descripcion, activo
            FROM configuracion_nomina
            WHERE activo = TRUE
            ORDER BY nombre_config
        """)
        results = cur.fetchall()
        cur.close()
        conn.close()
        
        return [{
            'id_config': r[0],
            'nombre_config': r[1],
            'valor_config': float(r[2]),
            'descripcion': r[3],
            'activo': r[4]
        } for r in results]


def update_configuracion_nomina(nombre_config, valor_config):
    """Actualiza una configuración de nómina"""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            UPDATE configuracion_nomina 
            SET valor_config = %s 
            WHERE nombre_config = %s
        """, (valor_config, nombre_config))
        conn.commit()
        return True, None
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        cur.close()
        conn.close()


# ==================== FUNCIONES DE LIQUIDACIÓN DE NÓMINA ====================

def get_turnos_pendientes_pago(fecha_inicio, fecha_fin, id_empleado=None):
    """Obtiene los turnos cerrados que no han sido pagados en un rango de fechas"""
    conn = get_connection()
    cur = conn.cursor()
    
    query = """
        SELECT 
            t.id_turno,
            t.id_empleado,
            e.nombre_empleado,
            e.cedula_empleado,
            e.salario_dia,
            COALESCE(s.nombre_sede, 'Sin Sede') as nombre_sede,
            DATE(t.hora_inicio AT TIME ZONE 'America/Bogota') as fecha,
            t.hora_inicio,
            t.hora_salida,
            COALESCE(th.total_horas, 0) as total_horas,
            COALESCE(he.total_horas_extra, 0) as horas_extra
        FROM turnos t
        INNER JOIN empleados e ON t.id_empleado = e.id_empleado
        LEFT JOIN sedes s ON e.id_sede = s.id_sede
        LEFT JOIN total_horas th ON t.id_turno = th.id_turno
        LEFT JOIN horas_extra he ON t.id_turno = he.id_turno
        WHERE t.hora_salida IS NOT NULL
          AND (t.pagado = FALSE OR t.pagado IS NULL)
          AND DATE(t.hora_inicio AT TIME ZONE 'America/Bogota') BETWEEN %s AND %s
    """
    
    params = [fecha_inicio, fecha_fin]
    
    if id_empleado:
        query += " AND t.id_empleado = %s"
        params.append(id_empleado)
    
    query += " ORDER BY e.nombre_empleado, t.hora_inicio"
    
    cur.execute(query, params)
    results = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return [{
        'id_turno': r[0],
        'id_empleado': r[1],
        'nombre_empleado': r[2],
        'cedula_empleado': r[3],
        'salario_dia': r[4] or 0,
        'nombre_sede': r[5],
        'fecha': r[6],
        'hora_inicio': r[7],
        'hora_salida': r[8],
        'total_horas': float(r[9]) if r[9] else 0,
        'horas_extra': float(r[10]) if r[10] else 0
    } for r in results]


def get_descuentos_pendientes_pago(fecha_inicio, fecha_fin, id_empleado=None):
    """Obtiene los descuentos que no han sido incluidos en una liquidación"""
    conn = get_connection()
    cur = conn.cursor()
    
    query = """
        SELECT 
            d.id_descuento,
            d.id_empleado,
            e.nombre_empleado,
            d.tipo_descuento,
            d.detalle,
            d.valor,
            d.fecha
        FROM descuentos_nomina d
        INNER JOIN empleados e ON d.id_empleado = e.id_empleado
        WHERE (d.pagado = FALSE OR d.pagado IS NULL)
          AND d.fecha BETWEEN %s AND %s
    """
    
    params = [fecha_inicio, fecha_fin]
    
    if id_empleado:
        query += " AND d.id_empleado = %s"
        params.append(id_empleado)
    
    query += " ORDER BY e.nombre_empleado, d.fecha"
    
    cur.execute(query, params)
    results = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return [{
        'id_descuento': r[0],
        'id_empleado': r[1],
        'nombre_empleado': r[2],
        'tipo_descuento': r[3],
        'detalle': r[4],
        'valor': float(r[5]) if r[5] else 0,
        'fecha': r[6]
    } for r in results]


def crear_liquidacion(fecha_inicio, fecha_fin, detalles_empleados, observaciones=None):
    """
    Crea una liquidación de nómina completa
    detalles_empleados: lista de diccionarios con los datos de cada empleado
    """
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # Calcular totales generales
        total_bruto = sum(d.get('subtotal_bruto', 0) for d in detalles_empleados)
        total_descuentos = sum(d.get('total_descuentos', 0) for d in detalles_empleados)
        total_neto = sum(d.get('total_neto', 0) for d in detalles_empleados)
        
        # Insertar la liquidación principal
        cur.execute("""
            INSERT INTO liquidaciones_nomina 
            (fecha_inicio, fecha_fin, total_bruto, total_descuentos, total_neto, estado, observaciones)
            VALUES (%s, %s, %s, %s, %s, 'pendiente', %s)
            RETURNING id_liquidacion
        """, (fecha_inicio, fecha_fin, total_bruto, total_descuentos, total_neto, observaciones))
        
        id_liquidacion = cur.fetchone()[0]
        
        # Insertar detalle por cada empleado
        for detalle in detalles_empleados:
            cur.execute("""
                INSERT INTO detalle_liquidacion (
                    id_liquidacion, id_empleado, dias_trabajados, horas_trabajadas,
                    horas_extra, salario_base, valor_horas_extra, subtotal_bruto,
                    descuento_comida_bruto, porcentaje_descuento_comida, descuento_comida_neto,
                    otros_descuentos, total_descuentos, total_neto, ajuste_manual, observaciones
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                id_liquidacion,
                detalle['id_empleado'],
                detalle.get('dias_trabajados', 0),
                detalle.get('horas_trabajadas', 0),
                detalle.get('horas_extra', 0),
                detalle.get('salario_base', 0),
                detalle.get('valor_horas_extra', 0),
                detalle.get('subtotal_bruto', 0),
                detalle.get('descuento_comida_bruto', 0),
                detalle.get('porcentaje_descuento_comida', 0),
                detalle.get('descuento_comida_neto', 0),
                detalle.get('otros_descuentos', 0),
                detalle.get('total_descuentos', 0),
                detalle.get('total_neto', 0),
                detalle.get('ajuste_manual', 0),
                detalle.get('observaciones', '')
            ))
            
            # Marcar turnos como pagados
            turnos_ids = detalle.get('turnos_ids', [])
            if turnos_ids:
                cur.execute("""
                    UPDATE turnos 
                    SET pagado = TRUE, id_liquidacion = %s 
                    WHERE id_turno = ANY(%s)
                """, (id_liquidacion, turnos_ids))
            
            # Marcar descuentos como pagados
            descuentos_ids = detalle.get('descuentos_ids', [])
            if descuentos_ids:
                cur.execute("""
                    UPDATE descuentos_nomina 
                    SET pagado = TRUE, id_liquidacion = %s 
                    WHERE id_descuento = ANY(%s)
                """, (id_liquidacion, descuentos_ids))
            
            # Marcar horas extra como pagadas
            horas_extra_ids = detalle.get('horas_extra_ids', [])
            if horas_extra_ids:
                cur.execute("""
                    UPDATE horas_extra 
                    SET pagado = TRUE, id_liquidacion = %s 
                    WHERE id = ANY(%s)
                """, (id_liquidacion, horas_extra_ids))
        
        conn.commit()
        return id_liquidacion, None
    except Exception as e:
        conn.rollback()
        return None, str(e)
    finally:
        cur.close()
        conn.close()


def get_liquidaciones(estado=None, fecha_inicio=None, fecha_fin=None):
    """Obtiene el listado de liquidaciones"""
    conn = get_connection()
    cur = conn.cursor()
    
    query = """
        SELECT 
            l.id_liquidacion,
            l.fecha_liquidacion,
            l.fecha_inicio,
            l.fecha_fin,
            l.total_bruto,
            l.total_descuentos,
            l.total_neto,
            l.estado,
            l.observaciones,
            (SELECT COUNT(*) FROM detalle_liquidacion WHERE id_liquidacion = l.id_liquidacion) as num_empleados
        FROM liquidaciones_nomina l
        WHERE 1=1
    """
    
    params = []
    
    if estado:
        query += " AND l.estado = %s"
        params.append(estado)
    
    if fecha_inicio and fecha_fin:
        query += " AND l.fecha_liquidacion BETWEEN %s AND %s"
        params.extend([fecha_inicio, fecha_fin])
    
    query += " ORDER BY l.fecha_liquidacion DESC"
    
    cur.execute(query, params)
    results = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return [{
        'id_liquidacion': r[0],
        'fecha_liquidacion': r[1],
        'fecha_inicio': r[2],
        'fecha_fin': r[3],
        'total_bruto': float(r[4]) if r[4] else 0,
        'total_descuentos': float(r[5]) if r[5] else 0,
        'total_neto': float(r[6]) if r[6] else 0,
        'estado': r[7],
        'observaciones': r[8],
        'num_empleados': r[9]
    } for r in results]


def get_detalle_liquidacion(id_liquidacion):
    """Obtiene el detalle de una liquidación por empleado"""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT 
            d.id_detalle,
            d.id_empleado,
            e.nombre_empleado,
            e.cedula_empleado,
            COALESCE(s.nombre_sede, 'Sin Sede') as nombre_sede,
            d.dias_trabajados,
            d.horas_trabajadas,
            d.horas_extra,
            d.salario_base,
            d.valor_horas_extra,
            d.subtotal_bruto,
            d.descuento_comida_bruto,
            d.porcentaje_descuento_comida,
            d.descuento_comida_neto,
            d.otros_descuentos,
            d.total_descuentos,
            d.total_neto,
            d.ajuste_manual,
            d.observaciones
        FROM detalle_liquidacion d
        INNER JOIN empleados e ON d.id_empleado = e.id_empleado
        LEFT JOIN sedes s ON e.id_sede = s.id_sede
        WHERE d.id_liquidacion = %s
        ORDER BY e.nombre_empleado
    """, (id_liquidacion,))
    
    results = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return [{
        'id_detalle': r[0],
        'id_empleado': r[1],
        'nombre_empleado': r[2],
        'cedula_empleado': r[3],
        'nombre_sede': r[4],
        'dias_trabajados': r[5],
        'horas_trabajadas': float(r[6]) if r[6] else 0,
        'horas_extra': float(r[7]) if r[7] else 0,
        'salario_base': float(r[8]) if r[8] else 0,
        'valor_horas_extra': float(r[9]) if r[9] else 0,
        'subtotal_bruto': float(r[10]) if r[10] else 0,
        'descuento_comida_bruto': float(r[11]) if r[11] else 0,
        'porcentaje_descuento_comida': float(r[12]) if r[12] else 0,
        'descuento_comida_neto': float(r[13]) if r[13] else 0,
        'otros_descuentos': float(r[14]) if r[14] else 0,
        'total_descuentos': float(r[15]) if r[15] else 0,
        'total_neto': float(r[16]) if r[16] else 0,
        'ajuste_manual': float(r[17]) if r[17] else 0,
        'observaciones': r[18]
    } for r in results]


def actualizar_estado_liquidacion(id_liquidacion, nuevo_estado):
    """Actualiza el estado de una liquidación (pendiente, pagado, anulado)"""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            UPDATE liquidaciones_nomina 
            SET estado = %s 
            WHERE id_liquidacion = %s
        """, (nuevo_estado, id_liquidacion))
        conn.commit()
        return True, None
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        cur.close()
        conn.close()


def anular_liquidacion(id_liquidacion):
    """Anula una liquidación y libera los turnos/descuentos para futuras liquidaciones"""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # Liberar turnos
        cur.execute("""
            UPDATE turnos 
            SET pagado = FALSE, id_liquidacion = NULL 
            WHERE id_liquidacion = %s
        """, (id_liquidacion,))
        
        # Liberar descuentos
        cur.execute("""
            UPDATE descuentos_nomina 
            SET pagado = FALSE, id_liquidacion = NULL 
            WHERE id_liquidacion = %s
        """, (id_liquidacion,))
        
        # Liberar horas extra
        cur.execute("""
            UPDATE horas_extra 
            SET pagado = FALSE, id_liquidacion = NULL 
            WHERE id_liquidacion = %s
        """, (id_liquidacion,))
        
        # Marcar como anulado
        cur.execute("""
            UPDATE liquidaciones_nomina 
            SET estado = 'anulado' 
            WHERE id_liquidacion = %s
        """, (id_liquidacion,))
        
        conn.commit()
        return True, None
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        cur.close()
        conn.close()


def eliminar_liquidacion(id_liquidacion):
    """Elimina permanentemente una liquidación y libera los turnos/descuentos"""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # Liberar turnos
        cur.execute("""
            UPDATE turnos 
            SET pagado = FALSE, id_liquidacion = NULL 
            WHERE id_liquidacion = %s
        """, (id_liquidacion,))
        
        # Liberar descuentos
        cur.execute("""
            UPDATE descuentos_nomina 
            SET pagado = FALSE, id_liquidacion = NULL 
            WHERE id_liquidacion = %s
        """, (id_liquidacion,))
        
        # Liberar horas extra
        cur.execute("""
            UPDATE horas_extra 
            SET pagado = FALSE, id_liquidacion = NULL 
            WHERE id_liquidacion = %s
        """, (id_liquidacion,))
        
        # Eliminar detalles (por CASCADE debería ser automático, pero por seguridad)
        cur.execute("""
            DELETE FROM detalle_liquidacion 
            WHERE id_liquidacion = %s
        """, (id_liquidacion,))
        
        # Eliminar liquidación
        cur.execute("""
            DELETE FROM liquidaciones_nomina 
            WHERE id_liquidacion = %s
        """, (id_liquidacion,))
        
        conn.commit()
        return True, None
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        cur.close()
        conn.close()


def actualizar_detalle_liquidacion(id_detalle, ajuste_manual, observaciones=None):
    """Actualiza el ajuste manual y observaciones de un detalle de liquidación"""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # Obtener datos actuales para recalcular
        cur.execute("""
            SELECT subtotal_bruto, total_descuentos, ajuste_manual 
            FROM detalle_liquidacion 
            WHERE id_detalle = %s
        """, (id_detalle,))
        result = cur.fetchone()
        
        if result:
            subtotal_bruto = float(result[0])
            total_descuentos = float(result[1])
            # Recalcular total neto con el nuevo ajuste
            total_neto = subtotal_bruto - total_descuentos + float(ajuste_manual)
            
            cur.execute("""
                UPDATE detalle_liquidacion 
                SET ajuste_manual = %s, total_neto = %s, observaciones = %s
                WHERE id_detalle = %s
            """, (ajuste_manual, total_neto, observaciones, id_detalle))
            
            # Recalcular totales de la liquidación
            cur.execute("""
                SELECT id_liquidacion FROM detalle_liquidacion WHERE id_detalle = %s
            """, (id_detalle,))
            id_liquidacion = cur.fetchone()[0]
            
            cur.execute("""
                UPDATE liquidaciones_nomina 
                SET total_neto = (
                    SELECT COALESCE(SUM(total_neto), 0) 
                    FROM detalle_liquidacion 
                    WHERE id_liquidacion = %s
                )
                WHERE id_liquidacion = %s
            """, (id_liquidacion, id_liquidacion))
            
            conn.commit()
            return True, None
        else:
            return False, "Detalle no encontrado"
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        cur.close()
        conn.close()


def get_horas_extra_pendientes_pago(fecha_inicio, fecha_fin, id_empleado=None):
    """Obtiene las horas extra no pagadas en un rango de fechas"""
    conn = get_connection()
    cur = conn.cursor()
    
    query = """
        SELECT 
            he.id,
            he.id_turno,
            t.id_empleado,
            e.nombre_empleado,
            he.total_horas_extra,
            th.fecha
        FROM horas_extra he
        INNER JOIN turnos t ON he.id_turno = t.id_turno
        INNER JOIN empleados e ON t.id_empleado = e.id_empleado
        INNER JOIN total_horas th ON he.id_hora = th.id
        WHERE (he.pagado = FALSE OR he.pagado IS NULL)
          AND th.fecha BETWEEN %s AND %s
    """
    
    params = [fecha_inicio, fecha_fin]
    
    if id_empleado:
        query += " AND t.id_empleado = %s"
        params.append(id_empleado)
    
    query += " ORDER BY e.nombre_empleado, th.fecha"
    
    cur.execute(query, params)
    results = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return [{
        'id': r[0],
        'id_turno': r[1],
        'id_empleado': r[2],
        'nombre_empleado': r[3],
        'total_horas_extra': float(r[4]) if r[4] else 0,
        'fecha': r[5]
    } for r in results]


# ==================== FUNCIONES DE PAGO DIARIO ====================

def get_turno_hoy_empleado(id_empleado):
    """Obtiene el turno de hoy de un empleado (cerrado, no pagado)"""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT 
            t.id_turno,
            t.hora_inicio,
            t.hora_salida,
            COALESCE(th.total_horas, 0) as total_horas,
            COALESCE(he.total_horas_extra, 0) as horas_extra,
            e.salario_dia
        FROM turnos t
        INNER JOIN empleados e ON t.id_empleado = e.id_empleado
        LEFT JOIN total_horas th ON t.id_turno = th.id_turno
        LEFT JOIN horas_extra he ON t.id_turno = he.id_turno
        WHERE t.id_empleado = %s
          AND t.hora_salida IS NOT NULL
          AND (t.pagado = FALSE OR t.pagado IS NULL)
          AND DATE(t.hora_inicio AT TIME ZONE 'America/Bogota') = (CURRENT_TIMESTAMP AT TIME ZONE 'America/Bogota')::DATE
        ORDER BY t.hora_inicio DESC
        LIMIT 1
    """, (id_empleado,))
    
    result = cur.fetchone()
    cur.close()
    conn.close()
    
    if result:
        return {
            'id_turno': result[0],
            'hora_inicio': result[1],
            'hora_salida': result[2],
            'total_horas': float(result[3]) if result[3] else 0,
            'horas_extra': float(result[4]) if result[4] else 0,
            'salario_dia': result[5] or 0
        }
    return None


def get_consumos_hoy_empleado(id_empleado):
    """Obtiene los consumos de hoy de un empleado (no pagados)"""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT 
            d.id_descuento,
            d.tipo_descuento,
            d.detalle,
            d.valor,
            d.fecha
        FROM descuentos_nomina d
        WHERE d.id_empleado = %s
          AND (d.pagado = FALSE OR d.pagado IS NULL)
          AND d.fecha = CURRENT_DATE
        ORDER BY d.create_at
    """, (id_empleado,))
    
    results = cur.fetchall()
    cur.close()
    conn.close()
    
    return [{
        'id_descuento': r[0],
        'tipo_descuento': r[1],
        'detalle': r[2],
        'valor': float(r[3]) if r[3] else 0,
        'fecha': r[4]
    } for r in results]


def get_consumos_cuenta_empleado(id_empleado):
    """Obtiene los consumos a cuenta pendientes de un empleado"""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT 
            id_consumo_cuenta,
            valor,
            descripcion,
            fecha_registro
        FROM consumos_cuenta
        WHERE id_empleado = %s
          AND pagado = FALSE
        ORDER BY fecha_registro
    """, (id_empleado,))
    
    results = cur.fetchall()
    cur.close()
    conn.close()
    
    return [{
        'id_consumo_cuenta': r[0],
        'valor': float(r[1]) if r[1] else 0,
        'descripcion': r[2],
        'fecha_registro': r[3]
    } for r in results]


def agregar_consumo_cuenta(id_empleado, id_descuento_original, valor, descripcion):
    """Agrega un consumo a la cuenta del empleado (sin descontar aún)"""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            INSERT INTO consumos_cuenta (id_empleado, id_descuento_original, valor, descripcion)
            VALUES (%s, %s, %s, %s)
            RETURNING id_consumo_cuenta
        """, (id_empleado, id_descuento_original, valor, descripcion))
        
        id_consumo = cur.fetchone()[0]
        
        # Si viene de un descuento, marcarlo como procesado
        if id_descuento_original:
            cur.execute("""
                UPDATE descuentos_nomina SET pagado = TRUE WHERE id_descuento = %s
            """, (id_descuento_original,))
        
        conn.commit()
        return id_consumo, None
    except Exception as e:
        conn.rollback()
        return None, str(e)
    finally:
        cur.close()
        conn.close()


def crear_pago_diario(id_empleado, id_turno, datos_pago, firma_bytes=None, foto_bytes=None):
    """Crea un registro de pago diario con firma y foto opcionales"""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            INSERT INTO pagos_diarios (
                id_empleado, id_turno, salario_dia, horas_trabajadas,
                horas_extra, valor_horas_extra, subtotal_bruto,
                consumos_descontados, consumos_a_cuenta, otros_descuentos,
                total_descuentos, total_neto, firma_empleado, foto_pago, observaciones
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id_pago
        """, (
            id_empleado,
            id_turno,
            datos_pago.get('salario_dia', 0),
            datos_pago.get('horas_trabajadas', 0),
            datos_pago.get('horas_extra', 0),
            datos_pago.get('valor_horas_extra', 0),
            datos_pago.get('subtotal_bruto', 0),
            datos_pago.get('consumos_descontados', 0),
            datos_pago.get('consumos_a_cuenta', 0),
            datos_pago.get('otros_descuentos', 0),
            datos_pago.get('total_descuentos', 0),
            datos_pago.get('total_neto', 0),
            firma_bytes,
            foto_bytes,
            datos_pago.get('observaciones', '')
        ))
        
        id_pago = cur.fetchone()[0]
        
        # Marcar turno como pagado
        if id_turno:
            cur.execute("""
                UPDATE turnos SET pagado = TRUE WHERE id_turno = %s
            """, (id_turno,))
        
        # Marcar descuentos como pagados
        descuentos_ids = datos_pago.get('descuentos_ids', [])
        if descuentos_ids:
            cur.execute("""
                UPDATE descuentos_nomina SET pagado = TRUE WHERE id_descuento = ANY(%s)
            """, (descuentos_ids,))
        
        # Marcar consumos a cuenta como pagados
        consumos_cuenta_ids = datos_pago.get('consumos_cuenta_ids', [])
        if consumos_cuenta_ids:
            cur.execute("""
                UPDATE consumos_cuenta SET pagado = TRUE, id_pago_diario = %s 
                WHERE id_consumo_cuenta = ANY(%s)
            """, (id_pago, consumos_cuenta_ids))
        
        conn.commit()
        return id_pago, None
    except Exception as e:
        conn.rollback()
        return None, str(e)
    finally:
        cur.close()
        conn.close()


def get_pagos_diarios(id_empleado=None, fecha_inicio=None, fecha_fin=None):
    """Obtiene historial de pagos diarios"""
    conn = get_connection()
    cur = conn.cursor()
    
    query = """
        SELECT 
            p.id_pago,
            p.id_empleado,
            e.nombre_empleado,
            e.cedula_empleado,
            COALESCE(s.nombre_sede, 'Sin Sede') as nombre_sede,
            p.fecha_pago,
            p.salario_dia,
            p.horas_trabajadas,
            p.horas_extra,
            p.subtotal_bruto,
            p.total_descuentos,
            p.total_neto,
            p.firma_empleado IS NOT NULL as tiene_firma,
            p.observaciones
        FROM pagos_diarios p
        INNER JOIN empleados e ON p.id_empleado = e.id_empleado
        LEFT JOIN sedes s ON e.id_sede = s.id_sede
        WHERE 1=1
    """
    
    params = []
    
    if id_empleado:
        query += " AND p.id_empleado = %s"
        params.append(id_empleado)
    
    if fecha_inicio and fecha_fin:
        query += " AND p.fecha_pago BETWEEN %s AND %s"
        params.extend([fecha_inicio, fecha_fin])
    
    query += " ORDER BY p.fecha_pago DESC, p.create_at DESC"
    
    cur.execute(query, params)
    results = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return [{
        'id_pago': r[0],
        'id_empleado': r[1],
        'nombre_empleado': r[2],
        'cedula_empleado': r[3],
        'nombre_sede': r[4],
        'fecha_pago': r[5],
        'salario_dia': float(r[6]) if r[6] else 0,
        'horas_trabajadas': float(r[7]) if r[7] else 0,
        'horas_extra': float(r[8]) if r[8] else 0,
        'subtotal_bruto': float(r[9]) if r[9] else 0,
        'total_descuentos': float(r[10]) if r[10] else 0,
        'total_neto': float(r[11]) if r[11] else 0,
        'tiene_firma': r[12],
        'observaciones': r[13]
    } for r in results]


def get_empleados_turno_cerrado_hoy(id_sede=None):
    """Obtiene empleados con turno cerrado hoy pendiente de pago, opcionalmente filtrado por sede"""
    conn = get_connection()
    cur = conn.cursor()
    
    base_query = """
        SELECT DISTINCT
            e.id_empleado,
            e.nombre_empleado,
            e.cedula_empleado,
            e.salario_dia,
            COALESCE(s.nombre_sede, 'Sin Sede') as nombre_sede,
            t.id_turno,
            t.hora_inicio,
            t.hora_salida,
            COALESCE(th.total_horas, 0) as total_horas
        FROM empleados e
        INNER JOIN turnos t ON e.id_empleado = t.id_empleado
        LEFT JOIN sedes s ON e.id_sede = s.id_sede
        LEFT JOIN total_horas th ON t.id_turno = th.id_turno
        WHERE t.hora_salida IS NOT NULL
          AND (t.pagado = FALSE OR t.pagado IS NULL)
          AND DATE(t.hora_inicio AT TIME ZONE 'America/Bogota') = (CURRENT_TIMESTAMP AT TIME ZONE 'America/Bogota')::DATE
    """
    
    if id_sede:
        base_query += " AND e.id_sede = %s"
        base_query += " ORDER BY e.nombre_empleado"
        cur.execute(base_query, (id_sede,))
    else:
        base_query += " ORDER BY e.nombre_empleado"
        cur.execute(base_query)
    
    results = cur.fetchall()
    cur.close()
    conn.close()
    
    return [{
        'id_empleado': r[0],
        'nombre_empleado': r[1],
        'cedula_empleado': r[2],
        'salario_dia': r[3] or 0,
        'nombre_sede': r[4],
        'id_turno': r[5],
        'hora_inicio': r[6],
        'hora_salida': r[7],
        'total_horas': float(r[8]) if r[8] else 0
    } for r in results]


def eliminar_pago_diario(id_pago):
    """Elimina un pago diario y revierte el estado de turno y descuentos"""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # Obtener info del pago para revertir
        cur.execute("""
            SELECT id_turno FROM pagos_diarios WHERE id_pago = %s
        """, (id_pago,))
        
        result = cur.fetchone()
        if not result:
            return False, "Pago no encontrado"
        
        id_turno = result[0]
        
        # Revertir turno a no pagado
        if id_turno:
            cur.execute("""
                UPDATE turnos SET pagado = FALSE WHERE id_turno = %s
            """, (id_turno,))
        
        # Revertir consumos a cuenta asociados
        cur.execute("""
            UPDATE consumos_cuenta SET pagado = FALSE, id_pago_diario = NULL 
            WHERE id_pago_diario = %s
        """, (id_pago,))
        
        # Eliminar el pago
        cur.execute("""
            DELETE FROM pagos_diarios WHERE id_pago = %s
        """, (id_pago,))
        
        conn.commit()
        return True, None
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        cur.close()
        conn.close()


def actualizar_pago_diario(id_pago, datos):
    """Actualiza un pago diario existente"""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            UPDATE pagos_diarios SET
                total_neto = %s,
                observaciones = %s
            WHERE id_pago = %s
        """, (
            datos.get('total_neto'),
            datos.get('observaciones', ''),
            id_pago
        ))
        
        conn.commit()
        return True, None
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        cur.close()
        conn.close()


def get_pago_diario_detalle(id_pago):
    """Obtiene el detalle completo de un pago diario incluyendo firma y foto"""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT 
            p.id_pago,
            p.id_empleado,
            e.nombre_empleado,
            e.cedula_empleado,
            COALESCE(s.nombre_sede, 'Sin Sede') as nombre_sede,
            p.id_turno,
            p.fecha_pago,
            p.salario_dia,
            p.horas_trabajadas,
            p.horas_extra,
            p.valor_horas_extra,
            p.subtotal_bruto,
            p.consumos_descontados,
            p.consumos_a_cuenta,
            p.otros_descuentos,
            p.total_descuentos,
            p.total_neto,
            p.firma_empleado,
            p.foto_pago,
            p.observaciones,
            p.create_at
        FROM pagos_diarios p
        INNER JOIN empleados e ON p.id_empleado = e.id_empleado
        LEFT JOIN sedes s ON e.id_sede = s.id_sede
        WHERE p.id_pago = %s
    """, (id_pago,))
    
    r = cur.fetchone()
    cur.close()
    conn.close()
    
    if not r:
        return None
    
    return {
        'id_pago': r[0],
        'id_empleado': r[1],
        'nombre_empleado': r[2],
        'cedula_empleado': r[3],
        'nombre_sede': r[4],
        'id_turno': r[5],
        'fecha_pago': r[6],
        'salario_dia': float(r[7]) if r[7] else 0,
        'horas_trabajadas': float(r[8]) if r[8] else 0,
        'horas_extra': float(r[9]) if r[9] else 0,
        'valor_horas_extra': float(r[10]) if r[10] else 0,
        'subtotal_bruto': float(r[11]) if r[11] else 0,
        'consumos_descontados': float(r[12]) if r[12] else 0,
        'consumos_a_cuenta': float(r[13]) if r[13] else 0,
        'otros_descuentos': float(r[14]) if r[14] else 0,
        'total_descuentos': float(r[15]) if r[15] else 0,
        'total_neto': float(r[16]) if r[16] else 0,
        'firma_empleado': r[17],
        'foto_pago': r[18],
        'observaciones': r[19],
        'create_at': r[20]
    }


# ==================== FUNCIONES DASHBOARD ====================

def get_dashboard_resumen_general():
    """Obtiene el resumen general del negocio para el dashboard"""
    conn = get_connection()
    cur = conn.cursor()
    
    # Total empleados
    cur.execute("SELECT COUNT(*) FROM empleados")
    total_empleados = cur.fetchone()[0]
    
    # Empleados con turno abierto hoy
    cur.execute("""
        SELECT COUNT(DISTINCT e.id_empleado)
        FROM empleados e
        INNER JOIN turnos t ON e.id_empleado = t.id_empleado
        WHERE t.hora_salida IS NULL
          AND DATE(t.hora_inicio AT TIME ZONE 'America/Bogota') = (CURRENT_TIMESTAMP AT TIME ZONE 'America/Bogota')::DATE
    """)
    empleados_trabajando = cur.fetchone()[0]
    
    # Turnos pendientes de pago
    cur.execute("""
        SELECT COUNT(*) FROM turnos 
        WHERE hora_salida IS NOT NULL 
          AND (pagado = FALSE OR pagado IS NULL)
    """)
    turnos_pendientes_pago = cur.fetchone()[0]
    
    # Total nómina pagada este mes (desde liquidaciones)
    cur.execute("""
        SELECT COALESCE(SUM(total_neto), 0)
        FROM liquidaciones_nomina
        WHERE EXTRACT(MONTH FROM fecha_liquidacion) = EXTRACT(MONTH FROM CURRENT_DATE)
          AND EXTRACT(YEAR FROM fecha_liquidacion) = EXTRACT(YEAR FROM CURRENT_DATE)
          AND estado = 'pagada'
    """)
    nomina_mes_total = float(cur.fetchone()[0])
    
    cur.close()
    conn.close()
    
    return {
        'total_empleados': total_empleados,
        'empleados_trabajando': empleados_trabajando,
        'turnos_pendientes_pago': turnos_pendientes_pago,
        'nomina_mes_total': nomina_mes_total
    }


def get_dashboard_consumos_estadisticas(fecha_inicio=None, fecha_fin=None):
    """Obtiene estadísticas de consumos para el dashboard"""
    conn = get_connection()
    cur = conn.cursor()
    
    # Filtros de fecha
    filtro_fecha = ""
    params = []
    if fecha_inicio and fecha_fin:
        filtro_fecha = "AND d.fecha BETWEEN %s AND %s"
        params = [fecha_inicio, fecha_fin]
    
    # Total consumos por tipo
    cur.execute(f"""
        SELECT 
            d.tipo_descuento,
            COUNT(*) as cantidad,
            COALESCE(SUM(d.valor), 0) as total_valor
        FROM descuentos_nomina d
        WHERE 1=1 {filtro_fecha}
        GROUP BY d.tipo_descuento
        ORDER BY total_valor DESC
    """, params)
    
    consumos_por_tipo = [{
        'tipo': r[0],
        'cantidad': r[1],
        'total': float(r[2])
    } for r in cur.fetchall()]
    
    # Total consumos alimento (para calcular subsidio del 10%)
    cur.execute(f"""
        SELECT COALESCE(SUM(d.valor), 0)
        FROM descuentos_nomina d
        WHERE d.tipo_descuento = 'Consumo Alimento' {filtro_fecha.replace('AND', 'AND ')}
    """, params)
    total_consumo_alimentos = float(cur.fetchone()[0])
    
    # Obtener configuración del porcentaje
    cur.execute("""
        SELECT COALESCE(valor_config, 10) FROM configuracion_nomina 
        WHERE nombre_config = 'descuento_comida_porcentaje' AND activo = TRUE
    """)
    result = cur.fetchone()
    porcentaje_subsidio = float(result[0]) if result else 10
    
    gasto_subsidio_comida = total_consumo_alimentos * (porcentaje_subsidio / 100)
    
    # Consumos pendientes vs pagados
    cur.execute(f"""
        SELECT 
            CASE WHEN d.pagado = TRUE THEN 'Pagado' ELSE 'Pendiente' END as estado,
            COUNT(*) as cantidad,
            COALESCE(SUM(d.valor), 0) as total
        FROM descuentos_nomina d
        WHERE 1=1 {filtro_fecha}
        GROUP BY d.pagado
    """, params)
    
    consumos_estado = [{
        'estado': r[0],
        'cantidad': r[1],
        'total': float(r[2])
    } for r in cur.fetchall()]
    
    cur.close()
    conn.close()
    
    return {
        'consumos_por_tipo': consumos_por_tipo,
        'total_consumo_alimentos': total_consumo_alimentos,
        'porcentaje_subsidio': porcentaje_subsidio,
        'gasto_subsidio_comida': gasto_subsidio_comida,
        'consumos_estado': consumos_estado
    }


def get_dashboard_gastos_empleados(fecha_inicio=None, fecha_fin=None):
    """Obtiene el detalle de gastos por empleado"""
    conn = get_connection()
    cur = conn.cursor()
    
    filtro_fecha_turnos = ""
    params_turnos = []
    
    if fecha_inicio and fecha_fin:
        filtro_fecha_turnos = "AND DATE(t.hora_inicio) BETWEEN %s AND %s"
        params_turnos = [fecha_inicio, fecha_fin]
    
    # Gastos por liquidaciones por empleado
    cur.execute("""
        SELECT 
            e.id_empleado,
            e.nombre_empleado,
            COALESCE(s.nombre_sede, 'Sin Sede') as sede,
            COUNT(d.id_detalle) as pagos_realizados,
            COALESCE(SUM(d.total_neto), 0) as total_pagado,
            COALESCE(SUM(d.horas_trabajadas), 0) as horas_trabajadas,
            COALESCE(SUM(d.total_descuentos), 0) as descuentos_aplicados
        FROM empleados e
        LEFT JOIN detalle_liquidacion d ON e.id_empleado = d.id_empleado
        LEFT JOIN sedes s ON e.id_sede = s.id_sede
        GROUP BY e.id_empleado, e.nombre_empleado, s.nombre_sede
        ORDER BY total_pagado DESC
    """)
    
    gastos_empleados = [{
        'id_empleado': r[0],
        'nombre': r[1],
        'sede': r[2],
        'pagos_realizados': r[3],
        'total_pagado': float(r[4]) if r[4] else 0,
        'horas_trabajadas': float(r[5]) if r[5] else 0,
        'descuentos_aplicados': float(r[6]) if r[6] else 0
    } for r in cur.fetchall()]
    
    # Turnos pendientes de pago por empleado
    cur.execute(f"""
        SELECT 
            e.id_empleado,
            e.nombre_empleado,
            COUNT(t.id_turno) as turnos_pendientes,
            COALESCE(SUM(th.total_horas), 0) as horas_pendientes,
            COALESCE(SUM(e.salario_dia), 0) as salario_pendiente_estimado
        FROM empleados e
        INNER JOIN turnos t ON e.id_empleado = t.id_empleado
        LEFT JOIN total_horas th ON t.id_turno = th.id_turno
        WHERE t.hora_salida IS NOT NULL
          AND (t.pagado = FALSE OR t.pagado IS NULL)
          {filtro_fecha_turnos}
        GROUP BY e.id_empleado, e.nombre_empleado
        ORDER BY salario_pendiente_estimado DESC
    """, params_turnos if params_turnos else None)
    
    pendientes_empleados = [{
        'id_empleado': r[0],
        'nombre': r[1],
        'turnos_pendientes': r[2],
        'horas_pendientes': float(r[3]) if r[3] else 0,
        'salario_pendiente': float(r[4]) if r[4] else 0
    } for r in cur.fetchall()]
    
    cur.close()
    conn.close()
    
    return {
        'gastos_empleados': gastos_empleados,
        'pendientes_empleados': pendientes_empleados
    }


def get_dashboard_cuentas_pagar():
    """Obtiene las cuentas por pagar (descuentos pendientes)"""
    conn = get_connection()
    cur = conn.cursor()
    
    # Descuentos pendientes por empleado
    cur.execute("""
        SELECT 
            e.id_empleado,
            e.nombre_empleado,
            COALESCE(s.nombre_sede, 'Sin Sede') as sede,
            COUNT(d.id_descuento) as cantidad_descuentos,
            COALESCE(SUM(d.valor), 0) as total_cuenta
        FROM empleados e
        INNER JOIN descuentos_nomina d ON e.id_empleado = d.id_empleado
        LEFT JOIN sedes s ON e.id_sede = s.id_sede
        WHERE d.pagado = FALSE
        GROUP BY e.id_empleado, e.nombre_empleado, s.nombre_sede
        ORDER BY total_cuenta DESC
    """)
    
    cuentas_empleados = [{
        'id_empleado': r[0],
        'nombre': r[1],
        'sede': r[2],
        'cantidad': r[3],
        'total': float(r[4]) if r[4] else 0
    } for r in cur.fetchall()]
    
    # Total general
    cur.execute("""
        SELECT COALESCE(SUM(valor), 0) FROM descuentos_nomina WHERE pagado = FALSE
    """)
    total_cuentas = float(cur.fetchone()[0])
    
    cur.close()
    conn.close()
    
    return {
        'cuentas_empleados': cuentas_empleados,
        'total_cuentas': total_cuentas
    }


def get_dashboard_pagos_periodo(fecha_inicio=None, fecha_fin=None):
    """Obtiene resumen de pagos en un período"""
    conn = get_connection()
    cur = conn.cursor()
    
    params = []
    filtro = ""
    if fecha_inicio and fecha_fin:
        filtro = "WHERE fecha_liquidacion BETWEEN %s AND %s"
        params = [fecha_inicio, fecha_fin]
    
    # Liquidaciones (en lugar de pagos_diarios)
    cur.execute(f"""
        SELECT 
            COUNT(*) as total_pagos,
            COALESCE(SUM(total_neto), 0) as total_pagado,
            COALESCE(SUM(total_descuentos), 0) as total_descuentos,
            COALESCE(SUM(total_bruto), 0) as total_bruto,
            COALESCE(AVG(total_neto), 0) as promedio_pago
        FROM liquidaciones_nomina
        {filtro}
    """, params if params else None)
    
    r = cur.fetchone()
    pagos_diarios = {
        'total_pagos': r[0] if r[0] else 0,
        'total_pagado': float(r[1]) if r[1] else 0,
        'total_descuentos': float(r[2]) if r[2] else 0,
        'total_bruto': float(r[3]) if r[3] else 0,
        'promedio_pago': float(r[4]) if r[4] else 0
    }
    
    # Pagos por día de la semana
    cur.execute(f"""
        SELECT 
            EXTRACT(DOW FROM fecha_liquidacion) as dia_semana,
            COUNT(*) as cantidad,
            COALESCE(SUM(total_neto), 0) as total
        FROM liquidaciones_nomina
        {filtro}
        GROUP BY EXTRACT(DOW FROM fecha_liquidacion)
        ORDER BY dia_semana
    """, params if params else None)
    
    dias_semana = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb']
    pagos_por_dia = [{
        'dia': dias_semana[int(r[0])],
        'cantidad': r[1],
        'total': float(r[2]) if r[2] else 0
    } for r in cur.fetchall()]
    
    cur.close()
    conn.close()
    
    return {
        'pagos_diarios': pagos_diarios,
        'pagos_por_dia': pagos_por_dia
    }


def get_dashboard_liquidaciones_resumen():
    """Obtiene resumen de liquidaciones"""
    conn = get_connection()
    cur = conn.cursor()
    
    # Liquidaciones por estado
    cur.execute("""
        SELECT 
            estado,
            COUNT(*) as cantidad,
            COALESCE(SUM(total_neto), 0) as total
        FROM liquidaciones_nomina
        GROUP BY estado
    """)
    
    liquidaciones_estado = [{
        'estado': r[0],
        'cantidad': r[1],
        'total': float(r[2])
    } for r in cur.fetchall()]
    
    # Últimas 5 liquidaciones
    cur.execute("""
        SELECT 
            id_liquidacion,
            fecha_liquidacion,
            fecha_inicio,
            fecha_fin,
            total_bruto,
            total_descuentos,
            total_neto,
            estado
        FROM liquidaciones_nomina
        ORDER BY fecha_liquidacion DESC
        LIMIT 5
    """)
    
    ultimas_liquidaciones = [{
        'id': r[0],
        'fecha': r[1],
        'inicio': r[2],
        'fin': r[3],
        'bruto': float(r[4]),
        'descuentos': float(r[5]),
        'neto': float(r[6]),
        'estado': r[7]
    } for r in cur.fetchall()]
    
    cur.close()
    conn.close()
    
    return {
        'liquidaciones_estado': liquidaciones_estado,
        'ultimas_liquidaciones': ultimas_liquidaciones
    }


def get_dashboard_deuda_supermercado():
    """Obtiene el resumen de deuda al supermercado (CXP) - Solo negocios KIKES"""
    conn = get_connection()
    cur = conn.cursor()
    
    # Negocios de Kikes
    negocios_kikes = ('COMIDAS RAPIDAS KIKE', 'COMIDAS RAPIDAS KIKE 2', 'KIKES PIZZA')
    
    # Deuda total por remisiones - Solo KIKES
    cur.execute("""
        SELECT COALESCE(SUM(valor_remsion), 0) as total
        FROM remisiones
        WHERE estado_remision = 'open'
          AND nombre_negocio IN %s
    """, (negocios_kikes,))
    total_remisiones = float(cur.fetchone()[0])
    
    # Deuda total por facturas (balance pendiente) - Solo KIKES
    cur.execute("""
        SELECT COALESCE(SUM(balance_factura), 0) as total
        FROM facturas
        WHERE estado_factura = 'open'
          AND nombre_negocio IN %s
    """, (negocios_kikes,))
    total_facturas = float(cur.fetchone()[0])
    
    # Cantidad de remisiones y facturas abiertas - Solo KIKES
    cur.execute("""
        SELECT COUNT(*) FROM remisiones 
        WHERE estado_remision = 'open' AND nombre_negocio IN %s
    """, (negocios_kikes,))
    cantidad_remisiones = cur.fetchone()[0]
    
    cur.execute("""
        SELECT COUNT(*) FROM facturas 
        WHERE estado_factura = 'open' AND nombre_negocio IN %s
    """, (negocios_kikes,))
    cantidad_facturas = cur.fetchone()[0]
    
    cur.close()
    conn.close()
    
    return {
        'total_remisiones': total_remisiones,
        'total_facturas': total_facturas,
        'total_deuda': total_remisiones + total_facturas,
        'cantidad_remisiones': cantidad_remisiones,
        'cantidad_facturas': cantidad_facturas
    }


def get_dashboard_deuda_por_negocio():
    """Obtiene el detalle de deuda separado por negocio - Solo negocios KIKES"""
    conn = get_connection()
    cur = conn.cursor()
    
    # Negocios de Kikes
    negocios_kikes = ('COMIDAS RAPIDAS KIKE', 'COMIDAS RAPIDAS KIKE 2', 'KIKES PIZZA')
    
    # Remisiones por negocio - Solo KIKES
    cur.execute("""
        SELECT 
            nombre_negocio,
            COUNT(*) as cantidad,
            COALESCE(SUM(valor_remsion), 0) as total
        FROM remisiones
        WHERE estado_remision = 'open'
          AND nombre_negocio IN %s
        GROUP BY nombre_negocio
        ORDER BY total DESC
    """, (negocios_kikes,))
    
    remisiones_negocio = {r[0]: {'cantidad': r[1], 'total': float(r[2])} for r in cur.fetchall()}
    
    # Facturas por negocio - Solo KIKES
    cur.execute("""
        SELECT 
            nombre_negocio,
            COUNT(*) as cantidad,
            COALESCE(SUM(balance_factura), 0) as total
        FROM facturas
        WHERE estado_factura = 'open'
          AND nombre_negocio IN %s
        GROUP BY nombre_negocio
        ORDER BY total DESC
    """, (negocios_kikes,))
    
    facturas_negocio = {r[0]: {'cantidad': r[1], 'total': float(r[2])} for r in cur.fetchall()}
    
    # Combinar datos - Solo de los negocios KIKES
    negocios = set(list(remisiones_negocio.keys()) + list(facturas_negocio.keys()))
    
    resultado = []
    for negocio in negocios:
        rem = remisiones_negocio.get(negocio, {'cantidad': 0, 'total': 0})
        fac = facturas_negocio.get(negocio, {'cantidad': 0, 'total': 0})
        # Nombre corto para mostrar
        nombre_corto = negocio.replace('COMIDAS RAPIDAS ', '')
        resultado.append({
            'negocio': nombre_corto,
            'negocio_completo': negocio,
            'remisiones_cantidad': rem['cantidad'],
            'remisiones_total': rem['total'],
            'facturas_cantidad': fac['cantidad'],
            'facturas_total': fac['total'],
            'total_deuda': rem['total'] + fac['total']
        })
    
    # Ordenar por deuda total descendente
    resultado.sort(key=lambda x: x['total_deuda'], reverse=True)
    
    cur.close()
    conn.close()
    
    return resultado


def get_dashboard_gastos_por_sede():
    """Obtiene los gastos de nómina agrupados por sede"""
    conn = get_connection()
    cur = conn.cursor()
    
    # Liquidaciones por sede este mes
    cur.execute("""
        SELECT 
            COALESCE(s.nombre_sede, 'Sin Sede') as sede,
            COUNT(d.id_detalle) as pagos,
            COALESCE(SUM(d.total_neto), 0) as total_pagado,
            COALESCE(SUM(d.total_descuentos), 0) as total_descuentos
        FROM detalle_liquidacion d
        INNER JOIN liquidaciones_nomina l ON d.id_liquidacion = l.id_liquidacion
        INNER JOIN empleados e ON d.id_empleado = e.id_empleado
        LEFT JOIN sedes s ON e.id_sede = s.id_sede
        WHERE EXTRACT(MONTH FROM l.fecha_liquidacion) = EXTRACT(MONTH FROM CURRENT_DATE)
          AND EXTRACT(YEAR FROM l.fecha_liquidacion) = EXTRACT(YEAR FROM CURRENT_DATE)
        GROUP BY s.nombre_sede
        ORDER BY total_pagado DESC
    """)
    
    gastos_sede = [{
        'sede': r[0],
        'pagos': r[1],
        'total_pagado': float(r[2]) if r[2] else 0,
        'total_descuentos': float(r[3]) if r[3] else 0
    } for r in cur.fetchall()]
    
    cur.close()
    conn.close()
    
    return gastos_sede


def get_dashboard_resumen_nomina_mes():
    """Obtiene el resumen completo de nómina del mes actual"""
    conn = get_connection()
    cur = conn.cursor()
    
    # Total bruto pagado desde detalle_liquidacion (liquidaciones del mes)
    cur.execute("""
        SELECT 
            COALESCE(SUM(d.subtotal_bruto), 0) as bruto,
            COALESCE(SUM(d.total_descuentos), 0) as descuentos,
            COALESCE(SUM(d.total_neto), 0) as neto,
            COALESCE(SUM(d.descuento_comida_bruto), 0) as consumos,
            COUNT(*) as pagos
        FROM detalle_liquidacion d
        INNER JOIN liquidaciones_nomina l ON d.id_liquidacion = l.id_liquidacion
        WHERE EXTRACT(MONTH FROM l.fecha_liquidacion) = EXTRACT(MONTH FROM CURRENT_DATE)
          AND EXTRACT(YEAR FROM l.fecha_liquidacion) = EXTRACT(YEAR FROM CURRENT_DATE)
    """)
    
    r = cur.fetchone()
    pagos_diarios = {
        'bruto': float(r[0]) if r[0] else 0,
        'descuentos': float(r[1]) if r[1] else 0,
        'neto': float(r[2]) if r[2] else 0,
        'consumos': float(r[3]) if r[3] else 0,
        'pagos': r[4] if r[4] else 0
    }
    
    # Total consumo de alimentos del mes (para calcular subsidio)
    cur.execute("""
        SELECT COALESCE(SUM(valor), 0)
        FROM descuentos_nomina
        WHERE tipo_descuento = 'Consumo Alimento'
          AND EXTRACT(MONTH FROM fecha) = EXTRACT(MONTH FROM CURRENT_DATE)
          AND EXTRACT(YEAR FROM fecha) = EXTRACT(YEAR FROM CURRENT_DATE)
    """)
    total_consumo_alimentos = float(cur.fetchone()[0])
    
    # Porcentaje de subsidio
    cur.execute("""
        SELECT COALESCE(valor_config, 10) FROM configuracion_nomina 
        WHERE nombre_config = 'descuento_comida_porcentaje' AND activo = TRUE
    """)
    result = cur.fetchone()
    porcentaje_subsidio = float(result[0]) if result else 10
    
    gasto_subsidio = total_consumo_alimentos * (porcentaje_subsidio / 100)
    
    # Turnos pendientes de pago
    cur.execute("""
        SELECT 
            COUNT(*) as turnos,
            COALESCE(SUM(e.salario_dia), 0) as estimado
        FROM turnos t
        INNER JOIN empleados e ON t.id_empleado = e.id_empleado
        WHERE t.hora_salida IS NOT NULL
          AND (t.pagado = FALSE OR t.pagado IS NULL)
    """)
    r = cur.fetchone()
    pendientes = {
        'turnos': r[0],
        'estimado': float(r[1])
    }
    
    cur.close()
    conn.close()
    
    return {
        'pagos_diarios': pagos_diarios,
        'total_consumo_alimentos': total_consumo_alimentos,
        'porcentaje_subsidio': porcentaje_subsidio,
        'gasto_subsidio': gasto_subsidio,
        'pendientes': pendientes
    }