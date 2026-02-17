import serial
import time
import threading
from paho.mqtt.client import Client, CallbackAPIVersion

# conexión Serial con Arduino
arduino = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
time.sleep(2)  # espera que Arduino inicialice Serial

# configuración MQTT
BROKER = "ip_broker"
PORT = 1883
USER = "usuario_broker"
PASSWORD = "password_broker"
TOPIC_CMD = "silo/control"
TOPIC_STATUS = "silo/estado"

# crear conexion con el broker
client = Client(client_id="pi-arduino", callback_api_version=CallbackAPIVersion.VERSION2)
client.username_pw_set(USER, PASSWORD)

# Fución para enviar comandos al Arduino
def enviar_comando(cmd):
    arduino.write((cmd + '\n').encode())
    print(f"Comando enviado: {cmd}")

# Función para leer datos del Arduino constantemente
def leer_serial():
    while True:
        try:
            if arduino.in_waiting > 0:  # si hay datos disponibles
                respuesta = arduino.readline().decode().strip()
                if respuesta:
                    print("Arduino respondió:", respuesta)
                    # Publica el estado en MQTT
                    client.publish(TOPIC_STATUS, respuesta)
        except Exception as e:
            print(f"Error leyendo serial: {e}")
            time.sleep(0.1)
        time.sleep(0.1)  # pequeña pausa para no saturar el CPU

# Callbacks MQTT
def on_connect(client, userdata, flags, reasonCode, properties=None):
    print("Conectado al broker con código:", reasonCode)
    client.subscribe(TOPIC_CMD)  # escuchar comandos

def on_message(client, userdata, msg):
    comando = msg.payload.decode()
    print("Comando recibido por MQTT:", comando)
    enviar_comando(comando)

client.on_connect = on_connect
client.on_message = on_message

# Conectar al broker y empezar el loop
client.connect(BROKER, PORT, 60)
client.loop_start()  # loop en segundo plano para recibir mensajes

# Hilo en segundo plano para leer el Serial
serial_thread = threading.Thread(target=leer_serial, daemon=True)
serial_thread.start()

print("Sistema iniciado. Presiona Ctrl+C para salir.")
print("> Envía comandos MQTT al topic:", TOPIC_CMD)
print("> Estados del relé se publican en:", TOPIC_STATUS)
print("> También puedes usar el botón físico en el Arduino")

# Mantener el programa corriendo hasta interrupción
try:
    while True:
        time.sleep(1) # sleep para no usar CPU innecesariamente
except KeyboardInterrupt:
    print("Cerrando...")
    client.loop_stop()
    arduino.close()