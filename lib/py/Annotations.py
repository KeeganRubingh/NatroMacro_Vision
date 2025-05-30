from ultralytics import YOLO
import easygui
import LiveFeed
import cv2 as cv
import random
import string
import numpy as np
import threading, os
import pathlib
from AnnotationVisuals import AnnotationDef,annotationClasses

model = YOLO("yolov8s")
feed = LiveFeed.LiveFeed()

annotations: list[AnnotationDef] = []

def SaveImage(img,name):
    tData = ""
    for v in annotations:
        vL = v.getListRepresentation()
        tData += str(vL["AnnotationClass"]) + " " + str(vL["CenterX"]) + " " + str(vL["CenterY"]) + " " + str(vL["Width"]) + " " + str(vL["Height"]) + "\n"
    with open('lib/py/trainingData/detect/labels/train/img' + name + ".txt",'w') as file:
        file.write(tData)
    cv.imwrite('lib/py/trainingData/detect/images/train/img'+ name + ".png",img)

def SaveAnnotation(annotClassName,frame,imShape):
    annotations.append(AnnotationDef.fromFrame(annotClassName,frame,imShape))

def DirectSaveAnnotations(path,annots: list[AnnotationDef]):
    tData = ""
    for v in annots:
        vL = v.getListRepresentation()
        tData += str(vL["AnnotationClass"]) + " " + str(vL["CenterX"]) + " " + str(vL["CenterY"]) + " " + str(vL["Width"]) + " " + str(vL["Height"]) + "\n"
    with open(path,'w') as file:
        file.write(tData)
        

def StartAnnotatingImages():
    feed.chooseStream()
    while True:     
        feed.viewStream()
        img = feed.getSingleFrame()
        imgName = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        windowName = "Pictured Frame - " + imgName
        shouldcontinue = True
        annotatedImage = img.copy()
        while(shouldcontinue):
            selection = cv.selectROI(windowName,annotatedImage,True,True)
            print(selection)
            if(selection[2] < 0 or selection[3] < 0):
                break
            if(selection == (0,0,0,0)):
                break
            selectedRegion = img[selection[1]:selection[1]+selection[3],selection[0]:selection[0]+selection[2]]
            try:
                cv.imshow("Selected Region",selectedRegion)
            except:
                continue
            annotType = easygui.choicebox("Pick the object type",choices=annotationClasses)
            cv.destroyWindow("Selected Region")
            if(not annotType):
                shouldcontinue=False
                break
            SaveAnnotation(annotType,selection,img.shape)
        cv.destroyWindow(windowName)
        SaveImage(img,imgName)

     
    
def DeserializeAnnotations(imgPath:pathlib.Path) -> list[AnnotationDef]:
    parts = list(imgPath.parts)
    parts[4] = "labels"
    finalpath = pathlib.Path("/".join(parts)).with_suffix(".txt")
    reader = finalpath.open()
    
    annots = []
    
    while(line := reader.readline()):
        annot = AnnotationDef.fromString(line)
        annots.append(annot)
    
    return annots

def renderEditor(annots:list[AnnotationDef], img:cv.Mat, selectedIndex:int, renderOtherThanSelection=True, emphasizeSelection=False):
    for k,v in enumerate(annots):
        if(not renderOtherThanSelection and k != selectedIndex):
            continue
        color = (0,0,255)
        showText = False
        if(k == selectedIndex):
            color = (255,0,0)
            showText = True
        if(emphasizeSelection):
            v.drawTo(img,color,2,suffix=str(k),showText=showText)
        else:
            v.drawTo(img,color,suffix=str(k),showText=showText)

    return img

def buildSortMap(annots):
    def sortFunc(a):
        return a.centerX
    sortedAnnots = annots.copy()
    sortedAnnots.sort(key=sortFunc)
    selectionmap = []
    for v in sortedAnnots:
        selectionmap.append(annots.index(v))
    return selectionmap

def StartEditingImages():
    path = pathlib.Path("lib/py/trainingData/detect/images")
    category = easygui.choicebox("Choose Category",choices=os.listdir(path))
    path = path.joinpath(category)
    
    finalpath = None
    img = None
    while(True):
        file = easygui.choicebox("Choose File",choices=os.listdir(path))
        finalpath = path.joinpath(file)
        img = cv.imread(str(finalpath.absolute()))
        cv.imshow("Opened Image" ,img)
        if(easygui.ccbox("Edit this image?")):
            break

    annots = DeserializeAnnotations(finalpath)
    
    selection = -1
    newimg = img.copy()
    editor = renderEditor(annots,newimg,selection)
    cv.destroyWindow("Opened Image")
    cv.imshow("Q+E, C, D, P, Enter",editor)
    easygui.msgbox("Q/E keys to select, C to reposition, D to delete, R to change annotation type, P to reset window,Enter to end")
    
    while(True):
        ## Create a map between the annotations and them sorted by length
        ## This makes the selection system make more sense while still allowing us to write back to the file
        selectionmap = buildSortMap(annots)
        
        ## Render our editor
        editor = renderEditor(annots,img.copy(),selectionmap[selection])
        cv.imshow("Q+E, C, D, P, Enter",editor)
        
        ## Wait for user input, then take actions based on that
        key = cv.waitKey()
        
        ##Select next
        if(key == ord('q')):
            selection = int(selection-1)%len(annots)
        
        if(key == ord('e')):
            selection = int(selection+1)%len(annots)
        
        if(key == ord('c')):
            selectionROI = cv.selectROI("Repositioning",renderEditor(annots,img.copy(),None,False,True),True,True)
            selectedAnnot = annots[selectionmap[selection]]
            if(selectionROI[2] < 0 or selectionROI[3] < 0):
                continue
            if(selectionROI == (0,0,0,0)):
                continue
            
            annots[selection] = AnnotationDef.fromFrame(annotationClasses[int(selectedAnnot.annotationIndex)],selectionROI,img.shape)
            cv.destroyWindow("Repositioning")
            
        if(key == ord('d')):
            annots.pop(selectionmap[selection])
            selection = selection%len(annots)
        
        if(key == ord('p')):
            cv.destroyAllWindows()
        
        if(key == ord('\r')):
            save = easygui.ccbox("Save changes?","Save",("Save","Exit without saving"))
            if(save):
                print("Saved!")
                DirectSaveAnnotations(finalpath.with_suffix(".txt"),annots)
            
            if(easygui.ccbox("Exit?","Exit",("Yes","No"))):
                exit()
            else:
                StartEditingImages()


if(__name__ == "__main__"):
    StartEditingImages()