from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import time
import math

# Global variables
plane_x, plane_y = 250, 250
plane_angle = 90
plane_health = 5
bullets = []
enemies = []
enemy_bullets = []
bullet_speed = 5
enemy_speed = 3
enemy_spawn_time = 5
firing_enemy_spawn_time = 12
last_spawn_time = time.time()
last_firing_enemy_spawn_time = time.time()
stars = []
star_brightness = []

# Midpoint Circle Algorithm
def midpoint_circle(x_center, y_center, radius):
    x = radius
    y = 0
    p = 1 - radius  # Initial decision parameter
    draw_point(x_center + x, y_center + y)  # Initial point
    while x > y:
        y += 1
        if p <= 0:
            p = p + 2 * y + 1
        else:
            x -= 1
            p = p + 2 * (y - x) + 1
        draw_point(x_center + x, y_center + y)
        draw_point(x_center - x, y_center + y)
        draw_point(x_center + x, y_center - y)
        draw_point(x_center - x, y_center - y)
        draw_point(x_center + y, y_center + x)
        draw_point(x_center - y, y_center + x)
        draw_point(x_center + y, y_center - x)
        draw_point(x_center - y, y_center - x)

# Midpoint Line Algorithm
def midpoint_line(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    p = 2 * dy - dx
    x = x1
    y = y1
    draw_point(x, y)  # Starting point
    if abs(dy) < abs(dx):
        if dx > 0:
            while x < x2:
                x += 1
                if p < 0:
                    p += 2 * dy
                else:
                    if dy > 0:
                        y += 1
                    else:
                        y -= 1
                    p += 2 * (dy - dx)
                draw_point(x, y)
        else:
            while x > x2:
                x -= 1
                if p < 0:
                    p += 2 * dy
                else:
                    if dy > 0:
                        y += 1
                    else:
                        y -= 1
                    p += 2 * (dy - dx)
                draw_point(x, y)
    else:
        if dy > 0:
            while y < y2:
                y += 1
                if p < 0:
                    p += 2 * dx
                else:
                    if dx > 0:
                        x += 1
                    else:
                        x -= 1
                    p += 2 * (dx - dy)
                draw_point(x, y)
        else:
            while y > y2:
                y -= 1
                if p < 0:
                    p += 2 * dx
                else:
                    if dx > 0:
                        x += 1
                    else:
                        x -= 1
                    p += 2 * (dx - dy)
                draw_point(x, y)

def draw_point(x, y, size=5, color=(1.0, 1.0, 1.0)):
    glPointSize(size)
    glBegin(GL_POINTS)
    glColor3f(*color)
    glVertex2f(x, y)
    glEnd()

# Function to draw the shooter plane (filled center):
def draw_plane(x, y):
    # Body of the plane - filled circle for the center
    draw_filled_circle(x, y, 8, color=(0.0, 1.0, 0.0))  # Green body
    # Wings of the plane - using midpoint line
    midpoint_line(x - 10, y - 10, x + 10, y - 10)


def draw_filled_circle(x_center, y_center, radius, color=(1.0, 1.0, 1.0)):
    glColor3f(*color)
    glBegin(GL_POINTS)
    for i in range(0, 360):
        for r in range(0, radius):
            angle_rad = math.radians(i)
            x = x_center + r * math.cos(angle_rad)
            y = y_center + r * math.sin(angle_rad)
            glVertex2f(x, y)
    glEnd()




def draw_line(x1, y1, x2, y2, color=(1.0, 1.0, 1.0)):
    num_points = 20  # Number of points to approximate the line
    line_points = []
    for i in range(num_points + 1):
        t = i / num_points
        px = x1 + t * (x2 - x1)
        py = y1 + t * (y2 - y1)
        line_points.append((px, py))
        draw_point(px, py, size=2, color=color)
    return line_points



def draw_bullet(x, y, angle):
    size = 5  # Size of the chevron arms

    # Calculate the angle
    angle_rad = math.radians(angle)
    tip_x = x + size * math.cos(angle_rad)  # Tip of the arrow
    tip_y = y + size * math.sin(angle_rad)

    left_arm_x = x - size * math.cos(angle_rad - math.pi / 4)
    left_arm_y = y - size * math.sin(angle_rad - math.pi / 4)
    right_arm_x = x - size * math.cos(angle_rad + math.pi / 4)
    right_arm_y = y - size * math.sin(angle_rad + math.pi / 4)

    # bullet arms
    draw_line(x, y, tip_x, tip_y, color=(1.0, 0.0, 0.0))  # Central line
    draw_line(left_arm_x, left_arm_y, tip_x, tip_y, color=(1.0, 0.0, 0.0))  # Left arm line
    draw_line(right_arm_x, right_arm_y, tip_x, tip_y, color=(1.0, 0.0, 0.0))  # Right arm line


    return [(x, y), (tip_x, tip_y), (left_arm_x, left_arm_y), (right_arm_x, right_arm_y)]


score = 0

def update_bullets():
    global bullets, enemies, score
    updated_bullets = []
    for bullet in bullets:
        bullet[0] += bullet_speed * math.cos(math.radians(bullet[2]))
        bullet[1] += bullet_speed * math.sin(math.radians(bullet[2]))

        # Get all points of the bullet for collision detection
        bullet_points = draw_bullet(bullet[0], bullet[1], bullet[2])

        # Check for collisions with enemies using all bullet points
        hit_detected = False
        for enemy in enemies:
            for bp_x, bp_y in bullet_points:
                if math.hypot(bp_x - enemy[0], bp_y - enemy[1]) < 15:
                    if enemy[3]:  # Firing enemy
                        score += 3
                        print(f"Score updated! Current Score: {score}")
                    else:  # Non-firing enemy
                        score += 1
                        print(f"Score updated! Current Score: {score}")
                    enemy[2] -= 1  # Reduce enemy health
                    if enemy[2] <= 0:
                        enemies.remove(enemy)
                    hit_detected = True
                    break
            if hit_detected:
                break

        # Keep bullet if it didn't hit any enemy
        if not hit_detected:
            updated_bullets.append(bullet)

    # Remove bullets out of bounds
    bullets = [b for b in updated_bullets if 0 <= b[0] <= 500 and 0 <= b[1] <= 500]


def update_enemy_bullets():
    global enemy_bullets, plane_health, plane_x, plane_y
    for bullet in enemy_bullets:
        bullet[0] += bullet_speed * math.cos(math.radians(bullet[2]))
        bullet[1] += bullet_speed * math.sin(math.radians(bullet[2]))
        # Check for collision with the plane
        if math.hypot(bullet[0] - plane_x, bullet[1] - plane_y) < 15:
            plane_health -= 1
            enemy_bullets.remove(bullet)  # Remove the bullet that hit
            print(f"Plane hit! Health remaining: {plane_health}")
            if plane_health <= 0:
                print(f"Game Over! Plane destroyed. Final Score: {score}")
                glutLeaveMainLoop()
    # Remove bullets out of bounds
    enemy_bullets = [b for b in enemy_bullets if 0 <= b[0] <= 500 and 0 <= b[1] <= 500]

# Example of game over logic for enemy collision:
def update_enemies():
    global enemies, plane_x, plane_y, score
    for enemy in enemies:
        angle_to_plane = math.degrees(math.atan2(plane_y - enemy[1], plane_x - enemy[0]))
        enemy[0] += enemy_speed * math.cos(math.radians(angle_to_plane))
        enemy[1] += enemy_speed * math.sin(math.radians(angle_to_plane))
        # Check for collision with the plane
        if math.hypot(enemy[0] - plane_x, enemy[1] - plane_y) < 20:
            print(f"Game Over! Plane collided with an enemy. Final Score: {score}")
            glutLeaveMainLoop()



def draw_ellipse(x_center, y_center, a, b):
    glBegin(GL_POINTS)
    for angle in range(360):
        x = a * math.cos(math.radians(angle))
        y = b * math.sin(math.radians(angle))
        glVertex2f(x_center + x, y_center + y)
    glEnd()


def draw_half_circle(x_center, y_center, radius):
    x = 0
    y = radius
    d = 1 - radius  # Decision parameter

    glBegin(GL_POINTS)
    while x <= y:
        glVertex2f(x_center + x, y_center + y)
        glVertex2f(x_center - x, y_center + y)
        glVertex2f(x_center + y, y_center + x)
        glVertex2f(x_center - y, y_center + x)

        if d < 0:
            d += 2 * x + 3
        else:
            d += 2 * (x - y) + 5
            y -= 1
        x += 1
    glEnd()




def draw_ufo(x, y, is_firing):
    if is_firing:
        base_color = (random.random(), random.random(), random.random())
    else:
        base_color = (0.3, 0.3, 0.3)

    glColor3f(*base_color)
    draw_filled_ellipse(x, y - 5, 30, 10)

    # UFO dome (half-circle, always white)
    glColor3f(1.0, 1.0, 1.0)
    draw_filled_half_circle(x, y + 5, 15)

def draw_filled_ellipse(x_center, y_center, a, b):
    glBegin(GL_POINTS)
    for angle in range(360):
        for r in range(0, b):
            x = a * math.cos(math.radians(angle)) * (r / b)
            y = b * math.sin(math.radians(angle)) * (r / b)
            glVertex2f(x_center + x, y_center + y)
    glEnd()

def draw_filled_half_circle(x_center, y_center, radius):
    glBegin(GL_POINTS)
    for angle in range(0, 181):
        for r in range(radius):
            x = r * math.cos(math.radians(angle))
            y = r * math.sin(math.radians(angle))
            glVertex2f(x_center + x, y_center + y)
    glEnd()

def draw_enemy(x, y, is_firing_enemy=False):
    draw_ufo(x, y, is_firing_enemy)



def draw_star(x, y, brightness):
    glColor3f(1,1,1)
    glBegin(GL_POINTS)
    glVertex2f(x, y)
    glEnd()


def draw_planet(center_x, center_y, radius, r, g, b):
    glColor3f(r, g, b)
    glBegin(GL_POINTS)
    for i in range(0, 360):
        for distance in range(0, radius):
            angle = math.radians(i)
            x = center_x + distance * math.cos(angle)
            y = center_y + distance * math.sin(angle)
            glVertex2f(x, y)
    glEnd()

# Update background to use static planets:
def draw_background():
    # Draw stars
    for _ in range(25):  # Adjust for the number of stars
        x = random.uniform(0, 500)  # Match your game window's width
        y = random.uniform(0, 500)  # Match your game window's height
        draw_point(x, y, size=1, color=(1.0, 1.0, 1.0))

    draw_planet(100, 300, 50, 1.0, 0.5, 0.0)  # Orange planet
    draw_planet(400, 500, 50, 1.0, 1.0, 0.0)  # Yellow planet
    draw_planet(200, 100, 50, 0.5, 0.0, 1.0)  # Purple planet
    draw_planet(500, 100, 50, 0.8, 0.4, 0.2)  # Brown planet
    draw_planet(250, 350, 75, 0.8, 0.8, 0.8)  # White planet



def spawn_normal_enemy():
    side = random.choice(["top", "bottom", "left", "right"])
    if side == "top":
        x, y = random.randint(0, 500), 500
    elif side == "bottom":
        x, y = random.randint(0, 500), 0
    elif side == "left":
        x, y = 0, random.randint(0, 500)
    elif side == "right":
        x, y = 500, random.randint(0, 500)
    enemies.append([x, y, 1, False])

def spawn_firing_enemy():
    side = random.choice(["top", "bottom", "left", "right"])
    if side == "top":
        x, y = random.randint(0, 500), 500
    elif side == "bottom":
        x, y = random.randint(0, 500), 0
    elif side == "left":
        x, y = 0, random.randint(0, 500)
    elif side == "right":
        x, y = 500, random.randint(0, 500)
    enemies.append([x, y, 4, True])  # Firing enemy with health and firing power


def fire_enemy_bullet():
    for enemy in enemies:
        if enemy[3]:  # Check if the enemy can shoot
            angle_to_plane = math.degrees(math.atan2(plane_y - enemy[1], plane_x - enemy[0]))
            enemy_bullets.append([enemy[0], enemy[1], angle_to_plane])

def keyboard_special(key, x, y):
    global plane_x, plane_y, plane_angle
    if key == GLUT_KEY_RIGHT:
        plane_x = min(plane_x + 5, 500)
        plane_angle = 0
    elif key == GLUT_KEY_LEFT:
        plane_x = max(plane_x - 5, 0)
        plane_angle = 180
    elif key == GLUT_KEY_UP:
        plane_y = min(plane_y + 5, 500)
        plane_angle = 90
    elif key == GLUT_KEY_DOWN:
        plane_y = max(plane_y - 5, 0)
        plane_angle = 270

def keyboard(key, x, y):
    global bullets, plane_angle
    if key == b' ':
        bullets.append([plane_x, plane_y, plane_angle])  # Add a bullet at the plane's position with its angle

def iterate():
    glViewport(0, 0, 500, 500)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0.0, 500, 0.0, 500, 0.0, 1.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def animate():
    global bullets, enemies, enemy_bullets
    update_bullets()
    update_enemies()
    update_enemy_bullets()
    # Spawn normal enemies every 5 seconds
    global last_spawn_time
    if time.time() - last_spawn_time > enemy_spawn_time:
        spawn_normal_enemy()
        last_spawn_time = time.time()

    # Spawn firing enemies every 12 seconds
    global last_firing_enemy_spawn_time
    if time.time() - last_firing_enemy_spawn_time > firing_enemy_spawn_time:
        spawn_firing_enemy()
        fire_enemy_bullet()
        last_firing_enemy_spawn_time = time.time()

def showScreen():
    """Main display function."""
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    iterate()

    # Call the animate function
    animate()

    # Draw the background and game elements
    draw_background()
    draw_plane(plane_x, plane_y)

    # Draw bullets
    for bullet in bullets:
        draw_bullet(bullet[0], bullet[1], bullet[2])

    # Draw enemies
    for enemy in enemies:
        draw_enemy(enemy[0], enemy[1], enemy[3])  # Last param is for firing enemy

    # Draw enemy bullets
    for bullet in enemy_bullets:
        draw_bullet(bullet[0], bullet[1], bullet[2])

    glutSwapBuffers()


glutInit()
glutInitDisplayMode(GLUT_RGBA)
glutInitWindowSize(500, 500)
glutInitWindowPosition(0, 0)
wind = glutCreateWindow(b"Space War")
glutDisplayFunc(showScreen)
glutIdleFunc(showScreen)
glutSpecialFunc(keyboard_special)
glutKeyboardFunc(keyboard)
glutMainLoop()
