#include "search_path.h"

using namespace cv;
using namespace std;

int variance = 40;
int Stop = 0,Forward = 1,Back = 2,Left = 3,Right = 4,Left_circle = 5,Right_circle = 6;

void search_track_fun()
{
    VideoCapture cap(0);
    Mat frame,pyrDown_image,gray_image,threshold_image;
    int x_1 = 0,y_1 = 0,
        x_2 = 0,y_2 = 0,
        x_3 = 0,y_3 = 0,
        x_4 = 0,y_4 = 0;
    int flag_1 = 0,flag_2 = 0,flag_3 = 0,flag_4 = 0;

    int count = 1;
    int fd;

    if(-1 == wiringPiSetup()){
            cerr<<"set up error"<<endl;
            exit(-1);
        }
    if((fd = serialOpen("/dev/ttyS0", 9600)) == -1){
        cerr<<"serial open error"<<endl;
        exit(-1);
    }

    while(1){
        cap>>frame;
        pyrDown(frame,pyrDown_image,Size(frame.cols/2,frame.rows/2));
        pyrDown(pyrDown_image,pyrDown_image,Size(pyrDown_image.cols/2,pyrDown_image.rows/2));
        cvtColor(pyrDown_image,gray_image,COLOR_BGR2GRAY);
        threshold(gray_image,threshold_image,80,255,THRESH_BINARY);
//        adaptiveThreshold(gray_image,threshold_image,255,ADAPTIVE_THRESH_GAUSSIAN_C,THRESH_BINARY,11,2);
        Mat element = getStructuringElement(MORPH_RECT,Size(25,25));
        erode(threshold_image,threshold_image,element);
        dilate(threshold_image,threshold_image,element);
        /***********************************area_1*********************************/
        for(int j = 0;j < (5*threshold_image.cols)/16;j++){//rows shi hang
            for(int i = 0;i < threshold_image.rows/3;i++){
                if(threshold_image.at<uchar>(i,j) == 0){
                    x_1 += i;
                    y_1 += j;
                    count++;
                }
            }
        }
        if(count > 200){
            flag_1 = 1;
            x_1 = x_1/count;
            y_1 = y_1/count;
        }
        count = 1;

        /***********************************area_2*********************************/
        for(int j = (11*threshold_image.cols)/16;j < threshold_image.cols;j++){//rows shi hang
            for(int i = 0;i < threshold_image.rows/3;i++){
                if(threshold_image.at<uchar>(i,j) == 0){
                    x_2 += i;
                    y_2 += j;
                    count++;
                }
            }
        }
        if(count > 200){
            flag_2 = 1;
            x_2 = x_2/count;
            y_2 = y_2/count;
        }
        count = 1;

        /***********************************area_3*********************************/
        for(int j = 0;j < threshold_image.cols;j++){//rows is hang
            for(int i = (3*threshold_image.rows)/9;i < (6*threshold_image.rows)/9;i++){
                if(threshold_image.at<uchar>(i,j) == 0){
                    x_3 += i;
                    y_3 += j;
                    count++;
                }
            }
        }
        if(count > 200){
            flag_3 = 1;
            x_3 = x_3/count;
            y_3 = y_3/count;
        }
        count = 1;

        /***********************************area_4*********************************/
        for(int j = 0;j < threshold_image.cols;j++){//rows shi hang
            for(int i = (7*threshold_image.rows)/9;i < threshold_image.rows;i++){
                if(threshold_image.at<uchar>(i,j) == 0){
                    x_4 += i;
                    y_4 += j;
                    count++;
                }
            }
        }
        if(count > 200){
            flag_4 = 1;
            x_4 = x_4/count;
            y_4 = y_4/count;
        }
        count = 1;

//        /***********************************stop*********************************/
//        for(int i = 10;i < threshold_image.rows/3;i++){//rows shi hang
//            for(int j = 0;j < threshold_image.cols;j++){
//                if(threshold_image.at<uchar>(i,j) == 0){
//                    count++;
//                }
//            }
//            if(count > 100){
//                flag_1 = 1;
//                flag_2 = 2;
//                count = 1;
//                break;
//            }
//        }
//        count = 1;



        /***********************************branch_judge*********************************/
//                cout<<flag_1<<"   "<<flag_2<<"   "<<flag_3<<"   "<<flag_4<<endl;
        if(abs(y_3 - y_4) > 4){//direction
            if(y_3 < y_4){
                serialPutchar(fd,Left_circle);
                cout<<"Left_circle"<<endl;
            }
            else{
                serialPutchar(fd,Right_circle);
                cout<<"Right_circle"<<endl;
            }
        }else if(abs(abs(y_3 + y_4)/2 - 100) > 25){//centre
            if(abs(y_3 + y_4)/2 < 80){
                serialPutchar(fd,Left);
                cout<<"Left"<<endl;
            }
            else{
                serialPutchar(fd,Right);
                cout<<"Right"<<endl;
            }
        }else if(flag_1 == 1 && flag_2 == 1){
            serialPutchar(fd,Stop);
            cout<<"stop"<<endl;
            //return ;
        }else{
            serialPutchar(fd,Forward);
            cout<<"Forward"<<endl;
        }


        circle(pyrDown_image,Point(y_1,x_1),4,Scalar(0,0,255),FILLED);
        circle(pyrDown_image,Point(y_2,x_2),4,Scalar(0,0,255),FILLED);
        circle(pyrDown_image,Point(y_3,x_3),4,Scalar(0,0,255),FILLED);
        circle(pyrDown_image,Point(y_4,x_4),4,Scalar(0,0,255),FILLED);
        circle(threshold_image,Point(y_1,x_1),4,Scalar(255,255,255),FILLED);
        circle(threshold_image,Point(y_2,x_2),4,Scalar(255,255,255),FILLED);
        circle(threshold_image,Point(y_3,x_3),4,Scalar(255,255,255),FILLED);
        circle(threshold_image,Point(y_4,x_4),4,Scalar(255,255,255),FILLED);
        flag_1 = 0;
        flag_2 = 0;
        flag_3 = 0;
        flag_4 = 0;
        imshow("pyrDown_image", pyrDown_image);
        imshow("threshold_image", threshold_image);
        waitKey(1);
    }
}
