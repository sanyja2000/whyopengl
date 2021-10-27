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
    def __init__(self,ph,props):
        self.objFile = props["file"]
        self.model = ph.loadFile(props["file"],props["texture"],textureRepeat=True)
        self.model.SetScale(10)
    def draw(self,shaderhandler,renderer,viewMat):
        self.model.DrawWithShader(shaderhandler.getShader("map"),renderer,viewMat)

class Noteblock13:
    def __init__(self,ph,props):
        self.model = ph.loadFile("res/noteblock1.obj","res/noteblock.png")
        self.model.SetScale(props["scale"])
        self.model.SetPosition(np.array(props["pos"]))
        self.model.SetRotation(np.array(props["rot"]))
        self.note = props["note"]
        self.lastPlayed = 0
       
    def draw(self,shaderhandler,renderer,viewMat):
        self.model.DrawWithShader(shaderhandler.getShader("noteblock"),renderer,viewMat,options={"u_Time":time.perf_counter(),"u_LastPlayed":self.lastPlayed})

class Door:
    def __init__(self,ph,props):
        #pos,rot,scale,puzzleId
        self.puzzleId = props["puzzleId"]
        self.open = False
        self.leftModel = ph.loadFile("res/doorleft.obj","res/wall_top.png",textureRepeat=True)
        self.leftModel.SetPosition(np.array(props["pos"])+np.array([0,0,0]))
        self.leftModel.SetRotation(np.array(props["rot"]))
        self.leftModel.SetScale(props["scale"])
        self.rightModel = ph.loadFile("res/doorright.obj","res/wall_top.png",textureRepeat=True)
        self.rightModel.SetPosition(np.array(props["pos"])+np.array([0,0,-0.01]))
        self.rightModel.SetRotation(np.array(props["rot"]))
        self.rightModel.SetScale(props["scale"])
    def draw(self,shaderhandler,renderer,viewMat):
        self.leftModel.DrawWithShader(shaderhandler.getShader("default"),renderer,viewMat)
        self.rightModel.DrawWithShader(shaderhandler.getShader("default"),renderer,viewMat)
