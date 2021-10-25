import math,pyrr, numpy as np

class Player:
    def __init__(self):
        self.pos = [0,0,0]
        self.rot = [0,0,0]
        self.vel = [0,0,0]
        self.maxVelocity = 5
        self.acc = [0,0,0]
        self.model = None
        self.camPosition = [0,-1,0]
        self.camRotation = [-1.57,0,0]
        self.xAng = 0
        self.yAng = 0
    def moveWithKeys(self,keysDown,deltaTime):
        if keysDown[b'd']:
            self.pos[0] += self.maxVelocity*math.cos(-self.xAng)*deltaTime
            self.pos[2] -= self.maxVelocity*math.sin(-self.xAng)*deltaTime
        if keysDown[b'a']:
            self.pos[0] -= self.maxVelocity*math.cos(-self.xAng)*deltaTime
            self.pos[2] += self.maxVelocity*math.sin(-self.xAng)*deltaTime
        if keysDown[b's']:
            self.pos[2] += self.maxVelocity*math.cos(-self.xAng)*deltaTime
            self.pos[0] += self.maxVelocity*math.sin(-self.xAng)*deltaTime
        if keysDown[b'w']:
            self.pos[2] -= self.maxVelocity*math.cos(-self.xAng)*deltaTime
            self.pos[0] -= self.maxVelocity*math.sin(-self.xAng)*deltaTime
    def update(self):
        if self.model != None:
            self.model.SetPosition(self.pos)
        self.camPosition = [-self.pos[0],self.pos[1]-1,-self.pos[2]]
        rotz = pyrr.matrix44.create_from_z_rotation(self.yAng*math.sin(self.xAng))
        rotx = pyrr.matrix44.create_from_x_rotation(self.yAng*math.cos(self.xAng))
        rot = np.matmul(np.matmul(pyrr.matrix44.create_from_y_rotation(self.xAng),rotz),rotx)
        self.camModel = np.matmul(rot,np.transpose(pyrr.matrix44.create_from_translation(np.array(self.camPosition))))
        
    
