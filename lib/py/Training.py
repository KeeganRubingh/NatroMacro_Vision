from ultralytics import YOLO
import easygui
from LiveFeed import LiveFeed
import cv2 as cv
import random
import string
import numpy as np

model = YOLO("yolov8s")
feed = LiveFeed()
annotationClasses = {
    "MiscToken",
    "TokenLink",
    "TokenBL",
    "TokenBomb",
    "TokenBoost",
    "FieldCorner",
    "Ladybug",
    "RhinoBeetle",
    "Mantis"
}

def SaveImage(img,name):
    pass
def SaveAnnotation(imgName,annotClassName,frame):
    pass
def StartAnnotatingImages():
    feed.chooseStream()
    while True:
        contBox = easygui.ccbox("Press continue to capture this frame or CANCEL to end capturing")
        if(not contBox):
            return
        img = feed.getSingleFrame()
        imgName = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        windowName = "Pictured Frame - " + imgName
        shouldcontinue = True
        SaveImage(img,imgName)
        annotatedImage = img.copy()
        while(shouldcontinue):
            selection = cv.selectROI(windowName,annotatedImage,True,True)
            print(selection)
            if(selection == (0,0,0,0)):
                break
            selectedRegion = img[selection[1]:selection[1]+selection[3],selection[0]:selection[0]+selection[2]]
            cv.imshow("Selected Region",selectedRegion)
            annotType = easygui.choicebox("Pick the object type",choices=annotationClasses)
            cv.destroyWindow("Selected Region")
            if(not annotType):
                shouldcontinue=False
                break
            p1 = (selection[0]+selection[2],selection[1])
            p2 = (selection[0],selection[1]+selection[3])
            cv.rectangle(annotatedImage,p1,p2,(0,0,255),4)
            cv.putText(annotatedImage,annotType,p1,1,1,(0,0,255),2)
            SaveAnnotation(imgName,annotType,selection)
        cv.destroyWindow(windowName)



StartAnnotatingImages()