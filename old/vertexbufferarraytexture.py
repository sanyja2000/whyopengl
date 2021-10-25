from OpenGL.GL import *
from OpenGL.GL import shaders
from OpenGL.GLUT import *
from OpenGL.GLU import *
from ctypes import c_void_p, pointer, sizeof, c_float
import numpy as np
import sys
import time, math
from renderer import VertexBuffer, IndexBuffer, VertexArray, VertexBufferLayout, Shader, Renderer, Texture, Camera
import pyrr

vshader = """
#version 330 core
in vec3 position;
in vec2 texCoord;
out vec2 v_TexCoord;
uniform mat4 u_MVP;
void main()
{
    gl_Position = u_MVP * vec4(position,1.0);
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
        glutInitContextVersion (3, 3)
        #glutInitContextProfile (GLUT_COMPATIBILITY_PROFILE)
        glutInitWindowSize(800, 600)
        glutInitWindowPosition(0, 0)
        self.window = glutCreateWindow("OpenGL Coding Practice")
        glutDisplayFunc(self.showScreen)
        glutIdleFunc(self.showScreen)
        glutKeyboardFunc(self.keyPressed)
        glutMouseFunc(self.mousePressed)
        glutPassiveMotionFunc(self.mouseHandler)
        self.mouseX = 0.0
        self.mouseY = 0.0
        
        #gluPerspective(45, 600/800, 0.1, 50.0)

        GLClearError()

        print(glGetString(GL_SHADING_LANGUAGE_VERSION))

        glClearColor(0.3,0.3,0.3,1.0)


        self.shader = Shader(vshader, fshader)


        self.points = np.array([-0.5, -0.5, 0.0,0.0, 0.0,
                                0.5, -0.5, 0.0,1.0, 0.0,
                                0.5, 0.5, 0.0,1.0, 1.0,
                                -0.5, 0.5, 0.0,0.0, 1.0],dtype='float32')

        self.indices = np.array([0,1,2, 2,3,0])


        self.va = VertexArray()
        self.vb = VertexBuffer(self.points)
        self.layout = VertexBufferLayout()
        self.layout.PushF(3)
        self.layout.PushF(2)
        self.va.AddBuffer(self.vb, self.layout)


        self.ib = IndexBuffer(self.indices, 6)

        self.shader.Bind()

        self.texture = Texture("res/Question_Block_small.png")
        self.texture.Bind()
        self.shader.SetUniform1i("u_Texture",0)

        
        self.camera = Camera()
        #self.proj = self.camera.Perspective(-2,2,-1.5,1.5,-1,1)
        #self.proj = np.matrix([[1,0,0,0],[0,1,0,0],[0,0,0,0],[0,0,0,1]])
        self.proj = pyrr.matrix44.create_perspective_projection(90.0, 800/600, 1.0, 10.0)
        #self.proj = pyrr.matrix44.create_orthogonal_projection(-2, 2, -1.5, 1.5, -1, 1)


        print("Error: ")
        print(glGetProgramInfoLog(self.shader.RendererId))


        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        self.va.UnBind()
        self.vb.UnBind()
        self.ib.UnBind()
        self.shader.UnBind()
        
        glBindBuffer(GL_ARRAY_BUFFER,0)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER,0)
        glBindVertexArray(0)

        self.a = 0
        self.renderer = Renderer()
        
        glutMainLoop()
    def errorMsg(self, *args):
        print(args)
        return 0
    def keyPressed(self,*args):
        print(args)
        if(args[0]==b'\x1b'):
            glutLeaveMainLoop()
            glutDestroyWindow(self.window)
            sys.quit()
    def mouseHandler(self, *args):
        self.mouseX = args[0]
        self.mouseY = 600-args[1]
    def mousePressed(self, *args):
        pass
    def showScreen(self):
        self.renderer.Clear()
        self.a += 0.001
        self.shader.Bind()

        self.move = np.matmul(np.transpose(pyrr.matrix44.create_from_translation(np.array([self.mouseX/200-2,self.mouseY/200-1.5,-2]))),pyrr.matrix44.create_from_y_rotation(self.a))
        #self.shader.SetUniform3f("u_MouseTime",self.mouseX,self.mouseY,time.perf_counter())

        self.mvp = np.matmul(self.proj,self.move)#,pyrr.matrix44.create_from_z_rotation(self.a/2))
        self.mvp = np.transpose(self.mvp)
        self.shader.SetUniformMat4f("u_MVP", self.mvp)

        self.renderer.Draw(self.va,self.ib,self.shader)
        
        
        glutSwapBuffers()
    def plane(self):
        pass
g = Game()
print("f")
