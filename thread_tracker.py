#!/usr/bin/python3
import cv2
import time
from command import Command


class tracker():    # {{{
    # Init {{{
    def __init__(self, videoDev, car, com, debug=False):
        self.cam = cv2.VideoCapture(videoDev)
        self.ele = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        self.command = Command.Stop
        self.car = car
        self.com = com
        self.isDebug = debug

        r, i = self.cam.read()
        while not r:
            r, i = self.cam.read()
            time.sleep(0.1)
        self.lastImg = i
        post = self.preprocess(i)
        # Y, toY, X,toX
        self.a1_rec = (0,
                       int(post.shape[0] / 3),
                       0,
                       int(post.shape[1] * 5 / 16))
        self.a2_rec = (0,
                       int(post.shape[0] / 3),
                       int(post.shape[1] * 11 / 16),
                       post.shape[1])
        self.a3_rec = (int(post.shape[0] / 3),
                       int(post.shape[0] * 2 / 3),
                       0,
                       post.shape[1])
        self.a4_rec = (int(post.shape[0] * 7 / 9),
                       post.shape[0],
                       0,
                       post.shape[1])

        pass
# }}}

    # Run, tracker loop {{{
    # Here, this function firstly check the current command from app.
    # If the current command is track, then calculate direction, and
    # the corresponding command. The tracker thread send the command
    # to car.
    def run(self):
        while True:
            c = Command(self.com.value)
            if c == Command.Track:
                self.command = self.getDir()
                self.car.move(self.command)
            else:
                self.car.move(Command.Stop)
                break
            # time.sleep(0.05)
        return
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
        # erd = cv2.erode(bi, self.ele)
        # dil = cv2.dilate(erd, self.ele)
        dil = cv2.morphologyEx(bi, cv2.MORPH_OPEN, self.ele)

        if self.isDebug:
            cv2.imshow('dil', dil)
            cv2.imshow('bi', bi)
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
        a1 = post[self.a1_rec[0]: self.a1_rec[1],
                  self.a1_rec[2]: self.a1_rec[3]]
        a2 = post[self.a2_rec[0]: self.a2_rec[1],
                  self.a2_rec[2]: self.a2_rec[3]]
        a3 = post[self.a3_rec[0]: self.a3_rec[1],
                  self.a3_rec[2]: self.a3_rec[3]]
        a4 = post[self.a4_rec[0]: self.a4_rec[1],
                  self.a4_rec[2]: self.a4_rec[3]]

        # Calculate center
        a1_p = self.calc(a1, self.a1_rec[2], self.a1_rec[0])
        a2_p = self.calc(a2, self.a2_rec[2], self.a2_rec[0])
        a3_p = self.calc(a3, self.a3_rec[2], self.a3_rec[0])
        a4_p = self.calc(a4, self.a4_rec[2], self.a4_rec[0])

        if self.isDebug:
            post = cv2.cvtColor(post, cv2.COLOR_GRAY2RGB)
            post = cv2.line(post,
                            (0, int(post.shape[0] / 3)),
                            (post.shape[1], int(post.shape[0] / 3)),
                            (255, 0, 0))
            post = cv2.line(post,
                            (0, int(post.shape[0] * 7 / 9)),
                            (post.shape[1], int(post.shape[0] * 7 / 9)),
                            (255, 0, 0))
            post = cv2.line(post,
                            (int(post.shape[1] * 5 / 16),
                             int(post.shape[0] / 3)),
                            (int(post.shape[1] * 5 / 16), 0),
                            (255, 0, 0))
            post = cv2.line(post,
                            (int(post.shape[1] * 11 / 16),
                             int(post.shape[0] / 3)),
                            (int(post.shape[1] * 11 / 16), 0),
                            (255, 0, 0))
            post = cv2.circle(post, (a1_p[1][0], a1_p[1][1]), 2, (0, 0, 255))
            post = cv2.circle(post, (a2_p[1][0], a2_p[1][1]), 2, (0, 0, 255))
            post = cv2.circle(post, (a3_p[1][0], a3_p[1][1]), 2, (0, 0, 255))
            post = cv2.circle(post, (a4_p[1][0], a4_p[1][1]), 2, (0, 0, 255))

            img = cv2.line(img,
                           (0, int(img.shape[0] / 3)),
                           (img.shape[1], int(img.shape[0] / 3)),
                           (255, 0, 0))
            img = cv2.line(img,
                           (0, int(img.shape[0] * 7 / 9)),
                           (img.shape[1], int(img.shape[0] * 7 / 9)),
                           (255, 0, 0))
            img = cv2.line(img,
                           (int(img.shape[1] * 5 / 16),
                            int(img.shape[0] / 3)),
                           (int(img.shape[1] * 5 / 16), 0),
                           (255, 0, 0))
            img = cv2.line(img,
                           (int(img.shape[1] * 11 / 16),
                            int(img.shape[0] / 3)),
                           (int(img.shape[1] * 11 / 16), 0), (255, 0, 0))

        # Motion calculate
        # if a1_p[0] > 200 and a2_p[0] > 200:
        #     self.command = Command.Stop
        if abs((a3_p[1][0] + a4_p[1][0]) / 2 - post.shape[1] / 2)\
                > post.shape[1] * 0.15:
            if (a3_p[1][0] + a4_p[1][0]) / 2 < post.shape[1] / 2:
                self.command = Command.LeftShift
            else:
                self.command = Command.RightShift
        elif abs(a3_p[1][0] - a4_p[1][0]) > 10:
            if a3_p[1][0] < a4_p[1][0]:
                self.command = Command.LeftRotate
            else:
                self.command = Command.RightRotate
        else:
            self.command = Command.Forward

        if self.isDebug:
            img = cv2.putText(img, str(self.command), (0, img.shape[0]),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 255))
            post = cv2.putText(post, str(self.command), (0, post.shape[0]),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 255))
            cv2.imshow('img', img)
            cv2.imshow('post', post)
            cv2.waitKey(20)

        return self.command
    # }}}
# }}}
