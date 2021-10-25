from objectHandler import Object3D
import numpy as np
import time

class prefabHandler:
    def __init__(self):
        self.loadedFiles = []
        self.loadedObjects = []
        self.emptyObj = Object3D(None,texture="res/1px.png")
    def loadFile(self,_filename,_texture,textureRepeat=False):
        if _filename in self.loadedFiles:
            index = self.loadedFiles.index(_filename)
            return self.loadedObjects[index].Clone()
        o = Object3D(_filename,texture=_texture,textureRepeat=textureRepeat)
        self.loadedFiles.append(_filename)
        self.loadedObjects.append(o)
        return o
    def empty(self):
        return self.emptyObj.Clone()

class BaseObject:
    def __init__(self):
        self.model = None
        

class Map:
    def __init__(self,ph,objFile,texture):
        self.objFile = objFile
        self.model = ph.loadFile(objFile,texture,textureRepeat=True)
        self.model.SetScale(10)
    def draw(self,shaderhandler,renderer,viewMat):
        self.model.DrawWithShader(shaderhandler.getShader("map"),renderer,viewMat)

class Noteblock13:
    def __init__(self,ph,name,note,pos, rot,scale):
        self.model = ph.loadFile("res/noteblock1.obj","res/noteblock.png")
        self.model.SetScale(scale)
        self.model.SetPosition(np.array(pos))
        self.model.SetRotation(np.array(rot))
        self.note = note
        self.lastPlayed = 0
       
    def draw(self,shaderhandler,renderer,viewMat):
        self.model.DrawWithShader(shaderhandler.getShader("noteblock"),renderer,viewMat,options={"u_Time":time.perf_counter(),"u_LastPlayed":self.lastPlayed})

class Door:
    def __init__(self,ph,pos,rot,scale):
        pass