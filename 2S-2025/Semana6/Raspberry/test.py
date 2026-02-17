import RPi.GPIO as GPIO
import time

# Configuración de pines
GPIO.setmode(GPIO.BOARD)
PIN_LED = 11      # LED de prueba
PIN_BUTTON = 12   # Botón de prueba

GPIO.setup(PIN_LED, GPIO.OUT)
GPIO.setup(PIN_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # pull-up interno

try:
    while True:
        if GPIO.input(PIN_BUTTON) == GPIO.LOW:  # botón presionado
            GPIO.output(PIN_LED, GPIO.HIGH)
            print("Botón presionado → LED ON")
        else:
            GPIO.output(PIN_LED, GPIO.LOW)
            print("Botón suelto → LED OFF")
        time.sleep(0.05)  # pequeño retardo para no saturar la CPU
except KeyboardInterrupt:
    print("Cerrando...")
finally:
    GPIO.cleanup()

