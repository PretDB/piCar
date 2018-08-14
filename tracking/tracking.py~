#!/usr/bin/python3

import cv2

# origin image from camera
def GetDir(img):
    down = cv2.pyrDown(img, (img.shape[0] / 2, img.shape[1] / 2))
    downdown = cv2.pyrDown(down, (down.shape[0] / 2, down.shape[1] / 2))
    gray = cv2.cvtColor(downdown, cv2.COLOR_BGR2GRAY)
    thv, thi = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)

    element = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 25))
    erode_img = cv2.erode(thi, element)
    dilate_img = cv2.dilate(erode_img, element)

    for i in range(5 * dilate_img.shape[1] / 16):
        for j in range(dilate_img.shape[0] / 3):
            if(thresho)

    return 0
