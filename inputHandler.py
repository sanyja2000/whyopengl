from OpenGL.GLUT import *
import sys
class InputHandler:
    def __init__(self):
        self.mouseX = 0
        self.mouseY = 0
        self.mouseXoffset = 3.14*1.5
        self.windowSize = [0,0]
        self.mouseCatched = True
        self.keysDown = {b'a':0,b's':0,b'd':0,b'w':0,b' ':0}
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
            self.mouseY = args[1]
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
    def hideCursor(self):
        pass
    def changeWindowSize(self,size):
        self.windowSize = size
