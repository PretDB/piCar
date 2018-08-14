#ifndef CONTROL_MOTOR_H
#define CONTROL_MOTOR_H
#include "wiringPi.h"
#include "wiringSerial.h"
#include <softPwm.h>

void motor_init(int speed_input);
void forward();
void back();
void left();
void right();
void left_forward();
void right_forward();
void left_back();
void right_back();

#endif // CONTROL_MOTOR_H
