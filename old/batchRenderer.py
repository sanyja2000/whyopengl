from OpenGL.GL import *
from OpenGL.GL import shaders
from OpenGL.GLUT import *
from OpenGL.GLU import *
import numpy as np
from ctypes import c_void_p, sizeof, c_float, c_uint32, addressof
from PIL import Image
import time

def xmul(a, b):
     out = np.empty_like(a)
     for j in range(a.shape[0]):
         out[j] = np.dot(a[j], b[j])
     return out

def mymatmul(vec,mat):
    out = [mat[0][0]*vec[0]+mat[0][1]*vec[1]+mat[0][2]*vec[2]+mat[0][3],
           mat[1][0]*vec[0]+mat[1][1]*vec[1]+mat[1][2]*vec[2]+mat[1][3],
           mat[2][0]*vec[0]+mat[2][1]*vec[1]+mat[2][2]*vec[2]+mat[2][3],
           1]
    
    return out

class BatchRenderer:
    def __init__(self):
        # vertex buffer layout float9: vec3 pos, vec2 uv, vec3 norm, float texId
        self.maxVertexCount = 4000
        self.maxIndexCount = self.maxVertexCount
        self.vbMem = np.zeros((self.maxVertexCount*9), np.float32)#np.array([],dtype=np.float32)
        self.ibMem = np.array([])
        self.lastIndexNumber = 0

        self.testData = np.array([0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,
                                  10.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,
                                  10.0,10.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0
                                  ]
                                 ,dtype="float32")


        self.logged = False
        self.maxTextureSlots = 8
        self.textureSlots = {}#np.array([])
        self.textureSlotIndex = 1


        #glCreateVertexArrays(1,)
        self.va = glGenVertexArrays(1)
        glBindVertexArray(self.va)
        
        #self.vb = glCreateBuffers(1)
        self.vb = glGenBuffers(1)

        
        glBindBuffer(GL_ARRAY_BUFFER, self.vb)
        glBufferData(GL_ARRAY_BUFFER, self.maxVertexCount * 4 * 9, None, GL_DYNAMIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, sizeof(c_float)*9, c_void_p(0))

        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, sizeof(c_float)*9, c_void_p(sizeof(c_float)*3))

        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, sizeof(c_float)*9, c_void_p(sizeof(c_float)*5))

        glEnableVertexAttribArray(3)
        glVertexAttribPointer(3, 1, GL_FLOAT, GL_FALSE, sizeof(c_float)*9, c_void_p(sizeof(c_float)*8))
        """
        
        glBindBuffer(GL_ARRAY_BUFFER, self.vb)
        glBufferData(GL_ARRAY_BUFFER, self.maxVertexCount * 4 * 8, None, GL_DYNAMIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, sizeof(c_float)*8, c_void_p(0))

        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, sizeof(c_float)*8, c_void_p(sizeof(c_float)*3))

        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, sizeof(c_float)*8, c_void_p(sizeof(c_float)*5))
          """
        #generate IndexBuffer for triangles

        self.ibMem = np.array([range(self.maxVertexCount)])

        #self.ib = glCreateBuffers(1)
        self.ib = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER,self.ib)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER,self.ibMem, GL_STATIC_DRAW)

        #1x1 white texture
        #self.whiteTexture = np.array([])
        #glCreateTextures(GL_TEXTURE_2D,1,c_void_p(self.whiteTexture))
        self.whiteTexture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.whiteTexture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER,GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER,GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S,GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T,GL_CLAMP_TO_EDGE)
        #color = c_uint32(0xffffffff)
        whiteColorPixel = Image.open("res/1px.png").tobytes("raw", "RGB", 0, -1)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, 1,1,0,GL_RGBA,GL_UNSIGNED_BYTE,whiteColorPixel)
        self.textureSlots[0] = self.whiteTexture
        for i in range(1,self.maxTextureSlots):
            self.textureSlots[i] = 0
        
    def DrawObjectWithTexture(self,obj):
        if self.textureSlotIndex > self.maxTextureSlots-1 or self.lastIndexNumber+len(obj.points)/8>= self.maxIndexCount:
            #print("Need bigger batch size")
            self.EndBatch()
            self.Flush()
            self.BeginBatch()

        textureIndex = 0
        for i in range(len(self.textureSlots)):
            if obj.texture.RendererId == self.textureSlots[i]:
                textureIndex = 1
                break

        if textureIndex == 0:
            textureIndex = self.textureSlotIndex
            self.textureSlots[self.textureSlotIndex] = obj.texture.RendererId
            self.textureSlotIndex+=1

        for ind in range(0,len(obj.points),8):
            #transposed = np.matmul([obj.points[ind],obj.points[ind+1],obj.points[ind+2],1],obj.modelMat)
            #transposed = np.matmul(np.array([obj.points[ind],obj.points[ind+1],obj.points[ind+2],1],np.float32),obj.modelMat)
            #transposed = mymatmul([obj.points[ind],obj.points[ind+1],obj.points[ind+2],1],obj.modelMat)
            """
            self.vbMem[self.lastIndexNumber*9] = transposed[0]
            self.vbMem[self.lastIndexNumber*9+1] = transposed[1]
            self.vbMem[self.lastIndexNumber*9+2] = transposed[2]
            """
            self.vbMem[self.lastIndexNumber*9] = obj.points[ind+0]
            self.vbMem[self.lastIndexNumber*9+1] = obj.points[ind+1]
            self.vbMem[self.lastIndexNumber*9+2] = obj.points[ind+2]
            #"""
            self.vbMem[self.lastIndexNumber*9+3] = obj.points[ind+3]
            self.vbMem[self.lastIndexNumber*9+4] = obj.points[ind+4]
            self.vbMem[self.lastIndexNumber*9+5] = obj.points[ind+5]
            self.vbMem[self.lastIndexNumber*9+6] = obj.points[ind+6]
            self.vbMem[self.lastIndexNumber*9+7] = obj.points[ind+7]
            self.vbMem[self.lastIndexNumber*9+8] = textureIndex
            
            self.lastIndexNumber+=1
        
            
    def BeginBatch(self):
        #self.vbMem = np.array([],dtype='float32')
        #self.ibMem = np.array([])
        pass
    def EndBatch(self):
        #print(", ".join([str(round(i,1)) for i in self.vbMem]))#,self.lastIndexNumber)
        glBindBuffer(GL_ARRAY_BUFFER,self.vb)
        glBufferSubData(GL_ARRAY_BUFFER, 0,sizeof(c_float)*len(self.vbMem),self.vbMem)
    def Flush(self):
        
        for i in range(self.textureSlotIndex):
            glActiveTexture(GL_TEXTURE1+i)
            glBindTexture(GL_TEXTURE_2D, self.textureSlots[i])
            #glBindTextureUnit(i, self.textureSlots[i])
        
        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_2D, self.textureSlots[0])
        glBindVertexArray(self.va)
        glBindBuffer(GL_ARRAY_BUFFER, self.vb)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ib)
        #print("drawing",self.lastIndexNumber,"triangles")
        #print(sizeof(c_float)*len(self.vbMem))
        glDrawElements(GL_TRIANGLES, self.lastIndexNumber, GL_UNSIGNED_INT, None)

        self.lastIndexNumber = 0
        self.textureSlotIndex = 1
        #self.textureSlots = {}
    def ResetStats(self):
        pass
