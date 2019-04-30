#!/usr/bin/python3
import cv2
import numpy
import time
import logging
from logging.handlers import RotatingFileHandler
from multiprocessing import Value
import cmath
import math
import random
import socket
import json
import threading


class Locator():    # {{{
    def __init__(self, benchmark=False,
                 lens=0,
                 release=True,
                 useServo=False,
                 showImg=False,
                 setCalib=None,
                 isDebug=None):    # {{{
        # Initiate network {{{
        self.targetAddress = ('<broadcast>', 6868)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        testS = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        testS.connect(('8.8.8.8', 80))
        self.localIP = testS.getsockname()[0]
        self.deviceName = int(socket.gethostname()) - 10
        # self.deviceName = socket.gethostname()
        testS.close()
        self.socket.bind(('', 9999))    # }}}

        # Servo initiation if needed. {{{
        self.useServo = useServo
        if useServo:
            import pca
            import servo
            import qmc
            pwm = pca.PCA()
            self.servo = servo.Servo(pwm, 4, maxAngle=270)
            self.servo.setAngle(self.servo.maxAngle / 2)
            pass
        # }}}

        # Compass initiation if needed. {{{
        if useServo:
            self.compass = qmc.QMC(True)
            self.lastCompassAngle = self.compass.readAngle()
        # }}}

        # Initiate hearbeat package {{{
        self.heartbeatPackage = {'FromID': self.deviceName,
                                 'Type': 'locate',
                                 'Msg': None}    # }}}

        # Initiate logger. {{{
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.NOTSET)

        termFormatter = logging.Formatter('%(asctime)s '
                                          + '\033[32m%(levelname)-10s\033[0m %(message)s')
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
        if release:
            hterm.setLevel(logging.WARNING)
        else:
            hterm.setLevel(logging.DEBUG)
        logging.getLogger('').addHandler(hterm)
        self.logger.addHandler(hterm)
        # self.logger.addHandler(hfile)    # }}}

        # Log basic configurations. {{{
        self.logger.info('Locator initiation started.')

        self.isBenchmark = benchmark
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

        self.lastLocateTime = time.time()
        self.nextLocateTime = time.time()
        self.tvec, self.rvec = None, None
        self.logger.info('Locator initiation done, start main thread.')
        self.showImg = showImg
        self.setCalib = setCalib
        if showImg:
            cv2.namedWindow('raw')
            pass
        pass    # }}}

    def oneEpoch(self, img):
        self.logger.debug('============== Epoch =============')
        tvec, rvec, code, markedImg = self.__locator(img)
        if time.time() - self.lastLocateTime < 0.5:
            return markedImg
        if time.time() < self.nextLocateTime:
            return markedImg
        self.lastLocateTime = time.time()

        if tvec is not None or rvec is not None:    # {{{
            loc = {'X': round(tvec[0], 5),
                   'Y': round(tvec[1], 5),
                   'Z': round(tvec[2], 5)}
            ang = round(rvec)
            self.logger.debug('Calculated done, loc=%s, angle=%d.'
                              % (str(loc), ang))

            # if self.tvec is not None:
            #     dis = ((tvec[0] - self.tvec[0]) ** 2 +
            #            (tvec[1] - self.tvec[1]) ** 2)
            #     self.logger.debug('Distance: %f', dis)
            #     if dis > 0.2 ** 2:
            #         continue

            if self.useServo:    # {{{
                thresh = 2
                error = 0
                if ang < 90 and ang - 0 > thresh:
                    error = -ang
                    pass
                elif ang < 270 and abs(ang - 180) > thresh:
                    error = 180 - ang
                    pass
                elif ang > 270 and 360 - ang > thresh:
                    error = 360 - ang

                self.logger.debug('Fix: ' + str(error))
                # Check servo angle.
                if self.servo.angle + error >\
                        self.servo.maxAngle:
                    error = error - 180
                elif self.servo.angle + error < 0:
                    error = 180 + error
                    # ang -= 180

                self.logger.debug('\033[32mPost Fix: %f.\033[0m' % (error))
                self.logger.debug('Servo: %d -> %d'
                                  % (self.servo.angle,
                                     self.servo.angle + error))
                self.servo.setAngle(self.servo.angle
                                    + error)
                # time.sleep(abs(error) * 0.008)
                self.nextLocateTime = time.time() + abs(error) * 0.010
                ang += self.servo.angle + error

            # }}}

            ang -= 35
            if ang < 0:
                ang += 360
            while ang > 360:
                ang -= 360
            self.logger.debug('\033[41morientation: %d\033[0m' % ang)
            self.heartbeatPackage['Msg'] = {'position': loc,
                                            'orientation': ang}
            self.tvec, self.rvec = tvec, rvec
            self.lastCompassAngle = self.compass.readAngle()
            dataRaw = json.dumps(self.heartbeatPackage)
            dataByte = dataRaw.encode('utf-8')
            self.logger.debug(dataByte)
            self.socket.sendto(dataByte, self.targetAddress)
            # self.logger.debug('Package: %s' % dataRaw)
            self.logger.debug('Locate: %s' % loc)
            # }}}
        else:    # {{{
            self.logger.warning('Locate failed, no valid loc got, '
                                + 'last loc %s'
                                % str(self.tvec) +
                                ', last orien: %s'
                                % str(self.rvec))
            self.heartbeatPackage['Msg'] = None
            dataRaw = json.dumps(self.heartbeatPackage)
            dataByte = dataRaw.encode('utf-8')
            self.logger.debug(dataByte)
            self.socket.sendto(dataByte, self.targetAddress)
            if self.useServo:
                compassAngle = self.compass.readAngle()
                compassError = compassAngle - self.lastCompassAngle
                self.logger.debug('Compass Fix: %f' % compassError)
                if self.servo.angle + compassError\
                        > self.servo.maxAngle:
                    compassError -= 180
                elif self.servo.angle + compassError < 0:
                    compassError += 180
                self.logger.debug('\033[32mCompass post fix: %f.\033[0m'
                                  % compassError)
                self.logger.debug('Compass servo fix: %f -> %f'
                                  % (self.servo.angle,
                                     self.servo.angle + compassError))
                self.logger.debug('Compass angle: %f, last: %f' % (compassAngle, self.lastCompassAngle))
                self.nextLocateTime = time.time() + abs(compassError) * 0.010
                self.servo.setAngle(self.servo.angle + compassError)
            self.logger.debug('%s' % json.dumps(self.heartbeatPackage))
        self.lastCompassAngle = self.compass.readAngle()
        return markedImg

    def run(self):    # {{{
        self.logger.info('Main thread running.')
        # Test camera {{{
        self.logger.info('Setting camera parameter: %s' %
                         ('Success' if
                          (self.cam['dev'].set(cv2.CAP_PROP_FRAME_HEIGHT,
                                               720) and
                           self.cam['dev'].set(cv2.CAP_PROP_FRAME_WIDTH,
                                               1280) and
                           self.cam['dev'].set(cv2.CAP_PROP_AUTO_EXPOSURE,
                                               0.25) and
                           self.cam['dev'].set(cv2.CAP_PROP_EXPOSURE,
                                               0.03))
                          else 'Failed'))
        while True:
            if self.setCalib is not None:
                if self.setCalib.value != 0:
                    self.logger.warning('isCalib: %s' % str(self.setCalib.value))
                    self.logger.debug('Start Cali, please wait')
                    self.compass.cali(True)
                    self.setCalib.value = 0
                pass

            self.logger.debug('=====================================')
            last = time.time()
            self.logger.debug('Exposure: %f'
                              % self.cam['dev'].get(cv2.CAP_PROP_EXPOSURE))
            # if self.useServo:
            #     self.lastCompassAngle = self.compass.readAngle()

            buffCount = 0
            self.logger.debug('Clear start: @ %f' % (time.time() - last))
            for i in range(4):
                self.cam['dev'].grab()
                # self.logger.warning('Buff count: %d @ %f'
                #                     % (buffCount, time.time() - last))
            read, img = self.cam['dev'].read()
            if read:    # {{{
                self.oneEpoch(img)

                if self.showImg:
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
                self.logger.error('locate Failed, can not get image')
                continue
            # }}}

            fps = round(1.0 / (time.time() - last), 1)

            if self.isBenchmark:
                self.logger.info('FPS: %s', fps)
        pass    # }}}

    def __distanceToLine(self, point, lp1, lp2):
        a = lp2[1] - lp1[1]
        b = lp1[0] - lp2[0]
        c = lp2[0] * lp1[1]\
            - lp1[0] * lp2[1]
        dis = abs(a * point[0] + b * point[1] + c)\
            / ((a * a + b * b) ** 0.5)
        return dis

    def __distanceToPoint(self, point, target):
        return ((point[0] - target[0]) ** 2
                + (point[1] - target[1]) ** 2) ** 0.5

    def __findLabel(self, contour):
        m = list()
        for i in range(len(contour)):
            for j in range(i + 1, len(contour)):
                for k in range(len(contour)):
                    if not k == i and not k == j:
                        d = self.__distanceToLine(contour[k],
                                                  contour[i],
                                                  contour[j])
                        dp1 = self.__distanceToPoint(contour[k],
                                                     contour[i])
                        dp2 = self.__distanceToPoint(contour[k],
                                                     contour[j])
                        m.append([d, dp1, dp2,
                                  k, i, j])
                        pass
                    else:
                        continue
        m.sort(key=(lambda x: x[0]))
        m = m[:3]
        m.sort(key=(lambda x: x[1] + x[2]))
        return m[0][3]
        pass

    def __validateContour(self, contour, img, imgSize=(1280, 720)):    # {{{
        area = cv2.contourArea(contour)
        if area < 200 or area > 5000:
            # if self.showImg:
            #     img = cv2.putText(img,
            #                       'area: %f' % area,
            #                       (contour[0][0][0], contour[0][0][1]),
            #                       cv2.FONT_HERSHEY_COMPLEX_SMALL,
            #                       1,
            #                       255)
            return False
        # if not cv2.isContourConvex(contour):
        #     return False

        # Filter by number of contours approxed whoes precision is defiened
        # by its length.
        rate = 0
        length = cv2.arcLength(contour, closed=True)
        # precision = rate * length
        # approxContour = cv2.approxPolyDP(contour, precision, closed=True)
        # while not len(approxContour) == 4:
        #     if rate > 0.1:
        #         return False
        #     rate += 0.01
        #     precision = rate * cv2.arcLength(contour, closed=True)
        #     approxContour = cv2.approxPolyDP(contour, precision, closed=True)
        # self.logger.debug('Approx Contour: %s' % str(approxContour))
        # self.logger.debug('Approx Contour: %s' % str(approxContour[0: 2]))
        # self.logger.debug('Approx Contour: %s' % str(approxContour[0: 4: 3]))
        # e0 = cv2.arcLength(approxContour[0: 2], closed=False)
        # e1 = cv2.arcLength(approxContour[1: 3], closed=False)
        # e2 = cv2.arcLength(approxContour[2: 4], closed=False)
        # e3 = cv2.arcLength(numpy.array([approxContour[0],
        #                                 approxContour[3]]), closed=False)
        # if abs(e0 - e2) / max(e0, e2) > 0.4\
        #         or abs(e1 - e3) / max(e1, e3) > 0.4:
        #     return False

        # Filter by convexity.
        hull = cv2.convexHull(contour)
        convexity = area / cv2.contourArea(hull)
        if convexity < 0.9:
            if self.showImg:
                img = cv2.putText(img,
                                  'convexity: %f' % convexity,
                                  (contour[0][0][0], contour[0][0][1]),
                                  cv2.FONT_HERSHEY_COMPLEX_SMALL,
                                  1,
                                  255)
            return False

        # Filter by circularity.
        cicularity = 4 * math.pi * area / length ** 2
        if cicularity > 0.85:
            if self.showImg:
                img = cv2.putText(img,
                                  'cicularity: %f' % cicularity,
                                  (contour[0][0][0], contour[0][0][1]),
                                  cv2.FONT_HERSHEY_COMPLEX_SMALL,
                                  1,
                                  255)
            return False

        # Filter by similarity between contour and its minimum binding
        # rectangle.
        minRect = cv2.minAreaRect(contour)
        minRect = cv2.boxPoints(minRect)
        simi = cv2.contourArea(contour) / cv2.contourArea(minRect)
        if simi <= 0.6:
            if self.showImg:
                img = cv2.putText(img,
                                  'simi: %f' % simi,
                                  (contour[0][0][0], contour[0][0][1]),
                                  cv2.FONT_HERSHEY_COMPLEX_SMALL,
                                  1,
                                  255)
            return False

        moment = cv2.moments(contour, True)
        center = (moment['m10'] / moment['m00'],
                  moment['m01'] / moment['m00'])
        rate = 0.1
        # Filter by center posiion.
        if center[0] < imgSize[0] * rate or center[0] > imgSize[0] * 0.9:
            if self.showImg:
                img = cv2.putText(img,
                                  'center: %s' % str(center),
                                  (contour[0][0][0], contour[0][0][1]),
                                  cv2.FONT_HERSHEY_COMPLEX_SMALL,
                                  1,
                                  255)
            return False

        # if img[round(center[1])][round(center[0])] < 250:
        #     return False

        return True    # }}}

    def __detectMarker(self, img):    # {{{
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        binaryImg = gray
        th, binaryImg = cv2.threshold(gray,
                                      250,
                                      255,
                                      cv2.THRESH_BINARY)

        # When environment is darker, this method performs good.
        # th, binaryImg = cv2.threshold(gray, 250, 255, cv2.THRESH_TOZERO)

        # Adaptive threshold
        # binaryImg = cv2.adaptiveThreshold(binaryImg, 255,
        #                                   cv2.ADAPTIVE_THRESH_MEAN_C,
        #                                   cv2.THRESH_BINARY,
        #                                   7,
        #                                   -10)

        binaryImg = cv2.morphologyEx(binaryImg, cv2.MORPH_CLOSE, (31, 31))

        c, contours, hierarchy = cv2.findContours(binaryImg,
                                                  cv2.RETR_EXTERNAL,
                                                  cv2.CHAIN_APPROX_SIMPLE)

        validContours = list()
        for i in range(len(contours)):
            if not self.__validateContour(contours[i], binaryImg):
                continue

            moment = cv2.moments(contours[i], True)
            try:
                centriod = (moment['m10'] / moment['m00'],
                            moment['m01'] / moment['m00'])
                ma = cv2.contourArea(contours[i])
                validResult = {'contour': contours[i],
                               'centriod': centriod,
                               'mass': ma}

                validContours.append(validResult)

                color = (round(random.randrange(100, 255)),
                         round(random.randrange(100, 255)),
                         round(random.randrange(100, 255)))
                img = cv2.drawContours(img,
                                       contours,
                                       i,
                                       color,
                                       2,
                                       cv2.LINE_AA)
            except ZeroDivisionError:
                continue

        img = cv2.putText(img,
                          '%d / %d' % (len(validContours), len(contours)),
                          (0, round(img.shape[0] / 2)),
                          cv2.FONT_HERSHEY_SIMPLEX,
                          5,
                          (0, 0, 255))
        return validContours, binaryImg, img
        pass    # }}}

    def __locator(self, image):    # {{{
        loc = None
        rot = None
        code = 0
        validContours, binaryImg, image = self.__detectMarker(image)

        calcImg = numpy.zeros([image.shape[0], image.shape[1], 3],
                              numpy.float32)
        markedImg = image

        if len(validContours) >= 5:    # Got valid contours {{{
            # Pick the first five big contour.
            validContours.sort(key=(lambda x: x['mass']), reverse=True)
            validContours = validContours[:5]
            # Calculate the miniman enclosing circle
            centriods = [p['centriod'] for p in validContours]
            centriodsArray = numpy.array(centriods, numpy.float32)

            # Remove marker {{{
            encCircle = cv2.minEnclosingCircle(centriodsArray)
            avgDis = list()
            marker = [0, 0]
            # for c in centriodsArray:
            #     if c in approximatedContours[:, 0]:
            #         avgDis.append(c)
            #     else:
            #         marker = c
            jm = self.__findLabel(centriodsArray)
            marker = centriods[jm]
            avgDis = centriods
            avgDis.remove(avgDis[jm])
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
                                              self.cam['dist'])
            #                                   flags=cv2.SOLVEPNP_ITERATIVE)
            # }}}

            # Calculate camera pose. {{{
            rotMat = cv2.Rodrigues(rvec)[0]
            w2cMatHomo = numpy.append(rotMat, tvec, axis=1)
            w2cMatHomo = numpy.append(w2cMatHomo,
                                      numpy.array([[0, 0, 0, 1]],
                                                  numpy.float32),
                                      axis=0)
            w2cMatHomo = numpy.matrix(w2cMatHomo)
            c2wMat = w2cMatHomo.I
            camLocInCamMat = numpy.append(numpy.array([0, 0, 0]), 1)
            camLocInWldMat = numpy.matmul(c2wMat, camLocInCamMat)
            c2wTVec = c2wMat[:3, 3]
            c2wTVec = camLocInWldMat

            c2wTVec = numpy.array(c2wTVec)
            angZ = math.atan2(rotMat[1][0], rotMat[0][0]) / math.pi * 180
            printLoc = (round(c2wTVec[0][0], 2),
                        round(c2wTVec[0][1], 2),
                        round(c2wTVec[0][2], 2))
            loc = printLoc
            rot = angZ
            loc = (round(-loc[0] / 1000.0 + 3 , 6),
                   round(loc[1] / 1000.0 + 2, 6),
                   round(loc[2] / 1000.0, 6))

            if rot < 0:
                rot += 360
            rot = 360 - rot
            # }}}
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

            # Draw {{{
            if self.showImg:
                # c = [numpy.array([approximatedContours])]
                # self.logger.debug('SContour: %s.' % str(c))
                # calcImg = cv2.drawContours(calcImg,
                #                            c,
                #                            0,
                #                            (100, 100, 200),
                #                            2)
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
            self.logger.warning('Contour error, contour: %d.'
                                % len(validContours))
            if self.showImg:
                cv2.imshow('bina', cv2.resize(binaryImg,
                                              (round(binaryImg.shape[1] / 2),
                                               round(binaryImg.shape[0] / 2))))
            code = 1

        return loc, rot, code, markedImg    # }}}
# }}}
