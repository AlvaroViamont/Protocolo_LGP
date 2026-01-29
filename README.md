📡 LGP - Lightweight GPS Protocol
=================================

Implementación de un protocolo de mensajería ligero diseñado para dispositivos GPS con restricciones críticas de **batería** y **ancho de banda**, operando sobre redes celulares inestables (2G/3G/4G).

> **Contexto del Proyecto:** Desarrollado como solución a un desafío de ingeniería para simular telemetría IoT eficiente.

📋 Características Principales
------------------------------

*   **Transporte Eficiente:** Utiliza **UDP** en lugar de TCP para minimizar el _overhead_ y el consumo energético (evita _handshakes_ costosos).
    
*   **Protocolo Compacto:** Trama de texto delimitada (|) que reduce el tamaño del mensaje en un 50% comparado con JSON.
    
*   **Seguridad e Integridad:** Implementación de **Hashing (SHA-256)** para validar que los datos no lleguen corruptos.
    
*   **Fiabilidad en Capa de Aplicación:** Sistema de confirmaciones (**ACK**) y reintentos inteligentes para manejar la pérdida de paquetes típica de UDP.
    
*   **Simulación Realista:** El cliente simula movimiento geográfico, descarga de batería y modo "Sleep" para ahorro de energía.
    

🛠️ Especificaciones Técnicas del Protocolo
-------------------------------------------

### Definición de la Trama

El mensaje se envía como una cadena de texto codificada en bytes con el siguiente formato:

HEADER | ID\_DISPOSITIVO | LATITUD | LONGITUD | BATERIA | TIMESTAMP | CHECKSUM

**Ejemplo de Trama Real:**

```bash  
LGP|GPS-MOVIL-01|-16.500123|-68.150987|85|1706543210|A1B2C3D4   
```

### Arquitectura de Comunicación

| **Parámetro** | **Valor** | **Justificación** |
|---|---|---|
| **Protocolo de Transporte** | UDP | Menor latencia y consumo de batería (radio 3G/4G activo menos tiempo). |
| **Puerto** | 5000 | Puerto no reservado estándar. |
| **Seguridad** | Checksum (Hash) | Integridad de datos sin coste computacional de SSL/TLS. |
| **Log** | Archivo Plano | Persistencia ligera en registro\_gps.txt. |

🚀 Instalación y Uso
--------------------

### Prerrequisitos

*   Python 3.x instalado.
    
*   (Opcional) Librería colorama para logs a color en consola.
    

**Bash**

```bash   
pip install colorama   
```

### 1\. Iniciar el Servidor (Central)

El servidor escuchará en el puerto 5000 y guardará los logs.


```bash  
python servidor.py   
```

> _Verás el mensaje: 📡 === SERVIDOR LGP (UDP) INICIADO ===_

### 2\. Iniciar el Cliente (Dispositivo GPS)

En una nueva terminal, inicia el simulador GPS. Este empezará a enviar coordenadas automáticamente.

```bash  
python cliente.py   
```

🧪 Escenarios de Prueba
-----------------------

El sistema está diseñado para probar resiliencia. Intenta lo siguiente:

1.  **Funcionamiento Normal:** Verás mensajes en **VERDE** (✅) indicando que el hash es correcto y el servidor recibió el dato.
    
2.  **Simulación de Caída de Red:** Cierra el servidor con Ctrl + C. El cliente mostrará alertas amarillas (⚠️ Timeout) y reintentará antes de descartar el paquete, simulando pérdida de cobertura.
    
3.  **Prueba de Integridad (Hack):** Modifica cliente.py para enviar un checksum falso. El servidor rechazará el paquete mostrando una alerta en **ROJO** (⛔ ERROR HASH) y no guardará el dato.
    

📂 Estructura del Proyecto
--------------------------
    Protocolo_LGP
    ├── src
    |    ├── cliente.py         
    |    └── servidor.py          
    ├── Resultados
    |    ├── Captura_Funcionamiento.png
    |    ├── Captura_Seguridad.png
    |    └── registro_gps.txt    
    ├── Documentación
    |    ├── Justificacion_Tecnica.pdf
    |    └── Protocolo_LGP_Esquema.png
    ├── requirements.txt
    └── README.md            


📝 Justificación de Diseño (¿Por qué UDP?)
------------------------------------------

Se eligió **UDP sobre TCP** debido a la naturaleza de los datos GPS en tiempo real:

1.  **Prioridad a la Actualidad:** En rastreo gps, es preferible perder un paquete y recibir el siguiente con la posición actual, que recibir un paquete antiguo con retraso por retransmisiones TCP (_Head-of-line blocking_).
    
2.  **Eficiencia Energética:** UDP permite un modelo "Fire and Forget". El dispositivo despierta, envía y vuelve a dormir inmediatamente, ahorrando ciclos de CPU y batería de la radio.