#include <ESP8266WiFi.h>
#include <PubSubClient.h>

// Configuración WiFi
const char* ssid = "***********";         // Cambia por tu red WiFi
const char* password = "***********";     // Cambia por tu contraseña WiFi

// Configuración MQTT
const char* mqtt_server = "192.168.1.5";
const int mqtt_port = 1883;
const char* mqtt_user = "smillermp";
const char* mqtt_password = "arqui2";
const char* client_id = "nodemcu-silo";

// Topics MQTT
const char* topic_cmd = "silo/control";
const char* topic_status = "silo/estado";

// Pines GPIO (NodeMCU)
const int PIN_RELAY = D1;    // GPIO5 - Pin del relé
const int PIN_BUTTON = D2;   // GPIO4 - Pin del botón

// Variables para el botón
bool ultimo_estado_boton = HIGH;
unsigned long ultimo_debounce = 0;
const unsigned long debounce_delay = 300;

// Variables para el relé
bool estado_rele = false;

// Objetos WiFi y MQTT
WiFiClient espClient;
PubSubClient client(espClient);

void setup() {
  Serial.begin(115200);
  Serial.println();
  Serial.println("Iniciando sistema de control de relé...");
  
  // Configurar pines
  pinMode(PIN_RELAY, OUTPUT);
  pinMode(PIN_BUTTON, INPUT_PULLUP);
  digitalWrite(PIN_RELAY, LOW);  // Relé apagado inicialmente
  
  // Conectar a WiFi
  setup_wifi();
  
  // Configurar MQTT
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);
  
  Serial.println("Sistema iniciado correctamente");
  Serial.println("Comandos MQTT en topic: " + String(topic_cmd));
  Serial.println("Estados publicados en: " + String(topic_status));
  Serial.println("También puedes usar el botón físico");
}

void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Conectando a WiFi: ");
  Serial.println(ssid);
  
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  Serial.println();
  Serial.println("WiFi conectado!");
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());
}

void callback(char* topic, byte* payload, unsigned int length) {
  // Convertir payload a string
  String comando = "";
  for (int i = 0; i < length; i++) {
    comando += (char)payload[i];
  }
  
  Serial.println("Comando recibido por MQTT: " + comando);
  procesarComando(comando);
}

void procesarComando(String comando) {
  if (comando == "RELE_ON") {
    digitalWrite(PIN_RELAY, HIGH);
    estado_rele = true;
    client.publish(topic_status, "RELE_ON", true);  // retain = true
    Serial.println("--> Relé ENCENDIDO");
    
  } else if (comando == "RELE_OFF") {
    digitalWrite(PIN_RELAY, LOW);
    estado_rele = false;
    client.publish(topic_status, "RELE_OFF", true);  // retain = true
    Serial.println("--> Relé APAGADO");
    
  } else {
    Serial.println("--> Comando no reconocido: " + comando);
  }
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Intentando conexión MQTT...");
    
    if (client.connect(client_id, mqtt_user, mqtt_password)) {
      Serial.println(" conectado!");
      
      // Suscribirse al topic de comandos
      client.subscribe(topic_cmd);
      Serial.println("Suscrito a: " + String(topic_cmd));
      
      // Publicar estado inicial
      String estado_inicial = estado_rele ? "RELE_ON" : "RELE_OFF";
      client.publish(topic_status, estado_inicial.c_str(), true);
      Serial.println("Estado inicial publicado: " + estado_inicial);
      
    } else {
      Serial.print(" falló, rc=");
      Serial.print(client.state());
      Serial.println(" reintentando en 5 segundos");
      delay(5000);
    }
  }
}

void leerBoton() {
  bool estado_actual_boton = digitalRead(PIN_BUTTON);
  unsigned long tiempo_actual = millis();
  
  // Detectar flanco descendente con debounce
  if (ultimo_estado_boton == HIGH && estado_actual_boton == LOW) {
    if (tiempo_actual - ultimo_debounce > debounce_delay) {
      
      // Cambiar estado del relé
      estado_rele = !estado_rele;
      digitalWrite(PIN_RELAY, estado_rele ? HIGH : LOW);
      
      // Publicar nuevo estado
      String nuevo_estado = estado_rele ? "RELE_ON" : "RELE_OFF";
      if (client.connected()) {
        client.publish(topic_status, nuevo_estado.c_str(), true);
      }
      
      Serial.println("Botón presionado. Estado del relé: " + nuevo_estado);
      ultimo_debounce = tiempo_actual;
    }
  }
  
  ultimo_estado_boton = estado_actual_boton;
}

void loop() {
  // Mantener conexión WiFi
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi desconectado, reintentando...");
    setup_wifi();
  }
  
  // Mantener conexión MQTT
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
  
  // Leer botón
  leerBoton();
  
  // Pequeña pausa para no saturar el procesador
  delay(50);
}