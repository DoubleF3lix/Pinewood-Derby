#include "timer.hpp"

#include <Arduino.h>
#include <FunctionalInterrupt.h>  // There's 2 implementations of attachInterrupt, this contains the one that allows lambdas to be passed in

#include "globals.hpp"
#include "http_client.hpp"

const uint8_t BLANK_SEGMENTS[] = {0b00000000, 0b00000000, 0b00000000, 0b00000000};
const uint8_t LINED_SEGMENTS[] = {0b01000000, 0b01000000, 0b01000000, 0b01000000};
const uint8_t FAIL_SEGMENTS[] = {0b01110001, 0b01110111, 0b00110000, 0b00111000};

const uint8_t digitToSegments[] = {
    // HGFEDCBA
    0b00111111,  // 0
    0b00000110,  // 1
    0b01011011,  // 2
    0b01001111,  // 3
    0b01100110,  // 4
    0b01101101,  // 5
    0b01111101,  // 6
    0b00000111,  // 7
    0b01111111,  // 8
    0b01101111,  // 9
    0b01110111,  // A
    0b01111100,  // b
    0b00111001,  // C
    0b01011110,  // d
    0b01111001,  // E
    0b01110001   // F
};

LaserTimer::LaserTimer(
    uint8_t laneID,
    uint8_t pinRunTimerCLK,
    uint8_t pinRunTimerDIO,
    uint8_t pinPositionDisplayCLK,
    uint8_t pinPositionDisplayDIO,
    uint8_t pinLaserOUT,
    // LaserTriggerCallback callback,
    uint8_t brightness)
    : laneID{laneID},
      pinRunTimerCLK{pinRunTimerCLK},
      pinRunTimerDIO{pinRunTimerDIO},
      pinPositionDisplayCLK{pinPositionDisplayCLK},
      pinPositionDisplayDIO{pinPositionDisplayDIO},

      pinLaserOUT{pinLaserOUT},
      // callback{callback},
      brightness{brightness},

      runTimeDisplay{pinRunTimerCLK, pinRunTimerDIO},
      positionDisplay{pinPositionDisplayCLK, pinPositionDisplayDIO} {
    // Make sure all the pins are primed and ready
    pinMode(this->pinRunTimerCLK, OUTPUT);
    pinMode(this->pinRunTimerDIO, OUTPUT);
    pinMode(this->pinPositionDisplayCLK, OUTPUT);
    pinMode(this->pinPositionDisplayDIO, OUTPUT);
    pinMode(this->pinLaserOUT, INPUT);

    this->runTimeDisplay.setBrightness(this->brightness);
    this->positionDisplay.setBrightness(this->brightness);

    attachInterrupt(
        digitalPinToInterrupt(this->pinLaserOUT), [this]() { this->laserTrippedFlag = true; }, RISING);

    // Initialize the display to show nothing
    this->clearDisplays();
}

void LaserTimer::newRun() {
    this->finishedRunTime = 0;
    this->runStartTime = -1;
    this->clearDisplays();
    this->position = 0;
}

void LaserTimer::startRunTimer() {
    this->runStartTime = millis();
    this->runActive = true;
}

void LaserTimer::stopRunTimer(bool isFail) {
    this->finishedRunTime = millis() - this->runStartTime;
    this->runActive = false;

    // See comment for laserTrippedDelayOver for explanation on why this is used
    this->queueTime = millis();
    this->queueIsFail = isFail;
}

void LaserTimer::showRunTimerValue() {
    this->runTimeDisplay.setSegments(this->millisToSegments(this->finishedRunTime));
}

void LaserTimer::showPositionValue() {
    this->positionDisplay.setSegments(this->numberToDisplaySegments(this->position), 4, 0);
}

void LaserTimer::clearRunTimerDisplay() {
    this->runTimeDisplay.setSegments(LINED_SEGMENTS, 4, 0);
}

void LaserTimer::clearPositionDisplay() {
    this->positionDisplay.setSegments(LINED_SEGMENTS, 4, 0);
}

void LaserTimer::clearDisplays() {
    // I guess there might be some overhead with calling a function so just duplicate the one-liner
    this->runTimeDisplay.setSegments(LINED_SEGMENTS, 4, 0);
    this->positionDisplay.setSegments(LINED_SEGMENTS, 4, 0);
}

void LaserTimer::markFail() {
    this->runTimeDisplay.setSegments(FAIL_SEGMENTS, 4, 0);
    // Just in case failing is marked after they've crossed
    this->positionDisplay.setSegments(LINED_SEGMENTS, 4, 0);

    this->finishedRunTime = 10000; // 10 seconds fail time (used to be 30, was way too long)
}

unsigned int LaserTimer::getRunTimeValue() {
    return this->finishedRunTime;
}

uint8_t LaserTimer::getPositionValue() {
    return this->position;
}

void LaserTimer::setRunTimeValue(unsigned int value) {
    this->finishedRunTime = value;
}

void LaserTimer::setPositionValue(unsigned int value) {
    this->position = value;
}

bool LaserTimer::laserTripped() {
    if (this->laserTrippedFlag && this->runActive) {
        this->laserTrippedFlag = false;

        // Make sure that the timer has been running for at least 1 second
        // Stops some false triggers at 0 milliseconds
        if ((millis() - this->runStartTime) > MIN_RUN_TIME) {
            return true;
        }
    } else {
        if ((millis() - this->queueTime > QUEUE_TIME) && (this->queueTime != 0)) {
            this->laserTrippedDelayOver();
        }
    }

    return false;
}

uint8_t* LaserTimer::millisToSegments(int millis) {
    // 10904 = 10.904 seconds
    // tens_seconds = 1; seconds = 0; tenths = 9; hundredths = 0; thousands = 4
    uint8_t tens_seconds = millis / 10000;  // May show A-F if it's higher than 100 seconds, but that's okay
    uint8_t seconds = (millis / 1000) % 10;
    uint8_t tenths = (millis / 100) % 10;
    uint8_t hundredths = (millis / 10) % 10;
    // Discard thousands because it won't fit on the display

    // First digit is blank instead of showing 0, second digit is bit shifted to turn on the colon (either the second or third digit need this bit, the first or fourth don't work)
    uint8_t* segments = new uint8_t[4]{
        // Need to cast because otherwise you get warnings about int to uint8_t
        static_cast<uint8_t>(tens_seconds != 0 ? digitToSegments[tens_seconds] : 0b00000000),
        static_cast<uint8_t>(digitToSegments[seconds] | 1 << 7),
        digitToSegments[tenths],
        digitToSegments[hundredths]};

    return segments;
}

uint8_t* LaserTimer::numberToDisplaySegments(uint8_t number) {
    return new uint8_t[4]{0b00000000, 0b00000000, digitToSegments[number], 0b00000000};
}

// Explanation of why this is used over showing displays directly on trip:
// Basically, it used to work so that the display would show the time and position when the laser was tripped.
// However, this caused about a 47 to 49 millisecond delay between when the laser trip body was entered and when it was exited.
// (that's without the network request to tell the backend!).
// This means that even if the cars finished within like 2 milliseconds of each other, it would show at least a 47-49 millisecond gap between them.
// So instead, the heavy stuff is offloaded to be 0.1 seconds after the actual trip. After 100 milliseconds has passed, we can accept another 50 millisecond inaccuracy since
// it's not really a close call anyway.
void LaserTimer::laserTrippedDelayOver() {
    if (this->showTimeOnFinish && !this->queueIsFail) {
        this->showRunTimerValue();
        this->showPositionValue();
    }

    if (this->queueIsFail) {
        this->markFail();
    }

    // This takes too long, but it does work. It doesn't block the time being read, but it does add a delay between displays
    std::string dataToSend = std::to_string(this->laneID) + "&" + std::to_string(this->finishedRunTime) + "&" + std::to_string(this->position) + "&" + std::to_string(this->queueIsFail);
    HTTPClientWrapper::post(serverURL + "/lane-end-triggered", dataToSend.c_str());

    this->queueTime = 0;
    this->queueIsFail = false;
}
