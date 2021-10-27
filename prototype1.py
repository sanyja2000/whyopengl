from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from ctypes import c_void_p, pointer, sizeof, c_float
import numpy as np
import sys, math
import time
from renderer import VertexBuffer, IndexBuffer, VertexArray, VertexBufferLayout, Shader, Renderer, Texture, Camera, FPSCounter
from inputHandler import InputHandler
from playerController import Player
from audioHandler import AudioHandler
from plane import *
from objloader import processObjFile
from objectHandler import Object3D
import pyrr
import random
from threading import Thread
from mapLoader import MapLoader
from shaderHandler import ShaderHandler
from classHandler import *

def dist(a,b):
    return math.sqrt((b[0]-a[0])**2+(b[1]-a[1])**2+(b[2]-a[2])**2)

def constrain(n,f,t):
    if n<f:
        return f
    if n>t:
        return t
    return n

def GLClearError():
    while glGetError() != GL_NO_ERROR:
        pass
        
def GLCheckError():
    while True:
        err = glGetError()
        if err == 0:
            break
        print("[OpenGL Error] ",err)

class Game:
    def __init__(self):
        glutInit()
        glutInitDisplayMode(GLUT_RGBA)

        OPENGL_VERSION = 3

        if OPENGL_VERSION == 3:
            glutInitContextVersion (3, 3)
        else:
            glutInitContextVersion (2, 1)
        glutInitContextProfile (GLUT_COMPATIBILITY_PROFILE)
        self.windowSize = [1280,720]
        glutInitWindowSize(self.windowSize[0], self.windowSize[1])
        glutInitWindowPosition(0, 0)
        self.window = glutCreateWindow("OpenGL Coding Practice")
        glutReshapeFunc(self.windowResize)
        
        glutDisplayFunc(self.showScreen)
        glutIdleFunc(self.showScreen)
        self.inputHandler = InputHandler()
        self.inputHandler.changeWindowSize(self.windowSize)
        glutKeyboardFunc(self.inputHandler.keyDownHandler)
        glutKeyboardUpFunc(self.inputHandler.keyUpHandler)

        glutMouseFunc(self.mouseClicked)
        glutPassiveMotionFunc(self.inputHandler.passiveMouseEventHandler)
        glutMotionFunc(self.inputHandler.passiveMouseEventHandler)

        
        GLClearError()

        print(glGetString(GL_SHADING_LANGUAGE_VERSION))

        glClearColor(0.52,0.80,0.92,1.0)

        self.shaderHandler = ShaderHandler()
        
        if OPENGL_VERSION == 3:
            self.shaderHandler.loadShader("default","shaders/3.3/vertex_new.shader","shaders/3.3/fragment_new.shader")
            self.shaderHandler.loadShader("map","shaders/3.3/vertex_new_room.shader","shaders/3.3/fragment_new_room.shader")
            self.shaderHandler.loadShader("noteblock","shaders/3.3/vertex_noteblock.shader","shaders/3.3/fragment_noteblock.shader")
        else:
            self.shaderHandler.loadShader("default","shaders/2.1/vertex_new.shader","shaders/2.1/fragment_new.shader")
            self.shaderHandler.loadShader("map","shaders/2.1/vertex_new_room.shader","shaders/2.1/fragment_new_room.shader")
            self.shaderHandler.loadShader("noteblock","shaders/2.1/vertex_noteblock.shader","shaders/2.1/fragment_noteblock.shader")    
        
        #print("Error: ")
        #print(glGetProgramInfoLog(self.shader.RendererId))

        self.audioHandler = AudioHandler()
    

        self.notes = ["C4","C#4","D4","D#4","E4","F4","F#4","G4","G#4","A4","A#4","B4","C5"]
        
        
            
        self.bulletModelPrefab = Object3D("res/bullet1.obj","res/bullet1.png")
        self.bulletModels = []

        self.proj = pyrr.matrix44.create_perspective_projection(45.0, self.windowSize[0]/self.windowSize[1], 1.0, 10.0)

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glEnable(GL_DEPTH_TEST)

        glutSetCursor(GLUT_CURSOR_NONE)
        self.renderer = Renderer()


        self.FPSCounter = FPSCounter()
        self.player = Player()        
        self.player.model = Object3D(None)

        self.timeDelay = 0.2
        self.lastPlayed = 0
        
        self.noteblocks = []

        self.mp = MapLoader("maps/test1.json")
        #print(self.mp.objects)
        for o in self.mp.objects:
            if isinstance(o, Noteblock13):
                o.model.SetPosition(np.array([o.model.pos[0], self.notes.index(o.note)*0.2, o.model.pos[2]]))
                o.sample = (np.sin(2*np.pi*np.arange(44100*1)*self.audioHandler.notes[self.notes[self.notes.index(o.note)]]/44100)).astype(np.float32)
                self.noteblocks.append(o)
        self.noteBlockCounter = 0

        glutMainLoop()
    def errorMsg(self, *args):
        print(args)
        return 0
    def windowResize(self, *args):
        self.windowSize = [args[0], args[1]]
        self.proj = pyrr.matrix44.create_perspective_projection(45.0, self.windowSize[0]/self.windowSize[1], 1.0, 10.0)
        glViewport(0,0,self.windowSize[0],self.windowSize[1])
        self.inputHandler.changeWindowSize(self.windowSize)
    def mouseClicked(self,*args):
        if len(self.bulletModels)<6 and args[1] == 0:
            b = self.bulletModelPrefab.Clone()
            b.SetScale(0.1)
            b.vx = math.sin(-self.player.xAng)
            b.vz = math.cos(self.player.xAng)
            b.vy = math.sin(self.player.yAng)
            b.SetRotation(np.array([self.player.yAng,self.player.xAng,0]))
            b.SetPosition(np.array(self.player.camPosition)*-1+np.array([0,-0.3,0]))
            self.bulletModels.append(b)
    def showScreen(self):
        now = time.perf_counter()

        if self.inputHandler.keysDown[b' '] == 1 and now-self.lastPlayed>self.timeDelay:
            self.audioHandler.playNote(self.noteblocks[self.noteBlockCounter].note,1)
            self.lastPlayed = now
            self.noteblocks[self.noteBlockCounter].lastPlayed = now
            self.noteBlockCounter = (self.noteBlockCounter+1)%len(self.noteblocks)

        if b'm' in self.inputHandler.keysDown and self.inputHandler.keysDown[b'm'] == 1:
            self.noteblocks = []
            self.mp = MapLoader("maps/test1.json")
            #print(self.mp.objects)
            for o in self.mp.objects:
                if isinstance(o, Noteblock13):
                    o.model.SetPosition(np.array([o.model.pos[0], self.notes.index(o.note)*0.2, o.model.pos[2]]))
                    o.sample = (np.sin(2*np.pi*np.arange(44100*1)*self.audioHandler.notes[self.notes[self.notes.index(o.note)]]/44100)).astype(np.float32)
                    self.noteblocks.append(o)

        if self.inputHandler.keysDown[b' '] == 0:
            self.noteBlockCounter = 0
        glutSetWindowTitle("FPS: "+str(self.FPSCounter.FPS)+" delta: "+str(self.FPSCounter.deltaTime)+" bullets: "+str(len(self.bulletModels)))
        self.renderer.Clear()

        self.player.xAng = self.inputHandler.mouseX/(self.windowSize[0]/2)*1.57-self.inputHandler.mouseXoffset
        self.player.yAng = constrain(self.inputHandler.mouseY/(self.windowSize[1]/2)*1.57,-math.pi/2,math.pi/2)
        
        self.player.moveWithKeys(self.inputHandler.keysDown,self.FPSCounter.deltaTime)
        self.player.update(self.FPSCounter.deltaTime)
        viewMat = np.matmul(self.proj,self.player.camModel)

        
        for b in self.bulletModels:
            b.SetPosition(np.array([b.pos[0]-10*b.vx*self.FPSCounter.deltaTime,b.pos[1]-10*b.vy*self.FPSCounter.deltaTime,b.pos[2]-10*b.vz*self.FPSCounter.deltaTime]))
            b.DrawWithShader(self.shaderHandler.getShader("default"),self.renderer,viewMat)

            if dist(b.pos,self.player.pos)>10:
                self.bulletModels.remove(b)
                continue
            for noteblock in self.noteblocks:
                if dist(b.pos, noteblock.model.pos)<0.5:
                    newNote = self.notes[(self.notes.index(noteblock.note)+1)%len(self.notes)]
                    noteblock.note = newNote#self.notes[self.notes.index(noteblock.note)+1]
                    noteblock.lastPlayed = now
                    noteblock.model.SetPosition([-6+self.noteblocks.index(noteblock)*0.8,0+self.notes.index(noteblock.note)*0.2,-2])
                    self.audioHandler.playNote(noteblock.note,1)
                    self.bulletModels.remove(b)
                    break
        """   
        for i in range(len(self.noteblocks)):
            self.noteblocks[i].model.DrawWithShader(self.noteblockShader,self.renderer,viewMat,options={"u_Time":now,"u_LastPlayed":self.noteblocks[i].lastPlayed})
        self.mapModel.DrawWithShader(self.roomShader,self.renderer,viewMat)
        """
        for i in self.mp.objects:
            i.draw(self.shaderHandler,self.renderer,viewMat)
        glutSwapBuffers()
        self.FPSCounter.drawFrame(now)

g = Game()

