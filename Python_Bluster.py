import math
import time
import random
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

width, height = 550, 800

shots = []
python_positions = [  # Corrected spelling from "postions" to "positions"
    (-169, 500), (-90, 498), (-15, 491), (59, 474), (135, 458), (207, 433),
    (255, 377), (207, 312), (135, 284), (59, 266), (-15, 250), (-90, 235),
    (-169, 221), (-244, 199), (-294, 132), (-244, 71), (-169, 50),
    (-90, 40), (-15, 28), (59, 21), (135, 0), (207, -25),
    (255, -83), (207, -150), (135, -174), (59, -190), (-15, -215), (-80, -280)
]
python_body = []
venoms = []
mint = (0.678, 1, 0.604)
lightgreen = (0.325, 0.741, 0.365)
lightlime = (0.412, 1, 0.275)
neon = (0.165, 0.851, 0)
green = (0, 0.6, 0.055)
colorlist = [mint, lightgreen, lightlime, neon, green]
itercounter = 0

score = 0
lives = 3

tank_last_attack = .0
shot_cooldown = 0.3  # seconds

last_venom = 0
venom_cooldown = 2.0  # seconds

game_over = False
pause = False
play_pause = "pause"
keys_pressed = set()
pressed_key = False

class cirBub:
    def __init__(self):
        self.x, self.y = random.randint(-200, 200), 350  # Random position for x, y
        self.r = random.randint(15, 35)  # Random radius between 15 and 35
        self.snake_head = 0.3  # Snake Head radius
        self.color = [random.uniform(0.5, 1) for _ in range(3)]


class Catcher:
    def __init__(self):
        self.x = 0
        self.color = [1] * 3

def draw(x, y, color):
    glPointSize(5)
    glColor3f(color[0], color[1], color[2])
    glBegin(GL_POINTS)
    glVertex2f(x, y)
    glEnd()

def toZone0(x, y, zone):
    zone_map = {
        0: (x, y),
        1: (y, x),
        2: (y, -x),
        3: (-x, y),
        4: (-x, -y),
        5: (-y, -x),
        6: (-y, x),
        7: (x, -y),
    }
    return zone_map.get(zone, (x, y))

def fromZone0(x, y, zone):
    zone_map = {
        0: (x, y),
        1: (y, x),
        2: (-y, x),
        3: (-x, y),
        4: (-x, -y),
        5: (-y, -x),
        6: (y, -x),
        7: (x, -y),
    }
    return zone_map.get(zone, (x, y))

def lineAlgo(x1, y1, x2, y2, color=(1, 1, 1)):
    dx = x2 - x1
    dy = y2 - y1

    # Zone determination
    if abs(dx) > abs(dy):
        if dx >= 0:
            zone = 0 if dy >= 0 else 7
        else:
            zone = 3 if dy >= 0 else 4
    else:
        if dy >= 0:
            zone = 1 if dx >= 0 else 2
        else:
            zone = 6 if dx >= 0 else 5

    x1, y1 = toZone0(x1, y1, zone)
    x2, y2 = toZone0(x2, y2, zone)

    dx, dy = x2 - x1, y2 - y1
    d = 2 * dy - dx
    del_E, del_NE = 2 * dy, 2 * (dy - dx)

    x, y = x1, y1
    temp = (*fromZone0(x, y, zone), color)
    draw(temp[0], temp[1], temp[2])

    for _ in range(x1, x2):
        d += del_E if d <= 0 else del_NE
        if d > 0:
            y += 1
        temp = (*fromZone0(x, y, zone), color)
        draw(temp[0], temp[1], temp[2])
        x += 1

def circleAlgo(r, cx=0, cy=0, color=(1, 1, 1)):
    glPointSize(3)
    glColor3f(color[0], color[1], color[2])
    glBegin(GL_POINTS)
    X = 0
    Y = r
    decision = 1 - r
    while Y > X:
        glVertex2f(X + cx, Y + cy)
        glVertex2f(X + cx, -Y + cy)
        glVertex2f(-X + cx, Y + cy)
        glVertex2f(-X + cx, -Y + cy)
        glVertex2f(Y + cx, X + cy)
        glVertex2f(Y + cx, -X + cy)
        glVertex2f(-Y + cx, X + cy)
        glVertex2f(-Y + cx, -X + cy)

        if decision < 0:
            decision += 2 * X + 3
        else:
            decision += 2 * X - 2 * Y + 5
            Y -= 1
        X += 1
    glEnd()

def drawCircle(point, radius, color=(1, 1, 1)):
    for i in range(1, radius + 1):
        circleAlgo(i, point[0], point[1], color)

def drawRect(x1, y1, x2, y2, color):  #x1, y1 first corner & x2, y2 opposite corner.

    x_min, x_max = min(x1, x2), max(x1, x2)
    y_min, y_max = min(y1, y2), max(y1, y2)

    # Iterate over each horizontal line in the rectangle
    for y in range(y_min, y_max + 1):
        lineAlgo(x_min, y, x_max, y, color)

def drawTri(p1, p2, p3, color=(1, 1, 1)):

    #p1, p2, p3 are the vertices of the triangle

    vertices = sorted([p1, p2, p3], key=lambda p: p[1]) # (ascending order)
    p1, p2, p3 = vertices

    def mediate(x1, y1, x2, y2, y):   #fill triangle
        if y2 == y1:  # Avoid division by zero
            return x1
        return x1 + (x2 - x1) * (y - y1) / (y2 - y1)

    for y in range(p1[1], p3[1] + 1):
        if y < p2[1]:  # Top half
            x_start = mediate(p1[0], p1[1], p2[0], p2[1], y)
            x_end = mediate(p1[0], p1[1], p3[0], p3[1], y)
        else:  # Bottom half
            x_start = mediate(p2[0], p2[1], p3[0], p3[1], y)
            x_end = mediate(p1[0], p1[1], p3[0], p3[1], y)

        x_start, x_end = int(min(x_start, x_end)), int(max(x_start, x_end))
        lineAlgo(x_start, y, x_end, y, color)

def draw_shots():
    global shots
    glPointSize(100)
    vivid_colors = tuple([random.uniform(0.5, 1) for _ in range(3)])
    for i in shots:
        circleAlgo(3, i[0], i[1], vivid_colors )  # Draw shots as small circles

catcher = Catcher()

def draw_python_parts():
    global colorlist, python_body, python_positions, lives
    power = random.randint(1, 5)

    # Ensure power index is within the range of colorlist
    if power > len(colorlist):
        power = len(colorlist)

    python_body.insert(0, [power, colorlist[power - 1]])
    #print(f"Added Python segment with power {power} and color {colorlist[power - 1]}.")

    if len(python_body) > len(python_positions):
        lives -= 1
        print(f"Python Killed a life. Lives left: {lives}")
        python_body = []
        if lives == 0:
            reason = "No more lives left"
            gameover(reason)

def draw_python():
    global python_body, python_positions, colorlist

    for i in range(len(python_body)):
        if i < len(python_positions):
            position = python_positions[i]
            #power, color = python_body[i]

            # Determine whether it's the snake's head (the last segment)
            if i == len(python_body) - 1:  # First circle (head)
                radius = 50  # Larger radius for the head
                color = (1, 0.8, 0)  # Marked with a special color (yellow, for example)

                eye_radius = 15  # Radius of the eyes
                eye_offset_x = 25  # Horizontal offset from the center of the
                eye_offset_y = 5  # Vertical offset from the center of the head

                # Draw the snake's head circle
                drawCircle((position[0], position[1]), radius, color)

                # Left eye (white color)
                drawCircle((position[0] - eye_offset_x, position[1] + eye_offset_y), eye_radius, (1, 1, 1))
                # Right eye (white color)
                drawCircle((position[0] + eye_offset_x, position[1] + eye_offset_y), eye_radius, (1, 1, 1))

                # Optionally, you can also add a smaller black circle for pupils
                pupil_radius = 5
                drawCircle((position[0] - eye_offset_x, position[1] - eye_offset_y), pupil_radius, (0, 0, 0))  # Left pupil
                drawCircle((position[0] + eye_offset_x, position[1] - eye_offset_y), pupil_radius, (0, 0, 0))  # Right pupil


                tongue_height = 35  # Height of the tongue (narrow)
                tongue_offset_y = -80  # Vertical offset below the head

                # First line (left part of the "V")
                lineAlgo(position[0] - 10, position[1] + tongue_offset_y,
                         position[0] - 5, position[1] + tongue_offset_y + tongue_height,
                         color=(1, 0, 0))

                # Second line (right part of the "V")
                lineAlgo(position[0], position[1] + tongue_offset_y,
                         position[0] - 5, position[1] + tongue_offset_y + tongue_height,
                         color=(1, 0, 0))

            else:
                radius = 38  # Normal radius for body parts
                color = python_body[i][1]  # Use the body segment color

                drawCircle((position[0], position[1]), radius, color)
            # if snake_head:
            #     print(f"First circle marked at position: {position} with radius {radius}")

def draw_venoms():
    global venoms
    for venom in venoms:
        circleAlgo(5, venom[0], venom[1], (0, 1, 0))

def draw_catcher():
    global catcher

    x = catcher.x
    y = -500

    # Tank Wheels
    drawRect(x + 30, y + 0, x + 49, y + 100, (0.4, 0.4, 0.45))  # (Gray_blue)
    drawRect(x - 30, y + 0, x - 49, y + 100, (0.4, 0.4, 0.45))  # (Gray_blue)
    drawRect(x + 43, y + 0, x + 47, y + 100, (0.6, 0.7, 0.8))  # (Sky Blue)
    drawRect(x - 43, y + 0, x - 47, y + 100, (0.6, 0.7, 0.8))  # (Sky Blue)

    # Tank Barrel
    drawRect(x + 18, y + 83, x + 25, y + 111, (0.6, 0.7, 0.8))  # (Sky Blue)
    drawRect(x - 18, y + 83, x - 25, y + 111, (0.6, 0.7, 0.8))  # (Sky Blue)
    drawRect(x + 3, y + 97, x - 3, y + 64, (0.6, 0.7, 0.8))  # (Sky Blue)

    # Tank Muzzle
    drawRect(x + 15, y + 108, x + 28, y + 133, (0.9, 0.9, 0.9))  # (white)
    drawRect(x - 15, y + 108, x - 28, y + 133, (0.9, 0.9, 0.9))  # (white)
    drawRect(x + 5, y + 94, x - 5, y + 110, (0.9, 0.9, 0.9))  # (white)

    # Tank Body
    drawRect(x + 29, y + 83, x - 29, y + 18, (0.1, 0.2, 0.4))  # dark bluish shade

    # Main body
    # Triangles for Tank Details
    drawTri((x + 25, y + 94), (x + 39, y + 63), (x + 16, y + 51), (0.1, 0.2, 0.4))  # (Dark_GreenishBlue)
    drawTri((x - 25, y + 94), (x - 39, y + 63), (x - 16, y + 51), (0.1, 0.2, 0.4))  # (Dark_GreenishBlue)
    drawTri((x + 16, y + 50), (x + 40, y + 37), (x + 24, y + 6), (0.1, 0.2, 0.4))  # (Dark_GreenishBlue)
    drawTri((x - 16, y + 50), (x - 40, y + 37), (x - 24, y + 6), (0.1, 0.2, 0.4))  # (Dark_GreenishBlue)

    # Head of the catcher (Outer square)
    drawRect(x + 15, y + 71, x - 15, y + 41, (0.6, 0.7, 0.8)) #(Sky Blue)

def heart():
    global lives

    if lives > 2:
        for i in range(lives):

            drawCircle((370 - 10, -450 + 10 + i*50), 10, (1, 0, 0))
            drawCircle((370 + 10, -450 + 10 + i*50), 10, (1, 0, 0))

            lineAlgo(370 - 20, -450 + 10 + i*50, 370, -460 + i*50, (1, 0, 0))
            lineAlgo(370 - 5, -450 + 1 + i*50, 370 + 5, -450 + 1 + i*50, (1, 0, 0))
            lineAlgo(370 + 20, -450 + 10 + i*50, 370, -460 + i*50, (1, 0, 0))

    elif 2 >= lives > 1:
        for i in range(lives):

            drawCircle((370 - 10, -450 + 10 + i*50), 10, (1, 0, 0))
            drawCircle((370 + 10, -450 + 10 + i*50), 10, (1, 0, 0))

            lineAlgo(370 - 20, -450 + 10 + i*50, 370, -460 + i*50, (1, 0, 0))
            lineAlgo(370 - 5, -450 + 1 + i*50, 370 + 5, -450 + 1 + i*50, (1, 0, 0))
            lineAlgo(370 + 20, -450 + 10 + i*50, 370, -460 + i*50, (1, 0, 0))
    else:

        drawCircle((370 - 10, -450 + 10), 10, (1, 0, 0))
        drawCircle((370 + 10, -450 + 10), 10, (1, 0, 0))

        lineAlgo(370 - 20, -450 + 10, 370, -460, (1, 0, 0))
        lineAlgo(370 - 5, -450 + 1, 370 + 5, -450 + 1, (1, 0, 0))
        lineAlgo(370 + 20, -450 + 10, 370, -460, (1, 0, 0))

def for_Exit():
    lineAlgo(330, 440, 380, 490, [1, 0, 0])
    lineAlgo(330, 490, 380, 440, [1, 0, 0])

def for_Play():

    lineAlgo(-380, 440, -380, 490, [0, 0, 1])
    lineAlgo(-380, 440, -330, 465, [0, 0, 1])
    lineAlgo(-380, 490, -330, 465, [0, 0, 1])

def for_pause():

    lineAlgo(-350, 440, -350, 490, [1, 1, 0])
    lineAlgo(-330, 440, -330, 490, [1, 1, 0])

def conversion(x, y):
    global width, height
    a = x - (width / 2)
    b = (height / 2) - y
    return a, b

def key_shoot_pp(key, x, y):
    global keys_pressed, shots, pause, game_over, catcher, tank_last_attack, pressed_key
    try:
        keyy = key.decode("utf-8")
        keys_pressed.add(keyy)

        if keyy == 'p' and not pressed_key:
            pressed_key = True  # Mark 'p' as pressed
            pause_play_toggle()  # Toggle pause/play
        # Shooting logic for space bar
        elif keyy == ' ':
            current_time = time.time()
            if not pause and not game_over and (current_time - tank_last_attack) >= shot_cooldown:
                # Append multiple shots with different positions and colors
                shots.append([catcher.x, -385, 5, (0.612, 1, 0.98)])  # Center shot
                shots.append([catcher.x + 22, -365, 7, (0, 0.843, 1)])  # Right shot
                shots.append([catcher.x - 22, -365, 7, (0, 0.843, 1)])  # Left shot
                tank_last_attack = current_time

    except Exception as e:
        print(f"Error in key_shoot_pp: {e}")

def key_up(key, x, y):
    global keys_pressed, pressed_key
    try:
        keyy = key.decode("utf-8")
        if keyy in keys_pressed:
            keys_pressed.remove(keyy)

        # Reset 'p' key state on release
        if keyy == 'p':
            pressed_key = False
    except Exception as e:
        print(f"Error in key_up: {e}")

def pause_play_toggle(key=None, x=None, y=None):
    global pause
    if pause == False and pressed_key == True:
        pause = True
    elif pause == True and pressed_key == True:
        pause = False

    print(f"Game {'paused' if pause else 'resumed'}.")

def handle_keys():
    global shots, pause, game_over, catcher
    if not pause and not game_over:
        # Handle left/right movement with 'a' and 'd' keys
        if 'a' in keys_pressed and catcher.x > -300:
            catcher.x -= 10  # Move left
        if 'd' in keys_pressed and catcher.x < 300:
            catcher.x += 10  # Move right

def mouseListener(button, state, x, y):
    global score

    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        # Convert screen coordinates to game coordinates
        exit_x, exit_y = conversion(x, y)
        #print(f"Clicked coordinates: Screen({x}, {y}) -> Game({exit_x}, {exit_y})")

        # Check if the click is within the bounds of the exit button
        if 223 <= exit_x <= 264 and 352 <= exit_y <= 396:
            print("Goodbye! Total Score:", score)
            glutDestroyWindow(glutGetWindow())

def display():
    global game_over, lives

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glClearColor(0, 0, 0, 0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    if not pause and not game_over:
        #gameCtrl()
        draw_python()
        draw_shots()
        draw_catcher()# Left
        draw_venoms()
        for_pause()
        heart()

    else:
        for_Play()
    for_Exit()
    glutSwapBuffers()

def animate():
    global itercounter, pause, bub, catcher, over, total, shots, target_miss, python_body, python_positions, score, last_venom, lives

    if pause:  # Skip animation logic if paused
        glutPostRedisplay()
        return

    else:
        current_time = time.time()
        delta_time = current_time - getattr(animate, 'start_time', current_time)
        animate.start_time = current_time


        itercounter += 1
        if itercounter % 2 == 0:  # frequency to reduce overhead
            itercounter = int(delta_time)
            draw_python_parts()

        to_pop_shots = []
        to_pop_body = []

        # Collision Detection
        for i in range(len(python_body) - 1, -1, -1):  # python_body in reverse
            for j in range(len(shots) - 1, -1, -1):  # shots in reverse
                x1, y1 = shots[j][0], shots[j][1]
                x2, y2 = python_positions[i][0], python_positions[i][1]

                # distance between shot and python segment
                distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
                if distance <= 48:  # Collision radius (38 + 10)
                    to_pop_shots.append(j)
                    if python_body[i][0] > 1:  # life decreased
                        score += 1
                        python_body[i][0] -= 1
                        python_body[i][1] = colorlist[python_body[i][0] - 1]
                        print(f"Score: {score}")

                    else:
                        to_pop_body.append(i)

        # Remove Collided Shots
        for j in sorted(set(to_pop_shots), reverse=True):
            del shots[j]

        # Remove Destroyed Python Segments
        for i in sorted(set(to_pop_body), reverse=True):
            del python_body[i]


        if current_time - last_venom > venom_cooldown:
            head_position = python_positions[len(python_body) - 1]
            venoms.append([head_position[0], head_position[1] - 50])
            last_venom = current_time

        to_remove_venoms = []
        for i, venom in enumerate(venoms):
            venom[1] -= 10  # Move down
            if venom[1] < -500:  # bounds
                to_remove_venoms.append(i)
            elif abs(venom[0] - catcher.x) < 50 and venom[1] < -400:  # Venom hits catcher
                to_remove_venoms.append(i)
                lives -= 1
                print(f"Venom killed a life. Lives left: {lives}")
                if lives == 0:
                    reason = "No more lives left"
                    gameover(reason)
                    return

        for i in sorted(to_remove_venoms, reverse=True):
            del venoms[i]

        for i in range(len(shots) - 1, -1, -1):
            if shots[i][1] < 500:
                shots[i][1] += 20  # Move shot upwards
            else:
                del shots[i]

        handle_keys()
        time.sleep(1 / 100)
        glutPostRedisplay()

def gameover(reason):
    global game_over
    game_over = True
    print("GAME OVER")
    print(reason)
    glutLeaveMainLoop()

def gameWin():
    print("Python is Destroyed. You won the game.")
    glutLeaveMainLoop()


def init():
    global pause, play_pause
    pause = False  # Start the game in play state
    play_pause = "pause"  # Show pause button initially

    glClearColor(0, 0, 0, 0)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-400, 400, -500, 500, -1, 1)

# Initialize python_body with initial segments
initial_segments = 1  # Set to 1 for starting with one segment
for _ in range(initial_segments):
    power = random.randint(1, len(colorlist))
    python_body.append([power, colorlist[power - 1]])
    #print(f"Initialized Python segment with power {power} and color {colorlist[power - 1]}.")

glutInit()
glutInitWindowSize(width, height)
glutInitWindowPosition(0, 0)
glutInitDisplayMode(GLUT_DEPTH | GLUT_DOUBLE | GLUT_RGB)
wind = glutCreateWindow(b"Python Blaster")
init()
glutDisplayFunc(display)
glutIdleFunc(animate)
glutMouseFunc(mouseListener)
glutKeyboardFunc(key_shoot_pp)
glutKeyboardUpFunc(key_up)
glutMainLoop()