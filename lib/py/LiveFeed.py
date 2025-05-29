import numpy as np
import cv2 as cv
import FlowerScan as processor
import easygui
import mss
import win32gui
import random,string,os
from ffmpeg import FFmpeg
import pathlib
import threading

SRC_WM = "Whole Monitor"
SRC_OBS = "OBS Virtual Camera"
SRC_VID = "Prerecorded Video"
class LiveFeed():
    saveToVid = False
    VID_PATH = pathlib.Path("lib/py/trainingVids")
    SEARCHED_WINDOW = "Roblox"
    pauseEvent = threading.Event()
    finishedPausingEvent = threading.Event()
    playEvent = threading.Event()
    stopEvent = threading.Event()
    streamOpen = False
    streamShown = True
    playerThread = None
    
    def __init__(self):
        self.getFrame = lambda:()
        self.cap = None
        self.cwr = None
        self.sourceType = None
        self.length = 0
        self.currentFrame = 0
        self.scrubbable = False
        self.streamShown = True
        self.fps = 0
        self.saveName = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

    def chooseStream(self):
        # User chooses source
        source = easygui.choicebox("Set video source",choices=[
            SRC_WM,
            SRC_OBS,
            SRC_VID
        ])
        # We find target window
        if(source == SRC_WM or source == SRC_OBS):
            try:
                window = win32gui.FindWindow(None,self.SEARCHED_WINDOW)
                rect = win32gui.GetWindowRect(window)
            except:
                print("Failed to find window!")
                exit()

        self.sourceType = source
        # When source is whole monitor
        if(source == SRC_WM):
            sct = mss.mss()
            monitors=sct.monitors[1:]
            cameraNum = monitors[0]
            #Set our choices to focus on the target window
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
        elif(source == SRC_OBS):
            contSelect = True
            cap = None
            while(contSelect):
                cameraNum = easygui.integerbox("Select Camera#")
                
                cap = cv.VideoCapture(cameraNum)
                
                if(not cap.isOpened()): 
                    easygui.msgbox("That camera does not exist!")
                    continue
                
                cap.set(cv.CAP_PROP_FRAME_WIDTH,rect[2])
                cap.set(cv.CAP_PROP_FRAME_HEIGHT,rect[3])
                
                ret,frame = cap.read()
                print(frame.shape)
                cv.imshow('Camera', frame)
                contSelect = not easygui.boolbox("Is this correct?","Window Select")
            self.cap = cap
            self.getFrame = lambda:self.cap.read()[1]
            
        elif(source == SRC_VID):
            choices = os.listdir(self.VID_PATH)
            capName = None
            print(choices)
            if(len(choices) < 1):
                print("No videos found!")
                exit()
            if(len(choices) < 2):
                capName = choices[0]
            else:
                capName = easygui.choicebox("Choose Video",choices=choices)
            fullPath = self.VID_PATH.joinpath(capName)
            cap = cv.VideoCapture(fullPath,0)
            if(not cap.isOpened()):
                print("Couldn't read video! Trying ffmpeg.")
                newName = fullPath.with_suffix(".mp4")
                cap = cv.VideoCapture(newName,0)
                if(not cap.isOpened()):
                    ffmpeg = (
                        FFmpeg()
                        .input(fullPath)
                        .output(
                            newName,
                            {"codec:v": "libx264"},
                            preset="veryslow",
                            crf=24,
                        )
                    )
                    ffmpeg.execute()
                cap = cv.VideoCapture(newName,0)
                if(not cap.isOpened()):
                    exit()
            self.cap = cap
            self.getFrame = lambda:self.cap.read()[1]
            self.length = cap.get(cv.CAP_PROP_FRAME_COUNT)
            self.scrubbable = True
            
            
        cv.destroyAllWindows()

    def getSingleFrame(self):
        return self.getFrame()
    
    def pause(self):
        self.pauseEvent.set()
    
    def play(self):
        if(not self.streamOpen):
            self.viewStream()
        self.playEvent.set()
        
    def stop(self):
        self.stopEvent.set()
        self.cleanup()

    def viewStream(self):
        self.streamOpen = True
        while True:
            # Capture frame-by-frame
            frame = self.getFrame()
            if(frame is None):
                print("Video Stream Returned None! (Likely just end of stream)")
                exit()
            
            # Our operations on the frame come here
            out = frame
            if(self.saveToVid):
                if(not self.cwr):
                    self.cwr = cv.VideoWriter(self.saveName,self.length,self.cap.get(cv.CAP_PROP_FPS),frame.size,True)
                    self.length = 0
                self.cwr.write(frame)
                self.length += 1
                
            
            # out = frame
            # Display the resulting frame
            if(self.streamShown):
                cv.imshow('Processed Stream', out)
            else:
                cv.destroyWindow('Processed Stream')
            self.currentFrame += 1
            if cv.waitKey(1) == ord('q') or self.stopEvent.is_set():
                break
            if(self.pauseEvent.is_set()):
                self.pauseEvent.clear()
                self.finishedPausingEvent.set()
                self.playEvent.wait()
                self.playEvent.clear()
                self.finishedPausingEvent.clear()
        
        return self.playerThread
    
    def viewStreamAndWait(self):
        thread = self.viewStream()
        thread.daemon
        
    
    def cleanup(self):
        # When everything done, release the capture
        if(self.cap):
            self.cap.release()
        if(self.cwr):
            self.cwr.release()

if(__name__ == "__main__"):
    import Training