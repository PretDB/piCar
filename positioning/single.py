#!/usr/bin/python

# USE 640x480

import cv2
import matplotlib.pyplot as plt
import socket


st = socket.gethostname()
if st == 'pret-arch':
    import camera_config_A as camera_config
else:
    import camera_config_B as camera_config
print(camera_config.cameraID)


# if __name__ == '__main__':
def get_location():
    camera = cv2.VideoCapture(0)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 640)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 480)
    matrix = camera_config.camera_matrix
    distortion = camera_config.camera_distortion
    sideSize = 500.0  # unit in mm

    dic = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_250)

    plt.ion()
    fig = plt.figure()
    ax = plt.gca()
    scatter = ax.scatter(0., 0., 50)

    while True:
        frame = cv2.imread("d.jpg", cv2.IMREAD_GRAYSCALE)
        # frame = cv2.adaptiveThreshold(frame, 255,
        #                               cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        #                               cv2.THRESH_BINARY,
        #                               11, 2)
        corners, ids, rejectedImgPoints = cv2.aruco.detectMarkers(frame,
                                                                  dic,)
        frame = cv2.aruco.drawDetectedMarkers(frame, corners, ids)
        R, t, _objPoints = cv2.aruco.estimatePoseSingleMarkers(corners,
                                                               sideSize,
                                                               matrix,
                                                               distortion)
        if R is not None:
            for i in range(len(R)):
                frame = cv2.aruco.drawAxis(frame,
                                           matrix,
                                           distortion,
                                           R[i], t[i], 15.0)

                scatter.remove()
                scatter = ax.scatter(t[0][0][0], t[0][0][1], 50)
                plt.pause(0.001)

        cv2.imshow('frame', frame)
        if cv2.waitKey(1) == ord('q'):
            break
    cv2.destroyAllWindows()



get_location()
