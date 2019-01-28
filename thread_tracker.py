#!/usr/bin/python3

import cv2
import multiprocessing as mp
import time
from command import Command


class tracker(mp.Process):
# Init {{{
    def __init__(self, videoDev, car, com):
        mp.Process.__init__(self)
        self.cam = cv2.VideoCapture(videoDev)
        self.ele = cv2.getStructuringElement(cv2.MORPH_RECT, (10, 10))
        self.command = Command.Stop
        self.car = car
        self.com = com

        self.com = com

        tmpImg = self.readImg()
        post = self.preprocess(tmpImg)
        self.lastImg = tmpImg
        # Y, toY, X,toX
        self.a1_rec = (0, int(post.shape[0] / 3), 0, int(post.shape[1] * 5 / 16))
        self.a2_rec = (0, int(post.shape[0] / 3), int(post.shape[1] * 11 / 16), post.shape[1])
        self.a3_rec = (int(post.shape[0] / 3), int(post.shape[0] * 2/ 3), 0, post.shape[1])
        self.a4_rec = (int(post.shape[0] * 7 / 9), post.shape[0], 0, post.shape[1])

        pass
# }}}

    # Run, main thread loop {{{
    # Here, this thrad firstly check the current command from app.
    # If the current command is track, then calculate direction, and
    # the corresponding command. The tracker thread send the command
    # to car.
    def run(self):
        while True:
            c = Command(self.com.value)
            if c == Command.Track:
                self.command = self.getDir()
                self.car.move(self.command)
            time.sleep(0.1)
        pass
    # }}}

    # Read image {{{
    def readImg(self):
        r, img = self.cam.read()
        if r:
            self.lastImg = img
        return self.lastImg
    # }}}

    # Image preprocess {{{
    def preprocess(self, img):
        # Down Sampling twice
        d1 = cv2.pyrDown(img, (img.shape[1] / 2, img.shape[0] / 2))
        d2 = cv2.pyrDown(d1, (d1.shape[1] / 2, d1.shape[0] / 2))

        # Grailize
        gray = cv2.cvtColor(d2, cv2.COLOR_BGR2GRAY)

        # Threshold ( OTSU, then binary_inv )
        th, bi = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU)
        th, bi = cv2.threshold(gray, th, 255, cv2.THRESH_BINARY_INV)

        # Erode and dilate
        erd = cv2.erode(bi, self.ele)
        dil = cv2.dilate(erd, self.ele)

        return dil
    # }}}

    # Calcuate the center and mass. {{{
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
    # }}}

    # Calculate direction. {{{
    def getDir(self):
        img = self.readImg()
        post = self.preprocess(img)

        # Cut image
        a1 = post[self.a1_rec[0] : self.a1_rec[1], self.a1_rec[2] : self.a1_rec[3]]
        a2 = post[self.a2_rec[0] : self.a2_rec[1], self.a2_rec[2] : self.a2_rec[3]]
        a3 = post[self.a3_rec[0] : self.a3_rec[1], self.a3_rec[2] : self.a3_rec[3]]
        a4 = post[self.a4_rec[0] : self.a4_rec[1], self.a4_rec[2] : self.a4_rec[3]]

        # Calculate center
        a1_p = self.calc(a1, self.a1_rec[2], self.a1_rec[0])
        a2_p = self.calc(a2, self.a2_rec[2], self.a2_rec[0])
        a3_p = self.calc(a3, self.a3_rec[2], self.a3_rec[0])
        a4_p = self.calc(a4, self.a4_rec[2], self.a4_rec[0])

        # Motion calculate
        if a1_p[0] > 200 and a2_p[0] > 200:
            self.command = Command.Stop
        elif abs((a3_p[1][0] + a4_p[1][0]) / 2 - post.shape[1] / 2) > post.shape[1] * 0.2:
            if (a3_p[1][0] + a4_p[1][0]) / 2 < post.shape[1] / 2:
                self.command = Command.LeftShift
            else:
                self.command = Command.RightShift
        elif abs(a3_p[1][0] - a4_p[1][0]) > 4:
            if a3_p[1][0] < a4_p[1][0]:
                self.command = Command.LeftRotate
            else:
                self.command = Command.RightRotate
        else:
            self.command = Command.Forward

        return self.command
    # }}}
    # Stop {{{
    def stop(self):
        self.running = False
    # }}}
