#include "control_motor.h"

int speed = 100;
int pwmPin_22 = 22,pwmPin_23 = 23,
    pwmPin_24 = 24,pwmPin_25 = 25,
    pwmPin_26 = 26,pwmPin_27 = 27,
    pwmPin_28 = 28,pwmPin_29 = 29;

void motor_init(int speed_input){
    speed = speed_input;
    wiringPiSetup();
    softPwmCreate(pwmPin_22,0,200);
    softPwmCreate(pwmPin_23,0,200);
    softPwmCreate(pwmPin_24,0,200);
    softPwmCreate(pwmPin_25,0,200);
    softPwmCreate(pwmPin_26,0,200);
    softPwmCreate(pwmPin_27,0,200);
    softPwmCreate(pwmPin_28,0,200);
    softPwmCreate(pwmPin_29,0,200);

    softPwmWrite(pwmPin_22,0);
    softPwmWrite(pwmPin_23,0);
    softPwmWrite(pwmPin_24,0);
    softPwmWrite(pwmPin_25,0);
    softPwmWrite(pwmPin_26,0);
    softPwmWrite(pwmPin_27,0);
    softPwmWrite(pwmPin_28,0);
    softPwmWrite(pwmPin_29,0);
}

void forward()
{
    softPwmWrite(pwmPin_22,0);
    softPwmWrite(pwmPin_23,speed);
    softPwmWrite(pwmPin_24,0);
    softPwmWrite(pwmPin_25,speed);
    softPwmWrite(pwmPin_26,0);
    softPwmWrite(pwmPin_27,speed);
    softPwmWrite(pwmPin_28,0);
    softPwmWrite(pwmPin_29,speed);
}

void back()
{
    softPwmWrite(pwmPin_22,speed);
    softPwmWrite(pwmPin_23,0);
    softPwmWrite(pwmPin_24,speed);
    softPwmWrite(pwmPin_25,0);
    softPwmWrite(pwmPin_26,speed);
    softPwmWrite(pwmPin_27,0);
    softPwmWrite(pwmPin_28,speed);
    softPwmWrite(pwmPin_29,0);
}

void left()
{
    softPwmWrite(pwmPin_22,speed);
    softPwmWrite(pwmPin_23,0);
    softPwmWrite(pwmPin_24,speed);
    softPwmWrite(pwmPin_25,0);
    softPwmWrite(pwmPin_26,0);
    softPwmWrite(pwmPin_27,speed);
    softPwmWrite(pwmPin_28,0);
    softPwmWrite(pwmPin_29,speed);
}

void right()
{
    softPwmWrite(pwmPin_22,0);
    softPwmWrite(pwmPin_23,speed);
    softPwmWrite(pwmPin_24,0);
    softPwmWrite(pwmPin_25,speed);
    softPwmWrite(pwmPin_26,speed);
    softPwmWrite(pwmPin_27,0);
    softPwmWrite(pwmPin_28,speed);
    softPwmWrite(pwmPin_29,0);
}

void left_forward()
{

}

void right_forward()
{

}

void left_back()
{

}

void right_back()
{

}
