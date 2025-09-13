import json
import mysql.connector
from paho.mqtt.client import Client, CallbackAPIVersion

# Configuracion
DB_HOST = "localhost"        
DB_PORT = 3306
DB_USER = "root"
DB_PASSWORD = "arqui2-database"
DB_NAME = "sensores"
DB_TABLE = "dht11_lecturas"

# Configuracion del broker MQTT
BROKER = "192.168.1.5"       
PORT = 1883
TOPIC_DHT = "silo/dht11"
MQTT_USER = "smillermp"
MQTT_PASSWORD = "arqui2"

# conexion a la base de datos MySQL
db = mysql.connector.connect(
    host=DB_HOST,
    port=DB_PORT,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME
)
cursor = db.cursor()

# Definir funciones de callback MQTT
def on_connect(client, userdata, flags, reasonCode, properties=None):
    print("Conectado al broker MQTT con código:", reasonCode)
    client.subscribe(TOPIC_DHT)
    print(f"Suscrito al topic: {TOPIC_DHT}")

def on_message(client, userdata, msg):
    try:
        # Convertimos el mensaje a diccionario
        payload = json.loads(msg.payload.decode())
        temp = payload.get("temp")
        hum = payload.get("hum")

        # Insertamos en MySQL
        sql = f"INSERT INTO {DB_TABLE} (temperatura, humedad) VALUES (%s, %s)"
        cursor.execute(sql, (temp, hum))
        db.commit()
        print(f"Insertado en DB -> Temp: {temp}, Hum: {hum}")
    except Exception as e:
        print("Error procesando mensaje:", e)

# Crear cliente MQTT y conectar
client = Client(client_id="consumer-pc", callback_api_version=CallbackAPIVersion.VERSION2)
client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, PORT, 60)
client.loop_forever()
