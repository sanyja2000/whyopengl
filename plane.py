from renderer import *
import numpy as np
import pyrr

class TexturePlane:
    def __init__(self,filename):
        self.filename = filename
        self.texture = Texture(filename)
        self.pos = np.array([0,0,0])
        self.rot = np.array([0,0,0])
        self.scale = 15
        self.GenerateModelMatrix()
        self.points = np.array([-0.5, -0.5, 0.0, 0.0,
                                0.5, -0.5, 1.0, 0.0,
                                0.5, 0.5, 1.0, 1.0,
                                -0.5, 0.5, 0.0, 1.0],dtype='float32')
        
        self.indices = np.array([0,1,2, 2,3,0])
        self.va = VertexArray()
        self.vb = VertexBuffer(self.points)
        self.layout = VertexBufferLayout()
        self.layout.PushF(2)
        self.layout.PushF(2)
        self.va.AddBuffer(self.vb, self.layout)
        self.ib = IndexBuffer(self.indices, 6)
    def DrawWithShader(self,shader,renderer,proj):
        shader.Bind()
        self.texture.Bind()
        shader.SetUniform1i("u_Texture",0)
        mvp = np.transpose(np.matmul(proj,self.modelMat))        
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
        
    
