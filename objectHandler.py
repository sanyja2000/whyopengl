import numpy as np
from objloader import processObjFile
from renderer import *
import pyrr

class Object3D:
    def __init__(self,filename,texture="res/Gun.png",textureRepeat=False):
        self.points, self.indices = np.array([]),np.array([])
        if filename != None:
            self.filePath = filename
            self.points, self.indices = processObjFile(self.filePath)
            self.va = VertexArray()
            self.vb = VertexBuffer(self.points)
            self.layout = VertexBufferLayout()
            self.layout.PushF(3)
            self.layout.PushF(2)
            self.layout.PushF(3)
            self.va.AddBuffer(self.vb, self.layout)
            self.ib = IndexBuffer(self.indices, len(self.indices))
            self.texture = Texture(texture,repeat=textureRepeat)
        
        self.pos = np.array([0,0,0])
        self.rot = np.array([0,0,0])
        self.scale = 1
        self.GenerateModelMatrix()
    def DrawWithShader(self,shader,renderer,viewMat,options={}):
        shader.Bind()
        self.texture.Bind()
        shader.SetUniform1i("u_Texture",0)
        for key in options:
            shader.SetUniform1f(key,options[key])
        mvp = np.transpose(np.matmul(viewMat,self.modelMat))        
        shader.SetUniformMat4f("u_MVP", mvp)
        renderer.Draw(self.va,self.ib,shader)
    def GenerateModelMatrix(self):
        rxyz = np.matmul(np.matmul(pyrr.matrix44.create_from_x_rotation(self.rot[0]),pyrr.matrix44.create_from_y_rotation(self.rot[1])),pyrr.matrix44.create_from_z_rotation(self.rot[2]))
        scl = pyrr.matrix44.create_from_scale(np.array([self.scale,self.scale,self.scale]))
        self.modelMat = np.transpose(np.matmul(np.matmul(scl,rxyz),pyrr.matrix44.create_from_translation(np.array(self.pos))))
    def SetPosition(self,vec):
        self.pos = vec
        self.GenerateModelMatrix()
    def SetRotation(self,vec):
        self.rot = vec
        self.GenerateModelMatrix()
    def SetScale(self,scl):
        self.scale=scl
        self.GenerateModelMatrix()
    def Clone(self):
        o = Object3D(None)
        o.va = self.va
        o.ib = self.ib
        o.points = self.points
        o.texture = self.texture
        return o
    def DistanceTo(self,vec):
        d = (vec[0]-self.pos[0])**2+(vec[1]-self.pos[1])**2+(vec[2]-self.pos[2])**2
        return d**0.5
