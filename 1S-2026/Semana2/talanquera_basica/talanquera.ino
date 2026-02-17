// Referencia https://programarfacil.com/blog/arduino-blog/servomotor-con-arduino/
// Referencia https://naylampmechatronics.com/blog/22_tutorial-modulo-lector-rfid-rc522.html
#include <LiquidCrystal_I2C.h>
#include <Servo.h>
#include <SPI.h>
#include <MFRC522.h>

//La dirección puede cambiar, 0x27 o 0x3F
LiquidCrystal_I2C lcd(0x27, 16, 2);

const int botonEspacio1 = 2;
const int botonEspacio2 = 3;

bool espacioOcupado1 = false;
bool espacioOcupado2 = false;


// Servomotor
Servo talanquera;
const int pinServo = 9;

const int botonPaso = 4;

// RFID
#define SS_PIN 10
#define RST_PIN 8
MFRC522 rfid(SS_PIN, RST_PIN);

// Estado talanquera
bool talanqueraAbierta = false;


void setup(){
  
//INPUT_PULLUP porque no usa resistencias externas, usa las internas de Arduino
  pinMode(botonEspacio1, INPUT_PULLUP);
  pinMode(botonEspacio2, INPUT_PULLUP);

  lcd.init();
  lcd.backlight();
//El cursor siempre se posiciona antes de escribir con print()
  lcd.setCursor(0, 0);
  lcd.print("Parqueo Arqui2");
  delay(300);

  // Servo
  talanquera.attach(pinServo);
  talanquera.write(0); // Cerrada

  pinMode(botonPaso, INPUT_PULLUP);

  // RFID
  SPI.begin();
  rfid.PCD_Init();

}

void loop(){
  bool nuevoEspacio1 = (digitalRead(botonEspacio1) == LOW);
  bool nuevoEspacio2 = (digitalRead(botonEspacio2) == LOW);

  if(nuevoEspacio1 != espacioOcupado1 || nuevoEspacio2 != espacioOcupado2){
    espacioOcupado1 = nuevoEspacio1;
    espacioOcupado2 = nuevoEspacio2;
    lcd.clear();
    lcd.setCursor(0, 0);
    if (espacioOcupado1 && espacioOcupado2) {
      lcd.print("Parqueo lleno");
    } else {
      lcd.print("Parqueo libre");
    }
    lcd.setCursor(0,1);
    if (espacioOcupado1) {
      lcd.print("OC1 ");
    } else {
      lcd.print("LIB1 ");
    }

    lcd.print(espacioOcupado2 ? "OC2 " : "LIB2 ");
  }

  // Aquí se lee el RFID
  if (!talanqueraAbierta && rfid.PICC_IsNewCardPresent() && rfid.PICC_ReadCardSerial()) {
    
    lcd.clear();
    lcd.setCursor(0,0);
    lcd.print("Acceso permitido");
    
    // Abriendo la talanquera
    for(int i = 0; i <= 90; i++){
      talanquera.write(i);
      delay(20);
    }
    talanqueraAbierta = true;

    rfid.PICC_HaltA();
  }

  // para cerrar la talanquera
  if (talanqueraAbierta && digitalRead(botonPaso) == LOW) {
    
    lcd.clear();
    lcd.setCursor(0,0);
    lcd.print("Vehiculo paso");
    
    talanquera.write(0); // Cerrar
    talanqueraAbierta = false;

    delay(500);
  }
  delay(150);
}