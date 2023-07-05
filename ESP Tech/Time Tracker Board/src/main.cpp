#include <ESPAsyncWebServer.h>
#include <HTTPClient.h>
#include <Preferences.h>
#include <WiFi.h>
#include <esp_wifi.h>
#include <inttypes.h>

#include "http_client.hpp"
#include "timer.hpp"
#include "utils.hpp"

const char* SSID = "PiD-AP";
const char* PASSWORD = "longleggedducks";

IPAddress gatewayIP(192, 168, 132, 100);
IPAddress subnet(255, 255, 255, 0);
IPAddress localIP(192, 168, 132, 180);

AsyncWebServer server(80);
HTTPClientWrapper http_client;

LaserTimer* Lane1;
LaserTimer* Lane2;

int lastConnectionAttemptTime = 0;
int timeBetweenConnectionAttempts = 10000;

void setup() {
    if (DEBUG) {
        Serial.begin(115200);
    }

    pinMode(LED_BUILTIN, OUTPUT);

    Preferences preferences;
    preferences.begin("wifi", false);
    if (!preferences.isKey("serverURL")) {
        preferences.putString("serverURL", "http://192.168.132.105:3000");
    }
    serverURL = preferences.getString("serverURL");

    // Connect to the access point with a static IP
    WiFi.config(localIP, gatewayIP, subnet);
    WiFi.begin(SSID, PASSWORD);

    Lane1 = new LaserTimer(
        1, 22, 23, 18, 19, 13);
    Lane2 = new LaserTimer(
        2, 25, 26, 32, 33, 27);

    while (WiFi.status() != WL_CONNECTED) {
        if (DEBUG) {
            Serial.println("Not connected yet, retrying...");
        }
        blink(100);   // Short blinks to indicate we haven't connected yet
        delay(1000);  // Wait until we're connected properly
        WiFi.reconnect();
    }

    if (DEBUG) {
        Serial.print("Connected to the network with IP: ");
        Serial.println(WiFi.localIP());
    }

    blink(999);  // Long blink to indicate we're good to go

    makeEndpoints(server, Lane1, Lane2);
    server.begin();
}

void loop() {
    if (Lane1->laserTripped()) {
        if (Lane2->getPositionValue() == 1) {
            Lane1->setPositionValue(2);
        } else {
            Lane1->setPositionValue(1);
        }
        Lane1->stopRunTimer();
    }

    if (Lane2->laserTripped()) {
        if (Lane1->getPositionValue() == 1) {
            Lane2->setPositionValue(2);
        } else {
            Lane2->setPositionValue(1);
        }
        Lane2->stopRunTimer();
    }

    if ((millis() - lastConnectionAttemptTime) > timeBetweenConnectionAttempts) {
        lastConnectionAttemptTime = millis();
        if (!HTTPClientWrapper::get(serverURL + "/check-connectivity", true)) {
            if (DEBUG) {
                Serial.println("Lost connection to the server, restarting...");
            }
            ESP.restart();
        }

        // Gives a 10 second window upon startup to change the IP
        if (timeBetweenConnectionAttempts > 1000) {
            timeBetweenConnectionAttempts = 1000;
            if (DEBUG) {
                Serial.println("IP change time window has passed, switching to normal connection attempts");
            }
        }
    }
}
