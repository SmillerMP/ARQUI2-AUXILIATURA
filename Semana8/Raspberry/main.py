import time
import threading
import board
import json
import adafruit_dht
from paho.mqtt.client import Client, CallbackAPIVersion

# Configuración
PIN_DHT = board.D23  # GPIO23 (pin físico 16)
BROKER = "192.168.1.5"
PORT = 1883
USER = "smillermp"
PASSWORD = "arqui2"
TOPIC_DHT = "silo/dht11"

# Crear conexión MQTT
client = Client(client_id="pi-zero2", callback_api_version=CallbackAPIVersion.VERSION2)
client.username_pw_set(USER, PASSWORD)

# Definir función de conexión
def on_connect(client, userdata, flags, reasonCode, properties=None):
    print("Conectado al broker con código:", reasonCode)

client.on_connect = on_connect

# Inicializar el sensor DHT11
dhtDevice = adafruit_dht.DHT11(PIN_DHT)

# Lectura del DHT11 y publicación en MQTT
def lecturaDHT():
    while True:
        try:
            temp = dhtDevice.temperature
            hum = dhtDevice.humidity
            if temp is not None and hum is not None:
                payload = {"temp": temp, "hum": hum}
                client.publish(TOPIC_DHT, json.dumps(payload), retain=True)
                print(f"DHT11 -> Temp: {temp:.1f}°C, Hum: {hum:.1f}%")
            else:
                print("Lectura inválida del DHT11")
        except Exception as e:
            # La librería puede lanzar errores si la lectura falla
            print("Error leyendo el DHT11:", e)
        time.sleep(5)  # leer cada 5 segundos


# Inciar conexión MQTT
client.connect(BROKER, PORT, 60)
client.loop_start()

# Iniciar hilo del DHT11
hilo_dht = threading.Thread(target=lecturaDHT, daemon=True)
hilo_dht.start()

print("Sistema iniciado. Ctrl+C para salir.")
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Cerrando...")
    client.loop_stop()
