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


def reset_all_remisiones_to_closed():
    """Marca todas las remisiones abiertas como cerradas (para sincronización completa)"""
    conn = get_connection()
    cur = conn.cursor()
    
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
    """Inserta o actualiza una remisión"""
    conn = get_connection()
    cur = conn.cursor()
    
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


# ==================== FUNCIONES DE EMPLEADOS ====================

def insert_empleado(nombre_empleado, tipo_documento, cedula_empleado, salario_dia):
    """Inserta un nuevo empleado en la base de datos"""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute(
            """INSERT INTO empleados (nombre_empleado, tipo_documento, cedula_empleado, salario_dia)
               VALUES (%s, %s, %s, %s) RETURNING id_empleado""",
            (nombre_empleado, tipo_documento, cedula_empleado, salario_dia)
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


# ==================== FUNCIONES DE TURNOS ====================

def get_empleado_by_cedula(cedula):
    """Obtiene un empleado por su número de cédula"""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute(
        "SELECT id_empleado, nombre_empleado, tipo_documento, cedula_empleado, salario_dia FROM empleados WHERE cedula_empleado = %s",
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
            'salario_dia': result[4]
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

def get_all_empleados_activos():
    """Obtiene todos los empleados activos para selección"""
    conn = get_connection()
    cur = conn.cursor()
    
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


def get_turnos_abiertos():
    """Obtiene todos los turnos abiertos (sin hora de salida)"""
    conn = get_connection()
    cur = conn.cursor()
    
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


def get_historial_turnos(fecha_inicio=None, fecha_fin=None, id_empleado=None, limit=100):
    """Obtiene el historial de turnos con filtros"""
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
        SELECT id_usuario, username, nombre_completo, es_master, es_empleado, es_admin, activo
        FROM usuarios 
        WHERE username = %s AND password_hash = %s AND activo = TRUE
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
        SELECT id_usuario, username, nombre_completo, es_master, es_empleado, es_admin, activo, create_at
        FROM usuarios 
        ORDER BY es_master DESC, es_admin DESC, nombre_completo
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
        'create_at': r[7]
    } for r in results]


def get_usuario_by_id(id_usuario):
    """Obtiene un usuario por su ID"""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT id_usuario, username, nombre_completo, es_master, es_empleado, es_admin, activo
        FROM usuarios 
        WHERE id_usuario = %s
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
            'activo': result[6]
        }
    return None


def insert_usuario(username, password, nombre_completo, es_master=False, es_empleado=False, es_admin=False):
    """Inserta un nuevo usuario"""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        password_hash = hash_password(password)
        cur.execute(
            """INSERT INTO usuarios (username, password_hash, nombre_completo, es_master, es_empleado, es_admin)
               VALUES (%s, %s, %s, %s, %s, %s) RETURNING id_usuario""",
            (username, password_hash, nombre_completo, es_master, es_empleado, es_admin)
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


def update_usuario(id_usuario, username=None, nombre_completo=None, es_master=None, es_empleado=None, es_admin=None, activo=None):
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

def get_total_horas_por_fecha(fecha_inicio=None, fecha_fin=None, id_empleado=None):
    """
    Obtiene los turnos con cálculo de horas trabajadas.
    Solo incluye turnos completados (con hora_salida).
    
    Args:
        fecha_inicio: Fecha inicial del filtro (opcional)
        fecha_fin: Fecha final del filtro (opcional)
        id_empleado: ID del empleado para filtrar (opcional)
    
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
            EXTRACT(EPOCH FROM (t.hora_salida - t.hora_inicio)) / 3600 as total_horas
        FROM turnos t
        INNER JOIN empleados e ON t.id_empleado = e.id_empleado
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
        'total_horas': round(r[7], 2) if r[7] else 0
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

def get_horas_extra(fecha_inicio=None, fecha_fin=None, id_empleado=None):
    """
    Obtiene los turnos con horas extra (más de 8 horas trabajadas).
    
    Args:
        fecha_inicio: Fecha inicial del filtro (opcional)
        fecha_fin: Fecha final del filtro (opcional)
        id_empleado: ID del empleado para filtrar (opcional)
    
    Returns:
        Lista de diccionarios con información de turnos y horas extra
    """
    conn = get_connection()
    cur = conn.cursor()
    
    query = """
        SELECT 
            t.id_turno,
            th.id_hora,
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
            END as horas_extra
        FROM turnos t
        INNER JOIN empleados e ON t.id_empleado = e.id_empleado
        LEFT JOIN total_horas th ON t.id_turno = th.id_turno
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
        'horas_extra': round(r[8], 2) if r[8] else 0
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
                th.id_hora,
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
    """Inserta un nuevo turno (la foto se ignora por ahora - convierte hora Colombia a UTC)"""
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
        # Nota: foto_bytes se ignora por ahora hasta agregar columna en BD
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


def cerrar_turno_con_foto(id_turno, hora_salida, foto_bytes=None):
    """Cierra un turno (la foto se ignora por ahora - convierte hora Colombia a UTC)"""
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
        # Nota: foto_bytes se ignora por ahora hasta agregar columna en BD
        cur.execute(
            """UPDATE turnos SET hora_salida = %s WHERE id_turno = %s""",
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