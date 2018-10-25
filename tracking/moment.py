import cv2
def getCenter(img):
    mo = cv2.moments(img, True)
    if int(mo['m00']) == 0:
        mo['m00'] = 1
    return ((int)(mo['m10'] / mo['m00']), int(mo['m01']) / int(mo['m00']))

def getCenter_for(img):
    x = 0
    y = 0
    count = 0
    for i in range(img.shape[1]):
        for j in range(img.shape[0]):
            if img[j][i] == 0:
                x += i
                y += j
                count += 1
    if count == 0:
        return (0, 0)
    else:
        x = x / count
        y = y / count
    return (x, y)

