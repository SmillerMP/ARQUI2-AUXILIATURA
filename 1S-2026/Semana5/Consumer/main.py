import json
import os
from datetime import datetime
from pymongo import MongoClient
import paho.mqtt.client as mqtt

# Configuración MongoDB (soporta variables de entorno para Docker)
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "27017"))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "arqui2-nosql")
DB_NAME = os.getenv("DB_NAME", "sensores")

# Configuración del broker MQTT (soporta variables de entorno para Docker)
BROKER = os.getenv("BROKER", "localhost")
PORT = int(os.getenv("PORT", "1883"))
TOPICS = ["parqueo/gas", "parqueo/espacio/#"]
MQTT_USER = os.getenv("MQTT_USER", "pro-auxes")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "arqui2")


# Conexión a MongoDB
try:
    mongo_uri = f"mongodb://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/?authSource=admin"
    mongo_client = MongoClient(mongo_uri)
    db = mongo_client[DB_NAME]
    print(f"[!] MongoDB conectado: {DB_NAME}", flush=True)
except Exception as e:
    print(f"[ERROR] Error MongoDB: {e}", flush=True)
    raise


def decide_collection(payload, topic):
    t = topic.lower() if topic else ""
    # Prioriza decisión por topic (publisher usa 'parqueo/gas' y 'parqueo/espacio/...')
    if t.startswith("parqueo/gas"):
        return "registro_gas"
    if t.startswith("parqueo/espacio"):
        return "registro_espacios"

    # Fallback: revisar payload por claves que indiquen gas
    if isinstance(payload, dict):
        if payload.get("type") == "gas" or "gas" in payload or "co" in payload:
            return "registro_gas"

    if "gas" in t:
        return "registro_gas"
    return "registro_espacios"


def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("[!] MQTT conectado", flush=True)
        for topic in TOPICS:
            client.subscribe(topic)
        print(f"[!] Suscrito a: {', '.join(TOPICS)}", flush=True)
    else:
        print(f"[ERROR] Error MQTT: código {rc}", flush=True)


def on_message(client, userdata, msg):
    try:
        raw = msg.payload.decode(errors="ignore")
        try:
            payload = json.loads(raw)
        except Exception:
            payload = raw

        doc = {
            "topic": msg.topic,
            "payload": payload,
            "received_at": datetime.now()
        }

        coll_name = decide_collection(payload, msg.topic)
        collection = db[coll_name]
        collection.insert_one(doc)
        print(f"[!] {msg.topic}: {payload}", flush=True)
    except Exception as e:
        print(f"[ERROR] {e}", flush=True)


def main():
    print("[Consumer] Iniciando...\n", flush=True)
    
    client = mqtt.Client(
        client_id="consumer-pc",
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2
    )
    client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    client.on_connect = on_connect
    client.on_message = on_message

    print(f"Conectando a {BROKER}:{PORT}...", flush=True)
    client.connect(BROKER, PORT, 60)
    client.loop_forever()


if __name__ == "__main__":
    main()