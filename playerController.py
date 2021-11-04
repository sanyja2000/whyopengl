import math,pyrr, numpy as np

class Player:
    def __init__(self):
        self.pos = [-6.75,0,-6.75]
        #self.pos = [-6.75,30,-6.75] #<- default, uncomment to fall on spawn
        self.rot = [0,0,0]
        self.vel = [0,0,0]
        self.maxVelocity = 5
        self.acc = [0,0,0]
        self.model = None
        self.camPosition = [0,-1,0]
        self.camRotation = [-1.57,0,0]
        self.grounded = False
        self.xAng = 0
        self.yAng = 0
        self.distanceTraveled = 0
        self.lastWalkSound = 0
        self.fallSound = False
    def moveWithKeys(self,inputHandler,deltaTime):
        keysDown = inputHandler.keysDown
        if not inputHandler.interactingWith is None:
            inputHandler.interactingWith.moveWithKeys(inputHandler,deltaTime)
            return
        if not self.grounded:
            return
        self.vel[0] = self.maxVelocity*math.cos(-self.xAng)*deltaTime
        self.vel[2] = self.maxVelocity*math.sin(-self.xAng)*deltaTime
        cubeW = 9.5
        moved = False
        if keysDown[b'd']:
            self.pos[0] += self.vel[0]
            self.pos[2] -= self.vel[2]
            moved = True
        if keysDown[b'a']:
            self.pos[0] -= self.vel[0]
            self.pos[2] += self.vel[2]
            moved = True
        if keysDown[b's']:
            self.pos[2] += self.vel[0]
            self.pos[0] += self.vel[2]
            moved = True
        if keysDown[b'w']:
            self.pos[2] -= self.vel[0]
            self.pos[0] -= self.vel[2]
            moved = True
 
        if moved:
            self.distanceTraveled += self.maxVelocity*deltaTime
        

        if self.pos[0] > cubeW:
            self.pos[0] = cubeW
        if self.pos[0] < -1*cubeW:
            self.pos[0] = -1*cubeW
        if self.pos[2] > cubeW:
            self.pos[2] = cubeW
        if self.pos[2] < -1*cubeW:
            self.pos[2] = -1*cubeW
    def update(self,deltaTime):
        inAHole = False
        if self.pos[0] > 5.5 and self.pos[0] < 7 and self.pos[2] > 5.5 and self.pos[2] < 7:
            inAHole = True
            self.grounded = False
        if not self.grounded:
            self.vel[1]+=-0.02*deltaTime
            if self.vel[1] > self.maxVelocity*3:
                self.vel[1] = self.maxVelocity*3
            if self.vel[1] < -1*self.maxVelocity*3:
                self.vel[1] = -1*self.maxVelocity*3
            self.pos[1]+=self.vel[1]
            if self.pos[1] < 0 and not inAHole:
                print("grounded")
                self.fallSound = True
                self.vel[1] = 0
                self.pos[1] = 0
                self.grounded = True
            if self.pos[1] < -7:
                self.pos = [-6.75,30,-6.75]
            
        if self.model != None:
            self.model.SetPosition(self.pos)
        self.camPosition = [-self.pos[0],-self.pos[1]-1+math.sin(self.distanceTraveled*2*2)*0.02,-self.pos[2]]
        rotz = pyrr.matrix44.create_from_z_rotation(self.yAng*math.sin(self.xAng))
        rotx = pyrr.matrix44.create_from_x_rotation(self.yAng*math.cos(self.xAng))
        rot = np.matmul(np.matmul(pyrr.matrix44.create_from_y_rotation(self.xAng),rotz),rotx)
        self.camModel = np.matmul(rot,np.transpose(pyrr.matrix44.create_from_translation(np.array(self.camPosition))))
        
    
