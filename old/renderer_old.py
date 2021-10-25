from OpenGL.GL import *
from OpenGL.GL import shaders
from OpenGL.GLUT import *
from OpenGL.GLU import *
from ctypes import c_void_p, pointer, sizeof, c_float, c_uint
import numpy as np
from PIL import Image

def GetSizeOfType(t):
    if t == GL_FLOAT:
        return 4
    if t == GL_UNSIGNED_INT:
        return 4
    return 1


class VertexBuffer:
    def __init__(self, data):
        self.RendererId = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.RendererId)
        glBufferData(GL_ARRAY_BUFFER, data, GL_STATIC_DRAW)
    def Bind(self):
        glBindBuffer(GL_ARRAY_BUFFER, self.RendererId)
    def UnBind(self):
        glBindBuffer(GL_ARRAY_BUFFER, 0)


class IndexBuffer:
    def __init__(self, data, count):
        self.RendererId = glGenBuffers(1)
        self.Count = count
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.RendererId)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, data, GL_STATIC_DRAW)
    def Bind(self):
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.RendererId)
    def UnBind(self):
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

class VertexArray:
    def __init__(self):
        self.RendererId = glGenVertexArrays(1)
    def AddBuffer(self,vb, layout):
        self.Bind()
        vb.Bind()
        elements = layout.Elements
        offset = 0
        for i in range(len(elements)):
            element = elements[i]
            glEnableVertexAttribArray(i)
            glVertexAttribPointer(i, element[1], element[0], element[2], layout.Stride, c_void_p(offset)) # WTF?!? 'None' should be 'offset'
            offset += element[1]*GetSizeOfType(element[0])
            
    def Bind(self):
        glBindVertexArray(self.RendererId)
    def UnBind(self):
        glBindVertexArray(0)
    
class VertexBufferLayout:
    def __init__(self):
        self.Elements = []
        self.Stride = 0
    def PushF(self, count):
        # type, size, normalized
        self.Elements.append((GL_FLOAT, count, GL_FALSE))
        self.Stride += count * sizeof(c_float)
    def PushI(self, count):
        # type, size, normalized
        self.Elements.append((GL_UNSIGNED_INT, count, GL_FALSE))
        self.Stride += count * GetSizeOfType(GL_UNSIGNED_INT)
            
class Shader:
    def __init__(self, vertexsrc, fragmentsrc):
        self.VertexSrc = vertexsrc
        self.FragmentSrc = fragmentsrc
        self.VertexShader = shaders.compileShader(self.VertexSrc,GL_VERTEX_SHADER)
        self.FragmentShader = shaders.compileShader(self.FragmentSrc,GL_FRAGMENT_SHADER)
        self.RendererId = shaders.compileProgram(self.VertexShader,self.FragmentShader)
        self.LocationCache = {}
        
    def SetUniform4f(self,name,v0,v1,v2,v3):
        glUniform4f(self.GetUniformLocation(name),v0,v1,v2,v3)
        
    def SetUniform3f(self,name,v0,v1,v2):
        glUniform3f(self.GetUniformLocation(name),v0,v1,v2)

    def SetUniform1i(self,name,v0):
        glUniform1i(self.GetUniformLocation(name),v0)

    def SetUniformMat4f(self,name, mat):
        glUniformMatrix4fv(self.GetUniformLocation(name), 1, GL_FALSE, mat)
    
    def Bind(self):
        shaders.glUseProgram(self.RendererId)

    def UnBind(self):
        shaders.glUseProgram(0)

    def GetUniformLocation(self,name):
        if name in self.LocationCache:
            return self.LocationCache[name]
        else:
            location = glGetUniformLocation(self.RendererId, name)
            if location == -1:
                print("Warning: uniform location doesn't exist")
            self.LocationCache[name] = location
            return location    

class Texture:
    def __init__(self,file):
        self.FilePath = file
        self.BPP = 0
        self.LocalBuffer = ""

        self.im = Image.open(self.FilePath)
        
        self.Width, self.Height = self.im.size

        #out = im.transpose(Image.FLIP_TOP_BOTTOM)
        
        self.RendererId = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D,self.RendererId)
        self.LocalBuffer = self.im.tobytes("raw", "RGBA", 0, -1)
        
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER,GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER,GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S,GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T,GL_CLAMP_TO_EDGE)

        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.Width, self.Height, 0, GL_RGBA, GL_UNSIGNED_BYTE, self.LocalBuffer)
        glBindTexture(GL_TEXTURE_2D, 0)
    def Bind(self,slot=0):
        glActiveTexture(GL_TEXTURE0+slot)
        glBindTexture(GL_TEXTURE_2D, self.RendererId)
    def UnBind(self):
        glBindTexture(GL_TEXTURE_2D, 0)


class Renderer:
    def __init__(self):
        pass
    def Clear(self):
        glClear(GL_COLOR_BUFFER_BIT)
    def Draw(self, vertarr, indbuf, shader):
        shader.Bind()
        vertarr.Bind()
        indbuf.Bind()
        glDrawElements(GL_TRIANGLES, indbuf.Count, GL_UNSIGNED_INT, None)
        
class Camera:
    def __init__(self):
        pass
    def Perspective(self, bottom, top, left, right, near, far):
        mat = np.matrix([[2*near/(right-left), 0, 0, 0],[0, 2*near/(top-bottom),0,0], [(right+left)/(right-left), (top+bottom)/(top-bottom), -1*(far+near)/(far-near), -1], [0,0,-1*(2*far*near)/(far-near),0]])
        #mat = np.matrix([[2*near/(right-left),0,0,0],[0,2*near/(top-bottom),0,0],[(right+left)/(right-left),(top+bottom)/(top-bottom),-1*(far+near)/(far-near),-1],[0,0,-1*(2*far*near)/(far-near),0]])
        return mat 
