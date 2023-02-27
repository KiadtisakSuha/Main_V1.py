"""import cv2 as cv
img= cv.imread("xxx.png",1)
#image[Top:Bottom,Left:Right]
#275 128 414 334
img = cv.rectangle(img, (275, 70), (90, 50), (0, 0, 255), 2)
cv.imshow("img",img)
cv.waitKey(0)"""
import cv2 as cv
import numpy as np
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
#((346.0000305175781, 367.5), (82.9999771118164, 168.0), 78.99999237060547)
# load the image
img = cv.imread('Point 2.bmp',0)
_Area = cv.imread('Master/_Area.bmp',0)
_Position = cv.imread('Master/_Position.bmp',0)
_Rotate = cv.imread('Master/_Rotate.bmp',0)

def rotateAndScale(img, scaleFactor = 0.5, degreesCCW = 11.00000762939453):
    (oldY,oldX) = img.shape #note: numpy uses (y,x) convention but most OpenCV functions use (x,y)
    M = cv.getRotationMatrix2D(center=(oldX/2,oldY/2), angle=degreesCCW, scale=scaleFactor) #rotate about center of image.

    #choose a new image size.
    newX,newY = oldX*scaleFactor,oldY*scaleFactor
    #include this if you want to prevent corners being cut off
    r = np.deg2rad(degreesCCW)
    newX,newY = (abs(np.sin(r)*newY) + abs(np.cos(r)*newX),abs(np.sin(r)*newX) + abs(np.cos(r)*newY))

    #the warpAffine function call, below, basically works like this:
    # 1. apply the M transformation on each pixel of the original image
    # 2. save everything that falls within the upper-left "dsize" portion of the resulting image.

    #So I will find the translation that moves the result to the center of that region.
    (tx,ty) = ((newX-oldX)/2,(newY-oldY)/2)
    M[0,2] += tx #third column of matrix holds translation, which takes effect after rotation.
    M[1,2] += ty

    rotatedImg = cv.warpAffine(img, M, dsize=(int(newX),int(newY)))
    return rotatedImg

"""
((345.5, 361.4999694824219), (49.00000762939453, 159.0), 77.0)
center = (346.0000305175781, 367.5)
width = 82.9999771118164
height = 168.0
angle = 78.99999237060547

# compute the vertices of the rotated rectangle
#rect = ((center[0], center[1]), (width, height), angle)
rect = ((center[0], center[1]), (width, height), angle)

box = cv.boxPoints(rect)

box = np.int0(box)


# find the minimum and maximum x and y coordinates of the rotated rectangle
x_min = np.min(box[:, 0])
x_max = np.max(box[:, 0])
y_min = np.min(box[:, 1])
y_max = np.max(box[:, 1])

# create a mask for the rotated rectangle
mask = np.zeros_like(img)
cv.drawContours(mask, [box], 0, (255, 255, 255), -1)
cv.drawContours(img, [box], 0, (0, 0, 0), 2)

# apply the mask to the image to extract the ROI
roi = cv.bitwise_and(img, mask)

# crop the ROI using the bounding box of the rotated rectangle
roi = roi[y_min:y_max, x_min:x_max]
#cv.imshow("roi",roi)
#cv.waitKey(0)
"""





"""fig = plt.figure()
ax = fig.add_subplot(2, 1, 1)
ax.set_title('Template2')
ax.imshow(Template2)
ax.autoscale(False)
ax2 = fig.add_subplot(2, 1, 2, sharex=ax, sharey=ax)
ax2.set_title('roi')
ax2.imshow(roi)
ax2.autoscale(False)
plt.show()

"""


def Process_Outline(image, Template):
    #image = cv.imread(image, 0)
    #Template = cv.imread(Template, 0)
    w, h = Template.shape[::-1]
    c = 0
    TemplateThreshold = 0.7
    curMaxVal = 0
    curMaxTemplate = -1
    curMaxLoc = (0, 0)
    for meth in ['cv.TM_CCOEFF_NORMED']:
        method = eval(meth)
        res = cv.matchTemplate(image, Template, method)
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)
        if max_val > TemplateThreshold and max_val > curMaxVal:
            if method in [cv.TM_SQDIFF]:
                top_left = min_loc
            else:
                top_left = max_loc
            curMaxVal = max_val
            curMaxTemplate = c
            curMaxLoc = max_loc
        c = c + 1
        #print(top_left)
        bottom_right = (top_left[0] + w, top_left[1] + h)
        #bottom_right = 0
        return (curMaxTemplate % 3, curMaxLoc, 1 - int(curMaxTemplate / 3) * 0.2, curMaxVal, bottom_right)


rotate = rotateAndScale(_Position)
#cv.imshow('rotate',_Position)
#cv.imshow('_Area',_Area)
cv.waitKey(0)
#print(Process_Outline(rotate,_Rotate))
#print(Process_Outline(_Position,_Area))


#print(sum(roi))
#print(sum(Template2))

def Rule_Of_Thirds(ROT):
    total = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    mod = len(ROT) % 9
    if mod != 0:
        for i in range(mod):
            total[9] += sum(ROT[len(ROT) - mod + i])
    layout = int(len(ROT) / 9)
    for i in range(9):
        i = i + 1
        for j in range(layout * i):
            total[i - 1] += sum(ROT[j])
    point = [total[0]]
    for k in range(8):
        point.append(total[k + 1] - total[k])
    if mod != 0:
        point.append(total[9])
    return point
#print(Rule_Of_Thirds(roi),Rule_Of_Thirds(Template2))


def Process_Area(Master, Template):
    Score_Ture = []
    Result_Score = 0
    swapped = False
    Couter = len(Master)
    for i in range(Couter):
        if Master[i] < Template[i]:
            Score_Ture.append((Master[i] / Template[i]) * 1000)
        else:
            Score_Ture.append((Template[i] / Master[i]) * 1000)
    for n in range(len(Score_Ture) - 1, 0, -1):
        for i in range(n):
            if Score_Ture[i] > Score_Ture[i + 1]:
                swapped = True
                Score_Ture[i], Score_Ture[i + 1] = Score_Ture[i + 1], Score_Ture[i]
    for i in range(len(Score_Ture)):
        if i < 5:
            Result_Score += Score_Ture[i]
    Result_Score = int(Result_Score / 5)
    return Result_Score

#print(Process_Area(Rule_Of_Thirds(roi),Rule_Of_Thirds(Template2)))

#cv.imshow("Template", roi)
#cv.waitKey(0)
#cv.imshow("Template1", Template2)
#cv.waitKey(0)


#plt.imshow(roi)
#plt.imshow(Template2)
#plt.show()

#new_image.save('Template2.bmp')
#roi.save("Template.bmp")

# display the cropped image
#cv.imshow('Cropped Image', roi)
#cv.waitKey(0)