#include <ESPAsyncWebServer.h>
#include <Preferences.h>

#include "globals.hpp"
#include "http_client.hpp"
#include "timer.hpp"

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
void makeEndpoints(AsyncWebServer& server, LaserTimer* lane1, LaserTimer* lane2) {
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

    server.on("/blink", HTTP_GET, [](AsyncWebServerRequest* request) {
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

    server.on("/get-run-time", HTTP_GET, [lane1, lane2](AsyncWebServerRequest* request) {
        if (DEBUG) {
            Serial.println("/get-run-time called");
        }

        if (!request->hasArg("lane")) {
            request->send(400, "text/plain", "Missing \"lane\" argument");
            return;
        }

        int lane = request->arg("lane").toInt();
        if (lane == 1) {
            request->send(200, "text/plain", std::to_string(lane1->getRunTimeValue()).c_str());
        } else if (lane == 2) {
            request->send(200, "text/plain", std::to_string(lane2->getRunTimeValue()).c_str());
        } else {
            std::string returnResponse = "Invalid \"lane\" argument. Expected 1 or 2, got " + std::to_string(lane) + ".";
            request->send(400, "text/plain", returnResponse.c_str());
        }
    });

    server.on("/set-run-time", HTTP_POST, [lane1, lane2](AsyncWebServerRequest* request) {
        if (DEBUG) {
            Serial.println("/set-run-time called");
        }

        if (!request->hasArg("lane")) {
            request->send(400, "text/plain", "Missing \"lane\" argument");
            return;
        }
        if (!request->hasArg("value")) {
            request->send(400, "text/plain", "Missing \"value\" argument");
            return;
        }

        int lane = request->arg("lane").toInt();
        unsigned int value = request->arg("value").toInt();
        if (lane == 1) {
            lane1->setRunTimeValue(value);
        } else if (lane == 2) {
            lane2->setRunTimeValue(value);
        } else {
            std::string returnResponse = "Invalid \"lane\" argument. Expected 1 or 2, got " + std::to_string(lane) + ".";
            request->send(400, "text/plain", returnResponse.c_str());
            return;
        }

        request->send(204);
    });

    server.on("/show-run-time", HTTP_POST, [lane1, lane2](AsyncWebServerRequest* request) {
        if (DEBUG) {
            Serial.println("/show-run-time called");
        }

        if (!request->hasArg("lane")) {
            request->send(400, "text/plain", "Missing \"lane\" argument");
            return;
        }

        int lane = request->arg("lane").toInt();
        if (lane == 1) {
            lane1->showRunTimerValue();
        } else if (lane == 2) {
            lane2->showRunTimerValue();
        } else {
            std::string returnResponse = "Invalid \"lane\" argument. Expected 1 or 2, got " + std::to_string(lane) + ".";
            request->send(400, "text/plain", returnResponse.c_str());
            return;
        }

        request->send(204);
    });

    server.on("/hide-run-time", HTTP_POST, [lane1, lane2](AsyncWebServerRequest* request) {
        if (DEBUG) {
            Serial.println("/hide-run-time called");
        }

        if (!request->hasArg("lane")) {
            request->send(400, "text/plain", "Missing \"lane\" argument");
            return;
        }

        int lane = request->arg("lane").toInt();
        if (lane == 1) {
            lane1->clearRunTimerDisplay();
        } else if (lane == 2) {
            lane2->clearRunTimerDisplay();
        } else {
            std::string returnResponse = "Invalid \"lane\" argument. Expected 1 or 2, got " + std::to_string(lane) + ".";
            request->send(400, "text/plain", returnResponse.c_str());
            return;
        }

        request->send(204);
    });

    server.on("/get-position", HTTP_GET, [lane1, lane2](AsyncWebServerRequest* request) {
        if (DEBUG) {
            Serial.println("/get-position called");
        }

        if (!request->hasArg("lane")) {
            request->send(400, "text/plain", "Missing \"lane\" argument");
            return;
        }

        int lane = request->arg("lane").toInt();
        if (lane == 1) {
            request->send(200, "text/plain", std::to_string(lane1->getPositionValue()).c_str());
        } else if (lane == 2) {
            request->send(200, "text/plain", std::to_string(lane2->getPositionValue()).c_str());
        } else {
            std::string returnResponse = "Invalid \"lane\" argument. Expected 1 or 2, got " + std::to_string(lane) + ".";
            request->send(400, "text/plain", returnResponse.c_str());
        }
    });

    server.on("/set-position", HTTP_POST, [lane1, lane2](AsyncWebServerRequest* request) {
        if (DEBUG) {
            Serial.println("/set-position called");
        }

        if (!request->hasArg("lane")) {
            request->send(400, "text/plain", "Missing \"lane\" argument");
            return;
        }
        if (!request->hasArg("value")) {
            request->send(400, "text/plain", "Missing \"value\" argument");
            return;
        }

        int lane = request->arg("lane").toInt();
        uint8_t value = request->arg("value").toInt();
        if (lane == 1) {
            lane1->setPositionValue(value);
        } else if (lane == 2) {
            lane2->setPositionValue(value);
        } else {
            std::string returnResponse = "Invalid \"lane\" argument. Expected 1 or 2, got " + std::to_string(lane) + ".";
            request->send(400, "text/plain", returnResponse.c_str());
            return;
        }

        request->send(204);
    });

    server.on("/show-position", HTTP_POST, [lane1, lane2](AsyncWebServerRequest* request) {
        if (DEBUG) {
            Serial.println("/show-position called");
        }

        if (!request->hasArg("lane")) {
            request->send(400, "text/plain", "Missing \"lane\" argument");
            return;
        }

        int lane = request->arg("lane").toInt();
        if (lane == 1) {
            lane1->showPositionValue();
        } else if (lane == 2) {
            lane2->showPositionValue();
        } else {
            std::string returnResponse = "Invalid \"lane\" argument. Expected 1 or 2, got " + std::to_string(lane) + ".";
            request->send(400, "text/plain", returnResponse.c_str());
            return;
        }

        request->send(204);
    });

    server.on("/hide-position", HTTP_POST, [lane1, lane2](AsyncWebServerRequest* request) {
        if (DEBUG) {
            Serial.println("/hide-position called");
        }

        if (!request->hasArg("lane")) {
            request->send(400, "text/plain", "Missing \"lane\" argument");
            return;
        }

        int lane = request->arg("lane").toInt();
        if (lane == 1) {
            lane1->clearPositionDisplay();
        } else if (lane == 2) {
            lane2->clearPositionDisplay();
        } else {
            std::string returnResponse = "Invalid \"lane\" argument. Expected 1 or 2, got " + std::to_string(lane) + ".";
            request->send(400, "text/plain", returnResponse.c_str());
            return;
        }

        request->send(204);
    });

    server.on("/begin-run", HTTP_POST, [lane1, lane2](AsyncWebServerRequest* request) {
        if (DEBUG) {
            Serial.println("/begun-run called");
        }

        // Cleanup variables
        lane1->newRun();
        lane2->newRun();

        lane1->startRunTimer();
        lane2->startRunTimer();

        request->send(204);
    });

    server.on("/mark-finish", HTTP_POST, [lane1, lane2](AsyncWebServerRequest* request) {
        if (DEBUG) {
            Serial.println("/mark-finish called");
        }

        if (!request->hasArg("lane")) {
            request->send(400, "text/plain", "Missing \"lane\" argument");
            return;
        }

        int lane = request->arg("lane").toInt();

        if (lane == 1) {
            if (lane2->getPositionValue() == 1) {
                lane1->setPositionValue(2);
            } else {
                lane1->setPositionValue(1);
            }
            lane1->stopRunTimer();

        } else if (lane == 2) {
            if (lane1->getPositionValue() == 1) {
                lane2->setPositionValue(2);
            } else {
                lane2->setPositionValue(1);
            }
            lane2->stopRunTimer();

        } else {
            std::string returnResponse = "Invalid \"lane\" argument. Expected 1 or 2, got " + std::to_string(lane) + ".";
            request->send(400, "text/plain", returnResponse.c_str());
            return;
        }

        request->send(204);
    });

    server.on("/mark-fail", HTTP_POST, [lane1, lane2](AsyncWebServerRequest* request) {
        if (DEBUG) {
            Serial.println("/mark-fail called");
        }

        if (!request->hasArg("lane")) {
            request->send(400, "text/plain", "Missing \"lane\" argument");
            return;
        }

        int lane = request->arg("lane").toInt();

        if (lane == 1) {
            // markFail is called in the delay finished function
            lane1->stopRunTimer(true);
        } else if (lane == 2) {
            lane2->stopRunTimer(true);
        } else {
            std::string returnResponse = "Invalid \"lane\" argument. Expected 1 or 2, got " + std::to_string(lane) + ".";
            request->send(400, "text/plain", returnResponse.c_str());
            return;
        }

        request->send(204);
    });

    server.on("/edit-show-time-on-finish", HTTP_POST, [lane1, lane2](AsyncWebServerRequest* request) {
        if (DEBUG) {
            Serial.println("/edit-show-time-on-finish called");
        }

        if (!request->hasArg("lane")) {
            request->send(400, "text/plain", "Missing \"lane\" argument");
            return;
        }

        if (!request->hasArg("value")) {
            request->send(400, "text/plain", "Missing \"value\" argument");
            return;
        }

        // 0 = false, 1 = true
        bool value = request->arg("value").toInt() == 1;

        int lane = request->arg("lane").toInt();
        if (lane == 1) {
            lane1->showTimeOnFinish = value;
        } else if (lane == 2) {
            lane2->showTimeOnFinish = value;
        } else {
            std::string returnResponse = "Invalid \"lane\" argument. Expected 1 or 2, got " + std::to_string(lane) + ".";
            request->send(400, "text/plain", returnResponse.c_str());
            return;
        }

        request->send(204);
    });
}
