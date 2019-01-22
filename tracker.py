#!/usr/bin/python3

import cv2
import threading
from command import Command


mode = 0


class tracker(threading.Thread):
    def __init__(self, videoDev):
        threading.Thread.__init__(self)
        self.cam = cv2.VideoCapture(videoDev)
        self.ele = cv2.getStructuringElement(cv2.MORPH_RECT, (10, 10))
        self.command = Command.Stop

    def run(self):
        while True:
            self.command = self.getDir()

        pass

    def readImg(self):
        r, img = self.cam.read()
        if r:
            self.lastImg = img
        return self.lastImg

    def preprocess(self, img):
        # Down Sampling twice
        d1 = cv2.pyrDown(img, (img.shape[1] / 2, img.shape[0] / 2))
        d2 = cv2.pyrDown(d1, (d1.shape[1] / 2, d1.shape[0] / 2))

        # Grailize
        gray = cv2.cvtColor(d2, cv2.COLOR_BGR2GRAY)

        # Threshold ( OTSU )
        th, bi = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU)
        th, bi = cv2.threshold(gray, th, 255, cv2.THRESH_BINARY_INV)

        # Erode and dilate
        erd = cv2.erode(bi, self.ele)
        dil = cv2.dilate(erd, self.ele)

        return dil

    # Calcuate the center and mass
    def calc(self, img, xbase, ybase):
        # post = self.preprocess(img)
        post = img
        center = [0, 0]  #
        m = 0

        mo = cv2.moments(post, True)
        if not int(mo['m00']) == 0:
            center[0] = (int)(mo['m10'] / mo['m00']) + xbase
            center[1] = (int)(mo['m01'] / mo['m00']) + ybase
            m = (int)(mo['m00'])

        return m, center

    def getDir(self):
        img = self.readImg()
        post = self.preprocess(img)


        # Y, toY, X,toX
        a1_rec = (0, int(post.shape[0] / 3), 0, int(post.shape[1] * 5 / 16))
        a2_rec = (0, int(post.shape[0] / 3), int(post.shape[1] * 11 / 16), post.shape[1])
        a3_rec = (int(post.shape[0] / 3), int(post.shape[0] * 2/ 3), 0, post.shape[1])
        a4_rec = (int(post.shape[0] * 7 / 9), post.shape[0], 0, post.shape[1])

        a1 = post[a1_rec[0] : a1_rec[1], a1_rec[2] : a1_rec[3]]
        a2 = post[a2_rec[0] : a2_rec[1], a2_rec[2] : a2_rec[3]]
        a3 = post[a3_rec[0] : a3_rec[1], a3_rec[2] : a3_rec[3]]
        a4 = post[a4_rec[0] : a4_rec[1], a4_rec[2] : a4_rec[3]]

        a1_p = self.calc(a1, a1_rec[2], a1_rec[0])
        a2_p = self.calc(a2, a2_rec[2], a2_rec[0])
        a3_p = self.calc(a3, a3_rec[2], a3_rec[0])
        a4_p = self.calc(a4, a4_rec[2], a4_rec[0])
        print(str(a1_p) + '\t' + str(a2_p) + '\t' + str(a3_p) + '\t' + str(a4_p))

        if a1_p[0] > 200 and a2_p[0] > 200:
            self.command = command.Command.Stop
        elif abs((a3_p[1][0] + a4_p[1][0]) / 2 - dil.shape[1] / 2) > dil.shape[1] * 0.2:
            if (a3_p[1][0] + a4_p[1][0]) / 2 < dil.shape[1] / 2:
                self.command = command.Command.LeftShift
            else:
                self.command = command.Command.RightShift
        elif abs(a3_p[1][0] - a4_p[1][0]) > 4:
            if a3_p[1][0] < a4_p[1][0]:
                self.command = command.Command.LeftRotate
            else:
                self.command = command.Command.RightRotate
        else:
            self.command = command.Command.Forward

        return self.command
