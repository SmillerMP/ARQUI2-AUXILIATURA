FROM eclipse-mosquitto:latest

# Crear directorios necesarios
RUN mkdir -p /mosquitto/config /mosquitto/data /mosquitto/log

# Copiar configuración
COPY config/mosquitto.conf /mosquitto/config/mosquitto.conf

# Copiar script de inicialización
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Asegurar permisos
RUN chown -R mosquitto:mosquitto /mosquitto

# El script creará el pwfile automáticamente si no existe
ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["/usr/sbin/mosquitto", "-c", "/mosquitto/config/mosquitto.conf"]
