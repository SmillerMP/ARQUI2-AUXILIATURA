unsigned long ultimaLectura;           //tiempo de la ultima lectura del botonLed
const long timpoActivo = 10000;        // tiempo de encendido activo del led
const uint8_t ledPin = 13;             // pin para el led
const uint8_t buttonInterrupcion = 2;  // boton para la interrupcion en el pin 2
const uint8_t buttonLed = 10;          //boton para el manejo del led en el pin 10
volatile bool ledActiva = false;

void setup() {
  // put your setup code here, to run once:

  Serial.begin(9600);

  // Pines para el manejo de led y botones
  pinMode(ledPin, OUTPUT);
  // botones en pullup,
  pinMode(buttonInterrupcion, INPUT_PULLUP);
  pinMode(buttonLed, INPUT_PULLUP);

  // interrupcion, llama a la funcion cancelar cuando el estado del pin cambia
  attachInterrupt(digitalPinToInterrupt(buttonInterrupcion), cancelar, CHANGE);
}


void loop() {
  // put your main code here, to run repeatedly:

  /*
    detecta si el boton esta precionado
    cambia ciertas variables para el control del led, 
    ledActiva y registra el tiempo de encendido actual con millis
  */
  if (digitalRead(buttonLed) == LOW) {
    Serial.println("Iniciando proceso de 10 segundos...");
    ledActiva = true;
    delay(200);
    ultimaLectura = millis();
  }


  /*
    verifica que la variable del led sea true y
    que el tiempo entre la ultima lectura y el tiempo de encendido actual (millis)
    sea menor a 10 segundos. (mantendra 10 segundos encendido el led)
  */
  if (ledActiva && (millis() - ultimaLectura < timpoActivo)) {
    digitalWrite(ledPin, HIGH);
  } else {
    digitalWrite(ledPin, LOW);
  }
}


// funcion para la interrupcion, debe ser una funcion corta y sin delay
void cancelar() {
  ledActiva = false;
  Serial.println("Proceso cancelado");
}