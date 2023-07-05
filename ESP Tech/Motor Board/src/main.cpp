#include <ESP32Servo.h>
#include <ESPAsyncWebServer.h>
#include <HTTPClient.h>
#include <Preferences.h>
#include <WiFi.h>
#include <esp_wifi.h>
#include <IRremote.hpp>
#include <IRFeedbackLED.hpp>

#include "globals.hpp"
#include "http_client.hpp"
#include "utils.hpp"

const char* SSID = "PiD-AP";
const char* PASSWORD = "longleggedducks";

IPAddress gatewayIP(192, 168, 132, 100);
IPAddress subnet(255, 255, 255, 0);
IPAddress localIP(192, 168, 132, 181);

AsyncWebServer server(80);
IRrecv receiver(IR_PIN);
int irFlag = 0;
Servo servoMotor;

int lastConnectionAttemptTime = 0;
int timeBetweenConnectionAttempts = 10000;

void swingMotor() {
    digitalWrite(SERVO_PIN, LOW);
    servoMotor.write(147);  // 135 degrees
    delay(250);
    digitalWrite(SERVO_PIN, HIGH);
    servoMotor.write(12);  // 0 degrees, 12 degree offset because
}

void setup() {
    if (DEBUG) {
        Serial.begin(115200);
    }

    pinMode(LED_BUILTIN, OUTPUT);
    pinMode(YELLOW_LED, OUTPUT);                     // Start sent, waiting approval (yellow)
    pinMode(GREEN_LED, OUTPUT);                      // Approval given (green)
    pinMode(READY_TO_START_BUTTON, INPUT_PULLDOWN);  // Start sent, waiting approval (button, activates yellow)
    pinMode(START_RUN_BUTTON, INPUT_PULLDOWN);       // Approval given, spins motor (button, deactivates both LEDs)

    digitalWrite(YELLOW_LED, LOW);
    digitalWrite(GREEN_LED, LOW);

    receiver.start();

    servoMotor.attach(SERVO_PIN, 500, 2400);
    servoMotor.setPeriodHertz(50);
    servoMotor.write(12);  // 12 degree offset because of the way I put the thing on

    Preferences preferences;
    preferences.begin("wifi", false);
    if (!preferences.isKey("serverURL")) {
        preferences.putString("serverURL", "http://192.168.132.105:3000");
    }
    serverURL = preferences.getString("serverURL");

    // Connect to the access point with a static IP
    WiFi.config(localIP, gatewayIP, subnet);
    WiFi.begin(SSID, PASSWORD);

    while (!WiFi.isConnected()) {
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

    makeEndpoints(server, swingMotor);
    server.begin();
}

void loop() {
    // Handle IR remote stuff
    if (receiver.decode()) {
        if (receiver.decodedIRData.decodedRawData == 3910598400) {
            irFlag = 1;
        } else if (receiver.decodedIRData.decodedRawData == 3860463360) {
            irFlag = 2;
        }
        receiver.resume();
    }

    // Track start attendee has the cars set and is ready to go
    if (digitalRead(19) == HIGH || irFlag == 1) {
        digitalWrite(YELLOW_LED, HIGH);
        carsReady = true;
        HTTPClientWrapper::post(serverURL + "/cars-ready");  // Let the backend know the cars are ready
    }

    // Track start attendee is trying to start the run
    // Checks if approval has been given, and if so, the motor will spin
    if (digitalRead(4) == HIGH || irFlag == 2) {
        if (carsReady && hasStartApproval) {
            digitalWrite(GREEN_LED, LOW);
            digitalWrite(YELLOW_LED, LOW);
            swingMotor();

            HTTPClientWrapper::post(serverURL + "/run-started");

            carsReady = false;
            hasStartApproval = false;

        } else if ((carsReady && !hasStartApproval) && DEBUG) {
            Serial.println("Tried to start motor by button - Cars are ready, but we don't have approval yet");
        } else if ((!carsReady && !hasStartApproval) && DEBUG) {
            Serial.println("Tried to start motor by button - Cars are not ready, and we don't have approval yet");
        }
    }

    irFlag = 0;

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
