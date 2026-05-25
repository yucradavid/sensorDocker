#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME680.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);
Adafruit_BME680 bme;

// NO subir tus datos reales a GitHub.
const char* ssid = "TU_WIFI";
const char* password = "TU_PASSWORD";

// Cambia esta IP por la IPv4 de tu PC. No uses localhost en el ESP32.
String api_url = "http://192.168.1.100:8000/api/air-quality";

const char* DEVICE_ID = "esp32-bme680-grupo-2";
const char* STATION_NAME = "Grupo 2 - Sensor";

float gas_reference = 0;
int gas_ref_count = 0;
bool calibrated = false;

const unsigned long SEND_INTERVAL_MS = 3000;
const unsigned long WIFI_RETRY_MS = 10000;
unsigned long lastSend = 0;
unsigned long lastWifiRetry = 0;

void mostrarMensaje(String linea1, String linea2 = "") {
  display.clearDisplay();
  display.setCursor(0, 10);
  display.println(linea1);
  if (linea2.length() > 0) display.println(linea2);
  display.display();
}

void conectarWiFi() {
  if (WiFi.status() == WL_CONNECTED) return;

  Serial.println("Conectando WiFi...");
  mostrarMensaje("Conectando", "WiFi...");

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  int intentos = 0;
  while (WiFi.status() != WL_CONNECTED && intentos < 30) {
    delay(500);
    Serial.print(".");
    intentos++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWiFi conectado");
    Serial.print("IP ESP32: ");
    Serial.println(WiFi.localIP());
    mostrarMensaje("WiFi OK", WiFi.localIP().toString());
    delay(1000);
  } else {
    Serial.println("\nNo se pudo conectar al WiFi");
    mostrarMensaje("Error WiFi", "Reintentando...");
  }
}

String clasificarCalidad(float iaq_score) {
  if (iaq_score < 100) return "Excelente";
  if (iaq_score < 200) return "Buena";
  return "Pobre";
}

String clasificarRiesgo(float iaq_score, float eco2, float voc) {
  if (iaq_score >= 200 || eco2 >= 800 || voc >= 15) return "ALTO";
  if (iaq_score >= 100 || eco2 >= 600 || voc >= 10) return "MEDIO";
  return "BAJO";
}

bool enviarDatos(float temperatura, float humedad, float presion, float altura, float gas, float iaq, float eco2, float voc, String calidad, String riesgo) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi no conectado. No se envio el evento.");
    return false;
  }

  HTTPClient http;
  http.begin(api_url);
  http.setTimeout(5000);
  http.addHeader("Content-Type", "application/json");

  StaticJsonDocument<768> doc;
  doc["estacion"] = STATION_NAME;
  doc["device_id"] = DEVICE_ID;
  doc["temperatura"] = temperatura;
  doc["humedad"] = humedad;
  doc["presion"] = presion;
  doc["altura"] = altura;
  doc["gas"] = gas;
  doc["iaq"] = iaq;
  doc["eco2"] = eco2;
  doc["voc"] = voc;
  doc["calidad_aire"] = calidad;
  doc["riesgo_aire"] = riesgo;
  doc["timestamp_ms"] = millis();

  String jsonStr;
  serializeJson(doc, jsonStr);

  Serial.println("Enviando evento:");
  Serial.println(jsonStr);

  int httpCode = http.POST(jsonStr);
  Serial.print("HTTP Response: ");
  Serial.println(httpCode);

  String response = http.getString();
  if (response.length() > 0) Serial.println(response);

  http.end();
  return httpCode >= 200 && httpCode < 300;
}

void setup() {
  Serial.begin(115200);
  delay(1000);

  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println("Error OLED");
    while (1);
  }

  display.clearDisplay();
  display.setTextColor(WHITE);
  display.setTextSize(1);
  mostrarMensaje("Iniciando...", "ESP32 BME680");

  if (!bme.begin(0x77)) {
    Serial.println("Error BME680 en 0x77. Probando 0x76...");
    if (!bme.begin(0x76)) {
      Serial.println("Error BME680. Revisar cableado I2C.");
      mostrarMensaje("Error BME680", "Revisar sensor");
      while (1);
    }
  }

  bme.setTemperatureOversampling(BME680_OS_8X);
  bme.setHumidityOversampling(BME680_OS_2X);
  bme.setPressureOversampling(BME680_OS_4X);
  bme.setIIRFilterSize(BME680_FILTER_SIZE_3);
  bme.setGasHeater(320, 150);

  conectarWiFi();
  Serial.println("Sistema listo.");
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    unsigned long nowWifi = millis();
    if (nowWifi - lastWifiRetry >= WIFI_RETRY_MS) {
      lastWifiRetry = nowWifi;
      conectarWiFi();
    }
  }

  if (!bme.performReading()) {
    Serial.println("No se pudo leer el BME680");
    delay(1000);
    return;
  }

  if (!calibrated) {
    gas_reference += bme.gas_resistance;
    gas_ref_count++;

    display.clearDisplay();
    display.setCursor(0, 10);
    display.println("Calibrando...");
    display.printf("%d/50\n", gas_ref_count);
    display.display();

    Serial.print("Calibrando gas: ");
    Serial.print(gas_ref_count);
    Serial.println("/50");

    if (gas_ref_count >= 50) {
      gas_reference /= 50.0;
      calibrated = true;
      Serial.println("Calibracion completa");
      Serial.print("Gas referencia: ");
      Serial.println(gas_reference);
      mostrarMensaje("Calibracion", "Completa");
      delay(1000);
    }

    delay(1000);
    return;
  }

  unsigned long now = millis();
  if (now - lastSend < SEND_INTERVAL_MS) return;
  lastSend = now;

  float temperatura = bme.temperature;
  float humedad = bme.humidity;
  float presion = bme.pressure / 100.0;
  float altura = bme.readAltitude(1013.25);
  float gas = bme.gas_resistance / 1000.0;

  float gas_score = (bme.gas_resistance / gas_reference) * 100.0;
  if (gas_score > 100) gas_score = 100;
  if (gas_score < 0) gas_score = 0;

  float hum_score;
  if (humedad >= 38 && humedad <= 42) {
    hum_score = 100;
  } else {
    hum_score = 100 - abs(humedad - 40) * 2.5;
    if (hum_score < 0) hum_score = 0;
  }

  float iaq_score = (0.75 * (100 - gas_score) + 0.25 * (100 - hum_score)) * 5;
  if (iaq_score < 0) iaq_score = 0;
  if (iaq_score > 500) iaq_score = 500;

  float eco2_real = 400 + (iaq_score * 1.8);
  float voc = gas_score / 10.0;

  String calidad = clasificarCalidad(iaq_score);
  String riesgo = clasificarRiesgo(iaq_score, eco2_real, voc);

  display.clearDisplay();
  display.setCursor(0, 0);
  display.println("--- MONITOR ---");
  display.printf("Temp: %.1f C\n", temperatura);
  display.printf("Hum: %.1f %%\n", humedad);
  display.printf("IAQ: %.0f\n", iaq_score);
  display.printf("eCO2: %.0f ppm\n", eco2_real);
  display.printf("Riesgo: %s\n", riesgo.c_str());
  display.display();

  bool enviado = enviarDatos(temperatura, humedad, presion, altura, gas, iaq_score, eco2_real, voc, calidad, riesgo);
  if (enviado) Serial.println("Evento enviado correctamente.");
  else Serial.println("Error al enviar evento.");
}
