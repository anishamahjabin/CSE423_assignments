from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random


WINDOW_WIDTH, WINDOW_HEIGHT = 500, 500
BOX_LEFT, BOX_RIGHT = -200, 200
BOX_BOTTOM, BOX_TOP = -200, 200

points = []
speed = 1.0
frozen = False
blink_on = False
blink_timer = 0.0


def setup_projection():
    glViewport(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-250, 250, -250, 250, 0, 1)
    glMatrixMode(GL_MODELVIEW)


def draw_scene():
    glLineWidth(2)
    glColor3f(1.0, 1.0, 1.0)
    glBegin(GL_LINES)
    glVertex2f(BOX_LEFT, BOX_BOTTOM); glVertex2f(BOX_RIGHT, BOX_BOTTOM)
    glVertex2f(BOX_RIGHT, BOX_BOTTOM); glVertex2f(BOX_RIGHT, BOX_TOP)
    glVertex2f(BOX_RIGHT, BOX_TOP); glVertex2f(BOX_LEFT, BOX_TOP)
    glVertex2f(BOX_LEFT, BOX_TOP); glVertex2f(BOX_LEFT, BOX_BOTTOM)
    glEnd()

    visible = not blink_on or int(blink_timer * 2) % 2 == 0
    glPointSize(8)
    glBegin(GL_POINTS)
    for point in points:
        if visible:
            glColor3f(point["r"], point["g"], point["b"])
        else:
            glColor3f(0.0, 0.0, 0.0)
        glVertex2f(point["x"], point["y"])
    glEnd()


def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    setup_projection()
    draw_scene()
    glutSwapBuffers()


def animate():
    global blink_timer

    if frozen:
        return

    if blink_on:
        blink_timer += 0.02

    for point in points:
        point["x"] += point["dx"] * speed
        point["y"] += point["dy"] * speed

        if point["x"] <= BOX_LEFT or point["x"] >= BOX_RIGHT:
            point["dx"] *= -1
            point["x"] = max(BOX_LEFT, min(BOX_RIGHT, point["x"]))

        if point["y"] <= BOX_BOTTOM or point["y"] >= BOX_TOP:
            point["dy"] *= -1
            point["y"] = max(BOX_BOTTOM, min(BOX_TOP, point["y"]))

    glutPostRedisplay()


def mouse_listener(button, state, x, y):
    global blink_on, blink_timer

    if frozen or state != GLUT_DOWN:
        return

    ox = x - (WINDOW_WIDTH / 2)
    oy = (WINDOW_HEIGHT / 2) - y

    if button == GLUT_RIGHT_BUTTON and BOX_LEFT <= ox <= BOX_RIGHT and BOX_BOTTOM <= oy <= BOX_TOP:
        points.append({
            "x": ox,
            "y": oy,
            "dx": random.choice([-1, 1]),
            "dy": random.choice([-1, 1]),
            "r": random.random(),
            "g": random.random(),
            "b": random.random()
        })
    elif button == GLUT_LEFT_BUTTON:
        blink_on = not blink_on
        blink_timer = 0.0

    glutPostRedisplay()


def special_key_listener(key, x, y):
    global speed

    if frozen:
        return

    if key == GLUT_KEY_UP:
        speed += 0.3
    elif key == GLUT_KEY_DOWN:
        speed = max(0.2, speed - 0.3)

    glutPostRedisplay()


def keyboard_listener(key, x, y):
    global frozen

    if key == b' ':
        frozen = not frozen

    glutPostRedisplay()


def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA)
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    glutInitWindowPosition(140, 140)
    glutCreateWindow(b"Task 2 - Amazing Box")

    glutDisplayFunc(display)
    glutIdleFunc(animate)
    glutMouseFunc(mouse_listener)
    glutSpecialFunc(special_key_listener)
    glutKeyboardFunc(keyboard_listener)
    glutMainLoop()


if __name__ == "__main__":
    main()
