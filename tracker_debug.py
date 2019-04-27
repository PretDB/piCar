#!/usr/bin/python3

import cv2
import command


def calc(img, xbase, ybase):
    # post = self.preprocess(img)
    post = img
    center = [0, 0]  #
    m = 0

    mo = cv2.moments(post, True)
    if not int(mo['m00']) == 0:
        center[0] = (int)(mo['m10'] / mo['m00']) + xbase
        center[1] = (int)(mo['m01'] / mo['m00']) + ybase
        m = (int)(mo['m00'])

    return [m, center]


if __name__ == "__main__":
    cv2.namedWindow('raw')
    cv2.namedWindow('gray')
    cv2.namedWindow('binary')
    cv2.namedWindow('dil')
    cam = cv2.VideoCapture('/dev/tracker')

    element = cv2.getStructuringElement(cv2.MORPH_RECT, (10, 10))
    cmd = command.Command.Stop


    while True:
        got, raw = cam.read()
        if got:
            d1 = cv2.pyrDown(raw, (raw.shape[1] / 2, raw.shape[0] / 2))
            img = cv2.pyrDown(d1, (d1.shape[1] / 2, d1.shape[0] / 2))

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            th, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU)
            th, binary = cv2.threshold(gray, th, 255, cv2.THRESH_BINARY_INV)


            erd = cv2.erode(binary, element)
            dil = cv2.dilate(erd, element)

            # Y, toY, X,toX
            a1_rec = (0, int(dil.shape[0] / 3), 0, int(dil.shape[1] * 5 / 16))
            a2_rec = (0, int(dil.shape[0] / 3), int(dil.shape[1] * 11 / 16), dil.shape[1])
            a3_rec = (int(dil.shape[0] / 3), int(dil.shape[0] * 2/ 3), 0, dil.shape[1])
            a4_rec = (int(dil.shape[0] * 7 / 9), dil.shape[0], 0, dil.shape[1])

            a1 = dil[a1_rec[0] : a1_rec[1], a1_rec[2] : a1_rec[3]]
            a2 = dil[a2_rec[0] : a2_rec[1], a2_rec[2] : a2_rec[3]]
            a3 = dil[a3_rec[0] : a3_rec[1], a3_rec[2] : a3_rec[3]]
            a4 = dil[a4_rec[0] : a4_rec[1], a4_rec[2] : a4_rec[3]]

            a1_p = calc(a1, a1_rec[2], a1_rec[0])
            a2_p = calc(a2, a2_rec[2], a2_rec[0])
            a3_p = calc(a3, a3_rec[2], a3_rec[0])
            a4_p = calc(a4, a4_rec[2], a4_rec[0])
            print(str(a1_p) + '\t' + str(a2_p) + '\t' + str(a3_p) + '\t' + str(a4_p))

            mk = cv2.cvtColor(dil, cv2.COLOR_GRAY2RGB)
            mk = cv2.line(mk, (0, int(mk.shape[0] / 3)), (mk.shape[1], int(mk.shape[0] / 3)), (255, 0, 0))
            mk = cv2.line(mk, (0, int(mk.shape[0] * 7 / 9)), (mk.shape[1], int(mk.shape[0] * 7 / 9)), (255, 0, 0))
            mk = cv2.line(mk, (int(mk.shape[1] * 5 / 16), int(mk.shape[0] / 3)), (int(mk.shape[1] * 5 / 16), 0), (255, 0, 0))
            mk = cv2.line(mk, (int(mk.shape[1] * 11 / 16), int(mk.shape[0] / 3)), (int(mk.shape[1] * 11 / 16), 0), (255, 0, 0))
            mk = cv2.circle(mk, (a1_p[1][0], a1_p[1][1]), 2, (0, 0, 255))
            mk = cv2.circle(mk, (a2_p[1][0], a2_p[1][1]), 2, (0, 0, 255))
            mk = cv2.circle(mk, (a3_p[1][0], a3_p[1][1]), 2, (0, 0, 255))
            mk = cv2.circle(mk, (a4_p[1][0], a4_p[1][1]), 2, (0, 0, 255))

            img = cv2.line(img, (0, int(img.shape[0] / 3)), (img.shape[1], int(img.shape[0] / 3)), (255, 0, 0))
            img = cv2.line(img, (0, int(img.shape[0] * 7 / 9)), (img.shape[1], int(img.shape[0] * 7 / 9)), (255, 0, 0))
            img = cv2.line(img, (int(img.shape[1] * 5 / 16), int(img.shape[0] / 3)), (int(img.shape[1] * 5 / 16), 0), (255, 0, 0))
            img = cv2.line(img, (int(img.shape[1] * 11 / 16), int(img.shape[0] / 3)), (int(img.shape[1] * 11 / 16), 0), (255, 0, 0))

            if a1_p[0] > 200 and a2_p[0] > 200:
                cmd = command.Command.Stop
            elif abs((a3_p[1][0] + a4_p[1][0]) / 2 - dil.shape[1] / 2) > dil.shape[1] * 0.2:
                if (a3_p[1][0] + a4_p[1][0]) / 2 < dil.shape[1] / 2:
                    cmd = command.Command.LeftShift
                else:
                    cmd = command.Command.RightShift
            elif abs(a3_p[1][0] - a4_p[1][0]) > 4:
                if a3_p[1][0] < a4_p[1][0]:
                    cmd = command.Command.LeftRotate
                else:
                    cmd = command.Command.RightRotate
            else:
                cmd = command.Command.Forward

            img = cv2.putText(img,str(cmd), (0, img.shape[0]), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0))
            mk = cv2.putText(mk,str(cmd), (0, img.shape[0]), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0))
            cv2.imshow('raw', img)
            cv2.imshow('gray', gray)
            cv2.imshow('binary', binary)
            cv2.imshow('dil', mk)
            cv2.waitKey(15)
