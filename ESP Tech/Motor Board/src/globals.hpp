#include <Arduino.h>

#define YELLOW_LED 26
#define GREEN_LED 22
#define READY_TO_START_BUTTON 4
#define START_RUN_BUTTON 19
#define SERVO_PIN 33
#define IR_PIN 18

extern const bool DEBUG;
extern String serverURL;
extern bool carsReady;
extern bool hasStartApproval;
