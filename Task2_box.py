from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random


WIDTH = 600
BOUND = 250

points = []
speed = 0.7
blinking = False
frozen = False
blink_counter = 0

SPEED_STEP = 1.20
SPEED_MIN = 0.15
SPEED_MAX = 2.0
BLINK_HALF_PERIOD = 30


def convert_coordinate(x, y):
   return x - (WIDTH / 2),( WIDTH / 2) - y
  

def box_border():
    glLineWidth(3)
    glColor3f(1.0, 1.0, 1.0)

    glBegin(GL_LINES)
    glVertex2f(-BOUND, -BOUND)
    glVertex2f(BOUND, -BOUND)

    glVertex2f(BOUND, -BOUND)
    glVertex2f(BOUND, BOUND)

    glVertex2f(BOUND, BOUND)
    glVertex2f(-BOUND, BOUND)

    glVertex2f(-BOUND, BOUND)
    glVertex2f(-BOUND, -BOUND)
    glEnd()


def draw_points():
    hidden_phase = blinking and ((blink_counter // BLINK_HALF_PERIOD) % 2 == 1)
    if hidden_phase:
        return

    glPointSize(8)
    glBegin(GL_POINTS)
    for p in points:
        glColor3f(*p["color"])
        glVertex2f(p["x"], p["y"])
    glEnd()


def setup_projection():
    glViewport(0, 0, WIDTH, WIDTH)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-BOUND - 20, BOUND + 20, -BOUND - 20, BOUND + 20, 0, 1)
    glMatrixMode(GL_MODELVIEW)


def display():
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    box_border()
    draw_points()

    glutSwapBuffers()


def animate():
    global blink_counter

    if frozen:
        glutPostRedisplay()
        return

    for p in points:
        p["x"] += p["dx"] * speed
        p["y"] += p["dy"] * speed

        if p["x"] > BOUND or p["x"] < -BOUND:
            p["dx"] *= -1
            p["x"] = max(-BOUND, min(BOUND, p["x"]))

        if p["y"] > BOUND or p["y"] < -BOUND:
            p["dy"] *= -1
            p["y"] = max(-BOUND, min(BOUND, p["y"]))

    blink_counter += 1
    glutPostRedisplay()


def mouse_listener(button, state, x, y):
    global blinking, blink_counter

    if frozen or state != GLUT_DOWN:
        return

    wx, wy = convert_coordinate(x, y)

    if button == GLUT_RIGHT_BUTTON:
        if -BOUND <= wx <= BOUND and -BOUND <= wy <= BOUND:
            dx = random.choice([-1, 1]) * random.uniform(1.5, 3.5)
            dy = random.choice([-1, 1]) * random.uniform(1.5, 3.5)
            color = (random.random(), random.random(), random.random())
            points.append({"x": wx, "y": wy, "dx": dx, "dy": dy, "color": color})

    elif button == GLUT_LEFT_BUTTON:
        blinking = not blinking
        blink_counter = 0

    glutPostRedisplay()


def specl_key_listener(key, x, y):
    global speed

    if frozen:
        return

    if key == GLUT_KEY_UP:
        speed = min(speed * SPEED_STEP, SPEED_MAX)
    elif key == GLUT_KEY_DOWN:
        speed = max(speed / SPEED_STEP, SPEED_MIN)

    glutPostRedisplay()


def key_listener(key, x, y):
    global frozen

    if key == b" ":
        frozen = not frozen
        glutPostRedisplay()


def main():
    glutInit()
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE)
    glutInitWindowSize(WIDTH, WIDTH)
    glutInitWindowPosition(170, 150)
    glutCreateWindow(b"The Amazing Box")

    setup_projection()
    glClearColor(0, 0, 0, 1)

    glutDisplayFunc(display)
    glutIdleFunc(animate)
    glutMouseFunc(mouse_listener)
    glutSpecialFunc(specl_key_listener)
    glutKeyboardFunc(key_listener)

    glutMainLoop()


if __name__ == "__main__":
    main()
