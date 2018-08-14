#!/usr/bin/python

# USE 640x480

import cv2
import matplotlib.pyplot as plt
import socket

def filter_fn(img):
    frame = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return frame

def filter(img):
    camera = cv2.VideoCapture(0)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 640)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 480)
    matrix = camera_config.camera_matrix
    distortion = camera_config.camera_distortion
    sideSize = 45.0  # unit in mm

    dic = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_250)

    plt.ion()
    fig = plt.figure()
    ax = plt.gca()
    ax.set_xlim(-150, 150)
    ax.set_ylim(-150, 150)
    scatter = ax.scatter(0., 0., 50)

    while True:
        ret, frame_raw = camera.read()
        frame = cv2.cvtColor(frame_raw, cv2.COLOR_BGR2GRAY)
        # ret, frame = cv2.threshold(frame, 180, 255, cv2.THRESH_BINARY)
        # ret, frame = cv2.threshold(frame, 0, 255, cv2.THRESH_OTSU)
        # frame = cv2.adaptiveThreshold(frame, 255,
        #                               cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        #                               cv2.THRESH_BINARY,
        #                               11, 2)
        element = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        # frame = cv2.erode(frame, element)
        corners, ids, rejectedImgPoints = cv2.aruco.detectMarkers(frame,
                                                                  dic,)
        frame_raw = cv2.aruco.drawDetectedMarkers(frame_raw, corners, ids)
        R, t, _objPoints = cv2.aruco.estimatePoseSingleMarkers(corners,
                                                               sideSize,
                                                               matrix,
                                                               distortion)

def init_filter():
    return filter_fn
