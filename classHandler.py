import math
from numpy.lib.function_base import delete
from objectHandler import Object3D
from renderer import Texture
import numpy as np
import time
from puzzles import *
        

class Map:
    def __init__(self,ph,props):
        self.objFile = props["file"]
        self.name = props["name"]
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

class Noteblock13:
    def __init__(self,ph,props):
        self.puzzleId = props["puzzleId"]
        self.name = props["name"]
        self.model = ph.loadFile("res/noteblock1.obj","res/fire.png")
        self.model.SetScale(props["scale"])
        self.model.SetPosition(np.array(props["pos"]))
        self.model.SetRotation(np.array(props["rot"]))
        self.note = props["note"]
        self.lastPlayed = 0
       
    def draw(self,shaderhandler,renderer,viewMat):
        self.model.DrawWithShader(shaderhandler.getShader("noteblock"),renderer,viewMat,options={"u_Time":time.perf_counter(),"u_LastPlayed":self.lastPlayed})

class Notepiece13:
    def __init__(self,ph,props):
        self.puzzleId = props["puzzleId"]
        self.name = props["name"]
        self.model = ph.loadFile("res/notepiece.obj","res/fire.png")
        self.model.SetScale(props["scale"])
        self.model.SetPosition(np.array(props["pos"]))
        self.model.SetRotation(np.array(props["rot"]))
        self.note = props["note"]
        self.lastPlayed = 0
       
    def draw(self,shaderhandler,renderer,viewMat):
        self.model.DrawWithShader(shaderhandler.getShader("notepiece"),renderer,viewMat,options={"u_Time":time.perf_counter(),"u_LastPlayed":self.lastPlayed})


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
        #self.model = ph.loadFile("res/crystal.obj","res/crystal.png")
        self.model = ph.loadFile("res/card.obj","res/aceOfSpades.png")
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
        self.sound = props["sound"]
        self.isInteracting = False
        self.opened = False
        self.animationTime = 0
        self.openPercent = 0

    def draw(self,shaderhandler,renderer,viewMat):
        self.model.DrawWithShader(shaderhandler.getShader("default"),renderer,viewMat)
        self.holdermodel.DrawWithShader(shaderhandler.getShader("default"),renderer,viewMat)
    def open(self):
        if not self.opened:
            self.opened = True
    def update(self,deltaTime,audioHandler):
        if self.opened and self.openPercent<1:
            self.openPercent += 1*deltaTime
            if self.openPercent > 1:
                self.openPercent = 1
        if not self.opened and self.openPercent>0:
            self.openPercent -= 1*deltaTime
            if self.openPercent < 0:
                self.openPercent = 0
        self.animationTime += deltaTime
        self.model.SetRotation(np.array([0,self.animationTime,0]))
        self.model.SetPosition(self.model.defaultPosition + np.array([0,math.sin(self.animationTime)*0.1,0]) +np.array([0,8*self.scale*self.openPercent,0]))


        #self.model.SetPosition(self.model.defaultPosition+np.array([0,8*self.scale*self.openPercent,0]))
        self.holdermodel.SetPosition(self.holdermodel.defaultPosition+np.array([0,8*self.scale*self.openPercent,0]))


class Puzzle:
    def __init__(self,mapHandler,props):
        self.mapHandler = mapHandler
        self.solved = False
        self.solveCheck = props["solveFunction"]
    def trySolve(self):
        didSolve = eval(self.solveCheck+"(self.mapHandler)")
        if didSolve:
            self.mapHandler.getObject("Door1").open()
            print("puzzle solved!")
        else:
            self.mapHandler.getObject("Door1").close()
            print("not solved yet")

class Button:
    def __init__(self,ph,props):
        self.puzzleId = props["puzzleId"]
        self.name = props["name"]
        self.model = ph.loadFile("res/testbutton1.obj","res/uv_testbuttonfilled.png")
        self.model.SetScale(props["scale"])
        self.model.SetPosition(np.array(props["pos"]))
        self.model.SetRotation(np.array(props["rot"]))
    def draw(self,shaderhandler,renderer,viewMat):
        self.model.DrawWithShader(shaderhandler.getShader("default"),renderer,viewMat)
        
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
        self.model = ph.loadFile("res/squarePlane.obj","res/puzzleHolderTestSuccess.png")
        self.model.SetScale(props["scale"]*1.25)
        self.model.SetPosition(np.array(props["pos"])+np.array([0,2.01,0])*props["scale"])
        self.model.SetRotation(np.array(props["rot"])+np.array([-0.785,-1.57,0]))
        
        self.holderModel = ph.loadFile("res/puzzleHolder.obj","res/sandstoneTexture.png")
        self.holderModel.textureFile = "res/sandstoneTexture.png"
        self.holderModel.SetScale(props["scale"])
        self.holderModel.SetPosition(np.array(props["pos"]))
        self.holderModel.SetRotation(np.array(props["rot"]))
        
        self.sound = props["sound"]
        self.solved = False
        self.playedSound = False
        self.isInteracting = False
        with open(props["mapfile"],"r") as f:
            self.mapfile = f.read().split("\n")
        #self.mapfile = ["####...#","##.....#","#...G...","#.......","#.......","#.......","#...g...","#......."]
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
            audioHandler.playSound("res/audio/puzzle_move.wav")
            self.justMoved = False
        if self.solved and self.holderModel.textureFile == "res/puzzleHolderTestFail.png":
            self.holderModel.textureFile = "res/puzzleHolderTestSuccess.png"
            self.holderModel.texture = Texture("res/puzzleHolderTestSuccess.png")
            
    def restart(self):
        self.solved = False
        self.playedSound = False
        self.holderModel.textureFile = "res/sandstoneTexture.png"
        self.holderModel.texture = Texture("res/sandstoneTexture.png")
        self.minigameModels = []
        ph = self.prefabHandler
        walls = []
        for y in range(self.dimensions):
            yline = []
            for x in range(self.dimensions):
                if(self.mapfile[y][x] == "#"):
                    p = PuzzleBox("wall",ph.loadFile("res/simpleBox.obj","res/boxWall.png"),self.dimensions-x,self.dimensions-y,self.boxScale,self.model,self.dimensions,self.rotationOffset)
                    yline.append(p)
                    walls.append(p)
                elif(self.mapfile[y][x] == "G"):
                    yline.append(PuzzleBox("G",ph.loadFile("res/simpleBox.obj","res/boxNoteG.png"),self.dimensions-x,self.dimensions-y,self.boxScale,self.model,self.dimensions,self.rotationOffset))
                elif(self.mapfile[y][x] == "p"):
                    yline.append(PuzzleBox("p",ph.loadFile("res/simpleBox.obj","res/boxPlayer.png"),self.dimensions-x,self.dimensions-y,self.boxScale,self.model,self.dimensions,self.rotationOffset))
                elif(self.mapfile[y][x] == "g"):
                    yline.append(PuzzleBox("g",ph.loadFile("res/simpleBox.obj","res/boxNoteGFinish.png"),self.dimensions-x,self.dimensions-y,self.boxScale,self.model,self.dimensions,self.rotationOffset))
                else:
                    yline.append(None)
            self.minigameModels.append(yline)

    def moveWithKeys(self,inputHandler,deltaTime):
        if b'r' in inputHandler.keysDown and inputHandler.keysDown[b'r'] == 1:
            self.restart()
        player = self.minigameModels[0]
        for yline in self.minigameModels:
            for mod in yline:
                if not mod is None:
                    if mod.name == "p":
                        player = mod
                        break
        
        dir = [0,0]
        if inputHandler.keysDown[b'w'] == 1:
            dir = [0,1]
        elif inputHandler.keysDown[b'a'] == 1:
            dir = [1,0]
        elif inputHandler.keysDown[b's'] == 1:
            dir = [0,-1]
        elif inputHandler.keysDown[b'd'] == 1:
            dir = [-1,0]
        newPos = [player.x+dir[0],player.y+dir[1]]
        canMove = True
        if -1<newPos[0]<self.dimensions and -1<newPos[1]<self.dimensions:
            nextPlace = self.minigameModels[self.dimensions-newPos[1]][self.dimensions-newPos[0]]
            if not nextPlace is None:
                if nextPlace.name == "G":
                    if self.minigameModels[self.dimensions-newPos[1]-dir[1]][self.dimensions-newPos[0]-dir[0]] is None:
                        self.minigameModels[self.dimensions-newPos[1]][self.dimensions-newPos[0]] = None
                        nextPlace.moveTo(newPos[0]+dir[0],newPos[1]+dir[1])
                        self.minigameModels[self.dimensions-newPos[1]-dir[1]][self.dimensions-newPos[0]-dir[0]] = nextPlace
                    elif self.minigameModels[self.dimensions-newPos[1]-dir[1]][self.dimensions-newPos[0]-dir[0]].name == "g":
                        self.minigameModels[self.dimensions-newPos[1]][self.dimensions-newPos[0]] = None
                        nextPlace.moveTo(newPos[0]+dir[0],newPos[1]+dir[1])
                        self.minigameModels[self.dimensions-newPos[1]-dir[1]][self.dimensions-newPos[0]-dir[0]] = nextPlace
                        self.solved = True
                    else:
                        canMove = False
                else:
                    canMove = False
            if canMove:
                self.minigameModels[self.dimensions-player.y][self.dimensions-player.x] = None
                player.moveTo(newPos[0],newPos[1])
                self.minigameModels[self.dimensions-newPos[1]][self.dimensions-newPos[0]] = player
                self.justMoved = True


class SnakePlane:
    def __init__(self,ph,props):
        self.prefabHandler = ph
        self.interactText = "Press Q to leave - Press R to restart puzzle"
        self.puzzleId = props["puzzleId"]
        self.name = props["name"]
        self.model = ph.loadFile("res/squarePlane.obj","res/puzzleHolderTestSuccess.png")
        self.model.SetScale(props["scale"]*1.25)
        self.model.SetPosition(np.array(props["pos"])+np.array([0,2.01,0])*props["scale"])
        self.model.SetRotation(np.array(props["rot"])+np.array([-0.785,-1.57,0]))
        
        
        self.holderModel = ph.loadFile("res/puzzleHolder.obj","res/puzzleHolderTestFail.png")
        self.holderModel.textureFile = "res/puzzleHolderTestFail.png"
        self.holderModel.SetScale(props["scale"])
        self.holderModel.SetPosition(np.array(props["pos"]))
        self.holderModel.SetRotation(np.array(props["rot"]))
        
        self.moveDir = [0,-1]
        self.lastMove = 0
        self.solved = False
        self.isInteracting = False

        self.snakeBits = []
        self.dimensions = 8
        self.minigameModels = [[None for i in range(self.dimensions)] for i in range(self.dimensions)]

        self.sqrttwo = 1.4142135
        self.boxScale = 1/self.dimensions*0.9
        self.rotationOffset = [math.cos(self.model.rot[1]+3.14),1,math.sin(self.model.rot[1]+3.14)]

        for x in range(self.dimensions):
            for y in range(self.dimensions):
                if x==0 or y==0 or x==7 or y == 7:
                    self.minigameModels[y][x] = PuzzleBox("wall",ph.loadFile("res/simpleBox.obj","res/boxWall.png"),self.dimensions-x,self.dimensions-y,self.boxScale,self.model,self.dimensions,self.rotationOffset)
                if x==3 and y == 2:
                    self.minigameModels[y][x] = PuzzleBox("p",ph.loadFile("res/simpleBox.obj","res/boxPlayer.png"),self.dimensions-x,self.dimensions-y,self.boxScale,self.model,self.dimensions,self.rotationOffset)
                if x==5 and y == 6:
                    self.minigameModels[y][x] = PuzzleBox("G",ph.loadFile("res/simpleBox.obj","res/boxNoteG.png"),self.dimensions-x,self.dimensions-y,self.boxScale,self.model,self.dimensions,self.rotationOffset)
        
        
    def draw(self,shaderhandler,renderer,viewMat):
        self.model.DrawWithShader(shaderhandler.getShader("default"),renderer,viewMat)
        self.holderModel.DrawWithShader(shaderhandler.getShader("default"),renderer,viewMat)
        for yline in self.minigameModels:
            for mod in yline:
                if not mod is None:
                    mod.draw(shaderhandler,renderer,viewMat)
    def update(self,deltaTime,audioHandler):
        if self.isInteracting:
            now = time.perf_counter()
            if now-self.lastMove>0.5:
                self.lastMove = now
                player = self.minigameModels[0]
                for yline in self.minigameModels:
                    for mod in yline:
                        if not mod is None:
                            if mod.name == "p":
                                player = mod
                                break
                if self.minigameModels[self.dimensions-player.y-self.moveDir[1]][self.dimensions-player.x-self.moveDir[0]] is None:
                    #print(self.minigameModels[self.dimensions-player.y+self.moveDir[1]][self.dimensions-player.x+self.moveDir[0]])
                    player.moveTo(player.x+self.moveDir[0],player.y+self.moveDir[1])
                    self.minigameModels[self.dimensions-player.y+self.moveDir[1]][self.dimensions-player.x+self.moveDir[0]] = player
                    self.minigameModels[self.dimensions-player.y][self.dimensions-player.x] = None

    def moveWithKeys(self,inputHandler,deltaTime):
        if inputHandler.keysDown[b'w'] == 1:
            self.moveDir = [0,1]
        elif inputHandler.keysDown[b'a'] == 1:
            self.moveDir = [1,0]
        elif inputHandler.keysDown[b's'] == 1:
            self.moveDir = [0,-1]
        elif inputHandler.keysDown[b'd'] == 1:
            self.moveDir = [-1,0]
        