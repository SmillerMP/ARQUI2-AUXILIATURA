const int8_t pinRele = 5;   //Variable para el pin del rele
const int8_t pinBoton = 3;  //Variable para el pin del boton

void setup() {
  // put your setup code here, to run once:

  pinMode(pinRele, OUTPUT);
  pinMode(pinBoton, INPUT_PULLUP);    // uso de la resistencia pull-up 

}

void loop() {
  // put your main code here, to run repeatedly:

  // Deteccion presion del boton
  if (digitalRead(pinBoton) == LOW) {
    digitalWrite(pinRele, HIGH);
    delay(3000);   
  } 

  digitalWrite(pinRele, LOW);
}
