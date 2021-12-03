import numpy as np
import json
from classHandler import *
from objectHandler import prefabHandler

class MapLoader:
    def __init__(self,filename,player):
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
    def getObject(self,objName):
        for o in self.objects:
            if o.name == objName:
                return o
        return None
