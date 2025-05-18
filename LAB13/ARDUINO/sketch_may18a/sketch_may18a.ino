#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>

// === CONFIG ===
#define DHTPIN 4
#define DHTTYPE DHT11
#define WIFI_SSID "TP-LINK_AP_F374"
#define WIFI_PASSWORD "89847862"
#define MQTT_SERVER "192.168.18.31"
#define MQTT_PORT 1883

DHT dht(DHTPIN, DHTTYPE);
WiFiClient espClient;
PubSubClient client(espClient);

unsigned long lastMsg = 0;
const long interval = 5000;  // Send every 5 seconds

// === Setup WiFi with timeout ===
void setup_wifi() {
  Serial.print("📶 Connecting to WiFi ");
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  int tries = 0;
  while (WiFi.status() != WL_CONNECTED && tries < 40) {
    delay(250);
    Serial.print(".");
    tries++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n✅ WiFi Connected");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\n❌ WiFi connection failed!");
    // Optionally restart ESP or go into low power mode
    while (true) {
      delay(1000);  // Halt the device (or blink LED)
    }
  }
}

// === MQTT Reconnect with retry ===
void reconnect() {
  while (!client.connected()) {
    Serial.print("🔌 Attempting MQTT connection...");
    String clientId = "ESP32Client-";
    clientId += String(random(0xffff), HEX);

    if (client.connect(clientId.c_str())) {
      Serial.println("✅ MQTT Connected");
    } else {
      Serial.print("❌ failed, rc=");
      Serial.print(client.state());
      Serial.println(" | retrying in 5s");
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  dht.begin();
  setup_wifi();
  client.setServer(MQTT_SERVER, MQTT_PORT);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  unsigned long now = millis();
  if (now - lastMsg > interval) {
    lastMsg = now;

    float temperature = dht.readTemperature();
    float humidity = dht.readHumidity();

    if (isnan(temperature) || isnan(humidity)) {
      Serial.println("⚠️ Failed to read from DHT sensor!");
      return;
    }

    String tempStr = String(temperature, 2);
    String humStr = String(humidity, 2);

    // Publish to MQTT
    client.publish("esp32/dht/temp", tempStr.c_str());
    client.publish("esp32/dht/hum", humStr.c_str());

    // Serial feedback
    Serial.print("🌡 Temp: ");
    Serial.print(tempStr);
    Serial.print(" °C | 💧 Humidity: ");
    Serial.print(humStr);
    Serial.println(" %");
  }
}
