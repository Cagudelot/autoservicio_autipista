import os
import base64
import requests
import time
from dotenv import load_dotenv
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data_base.controler import (
    get_last_remission_number,
    insert_cliente,
    insert_negocio,
    insert_remision,
    get_last_invoice_number,
    insert_factura,
    get_all_remisiones_open,
    update_remision_estado,
    get_all_facturas_open,
    update_factura_estado,
    update_remision_valor,
    update_factura_valor,
    get_all_remisiones_open_with_value,
    get_all_facturas_open_with_value,
    reset_all_remisiones_to_closed,
    reset_all_facturas_to_closed,
    upsert_remision,
    upsert_factura
)

# Cargo variables de entorno
load_dotenv()

BASE_URL = "https://api.alegra.com/api/v1"

# NITs de los negocios Kikes (solo sincronizar estos)
KIKES_NITS = [
    "1036944617",  # COMIDAS RAPIDAS KIKE 2
    "1036224936",  # KIKES PIZZA
    "1036944616",  # COMIDAS RAPIDAS KIKE (Principal) - verificar NIT correcto
]


def is_kikes_client(client):
    """Verifica si un cliente es de los Kikes"""
    nit = client.get("identification", "")
    nombre = client.get("name", "").upper()
    # Filtrar por NIT o por nombre que contenga KIKE
    return nit in KIKES_NITS or "KIKE" in nombre


def get_remisiones_excluidas():
    """Obtiene la lista de números de remisión excluidos de sincronización"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT numero_remision FROM remisiones_excluidas")
        excluidas = [row[0] for row in cur.fetchall()]
        cur.close()
        conn.close()
        return excluidas
    except Exception:
        return []


def get_credentials():
    """Retorna los headers con las credenciales"""
    email = os.getenv("ALEGRA_EMAIL")
    api_key = os.getenv("ALEGRA_API_KEY") or os.getenv("ALEGRA_TOKEN")
    
    credentials = f"{email}:{api_key}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    
    return {
        "accept": "application/json",
        "authorization": f"Basic {encoded_credentials}"
    }


def process_single_remission(remission):
    """Procesa y guarda una sola remisión en la BD (solo si es de Kikes)"""
    client = remission.get("client", {})
    nit = client.get("identification")
    nombre = client.get("name")
    
    if not nit or not nombre:
        return False
    
    # FILTRO: Solo procesar si es de los Kikes
    if not is_kikes_client(client):
        return False
    
    # Insertar cliente y obtener id
    id_cliente = insert_cliente(nit, nombre)
    
    # Insertar negocio
    insert_negocio(id_cliente, nombre)
    
    # Extraer datos de la remisión
    numero_remision = int(remission.get("number", 0))
    fecha = remission.get("date")
    valor = float(remission.get("total", 0))
    
    # Calcular estado REAL basado en missingQuantityToBilled
    api_status = remission.get("status", "unknown")
    if api_status == "void":
        estado = "void"
    else:
        items = remission.get("items", [])
        # Verificar si hay algún item con cantidad POSITIVA pendiente
        has_pending = any(float(item.get("missingQuantityToBilled", 0)) > 0 for item in items)
        estado = "open" if has_pending else "closed"
    
    # Insertar remisión
    insert_remision(numero_remision, id_cliente, fecha, estado, valor)
    
    return True


def get_total_remissions():
    """Obtiene el total de remisiones usando metadata"""
    headers = get_credentials()
    
    params = {
        "limit": 1,
        "metadata": "true"
    }
    
    response = requests.get(
        f"{BASE_URL}/remissions",
        headers=headers,
        params=params,
        timeout=15
    )
    
    if response.status_code == 200:
        data = response.json()
        return data.get("metadata", {}).get("total", 0)
    return 0


def initial_load():
    """Carga inicial - descarga desde remisión 1 y guarda al mismo tiempo"""
    headers = get_credentials()
    
    # Obtener total de remisiones
    total_remissions = get_total_remissions()
    print(f"Total de remisiones en Alegra: {total_remissions}")
    
    start = 1  # Empezar desde la remisión 1
    limit = 30
    request_count = 0
    saved_count = 0
    start_time = time.time()
    
    print("=" * 50)
    print("CARGA INICIAL DE REMISIONES")
    print("=" * 50)
    
    while True:
        params = {
            "start": start,
            "limit": limit,
            "order_direction": "ASC",
            "order_field": "id"
        }
        
        request_count += 1
        print(f"\n[Solicitud #{request_count}] Desde remisión: {start}...")
        
        try:
            response = requests.get(
                f"{BASE_URL}/remissions",
                headers=headers,
                params=params,
                timeout=15
            )
            
            if response.status_code != 200:
                print(f"  ✗ Error: {response.status_code} - {response.text}")
                break
            
            remissions = response.json()
            
            if not remissions:
                print("  → No hay más remisiones")
                break
            
            # Guardar cada remisión inmediatamente
            for remission in remissions:
                numero = int(remission.get("number", 0))
                if process_single_remission(remission):
                    saved_count += 1
                    print(f"    ✓ Remisión #{numero} guardada")
            
            print(f"  → Total guardadas: {saved_count}")
            
            # Siguiente página: avanzar 30 remisiones
            start += limit
            
            # Si ya pasamos el total, terminar
            if start > total_remissions:
                print("  → Todas las remisiones procesadas")
                break
            
        except Exception as e:
            print(f"  ✗ Error: {str(e)}")
            break
    
    total_time = time.time() - start_time
    print("\n" + "=" * 50)
    print(f"COMPLETADO")
    print(f"  Remisiones guardadas: {saved_count}")
    print(f"  Solicitudes: {request_count}")
    print(f"  Tiempo: {total_time:.2f}s")
    print("=" * 50)


def sync_remissions():
    """Sincroniza solo remisiones nuevas desde la última guardada"""
    headers = get_credentials()
    last_number = get_last_remission_number()
    
    print("=" * 50)
    print("SINCRONIZANDO REMISIONES NUEVAS")
    print(f"Última remisión en BD: {last_number}")
    print("=" * 50)
    
    # Empezar desde la siguiente remisión
    start = last_number + 1
    limit = 30
    saved_count = 0
    
    while True:
        params = {
            "start": start,
            "limit": limit,
            "order_direction": "ASC",
            "order_field": "id"
        }
        
        print(f"\n[Buscando desde remisión #{start}]...")
        
        response = requests.get(
            f"{BASE_URL}/remissions",
            headers=headers,
            params=params,
            timeout=15
        )
        
        if response.status_code != 200:
            print(f"  ✗ Error: {response.status_code}")
            break
        
        remissions = response.json()
        
        if not remissions:
            break
        
        for remission in remissions:
            numero = int(remission.get("number", 0))
            if process_single_remission(remission):
                saved_count += 1
                print(f"  ✓ Nueva remisión #{numero} guardada")
        
        start += limit
    
    print(f"\n✓ Sincronización completada. Nuevas: {saved_count}")


# ==================== FACTURAS ====================

def process_single_invoice(invoice):
    """Procesa y guarda una sola factura en la BD (solo si es de Kikes)"""
    client = invoice.get("client", {})
    nit = client.get("identification")
    nombre = client.get("name")
    
    # Omitir Consumidor Final
    if nit == "222222222222" or nombre == "Consumidor Final":
        return False
    
    if not nit or not nombre:
        return False
    
    # FILTRO: Solo procesar si es de los Kikes
    if not is_kikes_client(client):
        return False
    
    # Extraer datos de la factura (fullNumber está dentro de numberTemplate)
    number_template = invoice.get("numberTemplate", {})
    numero_factura = number_template.get("fullNumber", "")
    
    # Omitir si no tiene número de factura
    if not numero_factura:
        return False
    
    # Insertar cliente y obtener id
    id_cliente = insert_cliente(nit, nombre)
    
    # Insertar negocio
    insert_negocio(id_cliente, nombre)
    
    fecha = invoice.get("date")
    estado = invoice.get("status", "unknown")
    valor = float(invoice.get("total", 0))
    
    # Insertar factura
    insert_factura(numero_factura, id_cliente, fecha, estado, valor)
    
    return True


def get_total_invoices():
    """Obtiene el total de facturas usando metadata"""
    headers = get_credentials()
    
    params = {
        "limit": 1,
        "metadata": "true"
    }
    
    response = requests.get(
        f"{BASE_URL}/invoices",
        headers=headers,
        params=params,
        timeout=15
    )
    
    if response.status_code == 200:
        data = response.json()
        return data.get("metadata", {}).get("total", 0)
    return 0


def initial_load_invoices():
    """Carga inicial de facturas"""
    headers = get_credentials()
    
    total_invoices = get_total_invoices()
    print(f"Total de facturas en Alegra: {total_invoices}")
    
    start = 1
    limit = 30
    request_count = 0
    saved_count = 0
    skipped_count = 0
    start_time = time.time()
    
    print("=" * 50)
    print("CARGA INICIAL DE FACTURAS")
    print("=" * 50)
    
    while True:
        params = {
            "start": start,
            "limit": limit,
            "order_direction": "ASC",
            "order_field": "id"
        }
        
        request_count += 1
        print(f"\n[Solicitud #{request_count}] Desde factura: {start}...")
        
        try:
            response = requests.get(
                f"{BASE_URL}/invoices",
                headers=headers,
                params=params,
                timeout=15
            )
            
            if response.status_code != 200:
                print(f"  ✗ Error: {response.status_code} - {response.text}")
                break
            
            invoices = response.json()
            
            if not invoices:
                print("  → No hay más facturas")
                break
            
            for invoice in invoices:
                number_template = invoice.get("numberTemplate", {})
                numero = number_template.get("fullNumber", "")
                if process_single_invoice(invoice):
                    saved_count += 1
                    print(f"    ✓ Factura {numero} guardada")
                else:
                    skipped_count += 1
            
            print(f"  → Guardadas: {saved_count} | Omitidas: {skipped_count}")
            
            start += limit
            
            if start > total_invoices:
                print("  → Todas las facturas procesadas")
                break
            
        except Exception as e:
            print(f"  ✗ Error: {str(e)}")
            break
    
    total_time = time.time() - start_time
    print("\n" + "=" * 50)
    print(f"COMPLETADO")
    print(f"  Facturas guardadas: {saved_count}")
    print(f"  Facturas omitidas (Consumidor Final): {skipped_count}")
    print(f"  Solicitudes: {request_count}")
    print(f"  Tiempo: {total_time:.2f}s")
    print("=" * 50)


def sync_invoices():
    """Sincroniza solo facturas nuevas desde la última guardada"""
    headers = get_credentials()
    last_number = get_last_invoice_number()
    
    print("=" * 50)
    print("SINCRONIZANDO FACTURAS NUEVAS")
    print(f"Última factura en BD: {last_number}")
    print("=" * 50)
    
    start = 1
    limit = 30
    saved_count = 0
    skipped_count = 0
    
    while True:
        params = {
            "start": start,
            "limit": limit,
            "order_direction": "DESC",
            "order_field": "id"
        }
        
        print(f"\n[Buscando facturas nuevas...]")
        
        response = requests.get(
            f"{BASE_URL}/invoices",
            headers=headers,
            params=params,
            timeout=15
        )
        
        if response.status_code != 200:
            print(f"  ✗ Error: {response.status_code}")
            break
        
        invoices = response.json()
        
        if not invoices:
            break
        
        found_existing = False
        for invoice in invoices:
            number_template = invoice.get("numberTemplate", {})
            numero = number_template.get("fullNumber", "")
            
            # Si encontramos la última factura guardada, terminamos
            if numero == last_number:
                found_existing = True
                break
            
            if process_single_invoice(invoice):
                saved_count += 1
                print(f"  ✓ Nueva factura {numero} guardada")
            else:
                skipped_count += 1
        
        if found_existing:
            break
        
        start += limit
    
    print(f"\n✓ Sincronización completada. Nuevas: {saved_count} | Omitidas: {skipped_count}")


def get_remission_real_status(remission):
    """
    Determina el estado REAL de una remisión basándose en missingQuantityToBilled.
    - Si missingQuantityToBilled <= 0 para todos los items → 'closed' (facturada)
    - Si missingQuantityToBilled > 0 para algún item → 'open' (pendiente)
    - Si el status de la API es 'void' → 'void' (anulada)
    
    NOTA: missingQuantityToBilled puede ser negativo cuando se factura más de lo remitido.
          En ese caso, la remisión también se considera cerrada/facturada.
    """
    api_status = remission.get("status", "unknown")
    
    # Si está anulada, mantener ese estado
    if api_status == "void":
        return "void"
    
    # Calcular basándose en missingQuantityToBilled
    items = remission.get("items", [])
    
    # Verificar si hay algún item con cantidad POSITIVA pendiente por facturar
    has_pending = False
    for item in items:
        missing = float(item.get("missingQuantityToBilled", 0))
        if missing > 0:  # Solo si es POSITIVO hay pendiente real
            has_pending = True
            break
    
    # Si no hay pendientes positivos, está cerrada
    if not has_pending:
        return "closed"
    else:
        return "open"


def sync_remissions_status():
    """Sincroniza el estado y valor de remisiones basándose en missingQuantityToBilled"""
    headers = get_credentials()
    
    print("=" * 50)
    print("SINCRONIZANDO ESTADOS Y VALORES DE REMISIONES")
    print("(Usando missingQuantityToBilled como indicador)")
    print("=" * 50)
    
    # Obtener remisiones abiertas de la BD con sus valores
    remisiones_open = get_all_remisiones_open_with_value()
    total = len(remisiones_open)
    print(f"Remisiones abiertas en BD: {total}")
    
    if total == 0:
        print("No hay remisiones abiertas para verificar")
        return
    
    updated_estado_count = 0
    updated_valor_count = 0
    
    for numero_remision, estado_actual, valor_actual in remisiones_open:
        # Consultar remisión en la API buscando por número
        response = requests.get(
            f"{BASE_URL}/remissions",
            headers=headers,
            params={"number": numero_remision},
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                remission = data[0]
                
                # Calcular el estado REAL basado en missingQuantityToBilled
                nuevo_estado = get_remission_real_status(remission)
                
                # Obtener valor de la API
                nuevo_valor = float(remission.get("total", 0))
                valor_actual_float = float(valor_actual) if valor_actual else 0
                
                # Actualizar estado si cambió
                if nuevo_estado != estado_actual:
                    update_remision_estado(numero_remision, nuevo_estado)
                    updated_estado_count += 1
                    print(f"  ✓ Remisión #{numero_remision}: Estado {estado_actual} → {nuevo_estado}")
                
                # Actualizar valor si cambió (con tolerancia de 0.01 para evitar problemas de precisión)
                if abs(nuevo_valor - valor_actual_float) > 0.01:
                    update_remision_valor(numero_remision, nuevo_valor)
                    updated_valor_count += 1
                    print(f"  ✓ Remisión #{numero_remision}: Valor ${valor_actual_float:,.2f} → ${nuevo_valor:,.2f}")
    
    print(f"\n✓ Estados actualizados: {updated_estado_count}")
    print(f"✓ Valores actualizados: {updated_valor_count}")


def sync_invoices_status():
    """Sincroniza el estado y valor de facturas que están 'open' en la BD"""
    headers = get_credentials()
    
    print("=" * 50)
    print("SINCRONIZANDO ESTADOS Y VALORES DE FACTURAS")
    print("=" * 50)
    
    # Obtener facturas abiertas de la BD con sus valores
    facturas_open = get_all_facturas_open_with_value()
    total = len(facturas_open)
    print(f"Facturas abiertas en BD: {total}")
    
    if total == 0:
        print("No hay facturas abiertas para verificar")
        return
    
    updated_estado_count = 0
    updated_valor_count = 0
    
    for numero_factura, estado_actual, valor_actual in facturas_open:
        # Consultar estado actual en la API por fullNumber
        response = requests.get(
            f"{BASE_URL}/invoices",
            headers=headers,
            params={"numberTemplate.fullNumber": numero_factura},
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                invoice = data[0]
                nuevo_estado = invoice.get("status", "unknown")
                
                # Obtener valor de la API
                nuevo_valor = float(invoice.get("total", 0))
                valor_actual_float = float(valor_actual) if valor_actual else 0
                
                # Actualizar estado si cambió
                if nuevo_estado != estado_actual:
                    update_factura_estado(numero_factura, nuevo_estado)
                    updated_estado_count += 1
                    print(f"  ✓ Factura {numero_factura}: Estado {estado_actual} → {nuevo_estado}")
                
                # Actualizar valor si cambió (con tolerancia de 0.01 para evitar problemas de precisión)
                if abs(nuevo_valor - valor_actual_float) > 0.01:
                    update_factura_valor(numero_factura, nuevo_valor)
                    updated_valor_count += 1
                    print(f"  ✓ Factura {numero_factura}: Valor ${valor_actual_float:,.2f} → ${nuevo_valor:,.2f}")
    
    print(f"\n✓ Estados actualizados: {updated_estado_count}")
    print(f"✓ Valores actualizados: {updated_valor_count}")


def sync_all():
    """Sincroniza todo: nuevas remisiones, nuevas facturas y estados"""
    print("\n" + "=" * 50)
    print("SINCRONIZACIÓN COMPLETA")
    print("=" * 50 + "\n")
    
    # Sincronizar nuevas remisiones
    sync_remissions()
    
    # Sincronizar estados de remisiones
    sync_remissions_status()
    
    # Sincronizar nuevas facturas
    sync_invoices()
    
    # Sincronizar estados de facturas
    sync_invoices_status()
    
    print("\n" + "=" * 50)
    print("SINCRONIZACIÓN COMPLETA FINALIZADA")
    print("=" * 50)


def full_sync_remisiones_abiertas():
    """
    Sincronización COMPLETA de remisiones abiertas desde Alegra.
    
    Este método:
    1. Descarga TODAS las remisiones abiertas desde Alegra (usando status=open)
    2. Resetea todas las remisiones en la BD a 'closed'
    3. Actualiza/inserta las que están abiertas en Alegra con sus valores correctos
    
    Es la fuente de verdad definitiva: lo que está en Alegra es lo que cuenta.
    """
    headers = get_credentials()
    
    print("=" * 50)
    print("SINCRONIZACIÓN COMPLETA DE REMISIONES ABIERTAS")
    print("=" * 50)
    
    # Paso 1: Descargar TODAS las remisiones abiertas de Alegra
    print("\n[1/3] Descargando remisiones abiertas de Alegra...")
    
    all_open_remissions = []
    start = 0
    limit = 30
    
    while True:
        params = {
            "status": "open",
            "start": start,
            "limit": limit
        }
        
        response = requests.get(
            f"{BASE_URL}/remissions",
            headers=headers,
            params=params,
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"  ✗ Error: {response.status_code} - {response.text}")
            return
        
        remissions = response.json()
        
        if not remissions:
            break
        
        # Filtrar solo las que tienen missingQuantityToBilled > 0 Y son de Kikes
        for rem in remissions:
            client = rem.get("client", {})
            # Solo procesar clientes Kikes
            if not is_kikes_client(client):
                continue
            
            items = rem.get("items", [])
            has_pending = any(float(item.get("missingQuantityToBilled", 0)) > 0 for item in items)
            if has_pending:
                all_open_remissions.append(rem)
        
        print(f"    Página {start//limit + 1}: {len(remissions)} descargadas, {len(all_open_remissions)} abiertas reales")
        
        start += limit
        
        # Pequeña pausa para no saturar la API
        time.sleep(0.2)
    
    # Obtener remisiones excluidas (cerradas manualmente)
    excluidas = get_remisiones_excluidas()
    if excluidas:
        print(f"  ⚠ Remisiones excluidas de sincronización: {excluidas}")
    
    print(f"  ✓ Total remisiones abiertas en Alegra: {len(all_open_remissions)}")
    
    # Paso 2: Resetear todas las remisiones en BD a 'closed' (EXCEPTO las excluidas)
    print("\n[2/3] Reseteando remisiones en BD a 'closed' (excepto excluidas)...")
    reset_count = reset_all_remisiones_to_closed(excluidas)
    print(f"  ✓ {reset_count} remisiones marcadas como 'closed'")
    
    # Paso 3: Actualizar/insertar las abiertas con valores correctos (EXCEPTO excluidas)
    print("\n[3/3] Actualizando remisiones abiertas...")
    
    updated = 0
    inserted = 0
    skipped = 0
    total_valor = 0
    
    for rem in all_open_remissions:
        numero = int(rem.get("number", 0))
        
        # SALTAR remisiones excluidas (cerradas manualmente)
        if numero in excluidas:
            skipped += 1
            print(f"  ⊘ Remisión #{numero} excluida (cerrada manualmente)")
            continue
        
        fecha = rem.get("date")
        valor = float(rem.get("total", 0))
        
        # Obtener datos del cliente
        client = rem.get("client", {})
        nit_cliente = client.get("identification")
        nombre_cliente = client.get("name", "").strip()
        
        # Insertar cliente si no existe y obtener ID local
        id_cliente = insert_cliente(nit_cliente, nombre_cliente)
        
        # Upsert la remisión
        was_inserted = upsert_remision(numero, id_cliente, fecha, "open", valor, nombre_cliente)
        
        if was_inserted:
            inserted += 1
        else:
            updated += 1
        
        total_valor += valor
    
    print(f"\n  ✓ Actualizadas: {updated}")
    print(f"  ✓ Insertadas: {inserted}")
    print(f"  ⊘ Excluidas (no tocadas): {skipped}")
    print(f"  ✓ Total remisiones abiertas: {len(all_open_remissions) - skipped}")
    print(f"  ✓ Valor total: ${total_valor:,.2f}")
    
    print("\n" + "=" * 50)
    print("SINCRONIZACIÓN DE REMISIONES COMPLETADA")
    print("=" * 50)
    
    return len(all_open_remissions), total_valor


def full_sync_facturas_abiertas():
    """
    Sincronización COMPLETA de facturas abiertas desde Alegra.
    
    Este método:
    1. Descarga TODAS las facturas abiertas desde Alegra (usando status=open)
    2. Resetea todas las facturas en la BD a 'closed'
    3. Actualiza/inserta las que están abiertas en Alegra con sus valores y balances correctos
    
    Es la fuente de verdad definitiva: lo que está en Alegra es lo que cuenta.
    """
    headers = get_credentials()
    
    print("=" * 50)
    print("SINCRONIZACIÓN COMPLETA DE FACTURAS ABIERTAS")
    print("=" * 50)
    
    # Paso 1: Descargar TODAS las facturas abiertas de Alegra
    print("\n[1/3] Descargando facturas abiertas de Alegra...")
    
    all_open_invoices = []
    start = 0
    limit = 30
    
    while True:
        params = {
            "status": "open",
            "start": start,
            "limit": limit
        }
        
        response = requests.get(
            f"{BASE_URL}/invoices",
            headers=headers,
            params=params,
            timeout=120
        )
        
        if response.status_code != 200:
            print(f"  ✗ Error: {response.status_code} - {response.text}")
            return
        
        invoices = response.json()
        
        if not invoices:
            break
        
        # Filtrar facturas con balance > 0, no Consumidor Final, Y solo Kikes
        for inv in invoices:
            client = inv.get("client", {})
            nit = client.get("identification")
            nombre = client.get("name")
            
            # Omitir Consumidor Final
            if nit == "222222222222" or nombre == "Consumidor Final":
                continue
            
            # Solo procesar clientes Kikes
            if not is_kikes_client(client):
                continue
            
            balance = float(inv.get("balance", 0))
            if balance > 0:
                all_open_invoices.append(inv)
        
        print(f"    Página {start//limit + 1}: {len(invoices)} descargadas, {len(all_open_invoices)} abiertas reales")
        
        start += limit
        
        # Pequeña pausa para no saturar la API
        time.sleep(0.2)
    
    print(f"  ✓ Total facturas abiertas en Alegra: {len(all_open_invoices)}")
    
    # Paso 2: Resetear todas las facturas en BD a 'closed'
    print("\n[2/3] Reseteando facturas en BD a 'closed'...")
    reset_count = reset_all_facturas_to_closed()
    print(f"  ✓ {reset_count} facturas marcadas como 'closed'")
    
    # Paso 3: Actualizar/insertar las abiertas con valores correctos
    print("\n[3/3] Actualizando facturas abiertas...")
    
    updated = 0
    inserted = 0
    total_valor = 0
    total_balance = 0
    
    for inv in all_open_invoices:
        # Obtener número de factura
        number_template = inv.get("numberTemplate", {})
        numero = number_template.get("fullNumber", "")
        
        if not numero:
            continue
        
        fecha = inv.get("date")
        valor = float(inv.get("total", 0))
        balance = float(inv.get("balance", 0))
        
        # Obtener datos del cliente
        client = inv.get("client", {})
        nit_cliente = client.get("identification")
        nombre_cliente = client.get("name", "").strip()
        
        # Insertar cliente si no existe y obtener ID local
        id_cliente = insert_cliente(nit_cliente, nombre_cliente)
        
        # Upsert la factura
        was_inserted = upsert_factura(numero, id_cliente, fecha, "open", valor, balance, nombre_cliente)
        
        if was_inserted:
            inserted += 1
        else:
            updated += 1
        
        total_valor += valor
        total_balance += balance
    
    print(f"\n  ✓ Actualizadas: {updated}")
    print(f"  ✓ Insertadas: {inserted}")
    print(f"  ✓ Total facturas abiertas: {len(all_open_invoices)}")
    print(f"  ✓ Valor total facturado: ${total_valor:,.2f}")
    print(f"  ✓ Balance total (por cobrar): ${total_balance:,.2f}")
    
    print("\n" + "=" * 50)
    print("SINCRONIZACIÓN DE FACTURAS COMPLETADA")
    print("=" * 50)
    
    return len(all_open_invoices), total_balance


def full_sync_all():
    """
    Sincronización COMPLETA desde Alegra.
    
    Este es el método principal que debe usarse para asegurar que la BD
    está 100% sincronizada con Alegra.
    
    Sincroniza:
    - Todas las remisiones abiertas (con sus valores)
    - Todas las facturas abiertas (con sus valores y balances)
    """
    print("\n" + "=" * 60)
    print("   SINCRONIZACIÓN COMPLETA DESDE ALEGRA")
    print("=" * 60 + "\n")
    
    # Sincronizar remisiones
    result_rem = full_sync_remisiones_abiertas()
    
    print("\n")
    
    # Sincronizar facturas
    result_fac = full_sync_facturas_abiertas()
    
    print("\n" + "=" * 60)
    print("   RESUMEN FINAL")
    print("=" * 60)
    
    if result_rem:
        num_rem, valor_rem = result_rem
        print(f"   Remisiones abiertas: {num_rem:,}")
        print(f"   Valor remisiones: ${valor_rem:,.2f}")
    
    if result_fac:
        num_fac, balance_fac = result_fac
        print(f"   Facturas abiertas: {num_fac:,}")
        print(f"   Por cobrar (balance): ${balance_fac:,.2f}")
    
    print("=" * 60 + "\n")


if __name__ == "__main__":
    # initial_load()
    # initial_load_invoices()
    # sync_all()  # Sincronización incremental
    full_sync_all()  # Sincronización COMPLETA desde Alegra