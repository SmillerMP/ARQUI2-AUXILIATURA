import time
import threading
import RPi.GPIO as GPIO
from paho.mqtt.client import Client, CallbackAPIVersion

# pines GPIO
GPIO.setmode(GPIO.BOARD)
PIN_RELAY = 11
PIN_BUTTON = 12

# definir los tipos de pines
GPIO.setup(PIN_RELAY, GPIO.OUT)  # pin del relé
GPIO.setup(PIN_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # botón con resistencia pull-up
GPIO.output(PIN_RELAY, GPIO.LOW)  # relé apagado inicialmente

# configuración MQTT
BROKER = "192.168.1.5"
PORT = 1883
USER = "smillermp"
PASSWORD = "arqui2"
TOPIC_CMD = "silo/control"
TOPIC_STATUS = "silo/estado"

# crear conexion con el broker
client = Client(client_id="pi-zero2", callback_api_version=CallbackAPIVersion.VERSION2)
client.username_pw_set(USER, PASSWORD)

# Variable para controlar el hilo del botón

def lecturaBoton():
    """Función que corre en un hilo separado para leer el botón continuamente"""
    ultimo_estado = GPIO.input(PIN_BUTTON)  # Inicializamos la variable antes del bucle

    while True:
        estado_actual = GPIO.input(PIN_BUTTON)
        
        # Detectar flanco descendente (botón presionado)
        if ultimo_estado == GPIO.HIGH and estado_actual == GPIO.LOW:
            # Cambiar estado del relé
            GPIO.output(PIN_RELAY, not GPIO.input(PIN_RELAY))
            estado_rele = "RELE_ON" if GPIO.input(PIN_RELAY) else "RELE_OFF"
            
            # Publicar estado con mensaje retenido
            client.publish(TOPIC_STATUS, estado_rele, retain=True)
            print(f"Botón presionado. Estado del relé: {estado_rele}")

            # Debounce
            time.sleep(0.3)
        
        ultimo_estado = estado_actual
        time.sleep(0.05)  # Leer cada 50ms


def lecturaComando(comando):
    """Procesar comandos MQTT"""
    if comando == "RELE_ON":
        GPIO.output(PIN_RELAY, GPIO.HIGH)
        client.publish(TOPIC_STATUS, "RELE_ON", retain=True)
        print("--> Relé ENCENDIDO")
    elif comando == "RELE_OFF":
        GPIO.output(PIN_RELAY, GPIO.LOW)
        client.publish(TOPIC_STATUS, "RELE_OFF", retain=True)
        print("--> Relé APAGADO")
    else:
        print("--> Comando no reconocido:", comando)

# Callbacks MQTT
def on_connect(client, userdata, flags, reasonCode, properties=None):
    print("Conectado al broker con código:", reasonCode)
    client.subscribe(TOPIC_CMD)  # escuchar comandos
    
    # Publicar estado inicial del relé al conectarse
    estado_inicial = "RELE_ON" if GPIO.input(PIN_RELAY) else "RELE_OFF"
    client.publish(TOPIC_STATUS, estado_inicial, retain=True)
    print(f"Estado inicial publicado: {estado_inicial}")

def on_message(client, userdata, msg):
    comando = msg.payload.decode()
    print("Comando recibido por MQTT:", comando)
    lecturaComando(comando)

client.on_connect = on_connect
client.on_message = on_message

# Conectar al broker y empezar el loop
client.connect(BROKER, PORT, 60)
client.loop_start()  # loop en segundo plano para recibir mensajes

# Crear y iniciar el hilo para leer el botón
hilo_boton = threading.Thread(target=lecturaBoton, daemon=True)
hilo_boton.start()

print("Sistema iniciado. Presiona Ctrl+C para salir.")
print("> Envía comandos MQTT al topic:", TOPIC_CMD)
print("> Estados del relé se publican en:", TOPIC_STATUS)
print("> También puedes usar el botón físico")

# Mantener el programa corriendo hasta interrupción
try:
    while True:
        time.sleep(1)  # sleep para no usar CPU innecesariamente
except KeyboardInterrupt:
    print("Cerrando...")
    client.loop_stop()
    GPIO.cleanup()  # Limpiar GPIO al salir
