import cv2

def preprocess(img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thv, img = cv2.threshold(img, 200, 255, cv2.THRESH_OTSU, cv2.THRESH_BINARY)
    return img

