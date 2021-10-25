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

def DrawWithShadow(obj,renderer,shader,depthText, projView, shadowMat, camPosition):
    #obj,renderer,shader,depthText, projView, shadowMat, camPos
    shader.Bind()

    shader.SetUniform1i("shadowMap",0)
    shader.SetUniform1i("diffuseTexture",1)

    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_2D, depthText)
    glActiveTexture(GL_TEXTURE1)
    glBindTexture(GL_TEXTURE_2D, obj.texture.RendererId)
    #obj.texture.Bind(slot=1)

    shader.SetUniformMat4f("u_VP", projView)
    shader.SetUniformMat4f("u_model", obj.modelMat)
    shader.SetUniformMat4f("u_shadowMatrix", shadowMat)
    shader.SetUniform3f("lightPos",0, 1, -5.0)
    shader.SetUniform3f("viewPos",camPosition[0],camPosition[1],camPosition[2])
    renderer.Draw(obj.va,obj.ib,shader)

class Noteblock:
    def __init__(self):
        self.lastPlayed = 0
        self.model = Object3D("res/noteblock1.obj","res/noteblock.png").Clone()

class Game:
    def __init__(self):
        glutInit()
        glutInitDisplayMode(GLUT_RGBA)
        glutInitContextVersion (3, 3)
        glutInitContextProfile (GLUT_COMPATIBILITY_PROFILE)
        self.windowSize = [1024,768]
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

        with open("shaders/vertex_new.shader","r") as vert:
            vshader = "".join(vert.readlines())

        with open("shaders/fragment_new.shader","r") as frag:
            fshader = "".join(frag.readlines())

        with open("shaders/vertex_new_room.shader","r") as vert:
            roomvshader = "".join(vert.readlines())

        with open("shaders/fragment_new_room.shader","r") as frag:
            roomfshader = "".join(frag.readlines())

        with open("shaders/vertex_shadow.shader","r") as vert:
            shadowvshader = "".join(vert.readlines())

        with open("shaders/fragment_shadow.shader","r") as frag:
            shadowfshader = "".join(frag.readlines())

        with open("shaders/vertex_with_shadow.shader","r") as vert:
            defaultShadowvshader = "".join(vert.readlines())

        with open("shaders/fragment_with_shadow.shader","r") as frag:
            defaultShadowfshader = "".join(frag.readlines())
    

        


        self.shader = Shader(vshader, fshader)
        self.roomShader = Shader(roomvshader, roomfshader)
        self.shadowShader = Shader(shadowvshader, shadowfshader)
        self.defaultShadowShader = Shader(defaultShadowvshader, defaultShadowfshader)
        #self.noteblockShader = Shader(nblockvshader, nblockfshader)
        print("Error: ")
        print(glGetProgramInfoLog(self.shader.RendererId))



        
        #self.models = []
        self.noteblocks = []
        self.gunModelPrefab = Object3D("res/noteblock1.obj","res/noteblock.png")
        
        #self.mapModel = Object3D("res/map1.obj","res/map1.png")
        self.mapModel = Object3D("res/simplePlane.obj","res/wall_top.png",textureRepeat=True)#Object3D("res/room1.obj","res/wall_top.png",textureRepeat=True)
        self.mapModel.SetPosition(np.array([0,0,0]))
        self.mapModel.SetScale(10)
        self.n = 20
        
        self.audioHandler = AudioHandler()
    

        self.notes = ["C4","C#4","D4","D#4","E4","F4","F#4","G4","G#4","A4","A#4","B4","C5"]

        
        
        for i in range(len(self.notes)):
            n = Noteblock()
            n.model.SetScale(0.3)
            n.note = self.notes[i]
            n.model.SetPosition([-6+i*0.8,0+self.notes.index(n.note)*0.2,0])
            n.sample = (np.sin(2*np.pi*np.arange(44100*1)*self.audioHandler.notes[self.notes[i]]/44100)).astype(np.float32)
            
            self.noteblocks.append(n)
            
            
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
        self.player.model = self.gunModelPrefab.Clone()

        self.noteBlockCounter = 0
        self.timeDelay = 0.2
        self.lastPlayed = 0



        #SHADOWS

        self.depthMapFBO = glGenFramebuffers(1)

        self.SHADOW_WIDTH = 1024
        self.SHADOW_HEIGHT = 1024

        self.depthMap = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.depthMap)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT, 
                     self.SHADOW_WIDTH, self.SHADOW_HEIGHT, 0, GL_DEPTH_COMPONENT, GL_FLOAT, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        #glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT) 
        #glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)



        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_BORDER);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_BORDER);
        borderColor = np.array([ 1.0, 1.0, 1.0, 1.0]);
        glTexParameterfv(GL_TEXTURE_2D, GL_TEXTURE_BORDER_COLOR, borderColor);  

        glBindFramebuffer(GL_FRAMEBUFFER, self.depthMapFBO)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D, self.depthMap, 0)
        glDrawBuffer(GL_NONE)
        glReadBuffer(GL_NONE)
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glBindTexture(GL_TEXTURE_2D, 0)

        self.shadowProj = pyrr.matrix44.create_orthogonal_projection(-10.0, 10.0, -10.0, 10.0, 1.0, 10)
        self.shadowView = pyrr.matrix44.create_look_at(np.array([0, 1.0, -5.0]), np.array( [0.0, 0.0,  0.0]), np.array( [0.0, 1.0,  0.0]))

        self.shadowMatrix = np.matmul(self.shadowProj,self.shadowView)

        
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

        #SHADOW RENDER
        glViewport(0, 0, self.SHADOW_WIDTH, self.SHADOW_HEIGHT);
        glBindFramebuffer(GL_FRAMEBUFFER, self.depthMapFBO);
        glClear(GL_DEPTH_BUFFER_BIT);
        for i in range(len(self.noteblocks)):
            self.noteblocks[i].model.DrawWithShader(self.shadowShader,self.renderer,self.shadowMatrix)
        self.mapModel.DrawWithShader(self.shadowShader,self.renderer,self.shadowMatrix)

        #NORMAL RENDER
        glBindFramebuffer(GL_FRAMEBUFFER, 0);
        self.renderer.Clear()
        glViewport(0,0,self.windowSize[0],self.windowSize[1])
        """
        if self.inputHandler.keysDown[b' '] == 1 and now-self.lastPlayed>self.timeDelay:
            self.audioHandler.playNote(self.noteblocks[self.noteBlockCounter].note,1)
            self.lastPlayed = now
            self.noteblocks[self.noteBlockCounter].lastPlayed = now
            self.noteBlockCounter = (self.noteBlockCounter+1)%len(self.noteblocks)

        if self.inputHandler.keysDown[b' '] == 0:
            self.noteBlockCounter = 0
        """
        glutSetWindowTitle("FPS: "+str(self.FPSCounter.FPS)+" delta: "+str(self.FPSCounter.deltaTime)+" bullets: "+str(len(self.bulletModels)))
        

        self.player.xAng = self.inputHandler.mouseX/(self.windowSize[0]/2)*1.57-1.57
        self.player.yAng = constrain(self.inputHandler.mouseY/(self.windowSize[1]/2)*1.57-1.57,-math.pi/2,math.pi/2)
        
        self.player.moveWithKeys(self.inputHandler.keysDown,self.FPSCounter.deltaTime)
        self.player.update()
        viewMat = np.matmul(self.proj,self.player.camModel)

        
        for b in self.bulletModels:
            b.SetPosition(np.array([b.pos[0]-10*b.vx*self.FPSCounter.deltaTime,b.pos[1]-10*b.vy*self.FPSCounter.deltaTime,b.pos[2]-10*b.vz*self.FPSCounter.deltaTime]))
            #b.DrawWithShader(self.shader,self.renderer,viewMat)

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
            self.noteblocks[i].model.DrawWithShader(self.shader,self.renderer,viewMat,options={"u_Time":now,"u_LastPlayed":self.noteblocks[i].lastPlayed})
        self.mapModel.DrawWithShader(self.shader,self.renderer,viewMat)
        """
        invcamPos = np.array([-1*self.player.camPosition[0],-1*self.player.camPosition[1],-1*self.player.camPosition[2]])
        #obj,renderer,shader,depthText, projView, shadowMat, camPos
        for i in range(len(self.noteblocks)):
            DrawWithShadow(self.noteblocks[i].model,self.renderer,self.defaultShadowShader,self.depthMap,viewMat,self.shadowMatrix,invcamPos)
        DrawWithShadow(self.mapModel,self.renderer,self.defaultShadowShader,self.depthMap,viewMat,self.shadowMatrix,invcamPos)

        glutSwapBuffers()
        self.FPSCounter.drawFrame(now)

g = Game()

