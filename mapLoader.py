import numpy as np
import json
from classHandler import *
from objectHandler import prefabHandler
from functools import partial

class MapLoader:
    def __init__(self,filename,player):
        print("loading map:"+filename)
        self.mapFile = ""
        self.objects = []
        self.prefabHandler = prefabHandler()
        self.puzzle = None
        player.camera = Camera({"name":"camf","pos":[0,0,0],"rot":[0,0,0],"movement":"free"})
        with open(filename, "r") as f:
            self.JSONContent = json.loads("".join(f.readlines()))
            self.type = self.JSONContent["type"]
            for obj in self.JSONContent["objectList"]:
                if obj["type"]=="mapObject":
                    self.objects.append(Map(self.prefabHandler,obj))
                elif obj["type"]=="door":
                    self.objects.append(Door(self.prefabHandler,obj))
                elif obj["type"]=="decoration":
                    self.objects.append(Decoration(self.prefabHandler,obj))
                elif obj["type"]=="puzzlePlane":
                    self.objects.append(PuzzlePlane(self.prefabHandler,obj))
                elif obj["type"]=="slidePlane":
                    self.objects.append(SlidePlane(self.prefabHandler,obj))
                elif obj["type"]=="teleportCrystal":
                    self.objects.append(TeleportCrystal(self.prefabHandler,obj))
                elif obj["type"]=="menuCard":
                    self.objects.append(MenuCard(self.prefabHandler,obj))
                elif obj["type"]=="camera":
                    #self.objects.append(Camera(self.prefabHandler,obj))
                    player.camera = Camera(obj)
                    player.pos = player.camera.pos
                elif obj["type"]=="shaderPlane":
                    self.objects.append(ShaderPlane(self.prefabHandler,obj))
                elif obj["type"]=="comment":
                    pass
                else:
                    print("Unknown type for object in json: "+obj["type"])
                    print(obj)
    def loadNewMap(self,filename,player):
        self.__init__(filename,player)
    def getObject(self,objName):
        for o in self.objects:
            if o.name == objName:
                return o
        return None



def startLoadingScreen(maploader,map,player,inputhandler):
    print("added loadingscreen")
    
    func = partial(loadMapAsync,maploader,map,player,inputhandler)
    
    maploader.objects.append(LoadingScreen(maploader.prefabHandler,{"name":"ldscreen","pos":[-0.2,0,0],"rot":[0,0,1.57],"scale":1.5,"animation":"grow","function":func}))
    
    # stop mouse
    inputhandler.mouseLocked = True

def unlockMouse(inputhandler):
    inputhandler.mouseLocked = False

def loadMapAsync(maploader,filename,player,inputhandler):
    #maploader.objects = []
    #maploader.type = "load"

    inputhandler.mouseX = 650
    inputhandler.mouseY = 0
    inputhandler.interactingWith = None
    func = partial(unlockMouse,inputhandler)

    maploader.loadNewMap(filename,player)#MapLoader(filename,player)
    if filename == "maps/menu.json":
        maploader.objects.append(LoadingScreen(maploader.prefabHandler,{"name":"ldscreen","pos":[-0.2,0,0],"rot":[0,0,1.57],"scale":1.5,"animation":"shrink","function":func}))
    else:
        maploader.objects.append(LoadingScreen(maploader.prefabHandler,{"name":"ldscreen","pos":[0,1,-4.5],"rot":[1.57,0,1.57],"scale":1.5,"animation":"shrink","function":func}))
    
    