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

# load the image
img = cv.imread('xxx.png',0)
Template2 = cv.imread('Template2.bmp',0)


center = (328, 267)
width = 384
height = 93
angle = 13

# compute the vertices of the rotated rectangle
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

fig = plt.figure()
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
        try:
            if curMaxTemplate == -1:
                return (0, (0, 0), 0, 0, (0, 0))
            else:
                bottom_right = (top_left[0] + w, top_left[1] + h)
                return (curMaxTemplate % 3, curMaxLoc, 1 - int(curMaxTemplate / 3) * 0.2, curMaxVal, bottom_right)
        except:
            return (0, (0, 0), 0, 0, (0, 0))


print(Process_Outline(roi,Template2))


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
print(Rule_Of_Thirds(roi),Rule_Of_Thirds(Template2))


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

print(Process_Area(Rule_Of_Thirds(roi),Rule_Of_Thirds(Template2)))"""

"""cv.imshow("Template", roi)
cv.waitKey(0)
cv.imshow("Template1", Template2)
cv.waitKey(0)"""
#plt.imshow(roi)
#plt.imshow(Template2)
#plt.show()

#new_image.save('Template2.bmp')
#roi.save("Template.bmp")

# display the cropped image
#cv.imshow('Cropped Image', roi)
#cv.waitKey(0)