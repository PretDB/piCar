#!/usr/bin/python3

import cv2
import threading
from command import Command


mode = 0


class tracker(threading.Thread):
    def __init__(self, videoDev):
        threading.Thread.__init__(self)
        self.cam = cv2.VideoCapture(videoDev)
        self.ele = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 25))
        self.command = Command.Stop

    def readImg(self):
        r, img = self.cam.read()
        if r:
            self.lastImg = img

    def preprocess(self, img):
        # Down Sampling twice
        d1 = cv2.pyrDown(img, (img.shape[1] / 2, img.shape[0] / 2))
        d2 = cv2.pyrDown(d1, (d1.shape[1] / 2, d1.shape[0] / 2))

        # Grailize
        gray = cv2.cvtColor(d2, cv2.COLOR_BGR2GRAY)

        # Threshold ( OTSU )
        th, bi = cv2.threshold(gray, 200, 255, cv2.THRESH_OTSU,
                               cv2.THRESH_BINARY)

        # Erode and dilate
        erd = cv2.erode(bi, self.ele)
        dil = cv2.dilate(erd, self.ele)

        return dil

    # Calcuate the center and mass
    def calc(self, img):
        post = self.preprocess(img)

        center = (0, 0)  #
        m = 0

        mo = cv2.moments(post, True)
        if not int(mo['m00']) == 0:
            center[0] = (int)(mo['m10'] / mo['m00'])
            center[1] = (int)(mo['m01'] / mo['m00'])
            m = (int)(mo['m00'])

        return m, center

    def getDir(self):
        img = self.readImg()
        post = self.preprocess(img)

        a1 = post[0:post.shape[0] / 3, 0:post.shape[1] * 5 / 1]
        a2 = post[0:post.shape[0] / 3, post.shape[1] * 11 / 16:post.shape[1]]
        a3 = post[post.shape[0] / 3:post.shape[0] * 2 / 3]
        a4 = post[post.shape[0] * 2 / 3:post.shape[0]]

        a1_p = self.calc(a1)
        a2_p = self.calc(a2)
        a3_p = self.calc(a3)
        a4_p = self.calc(a4)

        if abs(a3_p[1][1] - a4_p[1][1]) > 4:
            if a3_p[1][1] < a4_p[1][1]:
                self.command = Command.LeftRotate
            else:
                self.command = Command.RightRotate
        elif abs(abs(a3_p[1][1] + a4_p[1][1]) / 2 - 100 > 25):
            if abs(a3_p[1][1] + a4_p[1][1]) / 2 < 80:
                self.command = Command.LeftShift
            else:
                self.command = Command.RightShift
        elif a1_p[0] > 200 and a2_p[0] > 200:
            self.command = Command.Stop
        else:
            self.command = Command.Forward

        return self.command
