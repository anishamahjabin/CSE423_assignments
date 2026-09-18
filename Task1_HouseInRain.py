from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random


WIDTH, HEIGHT = 700, 700
rain_drops = []
rain_slant = 0.0
background_sky = 0.06


def make_rain():
    global rain_drops
    rain_drops = []
    for i in range(90):
        x = random.randint(-300, 245)
        y = random.randint(-240, 250)
        rain_drops.append([x, y])


def setup_projection():
    glViewport(0, 0, WIDTH, HEIGHT)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-250, 250, -250, 250, 0, 1)
    glMatrixMode(GL_MODELVIEW)


def scene():
    glBegin(GL_TRIANGLES)
    #sky
    glColor3f(background_sky, background_sky, background_sky + 0.05)
    glVertex2f(-250, -250); glVertex2f(250, -250); glVertex2f(250, 250)
    glVertex2f(-250, -250); glVertex2f(250, 250); glVertex2f(-250, 250)
    #ground
    glColor3f(0.22, 0.48, 0.24)
    glVertex2f(-250, -250); glVertex2f(250, -250); glVertex2f(250, -170)
    glVertex2f(-250, -250); glVertex2f(250, -170); glVertex2f(-250, -170)

    glEnd()


def house():
    glBegin(GL_TRIANGLES)
    #House walls using two triangles
    glColor3f(0.90, 0.77, 0.66)
    glVertex2f(-130, -170); glVertex2f(130, -170); glVertex2f(130, 40)
    glVertex2f(-130, -170); glVertex2f(130, 40); glVertex2f(-130, 40)

    #house roof using one triangle
    glColor3f(0.67, 0.1, 0.46)
    glVertex2f(-165, 40); glVertex2f(0, 165); glVertex2f(165, 40)

    #house door using two triangles
    glColor3f(0.12, 0.12, 0.88)
    glVertex2f(-35, -170); glVertex2f(35, -170); glVertex2f(35, -40)
    glVertex2f(-35, -170); glVertex2f(35, -40); glVertex2f(-35, -40)

    #house windows using four triangles
    glColor3f(0.67, 0.77, 0.34)
    glVertex2f(-100, -45); glVertex2f(-55, -45); glVertex2f(-55, 0)
    glVertex2f(-100, -45); glVertex2f(-55, 0); glVertex2f(-100, 0)
    glVertex2f(55, -45); glVertex2f(100, -45); glVertex2f(100, 0)
    glVertex2f(55, -45); glVertex2f(100, 0); glVertex2f(55, 0)

    glEnd()

    # Draw house outline and window panes
    glLineWidth(2)
    glColor3f(0.03, 0.03, 0.03)
    glBegin(GL_LINES)

    glVertex2f(-130, -170); glVertex2f(130, -170)
    glVertex2f(130, -170); glVertex2f(130, 40)
    glVertex2f(130, 40); glVertex2f(-130, 40)
    glVertex2f(-130, 40); glVertex2f(-130, -170)
    glVertex2f(-165, 40); glVertex2f(0, 165)
    glVertex2f(0, 165); glVertex2f(165, 40)
    glVertex2f(-165, 40); glVertex2f(165, 40)
    glVertex2f(-35, -170); glVertex2f(-35, -40)
    glVertex2f(35, -170); glVertex2f(35, -40)
    glVertex2f(-35, -40); glVertex2f(35, -40)

    glEnd()

    #window divider
    glLineWidth(1)
    glBegin(GL_LINES)

    glVertex2f(-100, -22); glVertex2f(-55, -22)
    glVertex2f(-78, -45); glVertex2f(-78, 0)
    glVertex2f(55, -22); glVertex2f(100, -22)
    glVertex2f(78, -45); glVertex2f(78, 0)

    glEnd()

    # door handle
    glLineWidth(5)
    glColor3f(0.25, 1, 0.40)
    glBegin(GL_LINES)
    glVertex2f(20, -105); glVertex2f(25, -105)
    glEnd()


def rain():
    glLineWidth(1)
    glColor3f(0.35, 0.75, 1.0)
    glBegin(GL_LINES)
    for drop in rain_drops:
        x, y = drop
        glVertex2f(x, y)
        glVertex2f(x + rain_slant, y - 18)
    glEnd()

def animate():
    global rain_drops

    for drop in rain_drops:
        drop[0] += rain_slant * 0.05
        drop[1] -= 3

        if drop[1] < -250:
            drop[1] = 250
            drop[0] = random.randint(-245, 245)

        if drop[0] < -250:
            drop[0] = 250
        elif drop[0] > 250:
            drop[0] = -250
    #redraw the scene continuously after updating the rain drops
    glutPostRedisplay()


def keyboard(key, x, y):
    global background_sky

    # Day
    if key == b'd':
        background_sky += 0.03
        if background_sky > 0.9:
            background_sky = 0.9
    #keeps the value within a valid range(0.01-0.9) to avoid unrealistic sky colors
    # Night
    elif key == b'n':
        background_sky -= 0.03
        if background_sky < 0.01:
            background_sky = 0.01

    glutPostRedisplay()


def special_keys(key, x, y):
    global rain_slant

    if key == GLUT_KEY_LEFT:
        rain_slant -= 1

    elif key == GLUT_KEY_RIGHT:
        rain_slant += 1
    
    #limits the slant between -16 to 16
    
    if rain_slant > 16:
        rain_slant = 16

    if rain_slant < -16:
        rain_slant = -16
    
    # redraw thw scene continuously after any changes
    glutPostRedisplay()


def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    
    setup_projection()
    scene()
    house()
    rain()

    glutSwapBuffers() #swaps the front and back buffers to display the rendered scene on the screen


def main():
    glutInit()
    glutInitDisplayMode(GLUT_RGBA)
    glutInitWindowSize(WIDTH, HEIGHT)
    glutInitWindowPosition(0,0)
    glutCreateWindow(b"House in Rainfall")
    make_rain()
    glutDisplayFunc(display)
    glutIdleFunc(animate)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(special_keys)

    glutMainLoop()


if __name__ == "__main__":
    main()   