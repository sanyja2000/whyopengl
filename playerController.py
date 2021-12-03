import math,pyrr, numpy as np

def lerp(f, t, n):
    return f*(1-n)+t*n

def lerpVec3(f,t,n):
    out = []
    for x in range(3):
        out.append(f[x]*(1-n)+t[x]*n)
    return np.array(out)

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
        self.grounded = True
        self.xAng = 0
        self.yAng = 0
        self.camera = None

        self.animating = 0
        self.lastInteractedWith = None

        self.distanceTraveled = 0
        self.lastWalkSound = 0
        self.fallSound = False
    def moveWithKeys(self,inputHandler,deltaTime):
        if self.camera.movement == "fixed":
            return
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
        if inputHandler.isKeyHeldDown(b'd'):
            self.pos[0] += self.vel[0]
            self.pos[2] -= self.vel[2]
            moved = True
        if inputHandler.isKeyHeldDown(b'a'):
            self.pos[0] -= self.vel[0]
            self.pos[2] += self.vel[2]
            moved = True
        if inputHandler.isKeyHeldDown(b's'):
            self.pos[2] += self.vel[0]
            self.pos[0] += self.vel[2]
            moved = True
        if inputHandler.isKeyHeldDown(b'w'):
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

    def update(self,deltaTime,inputHandler):
        if self.animating>0:
            self.animating -= deltaTime*3
            if self.animating<0:
                self.animating = 0

        if self.model != None:
            self.model.SetPosition(self.pos)

        

        if not inputHandler.interactingWith is None:
            self.lastInteractedWith = inputHandler.interactingWith
            a = lerp(self.yAng,0.7853,(1-self.animating))
            b = lerp(self.xAng%6.28,3.1415,(1-self.animating))
            #a = 0.7853
            #b = 3.1415
            #self.camPosition = -1*inputHandler.interactingWith.model.pos+np.array([0,-0.35,0.3])
            self.camPosition = lerpVec3([-self.pos[0],-self.pos[1]-1,-self.pos[2]],-1*inputHandler.interactingWith.model.pos+np.array([0,-0.35,0.3]),(1-self.animating))
        else:
            a = lerp(0.7853,self.yAng,(1-self.animating))
            b = lerp(3.1415,self.xAng%6.28,(1-self.animating))
            #a = self.yAng
            #b = self.xAng
        
            if self.lastInteractedWith is not None:
                self.camPosition = lerpVec3(-1*self.lastInteractedWith.model.pos+np.array([0,-0.35,0.3]),[-self.pos[0],-self.pos[1]-1+math.sin(self.distanceTraveled*2*2)*0.02,-self.pos[2]],(1-self.animating))
            else:
                self.camPosition = [-self.pos[0],-self.pos[1]-1+math.sin(self.distanceTraveled*2*2)*0.02,-self.pos[2]]
            #
            """
            rotz = pyrr.matrix44.create_from_z_rotation(self.yAng*math.sin(self.xAng))
            rotx = pyrr.matrix44.create_from_x_rotation(self.yAng*math.cos(self.xAng))
            rot = np.matmul(np.matmul(pyrr.matrix44.create_from_y_rotation(self.xAng),rotz),rotx)
            """
        if self.camera.movement == "free":
            rotz = pyrr.matrix44.create_from_z_rotation(a*math.sin(b))
            rotx = pyrr.matrix44.create_from_x_rotation(a*math.cos(b))
            rot = np.matmul(np.matmul(pyrr.matrix44.create_from_y_rotation(b),rotz),rotx)
        else:
            rotz = pyrr.matrix44.create_from_z_rotation(self.camera.rot[2])
            rotx = pyrr.matrix44.create_from_x_rotation(self.camera.rot[0])
            rot = np.matmul(np.matmul(pyrr.matrix44.create_from_y_rotation(self.camera.rot[1]),rotz),rotx)
        #rotz = pyrr.matrix44.create_from_z_rotation(a*math.sin(b))
        #rotx = pyrr.matrix44.create_from_x_rotation(a*math.cos(b))
        #rot = np.matmul(np.matmul(rotz,rotx),pyrr.matrix44.create_from_y_rotation(b))
        self.camModel = np.matmul(rot,np.transpose(pyrr.matrix44.create_from_translation(np.array(self.camPosition))))
        
    
