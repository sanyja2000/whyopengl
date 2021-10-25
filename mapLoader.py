import numpy as np
import json
from classHandler import *

class MapLoader:
    def __init__(self,filename):
        self.mapFile = ""
        self.objects = []
        self.prefabHandler = prefabHandler()
        with open(filename, "r") as f:
            self.JSONContent = json.loads("".join(f.readlines()))
            for x in self.JSONContent["objectList"]:
                if x["type"]=="noteblock13":
                    self.objects.append(Noteblock13(self.prefabHandler,x["name"],x["note"],x["pos"],x["rot"],x["scale"]))
                if x["type"]=="mapObject":
                    self.objects.append(Map(self.prefabHandler,x["file"],x["texture"]))
