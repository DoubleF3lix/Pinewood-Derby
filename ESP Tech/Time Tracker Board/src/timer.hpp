#ifndef LASER_TIMER
#define LASER_TIMER

#include <TM1637TinyDisplay.h>
#include <inttypes.h>

// typedef void (*LaserTriggerCallback)(void);

class LaserTimer {
   public:
    /// Manages a timer from a TM1637 display and stops the timer when a laser is tripped
    ///
    /// @param laneID The ID of the lane this timer is for
    /// @param pinTimerCLK The digital pin number connected to the timer's CLK pin
    /// @param pinTimerDIO The digital pin number connected to the timer's DIO pin
    /// @param pinPositionDisplayCLK The digital pin number connected to the position display's CLK pin
    /// @param pinPositionDisplayDIO The digital pin number connected to the position display's DIO pin
    /// @param pinLaserOUT The digital pin number connected to the lasers OUT pin
    /// @param brightness The brightness of the timer display
    LaserTimer(
        uint8_t laneID,
        uint8_t pinTimerCLK,
        uint8_t pinTimerDIO,
        uint8_t pinPositionDisplayCLK,
        uint8_t pinPositionDisplayDIO,
        uint8_t pinLaserOUT,
        // LaserTriggerCallback callback,
        uint8_t brightness = 7);
    /// @brief Create a new run, which resets timer values and clears the displays
    void newRun();

    /// @brief Starts the timer from 0
    void startRunTimer();

    /// @brief Stops the timer at its current position and saves it in timerValue
    /// @param isFail Whether or not the run was a fail, which will not display the position or run time regardless of showTimeOnFinish value
    void stopRunTimer(bool isFail = false);

    /// @brief Converts the value stored in timerValue and displays it on the run timer
    void showRunTimerValue();

    /// @brief Converts the value stored in timerValue and displays it on the run timer
    void showPositionValue();

    /// @brief Makes the run timer display 4 dashes (----)
    void clearRunTimerDisplay();

    /// @brief Makes the race timer display 4 dashes (----)
    void clearPositionDisplay();

    /// @brief Equivalent to calling both clearRunTimeDisplay and clearPositionDisplay
    void clearDisplays();

    /// @brief Makes the run timer display show FAIL
    void markFail();

    /// @brief Used for endpoints
    /// @return The value of the run time
    unsigned int getRunTimeValue();

    /// @brief Used for endpoints
    /// @return The value of the position
    uint8_t getPositionValue();

    /// @brief Used for set_run_time endpoint
    /// @param value The value to set the run time to
    void setRunTimeValue(unsigned int value);

    /// @brief Used for set_position endpoint
    /// @param value The value to set the position to
    void setPositionValue(unsigned int value);

    /// @brief Should be called inside the loop function to check if the laser has been tripped. This will return true exactly once for each trip and will not require manually setting the variable.
    /// @return True if the laser has been tripped, false otherwise
    bool laserTripped();

    /// @brief  Whether or not to show the time on the finish display when the laser is tripped. If false, it needs to be shown manually. Could be used for dramatic effect.
    bool showTimeOnFinish = true;

   private:
    const uint8_t laneID;
    const uint8_t pinRunTimerCLK;
    const uint8_t pinRunTimerDIO;
    const uint8_t pinPositionDisplayCLK;
    const uint8_t pinPositionDisplayDIO;
    const uint8_t pinLaserOUT;

    bool laserTrippedFlag = false;
    bool runActive = false;

    // This way we only have to calculate the time once we're done instead of constant incrementation which is probably just a terrible idea.
    unsigned int runStartTime;
    unsigned int finishedRunTime;  // Time in milliseconds to display on the run time
    uint8_t position;

    // Variables used to keep state for the delay after a laser is tripped (to wait for the heavy processing in case lanes finish close together)
    unsigned int queueTime = 0;
    bool queueIsFail;

    uint8_t brightness;  // optional

    TM1637TinyDisplay runTimeDisplay;
    TM1637TinyDisplay positionDisplay;

    /// @brief Converts time in milliseconds into a 4 digit array of segments
    /// @param millis The milliseconds to convert to segments
    /// @return The 4 digit array of segments to pass to display.setSegments();
    uint8_t* millisToSegments(int millis);

    /// @brief Converts a number to a 4 digit array of segments with the number on the 3rd display digit
    /// @param number The number to convert
    /// @return The 4 digit array of segments to pass to display.setSegments();
    uint8_t* numberToDisplaySegments(uint8_t number);

    /// @brief Automatically called by laserTripped after the delay is over if the laser was tripped
    void laserTrippedDelayOver();
};

#endif  // LASER_TIMER