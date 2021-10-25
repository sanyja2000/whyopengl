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
import pyrr

vshader = """
#version 330 core
in vec3 position;
in vec2 texCoord;
in vec3 normals;
out vec2 v_TexCoord;
out vec3 v_normals;

uniform mat4 u_MVP;
void main()
{
    gl_Position = u_MVP * vec4(position,1.0) ;
    v_TexCoord = texCoord;
}"""



fshader = """
#version 330 core
layout(location=0) out vec4 color;

in vec2 v_TexCoord;

uniform sampler2D u_Texture;

void main(){
    vec4 texColor = texture(u_Texture, v_TexCoord);
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
        
        #gluPerspective(45, 600/800, 0.1, 50.0)

        GLClearError()

        print(glGetString(GL_SHADING_LANGUAGE_VERSION))

        glClearColor(0.3,0.3,0.3,1.0)


        self.shader = Shader(vshader, fshader)

        """
        self.points = np.array([-0.5, -0.5, 0.0, 0.0,
                                0.5, -0.5, 1.0, 0.0,
                                0.5, 0.5, 1.0, 1.0,
                                -0.5, 0.5, 0.0, 1.0],dtype='float32')

        self.indices = np.array([0,1,2, 2,3,0])
        """
        self.points, self.indices = processObjFile("res/GunTri.obj")

        self.va = VertexArray()
        self.vb = VertexBuffer(self.points)
        self.layout = VertexBufferLayout()
        self.layout.PushF(3)
        self.layout.PushF(2)
        self.layout.PushF(3)
        self.va.AddBuffer(self.vb, self.layout)


        self.ib = IndexBuffer(self.indices, len(self.indices))

        self.shader.Bind()

        self.texture = Texture("res/Gun.png")
        self.texture.Bind()
        self.shader.SetUniform1i("u_Texture",0)

        
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

        self.va.UnBind()
        self.vb.UnBind()
        self.ib.UnBind()
        self.shader.UnBind()
        
        glBindBuffer(GL_ARRAY_BUFFER,0)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER,0)
        glBindVertexArray(0)

        #self.tp2 = TexturePlane("res/cat2.png")
        self.tp = TexturePlane("res/Pebbles.png")

        self.x = 0
        self.vx = 0
        self.direction = 0
        self.a = 0
        self.renderer = Renderer()
        
        glutMainLoop()
    def errorMsg(self, *args):
        print(args)
        return 0
    def keyPressed(self,*args):
        print(self.xAng)
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
        self.keysDown[args[0]] = 1
    def keyReleased(self,*args):
        self.keysDown[args[0]] = 0
    def mouseHandler(self, *args):
        self.mouseX += args[0]-400
        self.mouseY += args[1]-300
        glutWarpPointer(400, 300);
    def showScreen(self):
        #

        self.renderer.Clear()
        self.shader.Bind()
        self.texture.Bind()
        self.a += 0.001
        self.scale = 100

        self.xAng = self.mouseX/400*1.57-1.57

        if self.keysDown[b'a']:
            self.camPosition[0] += 0.01*math.cos(-self.xAng)
            self.camPosition[2] -= 0.01*math.sin(-self.xAng)
        if self.keysDown[b'd']:
            self.camPosition[0] -= 0.01*math.cos(-self.xAng)
            self.camPosition[2] += 0.01*math.sin(-self.xAng)
        if self.keysDown[b'w']:
            self.camPosition[2] += 0.01*math.cos(-self.xAng)
            self.camPosition[0] += 0.01*math.sin(-self.xAng)
        if self.keysDown[b's']:
            self.camPosition[2] -= 0.01*math.cos(-self.xAng)
            self.camPosition[0] -= 0.01*math.sin(-self.xAng)
        ##self.shader.SetUniform3f("u_MouseTime",self.mouseX,self.mouseY,time.perf_counter())
        #self.mvp = self.proj
        #self.easy = pyrr.matrix44.create_from_translation(np.array([0,0,1.5]))
        #self.easy = np.matmul(pyrr.matrix44.create_from_y_rotation(self.mouseX/100), self.easy)
        #self.mvp = np.matmul(self.proj,self.easy)#,pyrr.matrix44.create_from_z_rotation(self.a/2))
        #self.mvp = np.transpose(self.mvp)
        self.rot = np.array([self.mouseX/300*3.14,0,0])
        self.pos = np.array([0,0,-3])
        #rxyz = np.matmul(np.matmul(pyrr.matrix44.create_from_x_rotation(self.rot[0]),pyrr.matrix44.create_from_y_rotation(self.rot[1])),pyrr.matrix44.create_from_z_rotation(self.rot[2]))
        #self.modelMat = np.matmul(pyrr.matrix44.create_from_x_rotation(self.rot[0]),pyrr.matrix44.create_from_translation(self.pos))
        #self.modelMat = np.matmul(pyrr.matrix44.create_from_translation(self.pos),pyrr.matrix44.create_from_x_rotation(self.rot[0]))
        rotx = pyrr.matrix44.create_from_z_rotation((-self.mouseY/300*1.57+1.57))
        #rotxz = np.matmul(pyrr.matrix44.create_from_x_rotation((self.mouseY/300*1.57-1.57)*math.cos(self.xAng)),pyrr.matrix44.create_from_z_rotation((self.mouseY/300*1.57-1.57)*math.sin(self.xAng)))
        rot = pyrr.matrix44.create_from_y_rotation(self.xAng)
        self.camModel = np.matmul(rot,np.transpose(pyrr.matrix44.create_from_translation(np.array(self.camPosition))))
        
        #self.viewMat = np.linalg.inv(self.camModel)
        #self.viewMat = pyrr.matrix44.create_look_at(np.array([0,0,3]),np.array([0,0,0]),np.array([0,1,0]))
        #mvp = np.transpose(np.matmul(self.modelMat,np.matmul(self.viewMat,self.proj)))
        #mvp = np.transpose(self.proj * self.viewMat * self.modelMat)
        #mvp = np.transpose(np.matmul(self.proj,np.matmul(self.viewMat,self.modelMat)))    

        #mvp = np.transpose(np.matmul(self.proj,self.modelMat))
        self.move = np.matmul(np.transpose(pyrr.matrix44.create_from_translation(np.array([0,math.sin(self.a)/3,-2]))),pyrr.matrix44.create_from_y_rotation(0))
        #self.mvp = np.matmul(self.proj,self.move)#,pyrr.matrix44.create_from_z_rotation(self.a/2))
        self.mvp = np.matmul(self.proj,np.matmul(self.camModel,self.move))
        self.mvp = np.transpose(self.mvp)


        self.shader.SetUniformMat4f("u_MVP", self.mvp)

        self.renderer.Draw(self.va,self.ib,self.shader)
        
        
        
        self.tp.SetPosition(np.array([0,-1,-2]))
        self.tp.SetRotation(np.array([1.57,0,0]))
        self.tp.DrawWithShader(self.shader,self.renderer,np.matmul(self.proj,self.camModel))
        """
        #self.tp2.SetPosition(np.array([0,math.sin(self.a+math.pi),math.cos(self.a+math.pi)]))
        #self.tp2.DrawWithShader(self.shader,self.renderer,self.proj)
        """
        glutSwapBuffers()
    def plane(self):
        pass
g = Game()
print("f")
