from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random
import time


# Window and arena settings
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 800
GRID_LENGTH = 600
GRID_CELLS = 12
CELL_SIZE = (GRID_LENGTH * 2) / GRID_CELLS
PLAYER_LIMIT = GRID_LENGTH - 55

# Camera settings
fovY = 120
camera_angle = 45.0
camera_height = 650.0
camera_radius = 850.0
first_person = False
first_person_angle = 0.0

# Player and game state
player_x = 0.0
player_y = 0.0
player_angle = 0.0
player_life = 5
game_score = 0
bullets_missed = 0
game_over = False
cheat_mode = False
cheat_vision = False

# Animated objects
bullets = []
enemies = []
enemy_pulse = 0.0
last_update = time.time()
last_cheat_shot = 0.0


def draw_text(x, y, text, font= GLUT_BITMAP_HELVETICA_18):
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


def draw_cuboid(width, depth, height):
    glPushMatrix()
    glScalef(width, depth, height)
    glutSolidCube(1)
    glPopMatrix()


def draw_cylinder_between(start, end, radius):
    """Draw a cylinder whose local +Z axis runs from start to end."""
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    dz = end[2] - start[2]
    length = math.sqrt(dx * dx + dy * dy + dz * dz)
    if length == 0:
        return

    # Rotate the cylinder's default +Z direction onto the requested vector.
    angle = math.degrees(math.acos(max(-1.0, min(1.0, dz / length))))
    axis_x = -dy
    axis_y = dx

    glPushMatrix()
    glTranslatef(*start)
    if abs(angle) > 0.0001:
        glRotatef(angle, axis_x, axis_y, 0)
    gluCylinder(gluNewQuadric(), radius, radius, length, 10, 4)
    glPopMatrix()


def random_enemy_position():
    while True:
        x = random.uniform(-GRID_LENGTH + 70, GRID_LENGTH - 70)
        y = random.uniform(-GRID_LENGTH + 70, GRID_LENGTH - 70)
        if math.hypot(x - player_x, y - player_y) > 220:
            return [x, y]


def reset_enemy(enemy):
    position = random_enemy_position()
    enemy[0] = position[0]
    enemy[1] = position[1]


def reset_game():
    global player_x, player_y, player_angle
    global player_life, game_score, bullets_missed, game_over
    global cheat_mode, cheat_vision, first_person, first_person_angle
    global bullets, enemies
    global camera_angle, camera_height, last_update, last_cheat_shot

    restarting = game_over
    player_x = 0.0
    player_y = 0.0
    player_angle = 0.0
    player_life = 5
    game_score = 0
    bullets_missed = 0
    game_over = False
    cheat_mode = False
    cheat_vision = False
    first_person = False
    first_person_angle = 0.0
    camera_angle = 45.0
    camera_height = 650.0
    bullets = []
    enemies = [random_enemy_position() for _ in range(5)]
    last_update = time.time()
    last_cheat_shot = 0.0
    print("Game Restarted!" if restarting else "Game Started!", flush=True)
    print("Remaining Player Life: 5", flush=True)
    print("Game Score: 0", flush=True)
    print("Bullet missed: 0", flush=True)


def direction_from_angle(angle):
    radians = math.radians(angle)
    return -math.sin(radians), math.cos(radians)


def rotate_gun(angle_change):
    global player_angle
    player_angle = (player_angle + angle_change) % 360


def fire_bullet():
    if game_over:
        return
    dx, dy = direction_from_angle(player_angle)
    bullets.append([player_x + dx * 55, player_y + dy * 55, 55.0, dx, dy])
    print("Player Bullet Fired!", flush=True)


def draw_floor():
    half = GRID_LENGTH
    glBegin(GL_QUADS)
    for row in range(GRID_CELLS):
        for col in range(GRID_CELLS):
            if (row + col) % 2 == 0:
                glColor3f(1.0, 1.0, 1.0)
            else:
                glColor3f(0.65, 0.45, 0.9)
            x1 = -half + col * CELL_SIZE
            y1 = -half + row * CELL_SIZE
            x2 = x1 + CELL_SIZE
            y2 = y1 + CELL_SIZE
            glVertex3f(x1, y1, 0)
            glVertex3f(x2, y1, 0)
            glVertex3f(x2, y2, 0)
            glVertex3f(x1, y2, 0)
    glEnd()


def draw_boundaries():
    wall_height = 85
    wall_thickness = 22

    glColor3f(0.0, 0.0, 1.0)
    glPushMatrix()
    glTranslatef(-GRID_LENGTH, 0, wall_height / 2)
    draw_cuboid(wall_thickness, GRID_LENGTH * 2, wall_height)
    glPopMatrix()

    glColor3f(0.0, 1.0, 0.0)
    glPushMatrix()
    glTranslatef(GRID_LENGTH, 0, wall_height / 2)
    draw_cuboid(wall_thickness, GRID_LENGTH * 2, wall_height)
    glPopMatrix()

    glColor3f(0.0, 1.0, 1.0)
    glPushMatrix()
    glTranslatef(0, GRID_LENGTH, wall_height / 2)
    draw_cuboid(GRID_LENGTH * 2, wall_thickness, wall_height)
    glPopMatrix()

    glColor3f(1.0, 1.0, 1.0)
    glPushMatrix()
    glTranslatef(0, -GRID_LENGTH, wall_height / 2)
    draw_cuboid(GRID_LENGTH * 2, wall_thickness, wall_height)
    glPopMatrix()


def draw_player():
    glPushMatrix()
    glTranslatef(player_x, player_y, 0)
    glRotatef(player_angle, 0, 0, 1)
    if game_over:
        glTranslatef(0, 0, 28)
        glRotatef(90, 1, 0, 0)

    # Torso (cuboid)
    glColor3f(0.28, 0.40, 0.12)
    glPushMatrix()
    glTranslatef(0, 0, 62)
    draw_cuboid(55, 38, 72)
    glPopMatrix()

    # Do not draw the head around the camera in first-person view.
    if not first_person:
        glColor3f(0.0, 0.0, 0.0)
        glPushMatrix()
        glTranslatef(0, 0, 117)
        gluSphere(gluNewQuadric(), 20, 12, 10)
        glPopMatrix()

    # Arms reach diagonally toward the front (+Y), forming a V around the gun.
    glColor3f(1.0, 0.78, 0.58)
    for side in (-1, 1):
        shoulder = (side * 28, 8, 82)
        hand = (side * 9, 48, 82)
        draw_cylinder_between(shoulder, hand, 10)
        glPushMatrix()
        glTranslatef(*hand)
        gluSphere(gluNewQuadric(), 10, 10, 8)
        glPopMatrix()

    # Legs (cylinders)
    glColor3f(0.0, 0.0, 1.0)
    for side in (-1, 1):
        glPushMatrix()
        glTranslatef(side * 16, 0, 30)
        glRotatef(180, 1, 0, 0)
        gluCylinder(gluNewQuadric(), 10, 7, 34, 10, 4)
        glPopMatrix()

    # Gun barrel, aligned with the player's local forward (+Y) direction
    glColor3f(0.4, 0.4, 0.4)
    glPushMatrix()
    glTranslatef(0, 18, 85)
    glRotatef(-90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 8, 5, 62, 10, 4)
    glPopMatrix()

    glPopMatrix()


def draw_enemy(enemy):
    scale = 1.0 + 0.18 * math.sin(enemy_pulse)
    glPushMatrix()
    glTranslatef(enemy[0], enemy[1], 0)
    glScalef(scale, scale, scale)
    glColor3f(1.0, 0.0, 0.0)
    glPushMatrix()
    glTranslatef(0, 0, 27)
    gluSphere(gluNewQuadric(), 27, 12, 10)
    glPopMatrix()
    glColor3f(0.0, 0.0, 0.0)
    glPushMatrix()
    glTranslatef(0, 0, 58)
    gluSphere(gluNewQuadric(), 16, 10, 8)
    glPopMatrix()
    glPopMatrix()


def draw_bullets():
    glColor3f(1.0, 1.0, 0.0)
    for bullet in bullets:
        glPushMatrix()
        glTranslatef(bullet[0], bullet[1], bullet[2])
        glutSolidCube(12)
        glPopMatrix()


def nearest_enemy():
    if not enemies:
        return None
    return min(enemies, key=lambda enemy: math.hypot(enemy[0] - player_x,
                                                     enemy[1] - player_y))


def angle_to_enemy(enemy):
    dx = enemy[0] - player_x
    dy = enemy[1] - player_y
    return math.degrees(math.atan2(-dx, dy)) % 360


def angle_difference(a, b):
    return (a - b + 180) % 360 - 180


def keyboardListener(key, x, y):
    global player_x, player_y, player_angle, cheat_mode, cheat_vision
    global first_person_angle

    key = key.lower()
    if key == b'r' and game_over:
        reset_game()
        return
    if game_over:
        return

    if key == b'w' or key == b's':
        direction = 1 if key == b'w' else -1
        dx, dy = direction_from_angle(player_angle)
        player_x = max(-PLAYER_LIMIT, min(PLAYER_LIMIT,
                       player_x + direction * dx * 18))
        player_y = max(-PLAYER_LIMIT, min(PLAYER_LIMIT,
                       player_y + direction * dy * 18))
    elif key == b'a':
        rotate_gun(5)
    elif key == b'd':
        rotate_gun(-5)
    elif key == b'c':
        cheat_mode = not cheat_mode
        if cheat_mode:
            # Without V, cheat rotation is independent of the first-person view.
            first_person_angle = player_angle
        else:
            cheat_vision = False
    elif key == b'v' and cheat_mode:
        cheat_vision = not cheat_vision


def specialKeyListener(key, x, y):
    global camera_angle, camera_height
    if first_person:
        return
    if key == GLUT_KEY_UP:
        camera_height = min(1000, camera_height + 20)
    elif key == GLUT_KEY_DOWN:
        camera_height = max(180, camera_height - 20)
    elif key == GLUT_KEY_LEFT:
        camera_angle = (camera_angle + 3) % 360
    elif key == GLUT_KEY_RIGHT:
        camera_angle = (camera_angle - 3) % 360


def mouseListener(button, state, x, y):
    global first_person, first_person_angle
    if state != GLUT_DOWN:
        return
    if button == GLUT_LEFT_BUTTON:
        fire_bullet()
    elif button == GLUT_RIGHT_BUTTON:
        first_person = not first_person
        if first_person:
            first_person_angle = player_angle


def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, WINDOW_WIDTH / WINDOW_HEIGHT, 0.1, 2200)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    if first_person and not game_over:
        # Normal first person follows manual aiming. During cheat mode it stays
        # fixed unless V enables automatic following of the rotating gun.
        view_angle = player_angle
        if cheat_mode and not cheat_vision:
            view_angle = first_person_angle
        dx, dy = direction_from_angle(view_angle)
        # Right-click view: camera is mounted at the player's head. It always
        # follows movement; V decides whether it also follows cheat rotation.
        eye_x = player_x
        eye_y = player_y
        eye_z = 118
        target_x = player_x + dx * 500
        target_y = player_y + dy * 500
        target_z = 75
        gluLookAt(eye_x, eye_y, eye_z,
                  target_x, target_y, target_z,
                  0, 0, 1)
    else:
        radians = math.radians(camera_angle)
        camera_x = camera_radius * math.cos(radians)
        camera_y = camera_radius * math.sin(radians)
        gluLookAt(camera_x, camera_y, camera_height,
                  0, 0, 0,
                  0, 0, 1)


def update_game(dt):
    global player_life, game_score, bullets_missed, game_over
    global enemy_pulse, player_angle, last_cheat_shot

    if game_over:
        return

    enemy_pulse += dt * 5.0

    # Cheat mode rotates continuously and shoots only while an enemy is aligned.
    if cheat_mode:
        rotate_gun(95.0 * dt)
        now = time.time()
        for enemy in enemies:
            if abs(angle_difference(angle_to_enemy(enemy), player_angle)) < 3.5:
                if now - last_cheat_shot >= 0.18:
                    fire_bullet()
                    last_cheat_shot = now
                break

    # Advance bullets and count bullets that leave the arena.
    for bullet in bullets[:]:
        bullet[0] += bullet[3] * 430 * dt
        bullet[1] += bullet[4] * 430 * dt
        if abs(bullet[0]) > GRID_LENGTH or abs(bullet[1]) > GRID_LENGTH:
            bullets.remove(bullet)
            bullets_missed = min(10, bullets_missed + 1)
            print(f"Bullet missed: {bullets_missed}", flush=True)

    # Move every enemy toward the current player position.
    for enemy in enemies:
        dx = player_x - enemy[0]
        dy = player_y - enemy[1]
        distance = math.hypot(dx, dy)
        if distance > 0:
            enemy[0] += dx / distance * 38 * dt
            enemy[1] += dy / distance * 38 * dt

        # Enemy/player collision costs one life and immediately respawns it.
        if math.hypot(enemy[0] - player_x, enemy[1] - player_y) < 48:
            player_life = max(0, player_life - 1)
            print(f"Remaining Player Life: {player_life}", flush=True)
            reset_enemy(enemy)
            if player_life == 0:
                break

    # Bullet/enemy collision increases score and respawns the hit enemy.
    for bullet in bullets[:]:
        hit_enemy = None
        for enemy in enemies:
            if math.hypot(bullet[0] - enemy[0], bullet[1] - enemy[1]) < 38:
                hit_enemy = enemy
                break
        if hit_enemy is not None:
            bullets.remove(bullet)
            game_score += 1
            print(f"Game Score: {game_score}", flush=True)
            reset_enemy(hit_enemy)

    if player_life <= 0 or bullets_missed >= 10:
        game_over = True
        reason = "Player life reached zero." if player_life <= 0 else "10 bullets missed."
        print(f"GAME OVER! {reason}", flush=True)
        print(f"Final Score: {game_score}", flush=True)
        print("Press R to restart the game.", flush=True)


def idle():
    global last_update
    now = time.time()
    dt = min(now - last_update, 0.05)
    last_update = now
    update_game(dt)
    glutPostRedisplay()


def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
    setupCamera()

    draw_floor()
    draw_boundaries()
    draw_player()
    for enemy in enemies:
        draw_enemy(enemy)
    draw_bullets()

    draw_text(25, 760, f"Player Life Remaining: {player_life}")
    draw_text(25, 730, f"Game Score: {game_score}")
    draw_text(25, 700, f"Player Bullet Missed: {bullets_missed}")
    if cheat_mode:
        draw_text(25, 670, "Cheat Mode: ON")
    if game_over:
        draw_text(360, 430, f"GAME OVER - Final Score: {game_score}")
        draw_text(390, 400, "Press R to Restart")

    glutSwapBuffers()


def main():
    reset_game()
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    # Center the 1000x800 window on a 1920x1080 display.
    glutInitWindowPosition(460, 140)
    glutCreateWindow(b"Bullet Frenzy")
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)
    glutMainLoop()


if __name__ == "__main__":
    main()
