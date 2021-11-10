import numpy as np
import json
from classHandler import *
from objectHandler import prefabHandler

class MapLoader:
    def __init__(self,filename):
        self.mapFile = ""
        self.objects = []
        self.prefabHandler = prefabHandler()
        self.puzzle = None
        with open(filename, "r") as f:
            self.JSONContent = json.loads("".join(f.readlines()))
            for obj in self.JSONContent["objectList"]:
                if obj["type"]=="noteblock13":
                    self.objects.append(Noteblock13(self.prefabHandler,obj))
                elif obj["type"]=="notepiece13":
                    self.objects.append(Notepiece13(self.prefabHandler,obj))
                elif obj["type"]=="mapObject":
                    self.objects.append(Map(self.prefabHandler,obj))
                elif obj["type"]=="door":
                    self.objects.append(Door(self.prefabHandler,obj))
                elif obj["type"]=="button":
                    self.objects.append(Button(self.prefabHandler,obj))
                elif obj["type"]=="decoration":
                    self.objects.append(Decoration(self.prefabHandler,obj))
                elif obj["type"]=="puzzlePlane":
                    self.objects.append(PuzzlePlane(self.prefabHandler,obj))
                elif obj["type"]=="snakePlane":
                    self.objects.append(SnakePlane(self.prefabHandler,obj))
                elif obj["type"]=="puzzle":
                    self.puzzle = Puzzle(self,obj)
                elif obj["type"]=="teleportCrystal":
                    self.objects.append(TeleportCrystal(self.prefabHandler,obj))
                elif obj["type"]=="comment":
                    pass
                else:
                    print("Unknown type for object in json: "+obj["type"])
                    print(obj)
    def getObject(self,objName):
        for o in self.objects:
            if o.name == objName:
                return o
