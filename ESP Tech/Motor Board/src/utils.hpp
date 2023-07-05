#include <ESPAsyncWebServer.h>
#include <Preferences.h>

#include "globals.hpp"
#include "http_client.hpp"

/// @brief Blinks the LED on the ESP32 (total cycle takes 1 second)
/// @param time_on The time the LED should be on for (max of 999)
void blink(int time_on = 400) {
    digitalWrite(LED_BUILTIN, HIGH);
    delay(time_on);
    digitalWrite(LED_BUILTIN, LOW);
    delay(1000 - time_on);
}

/// @brief Creates the endpoints for the web server
/// @param server The server to create the endpoints for
void makeEndpoints(AsyncWebServer& server, std::function<void(void)> swingMotorFunction) {
    // Check endpoints
    server.on("/check-get", HTTP_GET, [](AsyncWebServerRequest* request) {
        if (DEBUG) {
            Serial.println("/check-get called");
        }

        request->send(204);
    });

    server.on("/check-post", HTTP_POST, [](AsyncWebServerRequest* request) {
        if (DEBUG) {
            Serial.println("/check-post called");
        }

        if (!request->hasArg("sample")) {
            request->send(400, "text/plain", "Missing \"sample\" argument");
            return;
        }

        std::string returnResponse = "arg count: " + std::to_string(request->args()) + ", 'sample' content: " + request->arg("sample").c_str();
        request->send(200, "text/plain", returnResponse.c_str());
    });

    server.on("/get-temp", HTTP_GET, [](AsyncWebServerRequest* request) {
        if (DEBUG) {
            Serial.println("/get-temp called");
        }

        request->send(200, "text/plain", std::to_string(temperatureRead()).c_str());
    });

    server.on("/blink", HTTP_POST, [](AsyncWebServerRequest* request) {
        if (DEBUG) {
            Serial.println("/blink called");
        }

        blink();

        request->send(204);
    });

    server.on("/change-ip", HTTP_POST, [](AsyncWebServerRequest* request) {
        if (DEBUG) {
            Serial.println("/change-ip called");
        }

        if (!request->hasArg("ip")) {
            request->send(400, "text/plain", "Missing \"ip\" argument");
            return;
        }

        String newIP = request->arg("ip");

        Preferences preferences;
        preferences.begin("wifi", false);
    
        // Store it in the global variable and update the persistent memory
        preferences.putString("serverURL", newIP);
        serverURL = newIP;

        if (DEBUG) {
            Serial.println("New server URL: " + serverURL);
        }
        request->send(204);
    });

    server.on("/give-start-approval", HTTP_POST, [](AsyncWebServerRequest* request) {
        if (DEBUG) {
            Serial.println("/give-start-approval called");
        }

        if (carsReady) {
            hasStartApproval = true;
            digitalWrite(GREEN_LED, HIGH);
            request->send(204);
        } else {
            request->send(400);
        }
    });

    server.on("/force-spin-motor", HTTP_POST, [swingMotorFunction](AsyncWebServerRequest* request) {
        if (DEBUG) {
            Serial.println("/force-spin-motor called");
        }

        digitalWrite(GREEN_LED, LOW);
        digitalWrite(YELLOW_LED, LOW);

        carsReady = false;
        hasStartApproval = false;

        // If the silent argument is present, don't send a request to the server
        if (!request->hasArg("silent")) {
            HTTPClientWrapper::post(serverURL + "/run-started");
        }

        swingMotorFunction();
        request->send(204);
    });
}
