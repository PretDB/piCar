#!/usr/bin/python3

import cv2
import threading
import time


mode = 0

class tracker(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run():



# Preprocess of origin image
def preprocess(img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return cv2.threshold(img, 200, 255, cv2.THRESH_OTSU, cv2.THRESH_BINARY)[1]


cam = cv2.VideoCapture(0)


while True:
    # Read a frame from camera
    f = cam.read()[1]
    # Down sampling
    f = cv2.pyrDown(f, (f.shape[1] / 2, f.shape[0] / 2))
    f = cv2.pyrDown(f, (f.shape[1] / 2, f.shape[0] / 2))
    # Pre-process of the image
    binImg = preprocess(f)
    # Get element
    ele = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 25))
    # Erode and delate
    erd = cv2.erode(binImg, ele)
    dil = cv2.dilate(erd, ele)

    # ************** area 1 ******************