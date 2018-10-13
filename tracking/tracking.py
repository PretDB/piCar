#!/usr/bin/python3

import cv2
import numpy as np

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
    erd = cv2.erode(binImage, ele)
    dil = cv2.delate(erd, ele)


