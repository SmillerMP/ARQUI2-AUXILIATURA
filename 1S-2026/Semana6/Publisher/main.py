from paho.mqtt.client import Client, CallbackAPIVersion
import time
import random
import threading
import os


# Configuración MQTT (soporta variables de entorno para Docker)
BROKER = os.getenv("BROKER", "localhost")
PORT = int(os.getenv("PORT", "1883"))
TOPIC_GAS = "parqueo/gas"
TOPIC_ESPACIOS = "parqueo/espacio/#"
MQTT_USER = os.getenv("MQTT_USER", "")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "")
TOTAL_SPACES = 5


estado_habilitado = {espacio: True for espacio in range(1, TOTAL_SPACES + 1)}
estado_lock = threading.Lock()


def on_connect(client, userdata, flags, reasonCode, properties=None):
    if reasonCode == 0:
        print("[!] Conectado al broker MQTT", flush=True)
        client.subscribe(TOPIC_ESPACIOS)
        print(f"[!] Suscrito a: {TOPIC_ESPACIOS}", flush=True)
    else:
        print(f"[ERROR] Error de conexión: código {reasonCode}", flush=True)


def on_message(client, userdata, msg):
    topic = msg.topic or ""
    payload = msg.payload.decode(errors="ignore").strip().lower()

    if not topic.startswith("parqueo/espacio/"):
        return

    try:
        espacio = int(topic.split("/")[-1])
    except (ValueError, IndexError):
        return

    if espacio < 1 or espacio > TOTAL_SPACES:
        return

    with estado_lock:
        if payload == "deshabilitado":
            estado_habilitado[espacio] = False
            print(f"[P{espacio}] deshabilitado", flush=True)
        elif payload in ["libre", "ocupado"]:
            estado_habilitado[espacio] = True


def publicar_datos_gas():
    while True:
        valor = random.randint(10, 78)
        client.publish(TOPIC_GAS, valor, retain=False)
        print(f"[GAS] {valor} ppm", flush=True)
        time.sleep(random.randint(1, 5))

def publicar_datos_parqueo():
    while True:
        with estado_lock:
            espacios_habilitados = [espacio for espacio, enabled in estado_habilitado.items() if enabled]

        if not espacios_habilitados:
            print("[PARKING] Todos los espacios están deshabilitados", flush=True)
            time.sleep(3)
            continue

        espacio = random.choice(espacios_habilitados)
        topic_parqueos = f"parqueo/espacio/{espacio}"
        valor = random.choice(["ocupado", "libre"])
        client.publish(topic_parqueos, valor, retain=True)
        print(f"[P{espacio}] {valor}", flush=True)
        time.sleep(random.randint(5, 10))


# Crear conexión MQTT
client = Client(client_id="publisher-random", callback_api_version=CallbackAPIVersion.VERSION2)
client.username_pw_set(MQTT_USER, MQTT_PASSWORD)

client.on_connect = on_connect
client.on_message = on_message

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




