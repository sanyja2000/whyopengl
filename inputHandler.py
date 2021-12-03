from OpenGL.GLUT import *
import sys
class InputHandler:
    def __init__(self):
        """
        self.keysdown[key]
        - if key is not pressed 0 or KeyError-> care!
        - if key is just pressed 1
        - if key is held down 2
        """
        self.mouseX = 0
        self.mouseY = 0
        self.mouseXoffset = 3.14*1.5
        self.windowSize = [0,0]
        self.mouseCatched = True
        self.keysDown = {b'a':0,b's':0,b'd':0,b'w':0,b' ':0}
        self.interactingWith = None
    def passiveMouseEventHandler(self,*args):
        if self.mouseCatched:
            self.mouseX += args[0]-int(self.windowSize[0]/2)
            self.mouseY += args[1]-int(self.windowSize[1]/2)
            glutWarpPointer(int(self.windowSize[0]/2), int(self.windowSize[1]/2))
    def activeMouseEventHandler(self,*args):
        pass
    def passiveMouseEventHandler21(self,*args):
        if self.mouseCatched:
            self.mouseX = args[0]*3
            self.mouseY = args[1]*2-self.windowSize[1]/2
    def keyDownHandler(self, *args):
        if(args[0]==b'\x1b'):
            glutLeaveMainLoop()
            #glutDestroyWindow(self.window)
            sys.quit()
        if args[0]==b'o':
            self.mouseCatched = not self.mouseCatched
            if self.mouseCatched:
                glutSetCursor(GLUT_CURSOR_NONE)
            else:
                glutSetCursor(GLUT_CURSOR_INHERIT)
        self.keysDown[args[0]] = 1
    def keyUpHandler(self, *args):
        self.keysDown[args[0]] = 0
    def isKeyDown(self,key):
        if key in self.keysDown and self.keysDown[key] == 1:
            return True
        return False
    def isKeyHeldDown(self,key):
        if key in self.keysDown and self.keysDown[key] == 2:
            return True
        return False
    def updateKeysDown(self):
        for key in self.keysDown:
            if self.keysDown[key] == 1:
                self.keysDown[key] = 2
    def hideCursor(self):
        pass
    def changeWindowSize(self,size):
        self.windowSize = size
