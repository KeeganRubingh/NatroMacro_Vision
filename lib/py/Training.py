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

annotations = []

def SaveImage(img,name):
    tData = ""
    for v in annotations:
        tData += str(v["AnnotationClass"]) + " " + str(v["CenterX"]) + " " + str(v["CenterY"]) + " " + str(v["Width"]) + " " + str(v["Height"]) + "\n"
    with open('lib/py/trainingData/detect/labels/train/img' + name + ".txt",'w') as file:
        file.write(tData)
    cv.imwrite('lib/py/trainingData/detect/images/train/img'+ name + ".png",img)
def SaveAnnotation(annotClassName,frame,imWidth,imHeight):
    annotations.append({
        "AnnotationClass":annotClassName,
        "CenterX":(float(frame[0]) + float(frame[2])/2)/(imWidth),
        "CenterY":(float(frame[1]) + float(frame[3])/2)/(imHeight),
        "Width":float(frame[2])/float(imWidth),
        "Height":float(frame[3])/float(imHeight)
    })

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
            SaveAnnotation(annotType,selection,img.shape[0],img.shape[1])
        cv.destroyWindow(windowName)
        SaveImage(img,imgName)

StartAnnotatingImages()
# model.predict('lib/py/RoseField.png',save=True)