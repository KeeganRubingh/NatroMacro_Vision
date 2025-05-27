import numpy as np
import cv2 as cv
from mss import mss
import time, threading
import random


sct = mss()
menuMask = cv.imread("lib\py\MenuMask.png",cv.IMREAD_GRAYSCALE)

# params for ShiTomasi corner detection
feature_params = dict( maxCorners = 100,
                    qualityLevel = 0.3,
                    minDistance = 7,
                    blockSize = 7 )

# Parameters for lucas kanade optical flow
lk_params = dict( winSize  = (15, 15),
                maxLevel = 2,
                criteria = (cv.TERM_CRITERIA_EPS | cv.TERM_CRITERIA_COUNT, 10, 0.03))

# Create some random colors
color = np.random.randint(0, 255, (100, 3))

# Take first frame and find corners in it
old_frame = 0
old_gray = 0
p0 = 0
frame_gray = 0
good_new = 0

# Create a mask image for drawing purposes
mask = 0


def processScreenShot(img):
    # hsv = cv.cvtColor(img,cv.COLOR_BGR2HSV)

    # # redFlowerLow = np.array([20,100,20])
    # # redFlowerHigh = np.array([40,255,255])
    # dayGrassLow = np.array([20,40,0])
    # dayGrassHigh = np.array([30,255,255])

    # mask = cv.inRange(hsv, dayGrassLow, dayGrassHigh)
    # mask = cv.bitwise_and(mask,mask,mask=menuMask)

    # cscale = 10
    # kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE,(cscale,cscale))
    # flowermask = cv.morphologyEx(mask, cv.MORPH_TOPHAT, kernel)
    # cscale = 3
    # kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE,(cscale,cscale))
    # flowermask = cv.morphologyEx(flowermask, cv.MORPH_OPEN, kernel)
    # cscale = 9
    # kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE,(cscale,cscale))
    # flowermask = cv.morphologyEx(flowermask, cv.MORPH_DILATE, kernel)
    
    global feature_params
    global lk_params
    global color
    global old_gray
    global old_frame
    global frame_gray
    global p0
    global good_new
    global mask
    frame = img
    try:
        old_gray = frame_gray.copy()
        p0 = good_new.reshape(-1, 1, 2)
    except:
        old_frame = frame
        old_gray = cv.cvtColor(old_frame, cv.COLOR_BGR2GRAY)
        p0 = cv.goodFeaturesToTrack(old_gray, mask = None, **feature_params)
        mask = np.zeros_like(old_frame)

    frame_gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

    # calculate optical flow
    p1, st, err = cv.calcOpticalFlowPyrLK(old_gray, frame_gray, p0, None, **lk_params)

    # Select good points
    if p1 is not None:
        good_new = p1[st==1]
        good_old = p0[st==1]
        
    cv.recoverPose()
    img = cv.add(frame, mask)
    return img
 


if(__name__ == "__main__"):
    import LiveFeed