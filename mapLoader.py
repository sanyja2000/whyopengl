import numpy as np
import json
from classHandler import *

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
                if obj["type"]=="mapObject":
                    self.objects.append(Map(self.prefabHandler,obj))
                if obj["type"]=="door":
                    self.objects.append(Door(self.prefabHandler,obj))
                if obj["type"]=="puzzle":
                    self.puzzle = Puzzle(self,obj)
    def getObject(self,objName):
        for o in self.objects:
            if o.name == objName:
                return o
