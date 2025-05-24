import numpy as np
import cv2 as cv
from mss import mss
import time, threading


sct = mss()
# menuMask = cv.imread("lib\py\MenuMask.png",cv.IMREAD_GRAYSCALE)

def processScreenShot(img):
    hsv = cv.cvtColor(img,cv.COLOR_BGR2HSV)



    # redFlowerLow = np.array([20,100,20])
    # redFlowerHigh = np.array([40,255,255])
    dayGrassLow = np.array([20,40,0])
    dayGrassHigh = np.array([30,255,255])

    mask = cv.inRange(hsv, dayGrassLow, dayGrassHigh)
    # mask = cv.bitwise_and(mask,mask,mask=menuMask)

    cscale = 10
    kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE,(cscale,cscale))
    flowermask = cv.morphologyEx(mask, cv.MORPH_TOPHAT, kernel)
    cscale = 3
    kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE,(cscale,cscale))
    flowermask = cv.morphologyEx(flowermask, cv.MORPH_OPEN, kernel)
    cscale = 9
    kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE,(cscale,cscale))
    flowermask = cv.morphologyEx(flowermask, cv.MORPH_DILATE, kernel)

    contours, hierarchy = cv.findContours(flowermask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

    redflowers = 0
    whiteflowers = 0
    blueflowers = 0
    for k,v in enumerate(contours):
        targetSize = 110
        tolerance = 40
        if(abs(targetSize-cv.contourArea(v)) < tolerance):
            cv.drawContours(img,contours,k,(255,0,0),2)

    return cv.bitwise_and(img,img,mask= flowermask)

if(__name__ == "__main__"):
    import LiveFeed