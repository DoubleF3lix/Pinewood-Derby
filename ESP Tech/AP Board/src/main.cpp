#include "ESPAsyncWebServer.h"
#include "WiFi.h"
#include "esp_event.h"
#include "esp_wifi.h"

const char* SSID = "PiD-AP";
const char* PASSWORD = "longleggedducks";

const bool DEBUG = false;

IPAddress gatewayIP(192, 168, 132, 100);
IPAddress subnet(255, 255, 255, 0);

void blink() {
    digitalWrite(LED_BUILTIN, HIGH);
    delay(400);
    digitalWrite(LED_BUILTIN, LOW);
    delay(600);
}

void printMac(uint8_t* mac) {
    for (int i = 0; i < 6; i++) {
        Serial.printf("%02X", mac[i]);
        if (i < 5) Serial.print(":");
    }
}

void blinkAccordingToConnectedDevicesCount() {
    wifi_sta_list_t wifi_sta_list;
    tcpip_adapter_sta_list_t adapter_sta_list;

    memset(&wifi_sta_list, 0, sizeof(wifi_sta_list));
    memset(&adapter_sta_list, 0, sizeof(adapter_sta_list));

    esp_wifi_ap_get_sta_list(&wifi_sta_list);
    tcpip_adapter_get_sta_list(&wifi_sta_list, &adapter_sta_list);

    for (int i = 0; i < adapter_sta_list.num; i++) {
        blink();

        if (DEBUG) {
            Serial.print("Station #");
            Serial.print(i);
            Serial.print(" MAC: ");
            printMac(adapter_sta_list.sta[i].mac);
            Serial.println();
        }
    }
    if (DEBUG) {
        Serial.println("-----------");
    }
}

void setup() {
    // LED output
    pinMode(21, INPUT_PULLDOWN);
    pinMode(LED_BUILTIN, OUTPUT);

    WiFi.softAPConfig(gatewayIP, gatewayIP, subnet);
    WiFi.softAP(SSID, PASSWORD, 1, 0, 8);

    // Will not blink if the board gets stuck on a POWERON_RESET message. Press EN until it blinks properly.
    blink();

    if (DEBUG) {
        Serial.begin(115200);
        Serial.print("Starting AP with gateway IP of ");
        Serial.println(WiFi.softAPIP());
    }
}

void loop() {
    if (digitalRead(21) == HIGH) {
        blinkAccordingToConnectedDevicesCount();
    }
}