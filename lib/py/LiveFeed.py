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

class LiveFeed():
    
    def __init__(self):
        self.getFrame = lambda:()
        self.cap = None

    def chooseStream(self):
        try:
            window = win32gui.FindWindow(None,"Roblox")
            rect = win32gui.GetWindowRect(window)
        except:
            print("Failed to find roblox window!")
            exit()
        source = easygui.choicebox("Set video source",choices=[
            "Whole Monitor",
            "OBS Virtual Camera"
        ])


        if(source == "Whole Monitor"):
            sct = mss.mss()
            monitors=sct.monitors[1:]
            cameraNum = monitors[0]
            for c in monitors:
                c["left"] = rect[0]
                c["top"] = rect[1]
                c["width"] = rect[2]
                c["height"] = rect[3]

            if(len(monitors) >= 2):
                contSelect = True
                while(contSelect):
                    screenshot = np.array(sct.grab(win32gui.GetWindowRect(window)))
                    cv.imshow('Camera', screenshot)
                    contSelect = not easygui.boolbox("Is this correct?","Window Select")
            self.getFrame = lambda:(np.array(sct.grab(cameraNum)))
        elif(source == "OBS Virtual Camera"):
            camWin = None
            contSelect = True
            while(contSelect):
                cameraNum = easygui.integerbox("Select Camera#")
                
                cap = cv.VideoCapture(cameraNum)
                self.cap = cap
                
                if(not cap.isOpened()): 
                    easygui.msgbox("That camera does not exist!")
                    continue
                
                cap.set(cv.CAP_PROP_FRAME_WIDTH)
                
                ret,frame = cap.read()
                print(frame.shape)
                cv.imshow('Camera', frame)
                contSelect = not easygui.boolbox("Is this correct?","Window Select")
            self.getFrame = lambda:(cap.read()[1])

            
        cv.destroyAllWindows()

    def getSingleFrame(self):
        return self.getFrame()

    def viewStream(self):
        while True:
            # Capture frame-by-frame
            frame = self.getFrame()
            
            # Our operations on the frame come here
            out = processor.processScreenShot(frame)
            # out = frame
            # Display the resulting frame
            cv.imshow('Processed Stream', out)
            if cv.waitKey(1) == ord('q'):
                break
    
    def cleanup(self):
        # When everything done, release the capture
        if(self.cap):
            cap.release()
        cv.destroyAllWindows()

if(__name__ == "__main__"):
    feed = LiveFeed()
    feed.chooseStream()
    feed.viewStream()
    feed.cleanup()