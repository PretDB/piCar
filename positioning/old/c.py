#!/usr/bin/python

import cv2
import numpy as np
from MarkerDetector import MarkerDetector

camera = cv2.VideoCapture(0)

print('height', camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
print('width', camera.get(cv2.CAP_PROP_FRAME_WIDTH))
cv2.namedWindow('camera')
cv2.namedWindow('threshold')
cv2.namedWindow('contours')
cv2.namedWindow('pp')

detector = MarkerDetector()

while True:
    ret, frame = camera.read()
    grayscale = detector.prepareImage(frame)
    thresholded = detector.performThreshold(grayscale)
    contours = detector.findContours(thresholded, 50)
    candidateMarker = detector.findCandidates(contours)
    fc = frame
    cv2.drawContours(fc, contours, -1, (0, 0, 255))
    for i in range(len(candidateMarker)):
        marker = candidateMarker[i]

    cv2.imshow('camera', frame)
    cv2.imshow('threshold', thresholded)
    cv2.imshow('contours', fc)

    if cv2.waitKey(1) == ord('q'):
        break

cv2.destroyAllWindows()
