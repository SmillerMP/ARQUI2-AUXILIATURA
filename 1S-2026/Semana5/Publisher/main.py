from paho.mqtt.client import Client, CallbackAPIVersion
import time
import random
import threading
import os


# Configuración MQTT (soporta variables de entorno para Docker)
BROKER = os.getenv("BROKER", "localhost")
PORT = int(os.getenv("PORT", "1883"))
TOPIC_GAS = "parqueo/gas"
USERNAME = os.getenv("MQTT_USER", "pro-auxes")
PASSWORD = os.getenv("MQTT_PASSWORD", "arqui2")


def on_connect(client, userdata, flags, reasonCode, properties=None):
    if reasonCode == 0:
        print("[!] Conectado al broker MQTT", flush=True)
    else:
        print(f"[ERROR] Error de conexión: código {reasonCode}", flush=True)


def publicar_datos_gas():
    while True:
        valor = random.randint(10, 78)
        client.publish(TOPIC_GAS, valor, retain=False)
        print(f"[GAS] {valor} ppm", flush=True)
        time.sleep(random.randint(1, 5))

def publicar_datos_parqueo():
    while True:
        espacio = random.randint(1, 5)
        topic_parqueos = f"parqueo/espacio/{espacio}"
        valor = random.choice(["ocupado", "libre"])
        client.publish(topic_parqueos, valor, retain=True)
        print(f"[P{espacio}] {valor}", flush=True)
        time.sleep(random.randint(5, 15))


# Crear conexión MQTT
client = Client(client_id="publisher-random", callback_api_version=CallbackAPIVersion.VERSION2)
client.username_pw_set(USERNAME, PASSWORD)

client.on_connect = on_connect

print(f"Conectando a {BROKER}:{PORT}...", flush=True)
client.connect(BROKER, PORT, 60)
client.loop_start()


# preparacion hilos
hilo_gas = threading.Thread(target=publicar_datos_gas, daemon=True)
hilo_parqueo = threading.Thread(target=publicar_datos_parqueo, daemon=True)


if __name__ == "__main__":
    print("[Publisher] Iniciando...\n", flush=True)
    try:
        hilo_gas.start()
        hilo_parqueo.start()

        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[Publisher] Detenido", flush=True)
        client.loop_stop()




