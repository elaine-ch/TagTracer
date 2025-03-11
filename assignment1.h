
#ifndef _ASSIGNMENT_BODY_
#define _ASSIGNMENT_BODY_

#include <stdint.h>

// Macros
#define TURN_ON(pin) digitalWrite(pin, 1)
#define TURN_OFF(pin) digitalWrite(pin, 0)

#define READ(pin) digitalRead(pin)
#define WRITE(pin, x) digitalWrite(pin, x)

// Constants
#define RUNNING 3
#define PAUSE 2

#define LOW 0
#define HIGH 1

#define CLOCKWISE 0
#define COUNTER_CLOCKWISE 1

#define DETECT_SOUND 1
#define NO_SOUND 0

#define DETECT_MOTION 1
#define NO_MOTION 0

#define RED 0
#define PURPLE 1
#define GREEN 2
#define CYAN 3

// A. Pin number definitions (DO NOT MODIFY)
// We use 8 sensors.
//
// 1. Button
#define PIN_BUTTON 0

// 2. Infrared motion sensor
#define PIN_MOTION 4

// 3. Rotary encoder
#define PIN_ROTARY_CLK 5
#define PIN_ROTARY_DT 6

// 4. Microphone sound sensor
#define PIN_SOUND 7

// 5. DIP two-color LED (Dual In-line Package)
#define PIN_DIP_RED 8
#define PIN_DIP_GRN 9

// 6. SMD RGB LED (Surface Mount Device)
#define PIN_SMD_RED 27
#define PIN_SMD_GRN 28
#define PIN_SMD_BLU 29

// 7. Auto-flash LED
#define PIN_ALED 12

// 8. Passive Buzzer
#define PIN_BUZZER 13

#define DIP_OFF() { \
    softPwmWrite(PIN_DIP_RED, 0x00); \
    softPwmWrite(PIN_DIP_GRN, 0x00); \
}

#define DIP_GREEN() { \
    softPwmWrite(PIN_DIP_RED, 0x00); \
    softPwmWrite(PIN_DIP_GRN, 0xff); \
}

#define DIP_RED() { \
    softPwmWrite(PIN_DIP_RED, 0xff); \
    softPwmWrite(PIN_DIP_GRN, 0x00); \
}

#define SMD_OFF() { \
    softPwmWrite(PIN_SMD_RED, 0x00); \
    softPwmWrite(PIN_SMD_GRN, 0x00); \
    softPwmWrite(PIN_SMD_BLU, 0x00); \
}

#define SMD_RED() { \
    softPwmWrite(PIN_SMD_RED, 0xff); \
    softPwmWrite(PIN_SMD_GRN, 0x00); \
    softPwmWrite(PIN_SMD_BLU, 0x00); \
}

#define SMD_PURPLE() { \
    softPwmWrite(PIN_SMD_RED, 0xc8); \
    softPwmWrite(PIN_SMD_GRN, 0x00); \
    softPwmWrite(PIN_SMD_BLU, 0xee); \
}

#define SMD_GREEN() { \
    softPwmWrite(PIN_SMD_RED, 0x00); \
    softPwmWrite(PIN_SMD_GRN, 0xff); \
    softPwmWrite(PIN_SMD_BLU, 0x00); \
}

#define SMD_CYAN() { \
    softPwmWrite(PIN_SMD_RED, 0x00); \
    softPwmWrite(PIN_SMD_GRN, 0xff); \
    softPwmWrite(PIN_SMD_BLU, 0xff); \
}

// B. Shared structure
// All thread functions get a shared variable of the structure
// as the function parameter.
// If needed, you can add anything in this structure.
typedef struct shared_variable {
    int bProgramExit; // Once set to 1, the program will terminate.
    // You can add more variables if needed.
    int buttonDown;
    int system_state;
    int buzzer_state;
    int rgb_state;
    long buzzerStart;
} SharedVariable;

// C. Functions
// You need to implement the following functions.
// Do not change any function name here.
void init_shared_variable(SharedVariable* sv);
void init_sensors(SharedVariable* sv);
void body_button(SharedVariable* sv);     // Button
void body_motion(SharedVariable* sv);     // Infrared motion sensor
void body_sound(SharedVariable* sv);      // Microphone sound sensor
void body_encoder(SharedVariable* sv);    // Rotary encoder
void body_twocolor(SharedVariable* sv);   // DIP two-color LED
void body_rgbcolor(SharedVariable* sv);   // SMD RGB LED
void body_aled(SharedVariable* sv);       // Auto-flash LED
void body_buzzer(SharedVariable* sv);     // Buzzer

#endif
