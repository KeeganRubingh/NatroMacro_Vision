import numpy as np
import cv2 as cv
from mss import mss
import time, threading
import random


sct = mss()
menuMask = cv.imread("lib\py\MenuMask.png",cv.IMREAD_GRAYSCALE)
linkToken = cv.imread("nm_image_assets/TokenLink.png")

lastimgs = []
BLOBBERT_CACHE_LEN = 5

def processScreenShot(img):
    return Blobbert(img)

def Blobbert(img):
    img1 = img
    img2 = None
    
    lastimgs.append(img1)
    if(len(lastimgs)>BLOBBERT_CACHE_LEN):
        lastimgs.pop(0)
    
    img2 = lastimgs[len(lastimgs)-1]
    
    return img1 - img2
        
def SIFtor(img):
    img1 = img
    img2 = linkToken

    # Initiate SIFT detector
    sift = cv.SIFT_create()
    
    # find the keypoints and descriptors with SIFT
    kp1, des1 = sift.detectAndCompute(img1,None)
    kp2, des2 = sift.detectAndCompute(img2,None)
    
    FLANN_INDEX_KDTREE = 1
    index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
    search_params = dict(checks = 50)
    
    flann = cv.FlannBasedMatcher(index_params, search_params)
    
    matches = flann.knnMatch(des1,des2,k=2)
    
    # store all the good matches as per Lowe's ratio test.
    good = []
    for m,n in matches:
        if m.distance < 0.7*n.distance:
            good.append(m)

if(__name__ == "__main__"):
    from LiveFeed import LiveFeed
    feed = LiveFeed()
    feed.chooseStream()
    feed.modifyStream(Blobbert)
    feed.viewStream()
    