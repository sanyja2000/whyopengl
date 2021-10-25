from OpenGL.GL import *
from OpenGL.GL import shaders
from OpenGL.GLUT import *
from OpenGL.GLU import *
from ctypes import c_void_p, pointer, sizeof, c_float
import numpy as np
import sys
import time
from renderer import VertexBuffer, IndexBuffer, VertexArray, VertexBufferLayout, Shader, Renderer

vshader = """
#version 330 core
in vec4 position;
void main()
{
    gl_Position = position;
}"""



fshader = """
#version 330 core
layout(location=0) out vec4 color;
uniform vec3 u_MouseTime;
void main(){
    float d = distance(gl_FragCoord.xy, vec2(u_MouseTime[0],u_MouseTime[1]));
    if(d<40.0+sin(u_MouseTime[2])*10){
        color = vec4((gl_FragCoord.x-200)/400.0,(gl_FragCoord.y-150)/300.0,0.2,1.0);
    }else{
        color = vec4((gl_FragCoord.x-200)/600.0,(gl_FragCoord.y-150)/500.0,0.1,1.0);
    }
}"""



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
        glutInitContextProfile (GLUT_COMPATIBILITY_PROFILE)
        glutInitWindowSize(800, 600)
        glutInitWindowPosition(0, 0)
        self.window = glutCreateWindow("OpenGL Coding Practice")
        glutDisplayFunc(self.showScreen)
        glutIdleFunc(self.showScreen)
        glutKeyboardFunc(self.keyPressed)
        #glutMouseFunc(self.mouseHandler)
        glutPassiveMotionFunc(self.mouseHandler)
        self.mouseX = 0.0
        self.mouseY = 0.0
        
        #gluPerspective(45, 600/800, 0.1, 50.0)

        GLClearError()

        print(glGetString(GL_SHADING_LANGUAGE_VERSION))

        glClearColor(0.3,0.3,0.3,1.0)


        self.shader = Shader(vshader, fshader)

        print("Error: ")
        print(glGetProgramInfoLog(self.shader.RendererId))

        self.points = np.array([-0.5, -0.5, 0.0,
                                0.5, -0.5, 0.0,
                                0.5, 0.5, 0.0,
                                -0.5, 0.5, 0.0],dtype='float32')

        self.indices = np.array([0,1,2, 2,3,0])


        self.va = VertexArray()
        self.vb = VertexBuffer(self.points)
        self.layout = VertexBufferLayout()
        self.layout.PushF(3)
        self.va.AddBuffer(self.vb, self.layout)


        self.ib = IndexBuffer(self.indices, 6)

        self.shader.Bind()



        self.va.UnBind()
        self.vb.UnBind()
        self.ib.UnBind()
        self.shader.UnBind()
        
        glBindBuffer(GL_ARRAY_BUFFER,0)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER,0)
        glBindVertexArray(0)


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
    def showScreen(self):
        self.renderer.Clear()

        self.shader.Bind()
        self.shader.SetUniform3f("u_MouseTime",self.mouseX,self.mouseY,time.perf_counter())

        self.renderer.Draw(self.va,self.ib,self.shader)
        
        
        glutSwapBuffers()
    def plane(self):
        pass
g = Game()
print("f")
