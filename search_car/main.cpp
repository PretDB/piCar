#include "mainwindow.h"
#include <QApplication>
#include "wiringPi.h"
#include "wiringSerial.h"
#include <softPwm.h>
#include "QTime"
#include "opencv2/core.hpp"
#include "opencv2/opencv.hpp"
#include "control_motor.h"
#include "search_path.h"

using namespace std;
using namespace cv;

int main(int argc, char *argv[])
{
    QApplication a(argc, argv);
    //MainWindow w;
    //w.show();

    int search_track = 1;
    int signal = 1;

    motor_init(100);

    if(signal == search_track){
        search_track_fun();
    }

    return a.exec();
}
