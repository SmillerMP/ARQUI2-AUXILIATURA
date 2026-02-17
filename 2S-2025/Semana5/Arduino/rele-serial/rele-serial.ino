const uint8_t rele = 12;
const uint8_t botton = 8;

bool releEstado = false;

void setup() {
  Serial.begin(9600);
  pinMode(rele, OUTPUT);
  pinMode(botton, INPUT_PULLUP);
  digitalWrite(rele, LOW); 
}

void loop() {
  // Lectura del botón
  if (digitalRead(botton) == LOW) {
    releEstado = !releEstado;           // invierte estado
    digitalWrite(rele, releEstado);     
    Serial.println(releEstado ? "RELE_ON" : "RELE_OFF");
    delay(500); // debounce
  }

  // Lectura de comandos por Serial
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim(); // elimina saltos de línea u espacios

    if (cmd == "RELE_ON") {
      releEstado = true;
      digitalWrite(rele, HIGH);
      Serial.println("RELE_ON");
    } 
    else if (cmd == "RELE_OFF") {
      releEstado = false;
      digitalWrite(rele, LOW);
      Serial.println("RELE_OFF");
    }
  }
}
