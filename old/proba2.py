from OpenGL.GL import *
from OpenGL.GL import shaders
from OpenGL.GLUT import *
from OpenGL.GLU import *
from ctypes import c_void_p, pointer, sizeof, c_float
import numpy as np



vshader = """#version 330 core
layout(location=0) in vec4 position;
void main()
{
    gl_Position = position;
}"""


fshader = """#version 330 core
layout(location=0) out vec4 color;
uniform vec4 u_Color;
void main(){
    color = u_Color;
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
        
        glutInitWindowSize(800, 600)
        glutInitWindowPosition(0, 0)
        wind = glutCreateWindow("OpenGL Coding Practice")
        glutDisplayFunc(self.showScreen)
        glutIdleFunc(self.showScreen)
        glutKeyboardFunc(self.keyPressed)


        #gluPerspective(45, 600/800, 0.1, 50.0)

        GLClearError()

        print(glGetString(GL_SHADING_LANGUAGE_VERSION))

        glClearColor(0.3,0.3,0.3,1.0)

        self.vertexShader = shaders.compileShader(vshader,GL_VERTEX_SHADER)
        self.fragmentShader = shaders.compileShader(fshader,GL_FRAGMENT_SHADER)
        self.shader = shaders.compileProgram(self.vertexShader,self.fragmentShader)

        print("Error: ")
        print(glGetProgramInfoLog(self.shader))

        self.points = np.array([-0.5, -0.5, 0.0,
                                0.5, -0.5, 0.0,
                                0.5, 0.5, 0.0,
                                -0.5, 0.5, 0.0],dtype='float32')

        self.indices = np.array([0,1,2, 2,3,0])

        self.buffer = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.buffer)
        glBufferData(GL_ARRAY_BUFFER, self.points, GL_STATIC_DRAW)


        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 3*sizeof(c_float), None)

        self.ibo = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ibo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.indices, GL_STATIC_DRAW)

        shaders.glUseProgram(self.shader)

        location = glGetUniformLocation(self.shader, "u_Color")
        if(location == -1):
            print("UniformLocationNotFound")
        glUniform4f(location,0.8,0.3,0.8,1.0)
        

        glBindVertexArray(0)

        #glBindBuffer(GL_ARRAY_BUFFER, 0)
        
        #glTranslatef(0.0,0.0,-5)
        #glRotatef(0,0,0,0)

        self.r = 0.5
        
        glutMainLoop()

    def errorMsg(self, *args):
        print(args)
        return 0
    
    def keyPressed(self,*args):
        pass
    
    def showScreen(self):
        glRotatef(0.1,0.3,0.1,0.1)
        glClear(GL_COLOR_BUFFER_BIT)

        self.r = (self.r+0.05)%1

        location = glGetUniformLocation(self.shader, "u_Color")
        if(location == -1):
            print("UniformLocationNotFound")
        glUniform4f(location,self.r,0.3,0.8,1.0)
        
        glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)
        GLCheckError()
        #glRotatef(0,0,0,0)
        glutSwapBuffers()
    
    def plane(self):
        """
        glBegin(GL_QUADS)
        glVertex3fv((0,0,0))
        glVertex3fv((0,2,0))
        glVertex3fv((1,1,0))
        glVertex3fv((1,0,0))
        glEnd()
        """
        pass
        


if __name__ == '__main__':
    g = Game()
