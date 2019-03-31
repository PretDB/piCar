#!/usr/bin/python3
import cv2
import numpy
import sys
import getopt
import time
import logging
import cmath
import math
import random
import socket
import time
import json


class Locator():
    def __init__(self, benchmark=False, lens=0, release=True):
        # Initialize network
        self.targetAddress = ('<broadcast>', 6875)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        testS = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        testS.connect(('8.8.8.8', 80))
        self.localIP = testS.getsockname()[0]
        self.deviceName = (socket.gethostname())
        testS.close()
        self.socket.bind(('', 6875))

        # Initiate hearbeat package
        self.heartbeatPackage = {'FromIP': self.localIP,
                                 'FromName': self.deviceName,
                                 'FromRole': 'locator',
                                 'Type': 'locate',
                                 'Msg': None}
        self.heartbeatCount = 0

        if not release:
            cv2.namedWindow('raw')

        if release:
            hterm = logging.StreamHandler()
            hterm.setLevel(logging.INFO)
            hfile = logging.FileHandler('locator.log')
            hfile.setLevel(logging.WARNING)
            formater = logging.Formatter('%(asctime)s ' +
                                         '%(filename)s[line:%(lineno)sd] ' +
                                         '%(levelname)s %(message)s')
            hterm.setFormatter(formater)
            hfile.setFormatter(formater)
        else:
            hterm = logging.StreamHandler()
            hterm.setLevel(logging.DEBUG)
            hfile = logging.FileHandler('locator.log')
            hfile.setLevel(logging.DEBUG)
            formater = logging.Formatter('%(asctime)s ' +
                                         '%(filename)s[line:%(lineno)sd] ' +
                                         '%(levelname)s %(message)s')
            hterm.setFormatter(formater)
            hfile.setFormatter(formater)
        logger = logging.getLogger()
        logger.addHandler(hterm)
        logger.addHandler(hfile)
        self.logger = logger

        self.isBenchmark = benchmark
        self.isRelease = release

        # Device and environment initiation
        self.objPoints = numpy.array([[-1000.0, -750.0, 0],
                                      [1000.0, -750.0, 0],
                                      [1000.0, 750.0, 0],
                                      [-1000.0, 750.0, 0]],
                                     numpy.float32)
        self.cam = dict()
        if lens == 1:
            self.cam['inst'] = numpy.array([[788.893678755818,
                                             0, 932.290999805616],
                                            [0, 787.427354652960,
                                             529.198843943091],
                                            [0, 0, 1]])
            self.cam['dist'] = numpy.array([-0.217131042436646,
                                            0.0403307733242417,
                                            -0.00121853913549975,
                                            0.000367520074923063,
                                            -0.00325660495212412])
            pass
        else:
            self.cam['inst'] = numpy.array([[788.893678755818,
                                             0, 932.290999805616],
                                            [0, 787.427354652960,
                                             529.198843943091],
                                            [0, 0, 1]])
            self.cam['dist'] = numpy.array([-0.217131042436646,
                                            0.0403307733242417,
                                            -0.00121853913549975,
                                            0.000367520074923063,
                                            -0.00325660495212412])
            pass
        self.logger.info('Len %s loaded.' % (lens))

        self.cam['dev'] = cv2.VideoCapture('/dev/video1')
        # Test camera
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
            if i == 2:
                self.logger.critical('Camera is not available.')
            if read:
                break

        pass

    def run(self):
        while True:
            last = time.time()
            read, img = self.cam['dev'].read()
            if read:
                tvec, rvec = self.__locator(img)

                if not self.isRelease:
                    cv2.imshow('raw', cv2.resize(img,
                                                 (round(img.shape[1] / 2),
                                                  round(img.shape[0] / 2))))
                    key = cv2.waitKey(30)
                    if key == ord(' '):
                        key = cv2.waitKey(0)
                    if key == ord('q'):
                        break

                if tvec is not None or rvec is not None:
                    loc = {'X': round(tvec[0]),
                           'Y': round(tvec[1]),
                           'Z': round(tvec[2])}
                    ang = round(rvec)
                    self.heartbeatPackage['Msg'] = {'position': loc,
                                                    'angle': ang}
                    dataRaw = json.dumps(self.heartbeatPackage)
                    dataByte = dataRaw.encode('utf-8')
                    self.socket.sendto(dataByte, self.targetAddress)
                    print(dataRaw)
            else:
                continue
            fps = round(1.0 / (time.time() - last), 1)

            if self.isBenchmark:
                self.logger.info('FPS: %s', fps)

            pass
        pass

    def __validateContour(self, contour):
        if cv2.contourArea(contour) < 300:
            return False

        # Filter by number of contours approxed whoes precision is defiened
        # by its length.
        precision = 0.1 * cv2.arcLength(contour, closed=True)
        approxContour = cv2.approxPolyDP(contour, precision, closed=True)
        if not len(approxContour) == 4:
            return False

        # Filter by similarity between contour and its minimum binding
        # rectangle.
        minRect = cv2.minAreaRect(contour)
        minRect = cv2.boxPoints(minRect)
        if cv2.contourArea(contour) / cv2.contourArea(minRect) <= 0.7:
            return False

        return True

    def __detectMarker(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        th, binaryImg = cv2.threshold(gray, 250, 255, cv2.THRESH_TRIANGLE)
        binaryImg = cv2.morphologyEx(binaryImg, cv2.MORPH_CLOSE, (21, 21))
        c, contours, hierarchy = cv2.findContours(binaryImg,
                                                  cv2.RETR_TREE,
                                                  cv2.CHAIN_APPROX_SIMPLE)

        validContours = list()
        for i in range(len(contours)):
            if not self.__validateContour(contours[i]):
                continue

            moment = cv2.moments(contours[i], False)
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
                                           2,
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

    def __locator(self, image):
        loc = None
        rot = None
        if self.isRelease:
            validContours, = self.__detectMarker(image)
        else:
            validContours, binaryImg, image = self.__detectMarker(image)

        calcImg = numpy.zeros([image.shape[0], image.shape[1], 3],
                              numpy.uint8)
        markedImg = image

        if len(validContours) == 5:
            # Calculate the miniman enclosing circle
            centriods = [p['centriod'] for p in validContours]
            encCircle = cv2.minEnclosingCircle(numpy.array(centriods,
                                                           numpy.int32))
            # Remove marker
            avgDis = list()
            for point in centriods:
                distanceToCenter = (((point[0] - encCircle[0][0]) ** 2 +
                                     (point[1] - encCircle[0][1]) ** 2)
                                    ** 0.5)
                avgDis.append([point, distanceToCenter])
            avgDis.sort(key=(lambda x: x[1]))
            marker = avgDis[0]
            avgDis.remove(marker)

            # Get X and Y axis
            y = numpy.array([marker[0][0] - encCircle[0][0],
                             marker[0][1] - encCircle[0][1]],
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

            # Calculate affine matrix
            imagPoints = numpy.array([xArrow, encCircle[0], yArrow],
                                     numpy.float32)
            cplxPoints = numpy.array([[numpy.linalg.norm(xAxisImg), 0],
                                      [0, 0],
                                      [0, numpy.linalg.norm(yAxisImg)]],
                                     numpy.float32)
            affineMat = cv2.getAffineTransform(imagPoints, cplxPoints)

            # Warp affine transform onto points ( marker excepted )
            pointsComplex = list()
            for point in avgDis:
                p = numpy.array([point[0][0], point[0][1], 1], numpy.float32)
                pAffined = numpy.matmul(affineMat, p)
                pointsComplex.append(numpy.array([pAffined, point[0]],
                                                 numpy.float32))

            # Calculate angle in comples corrdinate
            pointsAngle = list()
            for pc in pointsComplex:
                c = complex(pc[0][0], pc[0][1])
                angle = cmath.log(c).imag
                if angle < 0:
                    angle += cmath.pi * 2
                pointsAngle.append([pc, angle])
            pointsAngle.sort(key=(lambda x: x[1]), reverse=True)

            # Pose estimating
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

            # Calculate camera pose.
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
            c2wRMat = c2wMat[:3, :3]
            c2wRVec = cv2.Rodrigues(c2wRMat)
            c2wTVec = camLocInWldMat

            angZ = math.atan2(rotMat[1][0], rotMat[0][0]) / math.pi * 180

            # Draw
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
                    loc = (int(round(p[0])), int(round(p[1])))
                    calcImg = cv2.circle(calcImg, loc, 10, (0, 0, 255), 1)
                printLoc = (round(tvec[0][0], 2),
                            round(tvec[1][0], 2),
                            round(tvec[2][0], 2))
                loc = printLoc
                rot = angZ
                markedImg = cv2.putText(markedImg, str(printLoc), (0, 100),
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
        return loc, rot


lctr = Locator(release=False)
lctr.run()
