import time
import threading
import json
import RPi.GPIO as GPIO
from paho.mqtt.client import Client, CallbackAPIVersion

# pines GPIO
GPIO.setmode(GPIO.BOARD)
PIN_LED = 11
PIN_BUTTON = 12

# definir los tipos de pines
GPIO.setup(PIN_LED, GPIO.OUT)  # pin del relé
GPIO.setup(PIN_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # botón con resistencia pull-up
GPIO.output(PIN_LED, GPIO.LOW)  # relé apagado inicialmente

# configuración MQTT
BROKER = "192.168.1.5"
PORT = 1883
USER = "smillermp"
PASSWORD = "arqui2"
TOPIC_CHAT = "chat/messages"

# crear conexion con el broker
client = Client(client_id="pi-zero2", callback_api_version=CallbackAPIVersion.VERSION2)
client.username_pw_set(USER, PASSWORD)

def lecturaBoton():
    """Función que corre en un hilo separado para leer el botón continuamente"""
    ultimo_estado = GPIO.input(PIN_BUTTON)  # Inicializamos la variable antes del bucle

    while True:
        estado_actual = GPIO.input(PIN_BUTTON)
        
        # Detectar flanco descendente (botón presionado)
        if ultimo_estado == GPIO.HIGH and estado_actual == GPIO.LOW:
            print("Botón presionado")

            # Publicar mensaje en el chat
            mensaje_chat = json.dumps({"sender": "pi-zero2", "message": "hola arqui 2"})
            client.publish(TOPIC_CHAT, mensaje_chat)

            # Debounce
            time.sleep(0.3)
        
        ultimo_estado = estado_actual
        time.sleep(0.05)  # Leer cada 50ms


def lecturaComando(comando):
    """Procesar comandos del chat"""
    if comando == "LED_ON":
        GPIO.output(PIN_LED, GPIO.HIGH)
        print("--> LED ENCENDIDO")
    elif comando == "LED_OFF":
        GPIO.output(PIN_LED, GPIO.LOW)
        print("--> LED APAGADO")
    else:
        print("--> Comando no reconocido:", comando)

# Callbacks MQTT
def on_connect(client, userdata, flags, reasonCode, properties=None):
    print("Conectado al broker con código:", reasonCode)
    client.subscribe(TOPIC_CHAT)
    print(f"LED inicial: {'ENCENDIDO' if GPIO.input(PIN_LED) else 'APAGADO'}")

def on_message(client, userdata, msg):
    try:
        # Parsear el mensaje JSON del chat
        payload = json.loads(msg.payload.decode())
        mensaje = payload.get("message", "")
        sender = payload.get("sender", "")
        
        print(f"Mensaje recibido de {sender}: {mensaje}")
        
        # Verificar si el mensaje contiene un comando
        mensaje_upper = mensaje.upper().strip()
        if mensaje_upper == "LED_ON" or mensaje_upper == "LED ON":
            lecturaComando("LED_ON")
        elif mensaje_upper == "LED_OFF" or mensaje_upper == "LED OFF":
            lecturaComando("LED_OFF")
            
    except json.JSONDecodeError:
        print("Error: Mensaje no es JSON válido")
    except Exception as e:
        print(f"Error procesando mensaje: {e}")

client.on_connect = on_connect
client.on_message = on_message

# Conectar al broker y empezar el loop
client.connect(BROKER, PORT, 60)
client.loop_start()  # loop en segundo plano para recibir mensajes

# Crear y iniciar el hilo para leer el botón
hilo_boton = threading.Thread(target=lecturaBoton, daemon=True)
hilo_boton.start()

print("Sistema iniciado. Presiona Ctrl+C para salir.")
print("> Escuchando comandos del chat en:", TOPIC_CHAT)
print("> Comandos disponibles: LED_ON, LED_OFF")

# Mantener el programa corriendo hasta interrupción
try:
    while True:
        time.sleep(1)  # sleep para no usar CPU innecesariamente
except KeyboardInterrupt:
    print("Cerrando...")
    client.loop_stop()
    GPIO.cleanup()  # Limpiar GPIO al salir
