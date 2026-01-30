import socket
import datetime
import hashlib
import sys

# Intentar importar colorama para una consola profesional
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    COLOR_OK = Fore.GREEN
    COLOR_ERR = Fore.RED
    COLOR_INFO = Fore.CYAN
    COLOR_WARN = Fore.YELLOW
    RESET = Style.RESET_ALL
except ImportError:
    # Fallback si no está instalado
    COLOR_OK = ""
    COLOR_ERR = ""
    COLOR_INFO = ""
    COLOR_WARN = ""
    RESET = ""

# --- CONFIGURACIÓN DEL PROTOCOLO ---
IP_SERVIDOR = "0.0.0.0"   # Escuchar en todas las interfaces
PUERTO = 5000             # Puerto UDP acordado
BUFFER_SIZE = 1024        # Tamaño de buffer suficiente para SRV
LOG_FILE = "registro_gps.txt"

def calcular_hash(contenido):
    """
    Genera un hash SHA-256 corto (primeros 4 bytes en hex) para validar integridad.
    Simula una verificación ligera para IoT.
    """
    return hashlib.sha256(contenido.encode('utf-8')).hexdigest()[:8].upper()

def guardar_log(mensaje, direccion):
    """Persistencia de datos en archivo de texto (Simulando BD)"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] IP:{direccion[0]} | DATA: {mensaje}\n"
    
    try:
        with open(LOG_FILE, "a") as f:
            f.write(log_entry)
    except Exception as e:
        print(f"{COLOR_ERR}Error escribiendo log: {e}{RESET}")

def iniciar_servidor():
    # Creación del Socket UDP (SOCK_DGRAM)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    try:
        sock.bind((IP_SERVIDOR, PUERTO))
        print(f"{COLOR_INFO} === SERVIDOR SRV (UDP) INICIADO ==={RESET}")
        print(f"{COLOR_INFO} Escuchando en puerto {PUERTO}...{RESET}")
        print(f"{COLOR_INFO} Guardando datos en '{LOG_FILE}'{RESET}")
        print("-" * 50)

        while True:
            # 1. RECEPCIÓN (Bloqueante hasta que llegue algo)
            data_bytes, addr = sock.recvfrom(BUFFER_SIZE)
            mensaje_full = data_bytes.decode('utf-8').strip()
            
            # Formato esperado: SRV|ID|LAT|LON|BAT|TIME|CHECKSUM
            
            # 2. PARSING (Análisis de la trama)
            if "|" not in mensaje_full:
                print(f"{COLOR_WARN}⚠️ Trama inválida de {addr}: {mensaje_full}{RESET}")
                continue

            partes = mensaje_full.split("|")
            
            # Validación básica de estructura (Mínimo debe tener cabecera, datos y checksum)
            if len(partes) < 7:
                 print(f"{COLOR_WARN}⚠️ Trama incompleta de {addr}{RESET}")
                 continue

            # Separar el contenido (Payload) del Checksum recibido
            # Reconstruimos el mensaje sin el último campo para recalcular el hash
            payload_sin_hash = "|".join(partes[:-1]) 
            checksum_recibido = partes[-1]
            checksum_calculado = calcular_hash(payload_sin_hash)

            device_id = partes[1] # Extraemos ID para log y respuesta

            # 3. VERIFICACIÓN DE INTEGRIDAD (SEGURIDAD)
            if checksum_recibido == checksum_calculado:
                # INTEGRIDAD OK
                print(f"{COLOR_OK}✅ [OK] {device_id} -> {payload_sin_hash} (Hash:{checksum_recibido}){RESET}")
                
                # Guardar en "Base de Datos"
                guardar_log(mensaje_full, addr)
                
                # 4. ENVIAR ACK (Confirmación de recepción)
                # Formato respuesta: ACK|ID_DISPOSITIVO|STATUS
                respuesta = f"ACK|{device_id}|200_OK"
                sock.sendto(respuesta.encode('utf-8'), addr)
                
            else:
                # INTEGRIDAD FALLIDA (Datos corruptos o ataque)
                print(f"{COLOR_ERR}⛔ [ERROR HASH] {device_id}: Recibido {checksum_recibido} != Calc {checksum_calculado}{RESET}")
                # Opcional: No enviar ACK para obligar al cliente a reintentar o enviar error
                respuesta_error = f"ACK|{device_id}|400_CORRUPT"
                sock.sendto(respuesta_error.encode('utf-8'), addr)

    except KeyboardInterrupt:
        print(f"\n{COLOR_INFO}🛑 Servidor detenido por el usuario.{RESET}")
    except OSError as e:
        print(f"\n{COLOR_ERR}❌ Error de red: {e} (¿El puerto {PUERTO} está ocupado?){RESET}")
    finally:
        sock.close()

if __name__ == "__main__":
    iniciar_servidor()