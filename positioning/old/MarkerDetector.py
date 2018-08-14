import numpy as np
import cv2


# class MarkerDetector {{{
class MarkerDetector:
    # Init {{{
    def __init__(self):
        print('init')
    # }}}

    # processFrame {{{
    def processFrame(self, frame):
        pass
    # }}}

    # getTransformations {{{
    def getTransformations(self):
        pass
    # }}}

    # findMarkers {{{
    def findMarkers(self, frame, detectedMarkers):
        pass
    # }}}

    # prepareImage {{{
    def prepareImage(self, bgrMat):
        grayscale = cv2.cvtColor(bgrMat, cv2.COLOR_BGR2GRAY)
        return grayscale
    # }}}

    # performThreshold {{{
    def performThreshold(self, image):
        thresholdImg = cv2.adaptiveThreshold(image,
                                             255,
                                             cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                             cv2.THRESH_BINARY_INV,
                                             7, 7)
        return thresholdImg
    # }}}

    # findContours {{{
    def findContours(self, thresholdImg, minContourPointsAllowed):
        contours = []
        allContours = cv2.findContours(thresholdImg,
                                      cv2.RETR_LIST,
                                      cv2.CHAIN_APPROX_NONE)[1]
        for i in range(len(allContours)):
            contourSize = len(allContours[i])
            if contourSize > minContourPointsAllowed:
                contours.append(allContours[i])
        return contours
    # }}}

    # findCandidates {{{
    def findCandidates(self, contours):
        approxCurve = []
        possibleMarkers = []

        for i in range(len(contours)):
            eps = len(contours[i]) * 0.05
            approxCurve = cv2.approxPolyDP(contours[i], eps, True)

            if len(approxCurve) != 4:
                continue

            if not cv2.isContourConvex(approxCurve):
                continue
            minDist = 1000000
            for i in range(4):
                side = np.array(approxCurve[i] - approxCurve[(i + 1) % 4])
                squaredSideLength = side.dot(side.transpose())
                minDist = min(minDist, squaredSideLength)
            # Marker
            points = []
            for i in range(4):
                points.append((approxCurve[i][0][0], approxCurve[i][0][1]))

            v1 = (points[1][0] - points[0][0], points[1][1] - points[0][1])
            v2 = (points[2][0] - points[0][0], points[2][0] - points[0][1])
            o = v1[0] * v2[1] - v1[1] * v2[0]
            if o < 0.0:
                jj = points[1]
                points[1] = points[3]
                points[3] = jj
            possibleMarkers.append(np.array(points))
        tooNearCandidates = []
        for i in range(len(possibleMarkers)):
            points1 = possibleMarkers[i]
            for j in range(i + 1, len(possibleMarkers)):
                points2 = possibleMarkers[j]
                distSquared = 0.

                for c in range(4):
                    v = np.array([points1[c][0] - points2[c][0], points1[c][1] - points2[c][1]])
                    distSquared = distSquared + v.dot(v)

                distSquared = distSquared / 4

                if distSquared < 100.:
                    tooNearCandidates.append((i, j))
        removalMask = [False] * len(possibleMarkers)
        for i in range(len(tooNearCandidates)):
            p1 = cv2.arcLength(possibleMarkers[tooNearCandidates[i][0]], True)
            p2 = cv2.arcLength(possibleMarkers[tooNearCandidates[i][1]], True)
            if p1 > p2:
                removalIndex = tooNearCandidates[i][1]
            else:
                removalIndex = tooNearCandidates[i][0]
            removalMask[removalIndex] = True
        detectedMarkers = []
        for i in range(len(possibleMarkers)):
            if not removalMask[i]:
                detectedMarkers.append(possibleMarkers[i])
        return detectedMarkers
    # }}}

    # detectMarkers {{{
    def detectMarkers(self, grayscale, detectedMarkers):
        pass
    # }}}

    # estimatePosition {{{
    def estimatePosition(self, detectedMarkers):
        pass
    # }}}

# }}}
