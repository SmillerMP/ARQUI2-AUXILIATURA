#!/bin/sh
set -e

MQTT_BROKER_URL=${MQTT_BROKER_URL:-localhost:9001}
MQTT_USER=${MQTT_USER}
MQTT_PASSWORD=${MQTT_PASSWORD}

CONFIG_TEMPLATE=/usr/share/nginx/html/config.template.js
CONFIG_FILE=/usr/share/nginx/html/config.js

echo "[INFO] Generando configuración del frontend..."
echo "[INFO] Broker URL: ${MQTT_BROKER_URL}"

if [ ! -f "$CONFIG_TEMPLATE" ]; then
    echo "[ERROR] No se encontró plantilla: $CONFIG_TEMPLATE"
    exit 1
fi

envsubst '${MQTT_BROKER_URL} ${MQTT_USER} ${MQTT_PASSWORD}' \
  < "$CONFIG_TEMPLATE" \
  > "$CONFIG_FILE"

echo "[INFO] Configuración generada en: $CONFIG_FILE"
echo "[INFO] Iniciando Nginx..."

exec "$@"
