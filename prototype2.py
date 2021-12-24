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
from audioHandler import AudioHandler
from plane import *
from objloader import processObjFile
from objectHandler import Object3D
import pyrr
import random
from threading import Thread
from mapLoader import MapLoader, startLoadingScreen
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

        self.knownCards = 0

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
            self.shaderHandler.loadShader("menuBg","shaders/3.3/vertex_new.shader","shaders/3.3/menuBg.shader")
        else:
            self.shaderHandler.loadShader("default","shaders/2.1/vertex_new.shader","shaders/2.1/fragment_new.shader")
            self.shaderHandler.loadShader("default_transparent","shaders/2.1/vertex_new.shader","shaders/2.1/fragment_def_transparent.shader")
            self.shaderHandler.loadShader("map","shaders/2.1/vertex_new_room.shader","shaders/2.1/fragment_map_infested.shader")
            self.shaderHandler.loadShader("noteblock","shaders/2.1/vertex_noteblock.shader","shaders/2.1/fragment_noteblock.shader")    
            self.shaderHandler.loadShader("notepiece","shaders/2.1/vertex_notepiece.shader","shaders/2.1/fragment_notepiece.shader")    
            self.shaderHandler.loadShader("font","shaders/2.1/vertex_font.shader","shaders/2.1/fragment_font.shader")
            self.shaderHandler.loadShader("menuBg","shaders/2.1/vertex_new.shader","shaders/2.1/menuBg.shader")
        #print("Error: ")
        #print(glGetProgramInfoLog(self.shader.RendererId))

        self.fontHandler = FontHandler(self.shaderHandler.getShader("font"))

        self.audioHandler = AudioHandler()
        
        

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

        #self.mp = MapLoader("maps/test2.json")

        self.mp = MapLoader("maps/menu.json",self.player,unlockedCards=self.knownCards)

        self.loopCounter = 200
        #self.audioSounds = ["res/audio/lastchristmas_drum.wav","res/audio/lastchristmas_bass.wav","res/audio/lastchristmas_chords.wav","res/audio/lastchristmas_melody.wav"]


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
        
        if self.mp.type == "menu":
            cards = []
            i=2
            c = self.mp.getObject("card1")
            while c:
                if c.isActive:
                    startLoadingScreen(self.mp,c.map,self.player,self.inputHandler)
                    self.audioHandler.stopAll()
                    return
                c = self.mp.getObject("card"+str(i))
                i+=1
    def showScreen(self):
        if self.mp.type == "load":
            return
        now = time.perf_counter()
        glutSetWindowTitle("FPS: "+str(self.FPSCounter.FPS)+" delta: "+str(self.FPSCounter.deltaTime)+" seconds: "+str(self.loopCounter))
    
        self.loopCounter += self.FPSCounter.deltaTime

        card = self.mp.getObject("crystal")

        if card != None and self.loopCounter >= card.beatLength:
            self.loopCounter = 0
            vi = 1
            for x in card.beats:
                self.audioHandler.playSound(x,volumeIndex=vi)
                vi+=1


        if self.mp.type == "menu":
            if self.loopCounter >= self.mp.beatLength:
                self.loopCounter = 0
                self.audioHandler.playSound("res/audio/menu_music.wav")
            # Menu music
            # Hovering over cards in menu
            cards = []
            i=2
            c = self.mp.getObject("card1")
            while c:
                cards.append(c)
                c = self.mp.getObject("card"+str(i))
                i+=1
            cur = self.mp.getObject("cursor")
            mouseX = self.inputHandler.mouseX/self.windowSize[0]*3-2
            mouseY = -self.inputHandler.mouseY/self.windowSize[1]*3
            mouseX = constrain(mouseX, -1.5,1.5)
            mouseY = constrain(mouseY, -0.75,0.75)
            cur.model.SetPosition([-0.1,mouseY,mouseX])
            #print(self.inputHandler.mouseX,self.inputHandler.mouseY)
            for x in cards:
                x.isActive = False
            if(cur.model.pos[2]<-0.6 and cur.model.pos[1]>-0.5 and cur.model.pos[1]<0.5):
                cards[0].isActive = True
                cards[0].mousePos = cur.model.pos
            elif(cur.model.pos[2]>0.6 and cur.model.pos[1]>-0.5 and cur.model.pos[1]<0.5):
                cards[2].isActive = True
                cards[2].mousePos = cur.model.pos
            elif(cur.model.pos[2]<0.6 and cur.model.pos[2]>-0.6 and cur.model.pos[1]>-0.5 and cur.model.pos[1]<0.5):
                cards[1].isActive = True
                cards[1].mousePos = cur.model.pos
            
        mapObj = self.mp.getObject("Map1")
        if mapObj:
            temparr = []
            for x in self.mp.objects:
                if isinstance(x, PuzzlePlane) and x.solved:
                    temparr.append([x.model.pos[0],x.model.pos[1]-10.25,x.model.pos[2],2+math.sin(now/2.0)/3.0])
            #mapObj.clearedPoints = np.array([[-5,-10.0,-5,2+math.sin(now/2.0)/3.0],[5,-10.0,-5,2+math.sin(now/2.0)/3.0]])
            if card != None and hasattr(card,"openTime"):
                temparr.append([0,-10,0,(now-card.openTime)*70/22])
            mapObj.clearedPoints = np.array(temparr)
        if self.inputHandler.isKeyDown(b'm'):
            #startLoadingScreen(self.mp)
            if self.mp.type != "menu":
                self.audioHandler.stopAll()
                startLoadingScreen(self.mp,"maps/menu.json",self.player,self.inputHandler)#MapLoader("maps/menu.json",self.player)
                self.inputHandler.interactingWith = self.mp.getObject("ldscreen")
        if b'l' in self.inputHandler.keysDown and self.inputHandler.keysDown[b'l'] == 1:
            self.mp.getObject("crystal").open()

        self.renderer.Clear()

        self.player.xAng = self.inputHandler.mouseX/(self.windowSize[0]/2)*1.57-self.inputHandler.mouseXoffset
        self.player.yAng = constrain(self.inputHandler.mouseY/(self.windowSize[1]/2)*1.57,-math.pi/2,math.pi/2)
        
        self.player.moveWithKeys(self.inputHandler,self.FPSCounter.deltaTime)
        if self.player.distanceTraveled - self.player.lastWalkSound > 1.5:
            self.player.lastWalkSound = self.player.distanceTraveled
            self.audioHandler.playSound("res/audio/walksound.wav")
        self.player.update(self.FPSCounter.deltaTime,self.inputHandler)
        if self.player.fallSound:
            self.audioHandler.playSound("res/audio/fallsound.wav")
            self.player.fallSound = False
        viewMat = np.matmul(self.proj,self.player.camModel)

        popupText = ""

        solvedPuzzles = 0
        playingSound = 0
        puzzleCount = 0

        # Temporary fix for menu
        if card == None:
            puzzleCount = -1


        for i in self.mp.objects:
            i.draw(self.shaderHandler,self.renderer,viewMat)
            if (isinstance(i, PuzzlePlane) or isinstance(i, SlidePlane)) and dist(i.model.pos,self.player.pos)<1 and not i.isInteracting:
                popupText = "Press E to interact"
                if self.inputHandler.isKeyDown(b'e'):
                    i.isInteracting = True
                    self.inputHandler.interactingWith = i
                    self.player.animating = 1.0
            if (isinstance(i, TeleportCrystal) and dist(i.model.pos,self.player.pos)<1.5 and not i.isInteracting):
                popupText = "Press E to travel"
                if self.inputHandler.isKeyDown(b'e'):
                    # load menu with animation
                    self.knownCards = self.knownCards | mapObj.cardNum
                    # stop music
                    solvedPuzzles = 0
                    self.mp = MapLoader("maps/menu.json",self.player,unlockedCards=self.knownCards)
                    self.audioHandler.stopAll()
                    break
            if (isinstance(i, PuzzlePlane) or isinstance(i, SlidePlane)) and i.isInteracting:
                popupText = i.interactText
                if self.inputHandler.isKeyDown(b'q') or i.solved:
                    i.isInteracting = False
                    self.inputHandler.interactingWith = None
                    self.player.animating = 1.0
            if (isinstance(i,PuzzlePlane) or isinstance(i, SlidePlane)):
                puzzleCount += 1
                solvedPuzzles += i.solved
            
            if hasattr(i, "update"):
                i.update(self.FPSCounter.deltaTime,self.audioHandler)

        for x in range(solvedPuzzles):
            self.audioHandler.channelVolume[x+1] = 1

        if solvedPuzzles == puzzleCount:
            if not card.opened and playingSound == 0:
                card.openTime = now
                #self.audioHandler.playSound(card.sound)
                card.open()
            

        
        self.fontHandler.drawText(popupText,-1*len(popupText)/50,-0.6,0.05,self.renderer)
        glutSwapBuffers()
        self.inputHandler.updateKeysDown()
        #self.audioHandler.update()
        self.FPSCounter.drawFrame(now)

g = Game()

