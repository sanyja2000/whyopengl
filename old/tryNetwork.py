from OpenGL.GL import *
from OpenGL.GL import shaders
from OpenGL.GLUT import *
from OpenGL.GLU import *
from ctypes import c_void_p, pointer, sizeof, c_float
import numpy as np
import sys, math
import time
from renderer import VertexBuffer, IndexBuffer, VertexArray, VertexBufferLayout, Shader, Renderer, Texture, Camera
from plane import *
from objloader import processObjFile
from objectHandler import Object3D
import pyrr
import random
from ChatClient import Client as NetworkClient

vshader = """
#version 330 core
layout(location=0) in vec3 position;
layout(location=1) in vec2 texCoord;
layout(location=2) in vec3 normal;
out vec2 v_TexCoord;
varying vec3 v_position;
varying vec3 v_normal;

uniform mat4 u_MVP;
void main()
{

    gl_Position = u_MVP * vec4(position,1.0);
    v_TexCoord = texCoord;
    v_normal = normalize(normal).xyz;
    v_position = position.xyz;
    
}"""



fshader = """
#version 330 core
layout(location=0) out vec4 color;

in vec2 v_TexCoord;
varying vec3 v_position;
varying vec3 v_normal;

uniform sampler2D u_Texture;

void main(){
    vec4 texColor = texture(u_Texture, v_TexCoord);
    
    vec3 lightPos = vec3(0.0,4.0,3.0);

     vec3 lightDir = normalize(lightPos-v_position);
      vec3 norm = v_normal;
     
      float diff = max(dot(norm, lightDir), 0.0);
    
    color = vec4(texColor.xyz*(0.3+diff),1.0);
    //color = vec4(0.8,0.3,0.2,1.0);
}
"""
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

        host, port = "127.0.0.1", 1234
        self.connId = random.randint(0,1000000)
        self.netClient = NetworkClient(host, port, self.connId)
        
        glutInit()
        glutInitDisplayMode(GLUT_RGBA)
        glutInitContextVersion (3, 3)
        glutInitContextProfile (GLUT_COMPATIBILITY_PROFILE)
        self.windowSize = [800,600]
        glutInitWindowSize(self.windowSize[0], self.windowSize[1])
        glutInitWindowPosition(0, 0)
        self.window = glutCreateWindow("OpenGL Coding Practice")
        glutDisplayFunc(self.showScreen)
        glutIdleFunc(self.showScreen)
        glutKeyboardFunc(self.keyPressed)
        glutKeyboardUpFunc(self.keyReleased)
        glutMouseFunc(self.mouseClicked)
        glutPassiveMotionFunc(self.mouseHandler)
        self.mouseX = 0.0
        self.mouseY = 0.0
        
        GLClearError()

        print(glGetString(GL_SHADING_LANGUAGE_VERSION))

        glClearColor(0.3,0.3,0.3,1.0)


        self.shader = Shader(vshader, fshader)

        self.players = {}
        
        self.models = []
        self.gunModelPrefab = Object3D("res/GunTri.obj","res/Gun.png")
        self.n = 20
        for i in range(self.n):
            self.models.append(self.gunModelPrefab)
            self.models[-1].SetScale(0.5)

        self.bulletModelPrefab = Object3D("res/bullet1.obj","res/bullet1.png")
        self.bulletModels = []
        #self.bulletModel = Object3D("res/bullet1.obj","res/bullet1.png")
        
        #self.camera = Camera()
        #self.proj = self.camera.Perspective(-2,2,-1.5,1.5,-1,1)
        #self.proj = np.matrix([[1,0,0,0],[0,1,0,0],[0,0,0,0],[0,0,0,1]])
        self.proj = pyrr.matrix44.create_perspective_projection(45.0, self.windowSize[0]/self.windowSize[1], 1.0, 10.0)
        #self.proj = pyrr.matrix44.create_perspective_projection_from_bounds(-20, 20, -15, 15, -10, 10)
        #self.proj = pyrr.matrix44.create_orthogonal_projection(-20, 20, -15, 15, -100, 100)
        

        print("Error: ")
        print(glGetProgramInfoLog(self.shader.RendererId))


        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glEnable(GL_DEPTH_TEST)
        
        self.camPosition = [0,0,-1]

        self.keysDown = {b'a':0,b's':0,b'd':0,b'w':0}

        self.shader.UnBind()
        
        glBindBuffer(GL_ARRAY_BUFFER,0)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER,0)
        glBindVertexArray(0)

        self.tp = TexturePlane("res/Pebbles.png")

        self.x = 0
        self.vx = 0
        self.direction = 0
        self.a = 0
        self.mouseCatched = True
        glutSetCursor(GLUT_CURSOR_NONE)
        self.renderer = Renderer()

        self.fpsCounter = []
        self.deltaTime = 0
        
        glutMainLoop()
    def errorMsg(self, *args):
        print(args)
        return 0
    def keyPressed(self,*args):
        if(args[0]==b'\x1b'):
            glutLeaveMainLoop()
            glutDestroyWindow(self.window)
            sys.quit()
        if args[0]==b'a':
           self.direction = -1
        if args[0]==b'd':
           self.direction = 1
        if args[0]==b's':
           self.direction = 0
        if args[0]==b'o':
            self.mouseCatched = not self.mouseCatched
            if self.mouseCatched:
                glutSetCursor(GLUT_CURSOR_NONE)
            else:
                glutSetCursor(GLUT_CURSOR_INHERIT)
        self.keysDown[args[0]] = 1
    def keyReleased(self,*args):
        self.keysDown[args[0]] = 0
    def mouseHandler(self, *args):
        if self.mouseCatched:
            self.mouseX += args[0]-self.windowSize[0]/2
            self.mouseY += args[1]-self.windowSize[1]/2
            glutWarpPointer(int(self.windowSize[0]/2), int(self.windowSize[1]/2))
    def mouseClicked(self,*args):
        b = self.bulletModelPrefab.Clone()
        b.vx = math.sin(-self.xAng)
        b.vz = math.cos(self.xAng)
        b.vy = math.sin(self.yAng)
        b.SetRotation(np.array([self.yAng,self.xAng,0]))
        b.SetPosition(np.array(self.camPosition)*-1+np.array([0,-0.3,0]))
        self.bulletModels.append(b)
    def showScreen(self):
        
        now = time.perf_counter()
        for x in range(len(self.fpsCounter)-1,0,-1):
            if self.fpsCounter[x]<now-1:
                self.fpsCounter.remove(self.fpsCounter[x])
        if len(self.fpsCounter)>0:
            self.deltaTime = now-self.fpsCounter[-1]
        self.fpsCounter.append(now)

        glutSetWindowTitle("FPS: "+str(len(self.fpsCounter))+" delta: "+str(self.deltaTime)+" bullets: "+str(len(self.bulletModels)))
        self.renderer.Clear()
        self.shader.Bind()
        
        self.a += 0.001
        self.scale = 100

        self.xAng = self.mouseX/400*1.57-1.57
        self.yAng = self.mouseY/300*1.57-1.57
        
        self.camSpeed = 5

        if self.keysDown[b'a']:
            self.camPosition[0] += self.camSpeed*math.cos(-self.xAng)*self.deltaTime
            self.camPosition[2] -= self.camSpeed*math.sin(-self.xAng)*self.deltaTime
        if self.keysDown[b'd']:
            self.camPosition[0] -= self.camSpeed*math.cos(-self.xAng)*self.deltaTime
            self.camPosition[2] += self.camSpeed*math.sin(-self.xAng)*self.deltaTime
        if self.keysDown[b'w']:
            self.camPosition[2] += self.camSpeed*math.cos(-self.xAng)*self.deltaTime
            self.camPosition[0] += self.camSpeed*math.sin(-self.xAng)*self.deltaTime
        if self.keysDown[b's']:
            self.camPosition[2] -= self.camSpeed*math.cos(-self.xAng)*self.deltaTime
            self.camPosition[0] -= self.camSpeed*math.sin(-self.xAng)*self.deltaTime

            
        rotz = pyrr.matrix44.create_from_z_rotation(self.yAng*math.sin(self.xAng))
        rotx = pyrr.matrix44.create_from_x_rotation(self.yAng*math.cos(self.xAng))
        rot = np.matmul(np.matmul(pyrr.matrix44.create_from_y_rotation(self.xAng),rotz),rotx)
        

        self.camModel = np.matmul(rot,np.transpose(pyrr.matrix44.create_from_translation(np.array(self.camPosition))))
        

        

        for b in self.bulletModels:
            b.SetScale(0.1)
            p = b.pos
            if p[2]<-10 or p[2]>10 or p[0]<-10 or p[0]>10:
                self.bulletModels.remove(b)
                continue
            b.SetPosition(np.array([b.pos[0]-10*b.vx*self.deltaTime,b.pos[1]-10*b.vy*self.deltaTime,b.pos[2]-10*b.vz*self.deltaTime]))
            b.DrawWithShader(self.shader,self.renderer,np.matmul(self.proj,self.camModel))

        i=0
        for pId in self.netClient.players:
            if pId == self.connId:
                continue
            self.models[i].SetPosition(np.array(self.netClient.players[pId]['pos']))
            self.models[i].SetRotation(np.array(self.netClient.players[pId]['rot']))
            self.models[i].DrawWithShader(self.shader,self.renderer,np.matmul(self.proj,self.camModel))
            i+=1
        #for i in range(self.n):
        #    self.models[i].SetPosition(np.array([-self.n*1.4/2+i*1.2,math.sin((self.a+i)*5)/3-0.5,-2]))
        #    self.models[i].DrawWithShader(self.shader,self.renderer,np.matmul(self.proj,self.camModel))
        
        self.tp.SetPosition(np.array([0,-1,-2]))
        self.tp.SetRotation(np.array([1.57,0,0]))
        self.tp.DrawWithShader(self.shader,self.renderer,np.matmul(self.proj,self.camModel))
        """
        #self.tp2.SetPosition(np.array([0,math.sin(self.a+math.pi),math.cos(self.a+math.pi)]))
        #self.tp2.DrawWithShader(self.shader,self.renderer,self.proj)
        """
        glutSwapBuffers()
        self.netClient.SendData([np.multiply(self.camPosition,-1),[0,self.xAng+1.57,0]])
        self.netClient.Loop()
g = Game()
print("f")
