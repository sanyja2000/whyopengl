from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from ctypes import c_void_p, pointer, sizeof, c_float
import numpy as np
import sys, math
import time
from renderer import VertexBuffer, IndexBuffer, VertexArray, VertexBufferLayout, Shader, Renderer, Texture, Camera, FPSCounter, ShaderHandler
from inputHandler import InputHandler
from playerController import Player
from simpleAudioHandler import AudioHandler
from plane import *
from objloader import processObjFile
from objectHandler import Object3D
import pyrr
import random
from threading import Thread
from mapLoader import MapLoader
from classHandler import *
from fontHandler import FontHandler

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

        OPENGL_VERSION = 2

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
        if OPENGL_VERSION == 3:
            glutPassiveMotionFunc(self.inputHandler.passiveMouseEventHandler)
            glutMotionFunc(self.inputHandler.passiveMouseEventHandler)
        else:
            glutPassiveMotionFunc(self.inputHandler.passiveMouseEventHandler21)
            glutMotionFunc(self.inputHandler.passiveMouseEventHandler21)
        
        GLClearError()

        print(glGetString(GL_SHADING_LANGUAGE_VERSION))

        glClearColor(0.52,0.80,0.92,1.0)

        self.shaderHandler = ShaderHandler()
        
        if OPENGL_VERSION == 3:
            self.shaderHandler.loadShader("default","shaders/3.3/vertex_new.shader","shaders/3.3/fragment_new.shader")
            self.shaderHandler.loadShader("default_transparent","shaders/3.3/vertex_new.shader","shaders/3.3/fragment_def_transparent.shader")
            self.shaderHandler.loadShader("map","shaders/3.3/vertex_new_room.shader","shaders/3.3/fragment_map_infested.shader")
            self.shaderHandler.loadShader("noteblock","shaders/3.3/vertex_noteblock.shader","shaders/3.3/fragment_noteblock.shader")
            self.shaderHandler.loadShader("font","shaders/3.3/vertex_font.shader","shaders/3.3/fragment_font.shader")
        else:
            self.shaderHandler.loadShader("default","shaders/2.1/vertex_new.shader","shaders/2.1/fragment_new.shader")
            self.shaderHandler.loadShader("default_transparent","shaders/2.1/vertex_new.shader","shaders/2.1/fragment_def_transparent.shader")
            self.shaderHandler.loadShader("map","shaders/2.1/vertex_new_room.shader","shaders/2.1/fragment_map_infested.shader")
            self.shaderHandler.loadShader("noteblock","shaders/2.1/vertex_noteblock.shader","shaders/2.1/fragment_noteblock.shader")    
            self.shaderHandler.loadShader("notepiece","shaders/2.1/vertex_notepiece.shader","shaders/2.1/fragment_notepiece.shader")    
            self.shaderHandler.loadShader("font","shaders/2.1/vertex_font.shader","shaders/2.1/fragment_font.shader")
        
        #print("Error: ")
        #print(glGetProgramInfoLog(self.shader.RendererId))

        self.fontHandler = FontHandler(self.shaderHandler.getShader("font"))

        self.audioHandler = AudioHandler()
        
            
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

        self.mp = MapLoader("maps/test2.json")

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
        pass
    def showScreen(self):
        now = time.perf_counter()
        glutSetWindowTitle("FPS: "+str(self.FPSCounter.FPS)+" delta: "+str(self.FPSCounter.deltaTime)+" bullets: "+str(len(self.bulletModels)))
    
        crystal = self.mp.getObject("crystal")
        crystal.model.SetRotation(np.array([0,now*3,0]))
        crystal.model.SetPosition(crystal.model.defaultPosition + np.array([0,math.sin(now)*0.1,0]))


        mapObj = self.mp.getObject("Map1")
        if mapObj:
            mapObj.clearedPoints = np.array([[-5,-10.0,-5,2+math.sin(now)],[5,-10.0,-5,2]])

        if b'm' in self.inputHandler.keysDown and self.inputHandler.keysDown[b'm'] == 1:
            self.mp = MapLoader("maps/test2.json")

        

        self.renderer.Clear()

        self.player.xAng = self.inputHandler.mouseX/(self.windowSize[0]/2)*1.57-self.inputHandler.mouseXoffset
        self.player.yAng = constrain(self.inputHandler.mouseY/(self.windowSize[1]/2)*1.57,-math.pi/2,math.pi/2)
        
        self.player.moveWithKeys(self.inputHandler,self.FPSCounter.deltaTime)
        if self.player.distanceTraveled - self.player.lastWalkSound > 1.5:
            self.player.lastWalkSound = self.player.distanceTraveled
            self.audioHandler.playSound("res/audio/walksound.wav")
        self.player.update(self.FPSCounter.deltaTime)
        if self.player.fallSound:
            self.audioHandler.playSound("res/audio/fallsound.wav")
            self.player.fallSound = False
        viewMat = np.matmul(self.proj,self.player.camModel)

        popupText = ""

        solvedPuzzles = 0
        playingSound = 0
        puzzleCount = 0
        for i in self.mp.objects:
            i.draw(self.shaderHandler,self.renderer,viewMat)
            if (isinstance(i, PuzzlePlane) or isinstance(i, SnakePlane)) and dist(i.model.pos,self.player.pos)<1 and not i.isInteracting:
                popupText = "Press E to interact"
                if b'e' in self.inputHandler.keysDown and self.inputHandler.keysDown[b'e'] == 1:
                    i.isInteracting = True
                    self.inputHandler.interactingWith = i
            if (isinstance(i, PuzzlePlane) or isinstance(i, SnakePlane)) and i.isInteracting:
                popupText = i.interactText
                if b'q' in self.inputHandler.keysDown and self.inputHandler.keysDown[b'q'] == 1:
                    i.isInteracting = False
                    self.inputHandler.interactingWith = None
            if (isinstance(i,PuzzlePlane) or isinstance(i, SnakePlane)):
                puzzleCount += 1
                solvedPuzzles += i.solved
                if i.solved and not i.playedSound:
                    self.audioHandler.playSound(i.sound)
                    i.playedSound = True
                playingSound += self.audioHandler.isStillPlaying(i.sound)
            if hasattr(i, "update"):
                i.update(self.FPSCounter.deltaTime,self.audioHandler)

        if solvedPuzzles == puzzleCount:
            door = self.mp.getObject("Door1")
            if not door.opened and playingSound == 0:
                self.audioHandler.playSound(door.sound)
                door.open()
            

        
        self.fontHandler.drawText(popupText,-1*len(popupText)/50,-0.6,0.05,self.renderer)
        glutSwapBuffers()
        self.inputHandler.updateKeysDown()
        self.FPSCounter.drawFrame(now)

g = Game()

