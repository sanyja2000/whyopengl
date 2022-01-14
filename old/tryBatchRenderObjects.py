from OpenGL.GL import *
from OpenGL.GL import shaders
from OpenGL.GLUT import *
from OpenGL.GLU import *
from ctypes import c_void_p, pointer, sizeof, c_float
import numpy as np
import sys, math
import time
from engine.renderer import VertexBuffer, IndexBuffer, VertexArray, VertexBufferLayout, Shader, Renderer, Texture, Camera
from plane import *
from engine.objloader import processObjFile
from engine.objectHandler import Object3D
import pyrr
import random
from batchRenderer import BatchRenderer

vshader = """
#version 330 core
in vec3 position;
in vec2 texCoord;
in vec3 normals;
in float texIndex;

uniform mat4 u_MVP;

out vec2 v_TexCoord;
out float v_TexIndex;

void main()
{
    gl_Position = u_MVP * vec4(position,1.0) ;
    v_TexCoord = texCoord;
    v_TexIndex = texIndex;
}"""



fshader = """
#version 330 core
layout(location=0) out vec4 color;

in vec2 v_TexCoord;
in float v_TexIndex;

uniform sampler2D u_Textures[32];

void main(){
    int index = int(v_TexIndex);
    vec4 texColor = texture(u_Textures[index], v_TexCoord);
    color = texColor;
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
        glutInit()
        glutInitDisplayMode(GLUT_RGBA)
        glutInitContextVersion (2, 1)
        glutInitContextProfile (GLUT_COMPATIBILITY_PROFILE)
        self.windowSize = [800,600]
        glutInitWindowSize(self.windowSize[0], self.windowSize[1])
        glutInitWindowPosition(0, 0)
        self.window = glutCreateWindow("OpenGL Coding Practice")
        glutDisplayFunc(self.showScreen)
        glutIdleFunc(self.showScreen)
        glutKeyboardFunc(self.keyPressed)
        glutKeyboardUpFunc(self.keyReleased)
        #glutMouseFunc(self.mouseHandler)
        glutPassiveMotionFunc(self.mouseHandler)
        self.mouseX = 0.0
        self.mouseY = 0.0
        
        GLClearError()

        print(glGetString(GL_SHADING_LANGUAGE_VERSION))

        glClearColor(0.3,0.3,0.3,1.0)


        self.shader = Shader(vshader, fshader)

        self.models = []

        # 20 guns, ~ 140-160 fps without batch
        
        self.n = 1
        for i in range(self.n):
            #self.models.append(Object3D("res/bullet1.obj","res/bullet1.png"))
            self.models.append(Object3D("res/GunTri.obj","res/Gun.png").Clone())
        
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

        self.shader.Bind()
        self.shader.SetUniform1iv("u_Textures", np.array(range(8)))
        #self.shader.SetUniform1i("u_Texture",0)
        self.batchRenderer = BatchRenderer()
        

        
        self.camPosition = [0,0,-1]

        self.keysDown = {b'a':0,b's':0,b'd':0,b'w':0}

        self.measuredTime = 0
        self.measuredTimeStart = 0
        

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
    def showScreen(self):
        now = time.perf_counter()
        for x in range(len(self.fpsCounter)-1,0,-1):
            if self.fpsCounter[x]<now-1:
                self.fpsCounter.remove(self.fpsCounter[x])
        if len(self.fpsCounter)>0:
            self.deltaTime = now-self.fpsCounter[-1]
        self.fpsCounter.append(now)

        
        glutSetWindowTitle("FPS: "+str(len(self.fpsCounter))+" delta: "+str(self.deltaTime)+" measuredTime: "+str(self.measuredTime))


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
        

       
        
        #rotx = pyrr.matrix44.create_from_z_rotation((-self.mouseY/300*1.57+1.57))
        #rot = pyrr.matrix44.create_from_y_rotation(self.xAng)
        rotz = pyrr.matrix44.create_from_z_rotation(self.yAng*math.sin(self.xAng))
        rotx = pyrr.matrix44.create_from_x_rotation(self.yAng*math.cos(self.xAng))
        rot = np.matmul(np.matmul(pyrr.matrix44.create_from_y_rotation(self.xAng),rotz),rotx)
        
        self.camModel = np.matmul(rot,np.transpose(pyrr.matrix44.create_from_translation(np.array(self.camPosition))))

        
        
        self.renderer.Clear()
        
        self.shader.Bind()

        
        
        self.batchRenderer.BeginBatch()

        start = time.perf_counter()
        
        for i in range(self.n):
            self.models[i].SetPosition(np.array([-self.n*1.4/2+i*1.2,math.sin(self.a+i)/3,-2]))
            #self.models[i].DrawWithShader(self.shader,self.renderer,np.matmul(self.proj,self.camModel))
            self.batchRenderer.DrawObjectWithTexture(self.models[i])        
        
        
        #self.models[0].SetPosition(np.array([-self.n*1.4/2+0*1.2,math.sin(self.a+0)/3,-2]))
        self.shader.SetUniformMat4f("u_MVP", np.transpose(np.matmul(np.matmul(self.proj,self.camModel),self.models[0].modelMat)))

        self.measuredTime = time.perf_counter()-start
        
        #self.batchRenderer.DrawObjectWithTexture(self.models[0])

        

        self.batchRenderer.EndBatch()
        
        self.batchRenderer.Flush()

        


        #GLClearError()
        #print(glGetProgramInfoLog(self.shader.RendererId))
        
        
        self.tp.SetPosition(np.array([0,-1,-2]))
        self.tp.SetRotation(np.array([1.57,0,0]))
        self.tp.DrawWithShader(self.shader,self.renderer,np.matmul(self.proj,self.camModel))

        
        glutSwapBuffers()
g = Game()
print("f")
