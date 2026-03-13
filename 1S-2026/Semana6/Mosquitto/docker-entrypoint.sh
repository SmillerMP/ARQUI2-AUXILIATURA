#!/bin/sh
set -e

# Configuración del usuario y contraseña
MQTT_USER=${MQTT_USER}
MQTT_PASSWORD=${MQTT_PASSWORD}
PWFILE=/mosquitto/config/pwfile

# Crear el archivo de contraseñas si no existe o está vacío
if [ ! -s "$PWFILE" ]; then
    echo "[INFO] Creando archivo de contraseñas para usuario: $MQTT_USER"
    mosquitto_passwd -b -c "$PWFILE" "$MQTT_USER" "$MQTT_PASSWORD"
    echo "[INFO] Usuario creado exitosamente"
else
    echo "[INFO] Archivo de contraseñas ya existe"
fi

# Asegurar permisos correctos
chmod 0600 "$PWFILE" 2>/dev/null || true
chown mosquitto:mosquitto "$PWFILE" 2>/dev/null || true

echo "[INFO] Iniciando Mosquitto..."

# Ejecutar el comando original de Mosquitto
exec "$@"
