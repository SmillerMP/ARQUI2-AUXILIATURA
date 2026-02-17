FROM eclipse-mosquitto

# copia el archivo de configuración de Mosquitto
COPY ./config/mosquitto.conf /mosquitto/config/mosquitto.conf
COPY ./config/pwfile /mosquitto/config/pwfile
# Exponemos el puerto 1883 para MQTT
EXPOSE 1883
# Exponemos el puerto 9001 para WebSockets
EXPOSE 9001

# Comando para iniciar Mosquitto
CMD ["mosquitto", "-c", "/mosquitto/config/mosquitto.conf", "-v"]

