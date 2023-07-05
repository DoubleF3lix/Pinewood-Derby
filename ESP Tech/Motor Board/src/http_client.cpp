#include <HTTPClient.h>

#include "http_client.hpp"
#include "globals.hpp"

bool HTTPClientWrapper::get(String url, bool silenceDebug) {
    HTTPClient baseClient;

    int responseCode = 0;

    baseClient.begin(url);
    responseCode = baseClient.GET();
    baseClient.end();

    if (DEBUG && !silenceDebug) {
        Serial.print("Attempted request to " + url + ". ");
        Serial.print("Response code: ");
        Serial.println(responseCode);
    }

    if (responseCode >= 200 && responseCode < 300) {
        return true;
    } else {
        return false;
    }
}

bool HTTPClientWrapper::post(String url, const char* body, bool silenceDebug) {
    HTTPClient baseClient;

    int responseCode = 0;

    baseClient.begin(url);
    baseClient.addHeader("Content-Type", "text/plain");
    responseCode = baseClient.POST(body);
    baseClient.end();

    if (DEBUG && !silenceDebug) {
        Serial.print("Attempted request to " + url + ". ");
        Serial.print("Response code: ");
        Serial.println(responseCode);
    }

    if (responseCode >= 200 && responseCode < 300) {
        return true;
    } else {
        return false;
    }
}
