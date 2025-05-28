import mss.base
import mss.darwin
import mss.factory
import numpy as np
import cv2 as cv
import FlowerScan as processor
import easygui
import threading
import mss
import win32gui
 
 
source = easygui.choicebox("Set video source",choices=[
    "Whole Monitor (MUST BE FULLSCREEN)",
    "OBS Virtual Camera"
])


getFrame = lambda:()
cap = None
window = win32gui.FindWindow(None,"Natro Macro")
width = win32gui.GetWindowRect(window)
print(width)

if(source == "Whole Monitor (MUST BE FULLSCREEN)"):
    sct = mss.mss()
    choices=sct.monitors[1:]
    cameraNum = choices[0]
    choices[:,0]

    if(len(choices) >= 2):
        contSelect = True
        while(contSelect):
            cameraNum = easygui.choicebox("Select Monitor",choices=choices)
            
            if(cameraNum == None):
                print("User cancelled monitor selection!")
                exit()
            
            screenshot = np.array(sct.grab(cameraNum))
            cv.imshow('Camera', screenshot)
            contSelect = not easygui.boolbox("Is this camera correct?","Camera Select")
    getFrame = lambda:(np.array(sct.grab(cameraNum)))
elif(source == "OBS Virtual Camera"):
    camWin = None
    contSelect = True
    while(contSelect):
        cameraNum = easygui.integerbox("Select Camera#")
        
        cap = cv.VideoCapture(cameraNum)
        
        if(not cap.isOpened()): 
            easygui.msgbox("That camera does not exist!")
            continue
        
        cap.set(cv.CAP_PROP_FRAME_WIDTH)
        
        ret,frame = cap.read()
        print(frame.shape)
        cv.imshow('Camera', frame)
        contSelect = not easygui.boolbox("Is this camera correct?","Camera Select")
    getFrame = lambda:(cap.read()[1])

    
cv.destroyAllWindows()

while True:
    # Capture frame-by-frame
    frame = getFrame()
    
    # Our operations on the frame come here
    # out = processor.processScreenShot(frame)
    out = frame
    # Display the resulting frame
    cv.imshow('Processed Stream', out)
    if cv.waitKey(1) == ord('q'):
        break
 
# When everything done, release the capture
if(cap):
    cap.release()
cv.destroyAllWindows()