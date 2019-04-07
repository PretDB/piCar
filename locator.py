#!/usr/bin/python3
import cv2
import numpy
import sys
import getopt
import time
import logging
from logging.handlers import RotatingFileHandler
import cmath
import math
import random
import socket
import json
import pca
import servo


class Locator():    # {{{
    def __init__(self, benchmark=False,
                 lens=0,
                 release=True,
                 useServo=False):    # {{{
        # Initiate network {{{
        self.targetAddress = ('<broadcast>', 6868)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        testS = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        testS.connect(('8.8.8.8', 80))
        self.localIP = testS.getsockname()[0]
        self.deviceName = int(socket.gethostname()) - 10
        testS.close()
        self.socket.bind(('', 9999))    # }}}

        # Servo initiation if needed. {{{
        self.useServo = useServo
        if useServo:
            pwm = pca.PCA()
            self.servo = servo.Servo(pwm, 4, maxAngle=270)
            self.servo.setAngle(0)
            time.sleep(2)
            self.servo.setAngle(self.servo.maxAngle)
            time.sleep(2)
            self.servo.setAngle(self.servo.maxAngle / 2)
            pass
        # }}}

        # Initiate hearbeat package {{{
        self.heartbeatPackage = {'FromID': self.deviceName,
                                 'Type': 'locate',
                                 'Msg': None}    # }}}

        # Initiate logger. {{{
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.NOTSET)

        termFormatter = logging.Formatter('%(asctime)s '
                                          + '%(levelname)-10s %(message)s')
        fileFormatter = logging.Formatter('[%(asctime)s] ' +
                                          '%(filename)s:%(lineno)-4d ' +
                                          '[%(levelname)s] ' +
                                          '%(message)s')
        hterm = logging.StreamHandler()
        hterm.setFormatter(termFormatter)
        hfile = RotatingFileHandler('locator.log',
                                    maxBytes=10*1024*1024,
                                    backupCount=10)
        hfile.setFormatter(fileFormatter)
        hfile.setLevel(logging.INFO)
        if benchmark:
            hterm.setLevel(logging.DEBUG)
        elif release:
            hterm.setLevel(logging.INFO)
        else:
            hterm.setLevel(logging.DEBUG)
        logging.getLogger('').addHandler(hterm)
        self.logger.addHandler(hterm)
        self.logger.addHandler(hfile)    # }}}

        # Log basic configurations. {{{
        self.logger.info('Locator initiation started.')

        self.isBenchmark = benchmark
        self.isRelease = release
        self.logger.info('Benchmark: ' + str(benchmark))
        self.logger.info('Release:' + str(release))
        self.logger.info('Use servo: ' + str(useServo))    # }}}

        # Device and environment initiation {{{
        self.objPoints = numpy.array([[-1000.0, -750.0, 0],
                                      [1000.0, -750.0, 0],
                                      [1000.0, 750.0, 0],
                                      [-1000.0, 750.0, 0]],
                                     numpy.float32)
        self.cam = dict()
        if lens == 1:
            self.cam['inst'] = numpy.array([[543.8368, 0, 631.7431],
                                            [0, 542.7832, 352.6432],
                                            [0, 0, 1]])
            self.cam['dist'] = numpy.array([-0.2667,
                                            0.0648,
                                            -1.4602e-4,
                                            0.0020,
                                            -0.0069])
            pass
        else:
            self.cam['inst'] = numpy.array([[543.8368, 0, 631.7431],
                                            [0, 542.7832, 352.6432],
                                            [0, 0, 1]])
            self.cam['dist'] = numpy.array([-0.2667,
                                            0.0648,
                                            -1.4602e-4,
                                            0.0020,
                                            -0.0069])
            pass
        self.logger.info('Len %s loaded.' % (lens))
        self.cam['dev'] = cv2.VideoCapture('/dev/locator')    # }}}

        # Test camera {{{
        self.logger.info('Setting camera parameter: %s' %
                         ('Success' if
                          (self.cam['dev'].set(cv2.CAP_PROP_FRAME_HEIGHT,
                                               720) &
                           self.cam['dev'].set(cv2.CAP_PROP_FRAME_WIDTH,
                                               1280))
                          else 'Failed'))
        for i in range(3):
            read, img = self.cam['dev'].read()
            self.logger.info('Attempt to read image from camera at ' +
                             ('%s tries: %s') %
                             (i + 1, 'Success' if read else 'Failed'))
            if read:
                break
            else:
                if i == 2:
                    self.logger.critical('Camera is not available.')
        # }}}

        self.tvec, self.rvec = None, None
        self.logger.info('Locator initiation done, start main thread.')
        if not release:
            cv2.namedWindow('raw')
        pass    # }}}

    def run(self):    # {{{
        self.logger.info('Main thread running.')
        while True:
            last = time.time()
            for i in range(10):
                self.cam['dev'].grab()
            read, img = self.cam['dev'].read()
            if read:    # {{{
                tvec, rvec = self.__locator(img)

                if tvec is not None or rvec is not None:    # {{{
                    loc = {'X': round(tvec[0], 2),
                           'Y': round(tvec[1], 2),
                           'Z': round(tvec[2], 2)}
                    ang = round(rvec)
                    self.logger.debug('=====================================')
                    self.logger.debug(time.ctime())
                    self.logger.debug('Calculated angle: ' + str(ang))

                    if self.useServo:    # {{{
                        thresh = 3
                        error = 0
                        if ang < 90 and ang - 0 > thresh:
                            error = -ang
                            pass
                        elif ang < 270 and abs(ang - 180) > thresh:
                            error = 180 - ang
                            pass
                        elif 360 - ang > thresh:
                            error = 360 - ang

                        self.logger.debug('Fix: ' + str(error))
                        # Check servo angle.
                        if self.servo.angle + error >\
                                self.servo.maxAngle:
                            # self.servo.setAngle(self.servo.angle - 180)
                            error = error - 180
                            ang += 180
                        if self.servo.angle + error < 0:
                            # self.servo.setAngle(self.servo.angle + 180)
                            error = 180 + error
                            ang -= 180

                        self.logger.debug('Post Fix: '
                                          + str(error))
                        self.servo.setAngle(self.servo.angle
                                            + error)
                        time.sleep(abs(error) / 60)
                        self.logger.debug('Servo: ' + str(self.servo.angle))
                        ang += error

                    # }}}

                    self.heartbeatPackage['Msg'] = {'position': loc,
                                                    'orientation': ang}
                    self.tvec, self.rvec = tvec, rvec
                    dataRaw = json.dumps(self.heartbeatPackage)
                    dataByte = dataRaw.encode('utf-8')
                    self.socket.sendto(dataByte, self.targetAddress)
                    self.logger.debug(dataRaw)
                    # }}}
                else:    # {{{
                    if self.isRelease:
                        self.logger.warning('Locate failed, no valid loc got, '
                                            + 'last loc %s'
                                            % str(self.tvec) +
                                            ', last orien: %s'
                                            % str(self.rvec))
                # }}}

                fps = round(1.0 / (time.time() - last), 1)

                if self.isBenchmark:
                    self.logger.debug('FPS: %s', fps)

                if not self.isRelease:
                    cv2.imshow('raw', cv2.resize(img,
                                                 (round(img.shape[1] / 2),
                                                  round(img.shape[0] / 2))))
                    key = cv2.waitKey(30)
                    if key == ord(' '):
                        key = cv2.waitKey(0)
                    if key == ord('q'):
                        break
            # }}}
            else:    # {{{
                if self.isRelease:
                    self.logger.error('locate Failed, can not get image')
                continue
            # }}}
        pass    # }}}

    def __validateContour(self, contour, img, imgSize=(1280, 720)):    # {{{
        area = cv2.contourArea(contour)
        if area < 500 or area > 5000:
            return False
        # if not cv2.isContourConvex(contour):
        #     return False

        # Filter by number of contours approxed whoes precision is defiened
        # by its length.
        # precision = 0.1 * cv2.arcLength(contour, closed=True)
        # approxContour = cv2.approxPolyDP(contour, precision, closed=True)
        # if not len(approxContour) == 4:
        #     return False

        # Filter by similarity between contour and its minimum binding
        # rectangle.
        minRect = cv2.minAreaRect(contour)
        minRect = cv2.boxPoints(minRect)
        if cv2.contourArea(contour) / cv2.contourArea(minRect) <= 0.6:
            return False

        moment = cv2.moments(contour, True)
        center = (moment['m10'] / moment['m00'],
                  moment['m01'] / moment['m00'])
        rate = 0.1
        if center[0] < imgSize[0] * rate or center[0] > imgSize[0] * 0.9:
            return False

        if img[round(center[1])][round(center[0])] < 250:
            return False

        return True    # }}}

    def __detectMarker(self, img):    # {{{
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # th, binaryImg = cv2.threshold(gray, 150, 255, cv2.THRESH_OTSU)
        th, binaryImg = cv2.threshold(gray, 250, 255, cv2.THRESH_TOZERO)
        # binaryImg = cv2.adaptiveThreshold(gray, 255,
        #                                   cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        #                                   cv2.THRESH_BINARY_INV,
        #                                   41,
        #                                   -20)
        binaryImg = cv2.morphologyEx(binaryImg, cv2.MORPH_CLOSE, (21, 21))
        c, contours, hierarchy = cv2.findContours(binaryImg,
                                                  cv2.RETR_TREE,
                                                  cv2.CHAIN_APPROX_SIMPLE)

        validContours = list()
        for i in range(len(contours)):
            if not self.__validateContour(contours[i], binaryImg):
                continue

            moment = cv2.moments(contours[i], True)
            try:
                centriod = (moment['m10'] / moment['m00'],
                            moment['m01'] / moment['m00'])
                validResult = {'contour': contours[i],
                               'centriod': centriod}

                validContours.append(validResult)

                if not self.isRelease:
                    color = (round(random.random() * 255),
                             round(random.random() * 255),
                             round(random.random() * 255))
                    img = cv2.drawContours(img,
                                           contours,
                                           i,
                                           color,
                                           1,
                                           cv2.LINE_AA)
            except ZeroDivisionError:
                continue

        if self.isRelease:
            return validContours
        else:
            img = cv2.putText(img, str(len(validContours)),
                              (0, round(img.shape[0] / 2)),
                              cv2.FONT_HERSHEY_DUPLEX,
                              5,
                              (0, 255, 0))
            return validContours, binaryImg, img
        pass    # }}}

    def __locator(self, image):    # {{{
        loc = None
        rot = None
        if self.isRelease:
            validContours = self.__detectMarker(image)
        else:
            validContours, binaryImg, image = self.__detectMarker(image)

        calcImg = numpy.zeros([image.shape[0], image.shape[1], 3],
                              numpy.uint8)
        markedImg = image

        if len(validContours) == 5:    # Got valid contours {{{
            # Calculate the miniman enclosing circle
            centriods = [p['centriod'] for p in validContours]
            centriodsArray = numpy.array(centriods, numpy.float32)

            # Remove marker {{{
            encCircle = cv2.minEnclosingCircle(centriodsArray)
            epsilon = 10
            approximatedContours = cv2.approxPolyDP(centriodsArray,
                                                    epsilon,
                                                    closed=True)
            while not len(approximatedContours) == 4:    # {{{
                epsilon = epsilon + 5
                approximatedContours = cv2.approxPolyDP(centriodsArray,
                                                        epsilon,
                                                        closed=True)
                if epsilon > 200:
                    return loc, rot
                # }}}
            avgDis = list()
            marker = [0, 0]
            for c in centriodsArray:
                if c in approximatedContours[:, 0]:
                    avgDis.append(c)
                else:
                    marker = c
            # }}}

            # Get X and Y axis {{{
            y = numpy.array([marker[0] - encCircle[0][0],
                             marker[1] - encCircle[0][1]],
                            numpy.float32)
            yAxis3d = numpy.array([y[0], y[1], 0], numpy.float32)
            zAxis3d = numpy.array([0, 0, 1], numpy.float32)
            xAxis3d = numpy.cross(zAxis3d, yAxis3d)
            xAxisImg = numpy.array([xAxis3d[0], xAxis3d[1]], numpy.float32)
            yAxisImg = numpy.array([yAxis3d[0], yAxis3d[1]], numpy.float32)

            # Coordinate points
            o = (int(round(encCircle[0][0])), int(round(encCircle[0][1], 0)))
            xArrow = (int(round(encCircle[0][0] + xAxisImg[0])),
                      int(round(encCircle[0][1] + xAxisImg[1])))
            yArrow = (int(round(encCircle[0][0] + yAxisImg[0])),
                      int(round(encCircle[0][1] + yAxisImg[1])))
            # }}}

            # Calculate affine matrix. {{{
            imagPoints = numpy.array([xArrow, encCircle[0], yArrow],
                                     numpy.float32)
            cplxPoints = numpy.array([[numpy.linalg.norm(xAxisImg), 0],
                                      [0, 0],
                                      [0, numpy.linalg.norm(yAxisImg)]],
                                     numpy.float32)
            affineMat = cv2.getAffineTransform(imagPoints, cplxPoints)
            # }}}

            # Warp affine transform onto points ( marker excepted ) {{{
            pointsComplex = list()
            for point in avgDis:
                p = numpy.array([point[0], point[1], 1], numpy.float32)
                pAffined = numpy.matmul(affineMat, p)
                pointsComplex.append(numpy.array([pAffined, point],
                                                 numpy.float32))
            # }}}

            # Calculate angle in comples corrdinate. {{{
            pointsAngle = list()
            for pc in pointsComplex:
                c = complex(pc[0][0], pc[0][1])
                angle = cmath.log(c).imag
                if angle < 0:
                    angle += cmath.pi * 2
                pointsAngle.append([pc, angle])
            pointsAngle.sort(key=(lambda x: x[1]), reverse=True)
            # }}}

            # Pose estimating {{{
            corners = numpy.zeros([1, 1, 2])
            for p in pointsAngle:
                cor = numpy.array([p[0][1]], dtype=numpy.float32, ndmin=3)
                corners = numpy.append(corners, cor, axis=1)
            corners = corners[:, 1: len(corners[0]), :]
            retval, rvec, tvec = cv2.solvePnP(self.objPoints,
                                              corners,
                                              self.cam['inst'],
                                              self.cam['dist'],
                                              flags=cv2.SOLVEPNP_ITERATIVE)
            # }}}

            # Calculate camera pose. {{{
            rotMat = cv2.Rodrigues(rvec)[0]
            w2cMatHomo = numpy.append(rotMat, tvec, axis=1)
            w2cMatHomo = numpy.append(w2cMatHomo,
                                      numpy.array([[0, 0, 0, 1]],
                                                  numpy.float32),
                                      axis=0)
            w2cMatHomo = numpy.matrix(w2cMatHomo)
            # c2wMat = w2cMatHomo.I
            # camLocInCamMat = numpy.append(numpy.array([0, 0, 0]), 1)
            # camLocInWldMat = numpy.matmul(c2wMat, camLocInCamMat)
            # c2wTVec = c2wMat[:3, 3]
            # c2wRMat = c2wMat[:3, :3]
            # c2wRVec = cv2.Rodrigues(c2wRMat)
            # c2wTVec = camLocInWldMat

            angZ = math.atan2(rotMat[1][0], rotMat[0][0]) / math.pi * 180
            printLoc = (round(tvec[0][0], 2),
                        round(tvec[1][0], 2),
                        round(tvec[2][0], 2))
            loc = printLoc
            rot = angZ
            loc = (round((-loc[0] / 1000.0 + 3) / 6, 2),
                   round((loc[1] / 1000.0 + 2) / 4, 2),
                   round(loc[2] / 1000.0, 2))

            if rot < 0:
                rot += 360
            rot = 360 - rot
            # }}}

            # Draw {{{
            if not self.isRelease:
                calcImg = cv2.line(calcImg, o, xArrow, (100, 100, 100), 2)
                calcImg = cv2.putText(calcImg,
                                      'x',
                                      xArrow,
                                      cv2.FONT_HERSHEY_COMPLEX_SMALL,
                                      1,
                                      (200, 100, 0))
                calcImg = cv2.line(calcImg, o, yArrow, (100, 100, 100), 2)
                calcImg = cv2.putText(calcImg,
                                      'y',
                                      yArrow,
                                      cv2.FONT_HERSHEY_COMPLEX_SMALL,
                                      1,
                                      (200, 100, 0))
                color = (50, 0, 0)
                f = 1
                for p in pointsAngle:
                    r = (int(round(p[0][1][0])), int(round(p[0][1][1])))
                    calcImg = cv2.line(calcImg, o, r, color, 3)
                    calcImg = cv2.putText(calcImg,
                                          str(f),
                                          r,
                                          cv2.FONT_HERSHEY_COMPLEX_SMALL,
                                          1,
                                          (0, 233, 233))
                    f += 1
                    color = (color[0], color[1] + 60, color[2])

                for p in centriods:
                    location = (int(round(p[0])), int(round(p[1])))
                    calcImg = cv2.circle(calcImg, location, 10, (0, 0, 255), 1)
                calcImg = cv2.circle(calcImg,
                                     (round(encCircle[0][0]),
                                      round(encCircle[0][1])),
                                     round(encCircle[1]),
                                     (100, 0, 200), 1)
                markedImg = cv2.putText(markedImg, str(loc), (0, 100),
                                        cv2.FONT_HERSHEY_COMPLEX_SMALL, 2,
                                        (150, 50, 150))

                markedImg = cv2.putText(markedImg, str(round(angZ)), (0, 150),
                                        cv2.FONT_HERSHEY_COMPLEX_SMALL, 2,
                                        (50, 50, 0))
                markedImg = cv2.aruco.drawAxis(markedImg,
                                               self.cam['inst'],
                                               self.cam['dist'],
                                               rvec,
                                               tvec,
                                               300)
                cv2.imshow('calc', cv2.resize(calcImg,
                                              (round(calcImg.shape[1] / 2),
                                               round(calcImg.shape[0] / 2))))
                cv2.imshow('mark', cv2.resize(markedImg,
                                              (round(markedImg.shape[1] / 2),
                                               round(markedImg.shape[0] / 2))))
                cv2.imshow('bina', cv2.resize(binaryImg,
                                              (round(binaryImg.shape[1] / 2),
                                               round(binaryImg.shape[0] / 2))))
            # }}}

            # }}}
        else:
            if not self.isRelease:
                cv2.imshow('bina', cv2.resize(binaryImg,
                                              (round(binaryImg.shape[1] / 2),
                                               round(binaryImg.shape[0] / 2))))

        return loc, rot    # }}}
# }}}


benchmark = False
release = False
lens = 0
useServo = False

opts, args = getopt.getopt(sys.argv[1:], 'hbl:rs')
for key, val in opts:
    if key == '-h':
        print('Usage: run [-h] [-b] [-l len] [-d]')
        print('-h: Show this help.')
        print('-b: Run benchmark, print fps only.')
        print('-l len: Select len, can be 0 or 1.')
        print('-r: Run under release mode, use smaller marker.')
        sys.exit(0)
    if key == '-b':
        benchmark = True
    if key == '-l':
        if val == '0':
            pass
        elif val == '1':
            pass
        else:
            pass
    if key == '-r':
        release = True
    if key == '-s':
        useServo = True

lctr = Locator(benchmark=benchmark,
               lens=lens,
               release=release,
               useServo=useServo)
lctr.run()
