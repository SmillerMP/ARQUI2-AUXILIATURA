#include <Wire.h>
#include <Adafruit_PN532.h>

// I2C
#define PN532_IRQ   (2)
#define PN532_RESET (3)

// ------------------ Tarjetas y Usuarios Autorizados ------------------
// Cada fila = UID de una tarjeta
uint8_t tarjetasUID[][7] = {
  {0x53, 0xA6, 0xF1, 0x2C, 0x00, 0x00, 0x00},
  {0x04, 0X9F, 0X71, 0X3A, 0XAB, 0x14, 0x90},
};

// Nombre asociado a cada UID
String usuarios[] = {
  "Pepe the Frog",
  "Elliot Alderson",
};

// cantidad de usuarios
const int totalUsuarios = sizeof(usuarios) / sizeof(usuarios[0]);

Adafruit_PN532 nfc(PN532_IRQ, PN532_RESET);

// ----------------------------------------------------------

void setup() {
  Serial.begin(115200);
  while (!Serial);

  Serial.println("Iniciando sistema RFID...");

  Wire.begin();
  nfc.begin();

  nfc.SAMConfig();

  Serial.println("Sistema listo. Acerque una tarjeta.");
}

// ----------------------------------------------------------

void loop() {

  boolean success;
  uint8_t uid[7];      // buffer donde se guarda el UID leído
  uint8_t uidLength;   // longitud real del UID

  success = nfc.readPassiveTargetID(PN532_MIFARE_ISO14443A, uid, &uidLength);

  if (success) {

    Serial.print("\nUID detectado:");
    for (uint8_t i = 0; i < uidLength; i++) {
      Serial.print(" 0x");
      if (uid[i] < 0x10) Serial.print('0');
      Serial.print(uid[i], HEX);
    }
    Serial.println();

    // buscar el usuario
    String nombre = buscarUsuario(uid, uidLength);

    if (nombre != "") {
      Serial.print("Acceso permitido -> ");
      Serial.println(nombre);
    } else {
      Serial.println("Acceso denegado");
    }

    delay(1500); // evita múltiples lecturas seguidas
  }

  delay(100);
}


// -----------------------------------------------------------------

// Busca el usuario según UID leído
String buscarUsuario(uint8_t *uidLeido, uint8_t uidLength) {

  for (int i = 0; i < totalUsuarios; i++) {
    if (compararUID(uidLeido, tarjetasUID[i], uidLength)) {
      return usuarios[i];
    }
  }

  return "";
}

// Compara dos UID byte por byte
bool compararUID(uint8_t *uid1, uint8_t *uid2, uint8_t length) {
  for (uint8_t i = 0; i < length; i++) {
    if (uid1[i] != uid2[i]) return false;
  }

  return true;
}
