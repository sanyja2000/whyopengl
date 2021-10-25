from OpenGL.GL import *
from PIL import Image, ImageFont, ImageDraw
from renderer import Shader,VertexArray, VertexBuffer, IndexBuffer, VertexBufferLayout
import numpy as np
from ctypes import sizeof, c_float

# tmp import
import time

class FontHandler:
    def __init__(self):
##        self.vshaderold = """
##        in vec2 position;
##        in vec2 texCoord;
##        out vec2 v_TexCoord;
##
##        uniform vec4 u_PosRotScl;
##        void main()
##        {
##            gl_Position = vec4(position.x*u_PosRotScl.w+u_PosRotScl.x,position.y*u_PosRotScl.w+u_PosRotScl.y,-1.0,1.0); // check this z
##            v_TexCoord = texCoord;
##        }
##        """
##        self.fshaderold = """
##        out vec4 color;
##
##        in vec2 v_TexCoord;
##        uniform sampler2D u_Texture;
##
##        void main(){
##            vec4 texColor = texture(u_Texture, v_TexCoord);
##           color = texColor;
##            //color = vec4(0.8,0.3,0.2,1.0);
##        }"""
        self.vshadernew = """
        #version 330
        layout(location=0) in vec2 position;
        layout(location=1) in vec2 texCoord;
        layout(location=2) in float charIndex;
        out vec2 v_TexCoord;
        out float v_charIndex;

        uniform vec4 u_PosRotScl;
        void main()
        {
            gl_Position = vec4(position.x*u_PosRotScl.w+u_PosRotScl.x,position.y*u_PosRotScl.w+u_PosRotScl.y,-1.0,1.0); // check this z
            v_TexCoord = texCoord;
            v_charIndex = charIndex;
        }
        """
        self.fshadernew = """
        #version 330
        layout(location=0) out vec4 color;

        in vec2 v_TexCoord;
        in float v_charIndex;
        uniform sampler2D u_Texture;

        void main(){
            float x = 1.0/16.0*mod(int(v_charIndex),16);
            float y = 1.0/16.0*(15.0-floor(v_charIndex/16));
            vec4 texColor = texture(u_Texture, vec2(x,y)+v_TexCoord);
            if(texColor.r<0.3){color = vec4(0.0,0.0,0.0,0.0);}
            else{color = texColor;}
            //color = vec4(0.8,0.3,0.2,1.0);
        }"""
        self.shader = Shader(self.vshadernew, self.fshadernew)

        self.letterDict = {" ":0,"!":1,'"':2,"#":3,"$":4,"%":5,"&":6,"'":7,"(":8,")":9,"*":10,"+":11,",":12,"-":13,".":14,"/":15,
                           "0":16,"1":17,"2":18,"3":19,"4":20,"5":21,"6":22,"7":23,"8":24,"9":25,":":26,";":27,"<":28,"=":29,">":30,"?":31,
                           "@":32,"A":33,"B":34,"C":35,"D":36,"E":37,"F":38,"G":39,"H":40,"I":41,"J":42,"K":43,"L":44,"M":45,"N":46,"O":47,
                           "P":48,"Q":49,"R":50,"S":51,"T":52,"U":53,"V":54,"W":55,"X":56,"Y":57,"Z":58,"[":59,"\\":60,"]":61,"^":62,"_":63}
        

        #vec2 pos, vec2 uv, float texIndex
        """
        self.points = np.array([0, 0, 0, 0, 1.0,
                                1, 0, 1/16, 0, 1.0,
                                1, 1, 1/16, 1/16, 1.0,
                                0, 1, 0, 1/16, 1.0],dtype='float32')

        """

        self.max_letter_count = 20
        
        self.indexList = []
        for i in range(self.max_letter_count):
            self.indexList += [0+i*4,1+i*4,2+i*4,2+i*4,3+i*4,0+i*4]
        #self.indices = np.array([0,1,2, 2,3,0, 4,5,6, 6,7,4])
        self.indices = np.array(self.indexList)


        self.values = [[0,0,0,0],[1,0,1/16,0],[1,1,1/16,1/16],[0,1,0,1/16]]

        
        self.va = VertexArray()
        self.vb = VertexBuffer(None, draw=GL_DYNAMIC_DRAW, size=self.max_letter_count*4*sizeof(c_float)*5)
        self.layout = VertexBufferLayout()
        self.layout.PushF(2)
        self.layout.PushF(2)
        self.layout.PushF(1)
        self.va.AddBuffer(self.vb, self.layout)
        self.ib = IndexBuffer(self.indices, len(self.indices))

        self.width = 100
        self.height = 50

        self.textureAtlas = Image.open("res/fontTexture.png") #256x256px 16x16 chars 16chars/row
        data = self.textureAtlas.tobytes("raw", "RGBA", 0, -1)
        
        self.width, self.height = self.textureAtlas.size

        self.TextureAtlasId = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D,self.TextureAtlasId)
        
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER,GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER,GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S,GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T,GL_CLAMP_TO_EDGE)

        
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.width, self.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, data)

        glBindTexture(GL_TEXTURE_2D, 0)
        #self.font = ImageFont.truetype("res/Montserrat-Regular.ttf", 70)
        
    def drawText(self,txt,x,y,scl,renderer):

        self.shader.Bind()
        self.va.Bind()
        glBindTexture(GL_TEXTURE_2D,self.TextureAtlasId)
        start = time.perf_counter()

        #txt = "SZIASZTOK!"
        self.points = np.zeros((len(txt)*20), np.float32)
        xoffset = 0.7
        for c in range(len(txt)):
            for d in range(4):
                self.points[c*20+d*5] = self.values[d][0]+c*xoffset
                self.points[c*20+1+d*5] = self.values[d][1]
                self.points[c*20+2+d*5] = self.values[d][2]
                self.points[c*20+3+d*5] = self.values[d][3]
                self.points[c*20+4+d*5] = self.letterDict[txt[c]]

        #print(self.points)     
        self.vb.Bind()
        glBufferSubData(GL_ARRAY_BUFFER, 0, sizeof(c_float)*len(self.points),self.points)
           

        end = time.perf_counter()
        self.shader.SetUniform4f("u_PosRotScl",x,y,0,scl)
        self.shader.SetUniform1i("u_Texture",0)
              
        renderer.Draw(self.va,self.ib,self.shader,drawUntil=len(txt)*6)
        glBindTexture(GL_TEXTURE_2D, 0)

        return end-start
