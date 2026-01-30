import socket
import time
import random
import hashlib
import sys

# Intentar importar colorama
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    C_DATA = Fore.CYAN
    C_OK = Fore.GREEN
    C_ERR = Fore.RED
    C_WARN = Fore.YELLOW
    RESET = Style.RESET_ALL
except ImportError:
    C_DATA = C_OK = C_ERR = C_WARN = RESET = ""

# --- CONFIGURACIÓN DEL DISPOSITIVO ---
IP_SERVIDOR = "127.0.0.4"  # Localhost (para pruebas locales)
PUERTO = 5000
ID_DISPOSITIVO = "GPS-MOVIL-04"
TIMEOUT_SEGUNDOS = 2     # Tiempo máximo de espera del ACK

def calcular_hash(contenido):
    """Genera el mismo tipo de hash que el servidor espera"""
    return hashlib.sha256(contenido.encode('utf-8')).hexdigest()[:8].upper()

def generar_coordenadas(lat_base, lon_base):
    """Simula movimiento aleatorio pequeño (caminata/auto)"""
    desvio_lat = random.uniform(-0.0005, 0.0005)
    desvio_lon = random.uniform(-0.0005, 0.0005)
    return lat_base + desvio_lat, lon_base + desvio_lon

def iniciar_cliente():
    print(f"{C_DATA}📡 === INICIANDO DISPOSITIVO GPS: {ID_DISPOSITIVO} ==={RESET}")
    print(f"{C_DATA}🎯 Destino: {IP_SERVIDOR}:{PUERTO}{RESET}")
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(TIMEOUT_SEGUNDOS) # Importante: Si no responden, lanza error
    
    # Datos iniciales simulados
    latitud = 6.5000
    longitud = -268.7500
    bateria = 100
    
    try:
        while bateria > 0:
            # 1. Simular datos de sensores
            latitud, longitud = generar_coordenadas(latitud, longitud)
            bateria -= random.randint(0, 2) # Batería baja aleatoriamente
            if bateria < 0: bateria = 0
            
            timestamp = int(time.time())
            
            # 2. Construir Trama (Payload)
            # Formato: LGP|ID|LAT|LON|BAT|TIME
            payload = f"LGP|{ID_DISPOSITIVO}|{latitud:.6f}|{longitud:.6f}|{bateria}|{timestamp}"
            
            # 3. Calcular Seguridad
            checksum = calcular_hash(payload)
            mensaje_final = f"{payload}|{checksum}"
            
            print(f"\n📤 Enviando: {mensaje_final}")
            
            # 4. Enviar y Esperar Confirmación (ACK)
            reintentos = 1
            while reintentos >= 0:
                try:
                    # Enviar
                    sock.sendto(mensaje_final.encode('utf-8'), (IP_SERVIDOR, PUERTO))
                    
                    # Esperar respuesta (Bloqueante por N segundos)
                    data, server = sock.recvfrom(1024)
                    respuesta = data.decode('utf-8')
                    
                    if "ACK" in respuesta and "OK" in respuesta:
                        print(f"{C_OK}✅ Confirmado por servidor: {respuesta}{RESET}")
                        break # Salir del bucle de reintentos
                    else:
                        print(f"{C_ERR}❌ Servidor rechazó el paquete (Error datos){RESET}")
                        break
                        
                except socket.timeout:
                    print(f"{C_WARN}⚠️ Timeout: No llegó ACK. (Reintentos restantes: {reintentos}){RESET}")
                    reintentos -= 1
                    if reintentos < 0:
                        print(f"{C_ERR}⛔ Error de Red: Se descarta el paquete y se sigue.{RESET}")
            
            # 5. Dormir para ahorrar energía (Simulado)
            tiempo_dormir = 5
            print(f"💤 Durmiendo {tiempo_dormir}s...")
            time.sleep(tiempo_dormir)

    except KeyboardInterrupt:
        print(f"\n{C_DATA}🛑 Dispositivo apagado.{RESET}")
    finally:
        sock.close()

if __name__ == "__main__":
    iniciar_cliente()