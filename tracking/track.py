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
    f = cam.read()[1]
    f = cv2.pyrDown(f, (f.shape[1] / 2, f.shape[0] / 2))
    f = cv2.pyrDown(f, (f.shape[1] / 2, f.shape[0] / 2))
    binImg = preprocess(f)
    ele = cv2.getStructureingElement(cv2.MORPH_RECT, (25, 25))
    erd = cv2.erode(binImg, ele)
    dil = cv2.delate(erd, ele)

    # ************** area 1 ******************
