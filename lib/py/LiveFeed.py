import numpy as np
import cv2 as cv
import FlowerScan as processor
import easygui
import threading
 
def rescale_frame(frame, scale):    # works for image, video, live video
    width = int(frame.shape[1] * scale)
    height = int(frame.shape[0] * scale)
    dimensions = (width, height)
    return cv.resize(frame, dimensions, interpolation=cv.INTER_AREA)


def displayStream(stream:cv.VideoCapture,title:str):
    while(True):
        ret,frame = stream.read()
        if(not ret):
            return
        cv.imshow(title, frame)
        timer = threading.Timer(0.5)
        timer.join()

contSelect = True
while(contSelect):
    cameraNum = easygui.integerbox("Select Camera#")
    try:
        cap = cv.VideoCapture(cameraNum)
    except:
        easygui.exceptionbox("That camera does not exist!")
    
    threading.Thread(None,displayStream,"StreamDispThread",[cap,"Camera Output"])
    contSelect = not easygui.boolbox("Is this camera correct?")
    
cap.set(cv.CAP_PROP_FRAME_WIDTH,1920)
cap.set(cv.CAP_PROP_FRAME_HEIGHT,1080)

if not cap.isOpened():
    print("Cannot open camera")
    exit()
while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
 
    # if frame is read correctly ret is True
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break
    # Our operations on the frame come here
    out = processor.processScreenShot(frame)
    # Display the resulting frame
    cv.imshow('Processed Stream', out)
    if cv.waitKey(1) == ord('q'):
        break
 
# When everything done, release the capture
cap.release()
cv.destroyAllWindows()