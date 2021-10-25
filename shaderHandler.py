from renderer import Shader

class ShaderHandler:
    def __init__(self):
        self.shaders = {}
    def loadShader(self,name,vfile,ffile):
        with open(vfile,"r") as vert:
            vshader = "".join(vert.readlines())
        with open(ffile,"r") as frag:
            fshader = "".join(frag.readlines())
        self.shaders[name] = Shader(vshader, fshader)
    def getShader(self,name):
        return self.shaders[name]