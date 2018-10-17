#!/usr/bin/python3

import cv2
# import moment
import preprocess


cam = cv2.VideoCapture(0)
cv2.namedWindow('dilate')
cv2.namedWindow('frame')
cv2.namedWindow('erode')
cv2.namedWindow('binary')
while True:
    f = cam.read()[1]
    f = cv2.pyrDown(f, (f.shape[1] / 2, f.shape[0] / 2))
    f = cv2.pyrDown(f, (f.shape[1] / 2, f.shape[0] / 2))
    bina = preprocess.preprocess(f)

    ele = cv2.getStructuringElement(cv2.MORPH_RECT, (10, 10))
    # ele = cv2.getStructuringElement(cv2.MORPH_RECT, (20, 20))
    er = cv2.erode(bina, ele)
    di = cv2.dilate(er, ele)

    mo = cv2.moments(di, True)
    if int(mo['m00']) == 0:
        mo['m00'] = 1
    mo = ((int)(mo['m10'] / mo['m00']), int(mo['m01'] / mo['m00']))

    f = cv2.circle(f, mo, 2, (0, 0, 255), 4)
    cv2.imshow('frame', f)
    cv2.imshow('erode', er)
    cv2.imshow('dilate', di)
    cv2.imshow('binary', bina)
    print(mo, f.shape)
    if cv2.waitKey(1) == ord('q'):
        break

cv2.destroyAllWindows()

