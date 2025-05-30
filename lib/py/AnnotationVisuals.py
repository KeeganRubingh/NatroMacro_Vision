import cv2 as cv
import numpy as np
annotationClasses = [
    "MiscToken",
    "TokenLink",
    "TokenBL",
    "TokenBomb",
    "TokenBoost",
    "FieldCorner",
    "Ladybug",
    "RhinoBeetle",
    "Mantis"
]
class AnnotationDef():
    def __init__(self,annotIndex,centerX,centerY,width,height):
        self.annotationIndex = annotIndex
        self.centerX = centerX
        self.centerY = centerY
        self.width = width
        self.height = height
    
    @classmethod
    def fromFrame(cls, annotClassName,frame,imShape) -> 'AnnotationDef':
        imWidth = imShape[1]
        imHeight = imShape[0]
        return AnnotationDef(
            str(annotationClasses.index(annotClassName)),
            (float(frame[0]) + float(frame[2])/2)/float(imWidth),
            (float(frame[1]) + float(frame[3])/2)/float(imHeight),
            float(frame[2])/float(imWidth),
            float(frame[3])/float(imHeight)
        )
    
    @classmethod
    def fromString(cls, string:str) -> 'AnnotationDef':
        spstr = string.split()
        return AnnotationDef(int(spstr[0]),float(spstr[1]),float(spstr[2]),float(spstr[3]),float(spstr[4]))
    
    def drawTo(self,img,color=(0,0,255),lineType=0,suffix=None,showText=True) -> None:
        xOff = self.width/2
        yOff = self.height/2
        p1 = (int((self.centerX - xOff)*img.shape[1]),int((self.centerY - yOff)*img.shape[0]))
        p2 = (int((self.centerX + xOff)*img.shape[1]),int((self.centerY + yOff)*img.shape[0]))
        text = annotationClasses[int(self.annotationIndex)]
        if(suffix):
            text += " - " + suffix
        cv.rectangle(img,p1,p2,color,4)
        if(showText):
            cv.putText(img,text,(p1[0],p1[1]-5),2,1,color,2,lineType)
    
    def getListRepresentation(self) -> dict:
        return {
            "AnnotationClass":self.annotationIndex,
            "CenterX":self.centerX,
            "CenterY":self.centerY,
            "Width":self.width,
            "Height":self.height
        }
   