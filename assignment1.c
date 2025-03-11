#include "assignment1.h"
#include <stdio.h>
#include <wiringPi.h>
#include <softPwm.h>

void init_shared_variable(SharedVariable* sv) {
    sv->bProgramExit = 0;
// You can initialize the shared variable if needed.
    sv->buttonDown = 0;
    sv->system_state = RUNNING;
    sv->buzzerStart = 0;
    sv->buzzer_state = 0;
}

void ledInit(void) {
    softPwmCreate(PIN_SMD_RED, 0, 0xff);
//......
//initialize SMD and DIP
    softPwmCreate(PIN_SMD_GRN, 0, 0xff);
    softPwmCreate(PIN_SMD_BLU, 0, 0xff);
    
    softPwmCreate(PIN_DIP_RED, 0, 0xff);
    softPwmCreate(PIN_DIP_GRN, 0, 0xff);
}

void init_sensors(SharedVariable* sv) {
// .......
    pinMode(PIN_BUTTON, INPUT);
    pinMode(PIN_MOTION, INPUT);
    pinMode(PIN_ROTARY_CLK, INPUT);
    pinMode(PIN_ROTARY_DT, INPUT);
    pinMode(PIN_SOUND, INPUT);
    
    pinMode(PIN_DIP_RED, OUTPUT);
    pinMode(PIN_DIP_GRN, OUTPUT);
    pinMode(PIN_SMD_RED, OUTPUT);
    pinMode(PIN_SMD_GRN, OUTPUT);
    pinMode(PIN_SMD_BLU, OUTPUT);
    pinMode(PIN_ALED, OUTPUT);
    pinMode(PIN_BUZZER, OUTPUT);
    ledInit();
}

// 1. Button
void body_button(SharedVariable* sv) {
    int button = READ(PIN_BUTTON);
    
    if (button == LOW) {
        if (sv->system_state == PAUSE && sv->buttonDown == 0) {
            sv->system_state = RUNNING;
            sv->buttonDown = 1;
        }
        else if (sv->system_state == RUNNING && sv->buttonDown == 0){
            sv->system_state = PAUSE;
            sv->buttonDown = 1;
        }
    }
    else {
        sv->buttonDown = 0;
    }
}

// 5. DIP two-color LED
void body_twocolor(SharedVariable* sv) {
    if (sv->system_state == PAUSE) {
        DIP_RED();
    }
    else {
        DIP_GREEN();
    }
}

// 6. SMD RGB LED
void body_rgbcolor(SharedVariable* sv) {
    // if (sv->rgb_state == RED) {
    //     SMD_RED();
    //     delay(10);
    //     sv->rgb_state = PURPLE;
    // }
    // else if (sv->rgb_state == PURPLE) {
    //     SMD_PURPLE();
    //     delay(10);
    //     sv->rgb_state = GREEN;
    // }
    // else if (sv->rgb_state == GREEN) {
    //     SMD_GREEN();
    //     delay(10);
    //     sv->rgb_state = CYAN;
    // }
    // else if (sv->rgb_state == CYAN) {
    //     SMD_CYAN();
    //     delay(10);
    //     sv->rgb_state = RED;
    // }
    if (sv->system_state == PAUSE) {
        SMD_PURPLE();
    }
    else {
        SMD_CYAN();
    }
}

// 7. Auto-flash LED
void body_aled(SharedVariable* sv) {
    if (sv->system_state == PAUSE) {
        TURN_OFF(PIN_ALED);
    }
    else {
        TURN_ON(PIN_ALED);
    }
    
}

// 8. Buzzer
void body_buzzer(SharedVariable* sv) {
    if (sv->system_state == PAUSE) {
        TURN_OFF(PIN_BUZZER);
    }
    else if (sv->system_state == RUNNING) {
        if(sv->buzzerStart == 0) {
            sv->buzzerStart = millis();
        }
        if (sv->buzzerStart != 0) {
            if (millis() - sv->buzzerStart < 3000) {
                if(sv->buzzer_state == 0) {
                    TURN_ON(PIN_BUZZER);
                }
                else {
                    TURN_OFF(PIN_BUZZER);
                }
                sv->buzzer_state = !sv->buzzer_state;
            }
            else {
                sv->buzzerStart = 0;
            }
        }
    }
}
