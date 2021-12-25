import math
from typing import Text
from objectHandler import Object3D
from renderer import IndexBuffer, Texture, VertexArray, VertexBuffer, VertexBufferLayout
import numpy as np
import time
from puzzles import *
from PIL import Image
import pyrr
import random
from OpenGL.GLUT import *

def easeInOutSine(x):
    return -(math.cos(math.pi * x) - 1) / 2


def lerp(f, t, n):
    return f*(1-n)+t*n

def lerpVec3(f,t,n):
    out = []
    for x in range(3):
        out.append(f[x]*(1-n)+t[x]*n)
    return np.array(out)


def dist(a,b):
    return math.sqrt((b[0]-a[0])**2+(b[1]-a[1])**2+(b[2]-a[2])**2)


class Map:
    def __init__(self,ph,props):
        self.objFile = props["file"]
        self.name = props["name"]
        self.cardNum = props["cardNum"]
        self.model = ph.loadFile(props["file"],props["texture"],textureRepeat=True)
        self.model.SetScale(10)
        self.model.SetPosition(np.array(props["pos"]))
        self.model.SetRotation(np.array(props["rot"]))
        # vec4 points, (x, y, z, radius) for sphere which is cleared
        # maximum of 5 points
        self.maxPoints = np.ones((5,4))
        self.clearedPoints = np.array([[-5,-10.0,-5,2],[5,-10.0,-5,2]])
    def draw(self,shaderhandler,renderer,viewMat):
        points = []
        for x in range(len(self.maxPoints)):
            if x<len(self.clearedPoints):
                points.append(self.clearedPoints[x])
            else:
                points.append(self.maxPoints[x])
        parameters = {"u_Time":time.perf_counter(),"4fv,clearedPoints":np.array(points),"numPoints":len(self.clearedPoints)}
        self.model.DrawWithShader(shaderhandler.getShader("map"),renderer,viewMat,options=parameters)
        #self.model.DrawWithShader(shaderhandler.getShader("default"),renderer,viewMat)


class Door:
    def __init__(self,ph,props):
        #pos,rot,scale,puzzleId
        self.puzzleId = props["puzzleId"]
        self.name = props["name"]
        self.scale = props["scale"]
        self.sound = props["sound"]
        self.opened = False
        self.openPercent = 0
        self.leftModel = ph.loadFile("res/trapdoor2.obj","res/wall_top.png",textureRepeat=True)
        self.leftModel.defaultPos = np.array(props["pos"])
        self.leftModel.SetPosition(self.leftModel.defaultPos)
        self.leftModel.SetRotation(np.array([0,3.14,0]))
        self.leftModel.SetScale(props["scale"])
        self.rightModel = ph.loadFile("res/trapdoor2.obj","res/wall_top.png",textureRepeat=True)
        self.rightModel.defaultPos = np.array(props["pos"])
        self.rightModel.SetPosition(self.rightModel.defaultPos+np.array([0,0,0]))
        self.rightModel.SetRotation(np.array(props["rot"]))
        self.rightModel.SetScale(props["scale"])
    def draw(self,shaderhandler,renderer,viewMat):
        self.leftModel.DrawWithShader(shaderhandler.getShader("default"),renderer,viewMat)
        self.rightModel.DrawWithShader(shaderhandler.getShader("default"),renderer,viewMat)
    def open(self):
        if not self.opened:
            #self.leftModel.SetPosition(self.leftModel.defaultPos+np.array([0.99*self.scale,0,0]))
            #self.rightModel.SetPosition(self.rightModel.defaultPos+np.array([-0.99*self.scale,0,0]))
            self.opened = True
    def close(self):
        if self.opened:
            #self.leftModel.SetPosition(self.leftModel.defaultPos)
            #self.rightModel.SetPosition(self.rightModel.defaultPos)
            self.opened = False
    def update(self,deltaTime,audioHandler):
        if self.opened and self.openPercent<1:
            self.openPercent += 1*deltaTime
            if self.openPercent > 1:
                self.openPercent = 1
        if not self.opened and self.openPercent>0:
            self.openPercent -= 1*deltaTime
            if self.openPercent < 0:
                self.openPercent = 0
        self.leftModel.SetPosition(self.leftModel.defaultPos+np.array([0.99*self.scale*self.openPercent,0,0]))
        self.rightModel.SetPosition(self.rightModel.defaultPos+np.array([-0.99*self.scale*self.openPercent,0,0]))


class TeleportCrystal:
    def __init__(self,ph,props):
        self.name = props["name"]
        self.picture = props["picture"]
        #self.model = ph.loadFile("res/crystal.obj","res/crystal.png")
        self.model = ph.loadFile("res/card.obj",self.picture)
        self.beats = props["beats"]
        self.scale = props["scale"]
        self.model.SetScale(props["scale"])
        self.model.SetPosition(np.array(props["pos"]))
        self.model.SetRotation(np.array(props["rot"]))
        self.model.defaultPosition = np.array(props["pos"])
        self.holdermodel = ph.loadFile("res/crystal_holder.obj","res/crystal_holder_color.png")
        self.holdermodel.SetScale(props["scale"])
        self.holdermodel.SetPosition(np.array(props["pos"]))
        self.holdermodel.SetRotation(np.array(props["rot"]))
        self.holdermodel.defaultPosition = np.array(props["pos"])
        self.isInteracting = False
        self.opened = False
        self.beatLength = props["beatLength"]
        self.animationTime = 0
        self.openPercent = 0

    def draw(self,shaderhandler,renderer,viewMat):
        self.model.DrawWithShader(shaderhandler.getShader("default_transparent"),renderer,viewMat)
        self.holdermodel.DrawWithShader(shaderhandler.getShader("default"),renderer,viewMat)
    def open(self):
        if not self.opened:
            self.opened = True
    def update(self,deltaTime,audioHandler):
        if self.opened and self.openPercent<1:
            self.openPercent += 0.3*deltaTime
            if self.openPercent > 1:
                self.openPercent = 1
        if not self.opened and self.openPercent>0:
            self.openPercent -= 0.3*deltaTime
            if self.openPercent < 0:
                self.openPercent = 0
        self.animationTime += deltaTime
        self.model.SetRotation(np.array([0,self.animationTime,0]))
        self.model.SetPosition(self.model.defaultPosition + np.array([0,math.sin(self.animationTime)*0.1,0]) +np.array([0,8*self.scale*self.openPercent,0]))


        #self.model.SetPosition(self.model.defaultPosition+np.array([0,8*self.scale*self.openPercent,0]))
        self.holdermodel.SetPosition(self.holdermodel.defaultPosition+np.array([0,8*self.scale*self.openPercent,0]))




class Decoration:
    def __init__(self,ph,props):
        self.name = props["name"]
        self.model = ph.loadFile(props["file"],props["texture"])
        self.model.SetScale(props["scale"])
        self.model.SetPosition(np.array(props["pos"]))
        self.model.SetRotation(np.array(props["rot"]))
        self.model.defaultPosition = np.array(props["pos"])
        self.shaderName = "default"
        if("transparent" in props):
            self.shaderName = "default_transparent"
    def draw(self,shaderhandler,renderer,viewMat):
        self.model.DrawWithShader(shaderhandler.getShader(self.shaderName),renderer,viewMat)

class PuzzleBox:
    def __init__(self,name,model,x,y,scale,parentModel,dimensions,rotationOffset):
        """
        name->not unique identifier
        model->3d model from prefabhandler
        x,y -> position in the NxN grid in minigame
        scale -> scale to fit in the NxN grid
        parentModel -> model of parent plane, to match rotation, position
        dimensions -> NxN dimension of uniform grid
        rotationOffset -> offset to match parent rotation
        """
        self.name = name
        self.x = x
        self.y = y
        self.model = model
        self.sqrttwo = 1.4142135
        self.rotationOffset = rotationOffset
        self.dimensions = dimensions
        self.scl = parentModel.scale*scale
        self.parentModel = parentModel
        x = self.rotationOffset[0]*self.x*self.scl*2+self.rotationOffset[2]*self.y*self.scl*self.sqrttwo
        z = self.rotationOffset[0]*self.y*self.scl*self.sqrttwo+self.rotationOffset[2]*self.x*self.scl*2
        self.offset = np.array([x,self.y*self.scl*self.sqrttwo,z])
        x = self.rotationOffset[0]*(-1*self.dimensions/2-0.5)*self.scl*2+self.rotationOffset[2]*(-1*self.dimensions/2)*self.scl*self.sqrttwo
        z = self.rotationOffset[0]*(-1*self.dimensions/2)*self.scl*self.sqrttwo+self.rotationOffset[2]*(-1*self.dimensions/2-0.5)*self.scl*2
        self.mapOffset = np.array([x,-0.5*self.parentModel.scale,z])
        
        self.model.SetPosition(parentModel.pos+self.offset+self.mapOffset)
        self.model.SetRotation(parentModel.rot)
        self.model.SetScale(parentModel.scale*scale)
    def moveTo(self,x,y):
        self.x = x
        self.y = y
        x = self.rotationOffset[0]*self.x*self.scl*2+self.rotationOffset[2]*self.y*self.scl*self.sqrttwo
        z = self.rotationOffset[0]*self.y*self.scl*self.sqrttwo+self.rotationOffset[2]*self.x*self.scl*2
        self.offset = np.array([x,self.y*self.scl*self.sqrttwo,z])
        self.model.SetPosition(self.parentModel.pos+self.offset+self.mapOffset)
    def draw(self,shaderhandler,renderer,viewMat):
        if self.name == "g":
           self.model.DrawWithShader(shaderhandler.getShader("default_transparent"),renderer,viewMat)
        else:
            self.model.DrawWithShader(shaderhandler.getShader("default"),renderer,viewMat)

class PuzzlePlane:
    def __init__(self,ph,props):
        self.prefabHandler = ph
        self.interactText = "Press Q to leave - Press R to restart puzzle"
        self.puzzleId = props["puzzleId"]
        self.name = props["name"]
        self.model = ph.loadFile("res/squarePlane.obj","res/sandstoneTextureLight.png")
        self.model.SetScale(props["scale"]*1.25)
        self.model.SetPosition(np.array(props["pos"])+np.array([0,2.01,0])*props["scale"])
        self.model.SetRotation(np.array(props["rot"])+np.array([-0.785,-1.57,0]))
        
        self.holderModel = ph.loadFile("res/puzzleHolder.obj","res/sandstoneTexture.png")
        self.holderModel.textureFile = "res/sandstoneTexture.png"
        self.holderModel.SetScale(props["scale"])
        self.holderModel.SetPosition(np.array(props["pos"]))
        self.holderModel.SetRotation(np.array(props["rot"]))
        
        self.solved = False
        self.playedSound = False
        self.isInteracting = False
        with open(props["mapfile"],"r") as f:
            self.mapfile = f.read().split("\n")
        self.dimensions = len(self.mapfile)
        self.minigameModels = []

        self.sqrttwo = 1.4142135
        self.boxScale = 1/self.dimensions*0.9
        self.rotationOffset = [math.cos(self.model.rot[1]+3.14),1,math.sin(self.model.rot[1]+3.14)]

        self.justMoved = False

        self.restart()

    def draw(self,shaderhandler,renderer,viewMat):
        self.model.DrawWithShader(shaderhandler.getShader("default"),renderer,viewMat)
        self.holderModel.DrawWithShader(shaderhandler.getShader("default"),renderer,viewMat)
        for yline in self.minigameModels:
            for mod in yline:
                if not mod is None:
                    mod.draw(shaderhandler,renderer,viewMat)
    def update(self,deltaTime,audioHandler):
        if self.justMoved:
            audioHandler.playSound("res/audio/puzzlemove.wav")
            self.justMoved = False
    
    def checkSolved(self):
        solvedCount = 0
        for y in range(self.dimensions):
            for x in range(self.dimensions):
                if not self.minigameModels[y][x] is None:
                    if self.minigameModels[y][x].name == "G":
                        if [x,y] in self.solvedPositions:
                            solvedCount += 1
        if solvedCount == len(self.solvedPositions):
            self.solved = True
    def restart(self):
        self.solved = False
        self.playedSound = False
        self.holderModel.textureFile = "res/sandstoneTexture.png"
        self.holderModel.texture = Texture("res/sandstoneTexture.png")
        self.minigameModels = []
        ph = self.prefabHandler
        walls = []
        self.solvedPositions = []
        for y in range(self.dimensions):
            yline = []
            for x in range(self.dimensions):
                if(self.mapfile[y][x] == "#"):
                    p = PuzzleBox("wall",ph.loadFile("res/simpleBox.obj","res/boxWall.png"),self.dimensions-x,self.dimensions-y,self.boxScale,self.model,self.dimensions,self.rotationOffset)
                    yline.append(p)
                    walls.append(p)
                elif(self.mapfile[y][x] == "G"):
                    yline.append(PuzzleBox("G",ph.loadFile("res/simpleBox.obj","res/boxNote.png"),self.dimensions-x,self.dimensions-y,self.boxScale,self.model,self.dimensions,self.rotationOffset))
                elif(self.mapfile[y][x] == "p"):
                    yline.append(PuzzleBox("p",ph.loadFile("res/simpleBox.obj","res/boxPlayer.png"),self.dimensions-x,self.dimensions-y,self.boxScale,self.model,self.dimensions,self.rotationOffset))
                elif(self.mapfile[y][x] == "g"):
                    yline.append(PuzzleBox("g",ph.loadFile("res/simpleBox.obj","res/boxNoteGFinish.png"),self.dimensions-x,self.dimensions-y,self.boxScale,self.model,self.dimensions,self.rotationOffset))
                    self.solvedPositions.append([x,y])
                elif(self.mapfile[y][x] == "s"):
                    yline.append(PuzzleBox("G",ph.loadFile("res/simpleBox.obj","res/boxNoteCorrect.png"),self.dimensions-x,self.dimensions-y,self.boxScale,self.model,self.dimensions,self.rotationOffset))
                    self.solvedPositions.append([x,y])
                else:
                    yline.append(None)
            self.minigameModels.append(yline)

    def moveWithKeys(self,inputHandler,deltaTime):
        if inputHandler.isKeyDown(b'r'):
            self.restart()
        if self.solved:
            return
        player = self.minigameModels[0]
        for yline in self.minigameModels:
            for mod in yline:
                if not mod is None:
                    if mod.name == "p":
                        player = mod
                        break
        
        dir = [0,0]
        if inputHandler.isKeyDown(b'w'):
            dir = [0,1]
        elif inputHandler.isKeyDown(b'a'):
            dir = [1,0]
        elif inputHandler.isKeyDown(b's'):
            dir = [0,-1]
        elif inputHandler.isKeyDown(b'd'):
            dir = [-1,0]
        newPos = [player.x+dir[0],player.y+dir[1]]
        canMove = True
        ph = self.prefabHandler
        if -1<newPos[0]<self.dimensions and -1<newPos[1]<self.dimensions:
            nextPlace = self.minigameModels[self.dimensions-newPos[1]][self.dimensions-newPos[0]]
            if not nextPlace is None:
                if nextPlace.name == "G":
                    if self.minigameModels[self.dimensions-newPos[1]-dir[1]][self.dimensions-newPos[0]-dir[0]] is None:
                        self.minigameModels[self.dimensions-newPos[1]][self.dimensions-newPos[0]] = None
                        nextPlace.moveTo(newPos[0]+dir[0],newPos[1]+dir[1])
                        self.minigameModels[self.dimensions-newPos[1]-dir[1]][self.dimensions-newPos[0]-dir[0]] = nextPlace
                        nextPlace.model.texture = Texture("res/boxNote.png")
                    elif self.minigameModels[self.dimensions-newPos[1]-dir[1]][self.dimensions-newPos[0]-dir[0]].name == "g":
                        self.minigameModels[self.dimensions-newPos[1]][self.dimensions-newPos[0]] = None
                        nextPlace.moveTo(newPos[0]+dir[0],newPos[1]+dir[1])
                        self.minigameModels[self.dimensions-newPos[1]-dir[1]][self.dimensions-newPos[0]-dir[0]] = nextPlace
                        # here we push it into a target place
                        # change color of model
                        nextPlace.model.texture = Texture("res/boxNoteCorrect.png")
                    else:
                        canMove = False
                elif nextPlace.name == "g":
                    pass
                else:
                    canMove = False
            if canMove:
                self.minigameModels[self.dimensions-player.y][self.dimensions-player.x] = None
                if [self.dimensions-player.x,self.dimensions-player.y] in self.solvedPositions:
                    self.minigameModels[self.dimensions-player.y][self.dimensions-player.x] = PuzzleBox("g",ph.loadFile("res/simpleBox.obj","res/boxNoteGFinish.png"),player.x,player.y,self.boxScale,self.model,self.dimensions,self.rotationOffset)
                player.moveTo(newPos[0],newPos[1])
                self.minigameModels[self.dimensions-newPos[1]][self.dimensions-newPos[0]] = player
                self.justMoved = True
        self.checkSolved()


class SlidePiece:
    def __init__(self,name,model,x,y,scale,parentModel,dimensions,rotationOffset):
        """
        name->not unique identifier
        model->3d model from prefabhandler
        x,y -> position in the NxN grid in minigame
        scale -> scale to fit in the NxN grid
        parentModel -> model of parent plane, to match rotation, position
        dimensions -> NxN dimension of uniform grid
        rotationOffset -> offset to match parent rotation
        """
        self.name = name
        self.x = x
        self.y = y
        self.model = model
        self.sqrttwo = 1.4142135
        self.rotationOffset = rotationOffset
        self.dimensions = dimensions
        self.scl = parentModel.scale*scale
        self.parentModel = parentModel
        x = self.rotationOffset[0]*self.x*self.scl*2+self.rotationOffset[2]*self.y*self.scl*self.sqrttwo
        z = self.rotationOffset[0]*self.y*self.scl*self.sqrttwo+self.rotationOffset[2]*self.x*self.scl*2
        self.offset = np.array([x,self.y*self.scl*self.sqrttwo,z])
        x = self.rotationOffset[0]*(-1*self.dimensions/2-0.5)*self.scl*2+self.rotationOffset[2]*(-1*self.dimensions/2)*self.scl*self.sqrttwo
        z = self.rotationOffset[0]*(-1*self.dimensions/2)*self.scl*self.sqrttwo+self.rotationOffset[2]*(-1*self.dimensions/2-0.5)*self.scl*2
        self.mapOffset = np.array([x,-0.5*self.parentModel.scale,z])
        
        self.model.SetPosition(parentModel.pos+self.offset+self.mapOffset)
        self.model.SetRotation(parentModel.rot)
        self.model.SetScale(parentModel.scale*scale)
    def moveTo(self,x,y):
        self.x = x
        self.y = y
        x = self.rotationOffset[0]*self.x*self.scl*2+self.rotationOffset[2]*self.y*self.scl*self.sqrttwo
        z = self.rotationOffset[0]*self.y*self.scl*self.sqrttwo+self.rotationOffset[2]*self.x*self.scl*2
        self.offset = np.array([x,self.y*self.scl*self.sqrttwo,z])
        self.model.SetPosition(self.parentModel.pos+self.offset+self.mapOffset)
    def draw(self,shaderhandler,renderer,viewMat):
        self.model.DrawWithShader(shaderhandler.getShader("default"),renderer,viewMat)

class SlidePlane:
    def __init__(self,ph,props):
        self.name = props["name"]
        self.pos = props["pos"]
        self.rot = props["rot"]
        self.scl = props["scale"]
        self.interactText = "Press Q to leave"
        self.prefabHandler = ph
        self.model = ph.loadFile("res/squarePlane.obj","res/sandstoneTextureLight.png")
        self.model.SetScale(props["scale"]*1.25)
        self.model.SetPosition(np.array(props["pos"])+np.array([0,2.01,0])*props["scale"])
        self.model.SetRotation(np.array(props["rot"])+np.array([-0.785,-1.57,0]))
        
        self.holderModel = ph.loadFile("res/puzzleHolder.obj","res/sandstoneTexture.png")
        self.holderModel.textureFile = "res/sandstoneTexture.png"
        self.holderModel.SetScale(props["scale"])
        self.holderModel.SetPosition(np.array(props["pos"]))
        self.holderModel.SetRotation(np.array(props["rot"]))

        self.rotationOffset = [math.cos(self.model.rot[1]+3.14),1,math.sin(self.model.rot[1]+3.14)]

        self.solved = False
        self.isInteracting = False
        self.justMoved = False

        self.size = [3,2]
        self.boxScale = 1/self.size[0]*0.9
        self.image = props["picture"]

        self.restart()
        self.shuffle()
    def shuffle(self):
        self.solved = False
        for i in range(30):
            direction = [0,0]
            move = random.randint(0,3)
            if move == 0:
                direction[1] = -1
            if move == 1:
                direction[0] = -1
            if move == 2:
                direction[1] = 1
            if move == 3:
                direction[0] = 1
            moved = False
            for y in range(self.size[1]):
                for x in range(self.size[0]):
                    if self.minigameModels[y][x] == None:
                        if abs(direction[0])>0 and 0<=x+direction[0]<self.size[0]:
                            self.minigameModels[y][x] = self.minigameModels[y][x+direction[0]]
                            self.minigameModels[y][x].moveTo(self.size[0]-x,self.size[1]-y)
                            self.minigameModels[y][x+direction[0]] = None
                            moved = True
                            break
                        elif abs(direction[1])>0 and 0<=y+direction[1]<self.size[1]:
                            self.minigameModels[y][x] = self.minigameModels[y+direction[1]][x]
                            self.minigameModels[y][x].moveTo(self.size[0]-x,self.size[1]-y)
                            self.minigameModels[y+direction[1]][x] = None
                            moved = True
                            break
                if moved:
                    break
            
    def checkSolved(self):
        self.solved = False
        for y in range(self.size[1]):
            for x in range(self.size[0]):
                if not self.minigameModels[y][x] is None:
                    if str(x)+","+str(y) != self.minigameModels[y][x].name:
                        return
        self.solved = True
    def moveWithKeys(self,inputHandler,deltaTime):
        if self.solved:
            return
        direction = [0,0]
        if inputHandler.isKeyDown(b's'):
            direction[1] = -1
        if inputHandler.isKeyDown(b'd'):
            direction[0] = -1
        if inputHandler.isKeyDown(b'w'):
            direction[1] = 1
        if inputHandler.isKeyDown(b'a'):
            direction[0] = 1
        moved = False
        for y in range(self.size[1]):
            for x in range(self.size[0]):
                if self.minigameModels[y][x] == None:
                    if abs(direction[0])>0 and 0<=x+direction[0]<self.size[0]:
                        self.minigameModels[y][x] = self.minigameModels[y][x+direction[0]]
                        self.minigameModels[y][x].moveTo(self.size[0]-x,self.size[1]-y)
                        self.minigameModels[y][x+direction[0]] = None
                        moved = True
                        break
                    elif abs(direction[1])>0 and 0<=y+direction[1]<self.size[1]:
                        self.minigameModels[y][x] = self.minigameModels[y+direction[1]][x]
                        self.minigameModels[y][x].moveTo(self.size[0]-x,self.size[1]-y)
                        self.minigameModels[y+direction[1]][x] = None
                        moved = True
                        break
            if moved:
                self.justMoved = True
                break
        self.checkSolved()
        
    def draw(self,shaderhandler,renderer,viewMat):
        self.model.DrawWithShader(shaderhandler.getShader("default"),renderer,viewMat)
        self.holderModel.DrawWithShader(shaderhandler.getShader("default"),renderer,viewMat)
        for yline in self.minigameModels:
            for mod in yline:
                if not mod is None:
                    mod.draw(shaderhandler,renderer,viewMat)
    def update(self,deltaTime,audioHandler):
        if self.justMoved:
            audioHandler.playSound("res/audio/puzzlemove.wav")
            self.justMoved = False
    def restart(self):
        # cut the image into 3x2 pieces
        im = Image.open(self.image)
        width, height = im.size
        
        ph = self.prefabHandler
        self.minigameModels = []
        for y in range(self.size[1]):
            yline = []
            top = (y)*height/self.size[1]
            bottom = (y+1)*height/self.size[1]
            for x in range(self.size[0]):
                if(x+y==self.size[0]+self.size[1]-2):
                    yline.append(None)
                    continue
                left = (x)*width/self.size[0]
                right = (x+1)*width/self.size[0]
                yline.append(SlidePiece(str(x)+","+str(y),ph.loadFile("res/slidebox.obj","res/puzzles/photo1.png",unique=True),self.size[0]-x,self.size[1]-y,self.boxScale,self.model,3,self.rotationOffset))
                yline[-1].model.texture.OverrideTexture(im.crop((left, top, right, bottom)),repeat=True)

            self.minigameModels.append(yline)
        self.shuffle()


        


class ShaderPlane:
    def __init__(self,ph,props):
        self.name = props["name"]
        self.pos = props["pos"]
        self.rot = props["rot"]
        self.scl = props["scale"]
        self.shaderName = props["shader"]
        self.model = ph.loadFile("res/simplePlane.obj","res/puzzleHolderTestSuccess.png")
        self.model.SetScale(props["scale"])
        self.model.SetPosition(np.array(props["pos"]))
        self.model.SetRotation(np.array(props["rot"]))
        self.model.defaultPosition = np.array(props["pos"])
    def draw(self,shaderhandler,renderer,viewMat):
        self.model.DrawWithShader(shaderhandler.getShader(self.shaderName),renderer,viewMat,options={"u_Time":time.perf_counter()})


class Camera:
    def __init__(self,props):
        #{"name":"camera1","type":"camera","movement":"fixed","pos":[0,1,0],"rot":[0,0,0]}
        self.name = props["name"]
        self.pos = props["pos"]
        self.rot = props["rot"]
        self.isActive = False
        self.movement = props["movement"]
        self.defaultPosition = np.array(props["pos"])
        self.shaderName = "default"
        if("transparent" in props):
            self.shaderName = "default_transparent"
    def draw(self,shaderhandler,renderer,viewMat):
        pass
    def update(self,deltaTime,audioHandler):
        """
        a = self.rot[1] #yMouseAngle
        b = self.rot[0] #xMouseAngle
        rotz = pyrr.matrix44.create_from_z_rotation(a*math.sin(b))
        rotx = pyrr.matrix44.create_from_x_rotation(a*math.cos(b))
        rot = np.matmul(np.matmul(pyrr.matrix44.create_from_y_rotation(b),rotz),rotx)
        self.camModel = np.matmul(rot,np.transpose(pyrr.matrix44.create_from_translation(np.array(self.camPosition))))
        """
        pass
        
class MenuCard:
    def __init__(self,ph,props):
        self.name = props["name"]
        if props["revealed"]:
            self.model = ph.loadFile("res/card.obj",props["picture"])
        else:
            self.model = ph.loadFile("res/card.obj","res/cards/unknown.png")
        self.model.SetScale(props["scale"])
        self.model.SetPosition(np.array(props["pos"]))
        self.model.SetRotation(np.array(props["rot"]))
        self.model.defaultPosition = np.array(props["pos"])
        self.model.defaultRotation = np.array(props["rot"])
        self.model.defaultScale = props["scale"]
        self.mousePos = None
        self.map = props["map"]
        self.animationTime = 0
        self.isActive = False
        self.soundPlayed = False
    def draw(self,shaderhandler,renderer,viewMat):
        self.model.DrawWithShader(shaderhandler.getShader("default_transparent"),renderer,viewMat)
    def update(self,deltaTime,audioHandler):
        if self.isActive and self.animationTime<1:
            if not self.soundPlayed:
                audioHandler.playSound("res/audio/card_sound.wav")
                self.soundPlayed = True
            self.animationTime+=deltaTime*5
            if self.animationTime>1:
                self.animationTime = 1
        if self.isActive and not self.mousePos is None:
            r = np.array([0,self.model.defaultPosition[2]-self.mousePos[2],-self.model.defaultPosition[1]-self.mousePos[1]])
            rot = lerpVec3(self.model.defaultRotation, self.model.defaultRotation+(r)/5,self.animationTime)
            self.model.SetRotation(rot)
        if not self.isActive and self.animationTime > 0:
            self.soundPlayed = False
            self.animationTime-=deltaTime*2
            if self.animationTime<0:
                self.animationTime = 0
            if not self.mousePos is None:
                r = np.array([0,self.model.defaultPosition[2]-self.mousePos[2],-self.model.defaultPosition[1]-self.mousePos[1]])
                rot = lerpVec3(self.model.defaultRotation, self.model.defaultRotation+(r)/5,self.animationTime)
                self.model.SetRotation(rot)
        s = lerp(self.model.defaultScale,self.model.defaultScale+0.25,self.animationTime)
        
        self.model.SetScale(s)

class LoadingScreen:
    def __init__(self,ph,props):
        self.name = props["name"]
        self.model = ph.loadFile("res/simplePlane.obj","res/black.png")#props["picture"])
        self.model.SetScale(props["scale"])
        self.model.SetPosition(np.array(props["pos"]))
        self.model.SetRotation(np.array(props["rot"]))
        self.model.defaultPosition = np.array(props["pos"])
        self.model.defaultRotation = np.array(props["rot"])
        self.model.defaultScale = props["scale"]
        self.animationTime = 0
        self.isActive = True
        self.done = False
        self.animation = props["animation"]
        if self.animation == "grow":
            self.model.SetScale(0)
        self.function = props["function"] if "function" in props else None

    def draw(self,shaderhandler,renderer,viewMat):
        #self.model.DrawWithShader(shaderhandler.getShader("default"),renderer,viewMat)
        if self.isActive:
            self.model.DrawWithShader(shaderhandler.getShader("default"),renderer,viewMat)
    def update(self,deltaTime,audioHandler):
        if self.isActive:
            if self.animationTime<1:
                if self.animation == "grow":
                    scl = lerp(0,self.model.defaultScale,self.animationTime)
                    self.model.SetScale(scl)
                    self.animationTime += deltaTime*0.7
                
                if self.animation == "shrink":
                    scl = lerp(self.model.defaultScale,0,self.animationTime)
                    self.model.SetScale(scl)
                    self.animationTime += deltaTime*0.4
                
                
                if self.animationTime>1:
                    self.done = True
                    self.animationTime = 1
            if self.done and self.function != None:
                print("function ran")
                self.function()
                self.isActive = False
                self.done = False
                return
    def moveWithKeys(self,inputHandler,deltaTime):
        pass



class PauseMenu:
    def __init__(self, hudShader):
        self.backgroundTexture = Texture("res/pauseMenu.png")
        self.points = np.array([0.33, -1, 0.0, 0.0,
                                1, -1, 1.0, 0.0,
                                1, 1, 1.0, 1.0,
                                0.33, 1, 0.0, 1.0],dtype='float32')
        self.shader = hudShader

        self.indices = np.array([0,1,2, 2,3,0])
        self.va = VertexArray()
        self.vb = VertexBuffer(self.points)
        self.layout = VertexBufferLayout()
        self.layout.PushF(2)
        self.layout.PushF(2)
        self.va.AddBuffer(self.vb, self.layout)
        self.ib = IndexBuffer(self.indices, 6)
        self.ownTime = 0
        self.currentlySelected = 0
        self.menuText = ["Resume", "Main Menu", "Quit Game"]
        self.openPercent = 0
        self.moving = 0
        self.openSpeed = 3
        self.backToMainMenu = False
        self.playingSound = None
    def draw(self,fontHandler,renderer):
        self.ownTime += 1

        # draw background
        
        self.backgroundTexture.Bind()
        self.shader.Bind()

        self.shader.SetUniform1i("u_Texture",0)
        self.shader.SetUniform1i("u_time",self.ownTime)
        self.shader.SetUniform1f("xcoord",(1-self.openPercent)*0.66)
        renderer.Draw(self.va,self.ib,self.shader)

        # draw text
        #easeInOutSine
        xoffset = easeInOutSine(1-self.openPercent)*0.66

        fontHandler.drawText("Pause Menu",-1*len("Pause Menu")/50+0.7+xoffset,0.6,0.06,renderer)

        for i in range(len(self.menuText)):
            text = self.menuText[i]
            if i == self.currentlySelected:
                text = "> "+text+" <" 
                fontHandler.drawText(text,-1*len(text)/50+0.7+xoffset,0.3-i*0.4+math.sin(self.ownTime/100)/100.0,0.05,renderer)
            else:
                fontHandler.drawText(text,-1*len(text)/50+0.7+xoffset,0.3-i*0.4,0.05,renderer)
                        
    def update(self,deltaTime,audioHandler,game):
        if self.playingSound == "slide":
            self.playingSound = None
            audioHandler.playSound("res/audio/menu_slide.wav")
        if self.playingSound == "move":
            self.playingSound = None
            audioHandler.playSound("res/audio/puzzlemove.wav")
        if game.mp.type == "menu":
            self.menuText = ["Resume", "Quit Game"]
        else:
            self.menuText = ["Resume", "Main Menu", "Quit Game"]
        self.openPercent += self.moving*deltaTime
        if self.openPercent>1:
            self.moving = 0
            self.openPercent = 1
        if self.openPercent<0:
            self.moving = 0
            self.openPercent = 0
    def open(self):
        self.currentlySelected = 0
        self.moving = self.openSpeed
        self.playingSound = "slide"
    def close(self):
        self.moving = -1*self.openSpeed
        self.playingSound = "slide"
    def moveWithKeys(self,inputHandler,deltaTime):
        if inputHandler.isKeyDown(b's'):
            # Menu down
            self.playingSound = "move"
            self.currentlySelected = (self.currentlySelected+1)%len(self.menuText)
        if inputHandler.isKeyDown(b'w'):
            # Menu up
            self.playingSound = "move"
            self.currentlySelected = (self.currentlySelected-1)%len(self.menuText)
        if inputHandler.isKeyDown(b'\r') or inputHandler.isKeyDown(b' '):
            if self.menuText[self.currentlySelected] == "Resume":
                # Resume
                self.close()
                inputHandler.interactingWith = None
            elif self.menuText[self.currentlySelected] == "Main Menu":
                # Load main menu
                self.close()
                self.backToMainMenu = True
            elif self.menuText[self.currentlySelected] == "Quit Game":
                # Exit game
                glutLeaveMainLoop()
                #sys.quit() ?