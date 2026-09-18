"Assignment->2"

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import time


WIDTH , HEIGHT = 650, 750
L_EDGE, R_EDGE = -300, 300
B_EDGE, T_EDGE = -350, 350

CATCHER_Y = -285
CATCHER_BOTTOM_WIDTH = 90
CATCHER_TOP_WIDTH = 64
CATCHER_HEIGHT = 28
DIAMOND_RADIUS = 18

INITIAL_FALL_SPEED = 118.0
SPEED_INCREASE = 11.0
FALL_ACCELERATION = 2.5
PLAYER_SPEED = 420.0


RED = (1.0, 0.15, 0.15)
WHITE = (1.0, 1.0, 1.0)

score = 0
fall_speed = INITIAL_FALL_SPEED
catcher_x = 0.0
diamond_x = 0.0
diamond_y = 0.0
paused = False
game_over = False
cheat_code = False
last_time = time.perf_counter()


def find_zone(x0, y0, x1, y1):
    """finding the zone."""
    dx, dy = x1 - x0, y1 - y0
    if abs(dx) >= abs(dy):
        if dx >= 0:
            return 0 if dy >= 0 else 7
        return 3 if dy >= 0 else 4
    if dx >= 0:
        return 1 if dy >= 0 else 6
    return 2 if dy >= 0 else 5


def convert_zone0(x, y, zone):
    """Map a point from any  zone to Zone 0."""
    if zone == 0:
        return x, y
    if zone == 1:
        return y, x
    if zone == 2:
        return y, -x
    if zone == 3:
        return -x, y
    if zone == 4:
        return -x, -y
    if zone == 5:
        return -y, -x
    if zone == 6:
        return -y, x
    return x, -y


def convert_from_zone0(x, y, zone):
    """Map a Zone-0 point back into its original Bresenham zone."""
    if zone == 0:
        return x, y
    if zone == 1:
        return y, x
    if zone == 2:
        return -y, x
    if zone == 3:
        return -x, y
    if zone == 4:
        return -x, -y
    if zone == 5:
        return -y, -x
    if zone == 6:
        return y, -x
    return x, -y


def midpoint_line(x0, y0, x1, y1):

    dx, dy = x1 - x0, y1 - y0
    d = 2 * dy - dx
    eastInc, north_eastInc = 2 * dy, 2 * (dy - dx)
    points = []
    while x0 <= x1:
        points.append((x0, y0))
        if d >= 0:
            y0 += 1
            d += north_eastInc
        else:
            d += eastInc
        x0 += 1
    return points


def plot_point(x, y):
    """Plot one generated midpoint pixel"""
    glVertex2f(x, y)


def draw_line(x0, y0, x1, y1):
    "Draw a line through 8-zone conversion and GL_POINTS."
    x0, y0, x1, y1 = round(x0), round(y0), round(x1), round(y1)
    if x0 == x1 and y0 == y1:
        glBegin(GL_POINTS)
        plot_point(x0, y0)
        glEnd()
        return

    zone = find_zone(x0, y0, x1, y1)
    zone0_start = convert_zone0(x0, y0, zone)
    zone0_end = convert_zone0(x1, y1, zone)
    if zone0_start[0] > zone0_end[0]:
        zone0_start, zone0_end = zone0_end, zone0_start

    glBegin(GL_POINTS)
    for point_x, point_y in midpoint_line(*zone0_start, *zone0_end):
        actual_x, actual_y = convert_from_zone0(point_x, point_y, zone)
        draw_pixel(actual_x, actual_y)
    glEnd()


def draw_catcher():
    color = RED if game_over else WHITE
    glColor3f(*color)
    half_bottom = CATCHER_BOTTOM_WIDTH / 2
    half_top = CATCHER_TOP_WIDTH / 2
    bottom_left = (catcher_x - half_bottom, CATCHER_Y)
    bottom_right = (catcher_x + half_bottom, CATCHER_Y)
    top_left = (catcher_x - half_top, CATCHER_Y + CATCHER_HEIGHT)
    top_right = (catcher_x + half_top, CATCHER_Y + CATCHER_HEIGHT)
    draw_line(*bottom_left, *bottom_right)
    draw_line(*bottom_left, *top_left)
    draw_line(*top_left, *top_right)
    draw_line(*top_right, *bottom_right)


def draw_diamond():
    glColor3f(1.0, 1.0, 1.0)
    top = (diamond_x, diamond_y + DIAMOND_RADIUS)
    right = (diamond_x + DIAMOND_RADIUS, diamond_y)
    bottom = (diamond_x, diamond_y - DIAMOND_RADIUS)
    left = (diamond_x - DIAMOND_RADIUS, diamond_y)
    draw_line(*top, *right)
    draw_line(*right, *bottom)
    draw_line(*bottom, *left)
    draw_line(*left, *top)


def play_pause_button():
    glColor3f(1.0, 0.68, 0.0)
    if paused or game_over:
        draw_line(-12, 286, -12, 324)
        draw_line(-12, 324, 20, 305)
        draw_line(20, 305, -12, 286)
    else:
        draw_line(-10, 286, -10, 324)
        draw_line(10, 286, 10, 324)

def restart_button():
    glColor3f(0.0, 0.85, 0.85)
    draw_line(-270, 305, -225, 305)
    draw_line(-270, 305, -252, 323)
    draw_line(-270, 305, -252, 287)


def exit_button():
    glColor3f(1.0, 0.15, 0.15)
    draw_line(245, 286, 280, 324)
    draw_line(245, 324, 280, 286)


def draw_buttons():
    restart_button()
    play_pause_button()
    exit_button()


def spawn_diamond():
    global diamond_x, diamond_y, diamond_color
    diamond_x = random.randint(LEFT_EDGE + DIAMOND_RADIUS, RIGHT_EDGE - DIAMOND_RADIUS)
    diamond_y = TOP_EDGE - 55
    # At least two strong channels keep every spawned color visibly bright.
    channels = [random.uniform(0.35, 1.0) for _ in range(3)]
    channels[random.randrange(3)] = 1.0
    diamond_color = tuple(channels)


def catcher_bounds():
    half_width = CATCHER_BOTTOM_WIDTH / 2
    return catcher_x - half_width, catcher_x + half_width, CATCHER_Y, CATCHER_Y + CATCHER_HEIGHT


def diamond_bounds():
    return (diamond_x - DIAMOND_RADIUS, diamond_x + DIAMOND_RADIUS,
            diamond_y - DIAMOND_RADIUS, diamond_y + DIAMOND_RADIUS)


def aabb_overlap(a, b):
    return a[0] <= b[1] and a[1] >= b[0] and a[2] <= b[3] and a[3] >= b[2]


def reset_game():
    global score, fall_speed, catcher_x, paused, game_over, last_time
    score = 0
    fall_speed = INITIAL_FALL_SPEED
    catcher_x = 0.0
    paused = False
    game_over = False
    spawn_diamond()
    last_time = time.perf_counter()
    print("Starting Over", flush=True)


def finish_game():
    global game_over
    game_over = True
    print(f"Game Over! Score: {score}", flush=True)


def animation():
    """Advance the game using delta time, then request the next rendered frame."""
    global diamond_y, fall_speed, score, catcher_x, last_time
    now = time.perf_counter()
    dt = min(now - last_time, 0.05)  # Avoid a giant jump after dragging a window.
    last_time = now

    if not game_over and not paused:
        if cheat_mode:
            # Move continuously, but fast enough to arrive before the diamond reaches the catcher.
            time_to_catcher = max((diamond_y - (CATCHER_Y + CATCHER_HEIGHT + DIAMOND_RADIUS)) / fall_speed, 0.01)
            needed_speed = abs(diamond_x - catcher_x) / time_to_catcher
            catch_step = max(PLAYER_SPEED, needed_speed * 1.05) * dt
            half_width = CATCHER_BOTTOM_WIDTH / 2
            # Centering the catcher is unnecessary; this reachable target still overlaps
            # the diamond and keeps the catcher entirely inside the window.
            target_x = max(L_EDGE + half_width, min(R_EDGE - half_width, diamond_x))
            if abs(target_x - catcher_x) <= step:
                catcher_x = target_x
            else:
                catcher_x += catch_step if target_x > catcher_x else -step

        fall_speed += FALL_ACCELERATION * dt
        diamond_y -= fall_speed * dt
        if aabb_overlap(catcher_bounds(), diamond_bounds()):
            score += 1
            print(f"Score: {score}", flush=True)
            fall_speed += SPEED_INCREASE
            spawn_diamond()
        elif diamond_y + DIAMOND_RADIUS < CATCHER_Y:
            finish_game()

    glutPostRedisplay()


def keyboard_call(key, _x, _y):
    global cheat_code
    if key.lower() == b"c":
        cheat_code = not cheat_code
    glutPostRedisplay()


def special_key_call(key, _x, _y):
    global catcher_x
    if game_over or paused or cheat_code:
        return
    move_amnt = 26
    half_width = CATCHER_BOTTOM_WIDTH / 2
    if key == GLUT_KEY_LEFT:
        catcher_x = max(L_EDGE + half_width, catcher_x - move_amnt)
    elif key == GLUT_KEY_RIGHT:
        catcher_x = min(R_EDGE - half_width, catcher_x + move_amnt)
    glutPostRedisplay()


def mouse_call(button, state, x, y):
    global paused, last_time
    if button != GLUT_LEFT_BUTTON or state != GLUT_DOWN:
        return
    click_x = x - WIDTH / 2
    click_y = HEIGHT / 2 - y
    if -285 <= world_x <= -210 and 275 <= world_y <= 335:
        reset_game()
    elif -45 <= world_x <= 45 and 275 <= world_y <= 335 and not game_over:
        paused = not paused
        last_time = time.perf_counter()
    elif 225 <= world_x <= 295 and 275 <= world_y <= 335:
        print(f"Goodbye! Score: {score}", flush=True)
        glutLeaveMainLoop()
    glutPostRedisplay()


def setup_projection():
    glViewport(0, 0, WIDTH, HEIGHT)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(L_EDGE, R_EDGE, BO_EDGE, T_EDGE, 0, 1)
    glMatrixMode(GL_MODELVIEW)


def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    draw_buttons()
    draw_diamond()
    draw_catcher()
    glutSwapBuffers()


def main():
    glutInit()
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE)
    glutInitWindowSize(WIDTH, HEIGHT)
    glutInitWindowPosition(110, 64)
    glutCreateWindow(b"lab 2 - Catch the Diamonds")
    setup_projection()
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glPointSize(2)
    spawn_diamond()
    print("Starting Over", flush=True)
    glutDisplayFunc(display)
    glutIdleFunc(animation)
    glutKeyboardFunc(keyboard_call)
    glutSpecialFunc(special_key_call)
    glutMouseFunc(mouse_call)
    glutMainLoop()


if __name__ == "__main__":
    main()
