from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

w,h= 500,500
def square(x,y,s):
    glBegin(GL_QUADS)
    glVertex3f(x, y,0)
    glVertex3f(x+s, y,0)
    glVertex3f(x+s, y+s,0)
    glVertex3f(x, y+s,1)
    glEnd()

x = 100
y = 100

def iterate():
    glViewport(0, 0, 500, 500)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, (500 / 500), 1, 500.0)
    #glOrtho(0.0, 500, 0.0, 500, 0.0, 1.0)
    glTranslatef(0.0, 0.0, -10)
    glMatrixMode (GL_MODELVIEW)
    glLoadIdentity()

def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    iterate()
    glColor3f(1.0, 0.0, 3.0)
    square(x,y,100)
    glutSwapBuffers()

def keyPressed(*args):
    global x
    x-=1
    print(args[0])

glutInit()
glutInitDisplayMode(GLUT_RGBA)
glutInitWindowSize(500, 500)
glutInitWindowPosition(0, 0)
wind = glutCreateWindow("OpenGL Coding Practice")
glutDisplayFunc(showScreen)
glutIdleFunc(showScreen)
glutKeyboardFunc(keyPressed)
glutMainLoop()
