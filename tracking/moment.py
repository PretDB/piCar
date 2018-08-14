
def GetMoment(img):
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
