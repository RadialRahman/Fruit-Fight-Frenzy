#Faizah Mohiuddin 23101306
#Radial Rahman 22201662
#Fardin Faiaz 22201187
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import time
from math import sin, cos, pi
paused = False

#camera vars and game vars
camera_pos = [0, 500, 500]
fovY = 120
GRID_LENGTH = 600

#fruit list
FRUITS = ['apple', 'orange', 'guava', 'pomegranate']
FRUIT_COLORS = {
    'apple': (1, 0, 0),
    'orange': (1, 0.5, 0),
    'guava': (0.7, 1.0, 0.6),
    'pomegranate': (0.7, 0, 0.2)
}



GRID_ROWS = 3
GRID_COLS = 3
TILE_SIZE = 150
TILE_MARGIN = 100

fruit_grid = []
revealed = []
matched = []
removed = []
selected = []
scores = [0, 0]
current_player = 0
start_time = 0
game_over = False
timer_limit = 120  # seconds
block_colors=[]
matched_time=[]

checking_match = False
match_check_start_time = 0

paused_start = 0
total_paused = 0




#initial game state 
game_state = "initial_reveal"    
reveal_start_time = 0

#dynamically platform grid
PLATFORM_GRID_SIZE = 20
platform_colors = []

def setup_platform_colors():
    global platform_colors
    platform_colors = []
    for row in range(PLATFORM_GRID_SIZE):
        for col in range(PLATFORM_GRID_SIZE):
            pastel_colors = [
                (0.9098039215686274, 0.2784313725490196, 0.11764705882352941),  # orange
                (0.12156862745098039, 0.8, 0.5490196078431373),  #paste
                (0.25098039215686274, 0.7803921568627451, 0.9294117647058824),      # pastel green
                (0.49019607843137253, 0.3803921568627451, 0.8117647058823529),      # pastel blue
            ]
            color = random.choice(pastel_colors)
            platform_colors.append(color)

def draw_platform_grid():
    cell_size = (2 * GRID_LENGTH) / PLATFORM_GRID_SIZE
    start_x = -GRID_LENGTH
    start_y = -GRID_LENGTH
    z = -TILE_SIZE//2 - 10
    idx = 0
    for row in range(PLATFORM_GRID_SIZE):
        for col in range(PLATFORM_GRID_SIZE):
            glColor3f(*platform_colors[idx])
            x0 = start_x + col * cell_size
            y0 = start_y + row * cell_size
            x1 = x0 + cell_size
            y1 = y0 + cell_size
            glBegin(GL_QUADS)
            glVertex3f(x0, y0, z)
            glVertex3f(x1, y0, z)
            glVertex3f(x1, y1, z)
            glVertex3f(x0, y1, z)
            glEnd()
            idx += 1

#drawing the four fruits
def draw_apple():
    glColor3f(*FRUIT_COLORS['apple'])
    quad = gluNewQuadric()
    gluSphere(quad, 18,16,16)
    glColor3f(0.4, 0.2, 0)
    glPushMatrix()
    glTranslatef(0, 0, 22)
    gluCylinder(gluNewQuadric(), 2, 1, 7, 10, 10)
    glPopMatrix()

def draw_orange():
    glColor3f(*FRUIT_COLORS['orange'])
    quad = gluNewQuadric()
    gluSphere(quad, 18,16,16)
    glColor3f(0.8, 0.7, 0.2)
    glPushMatrix()
    glTranslatef(0, 0, 18)
    quad = gluNewQuadric()
    gluSphere(quad, 3,10,10)
    glPopMatrix()

def draw_guava():
    glColor3f(*FRUIT_COLORS['guava'])
    quad = gluNewQuadric()
    gluSphere(quad, 17,16,16)
    
    glColor3f(1.0, 0.7, 0.8)
    glPushMatrix()
    glTranslatef(0, 0, 5)
    quad = gluNewQuadric()
    gluSphere(quad, 8,12,12)
    glPopMatrix()
    
    glColor3f(0.5, 0.8, 0.3)
    glPushMatrix()
    glTranslatef(0, 0, 18)
    gluCylinder(gluNewQuadric(), 2, 1, 7, 10, 10)
    glPopMatrix()


def draw_pomegranate():
    glColor3f(*FRUIT_COLORS['pomegranate'])
    quad = gluNewQuadric()
    gluSphere(quad, 16,16,16)
    glColor3f(1, 0.2, 0.4)
    glPushMatrix()
    glTranslatef(0, 0, 18)
    glutSolidCone(4, 8, 10, 10)
    base_radius = 4
    height = 8
    slices = 12
    tip = (0, 0, height)
    glBegin(GL_LINES)
    for i in range(slices):
        angle1 = 2 * pi * i / slices
        angle2 = 2 * pi * (i+1) / slices
        x1 = base_radius * cos(angle1)
        y1 = base_radius * sin(angle1)
        z1 = 0
        
        glVertex3f(x1, y1, z1)
        glVertex3f(*tip)
        
        x2 = base_radius * cos(angle2)
        y2 = base_radius * sin(angle2)
        glVertex3f(x1, y1, z1)
        glVertex3f(x2, y2, z1)
    glEnd()
    glPopMatrix()

def draw_fruit(fruit_type):
    if fruit_type == 'apple':
        draw_apple()
    elif fruit_type == 'orange':
        draw_orange()
    elif fruit_type == 'guava':
        draw_guava()
    elif fruit_type == 'pomegranate':
        draw_pomegranate()


#drawing the baskets
basket_fruits = [[], []]  # 2 indices for 2 players

def draw_basket(x, y, z, fruits):

    def basket_walls(x,y,z):

        glBegin(GL_QUADS)
    
        glVertex3f(-x, -y, 0)
        glVertex3f(-x, -y, z)
        glVertex3f(-x, y, z)
        glVertex3f(-x, y, 0)
        
        glVertex3f(x, -y, 0)
        glVertex3f(x, -y, z)
        glVertex3f(x, y, z)
        glVertex3f(x, y, 0)
        
        glVertex3f(-x, y, 0)
        glVertex3f(-x, y, z)
        glVertex3f(x, y, z)
        glVertex3f(x, y, 0)
        
        glVertex3f(-x, -y, 0)
        glVertex3f(-x, -y, z)
        glVertex3f(x, -y, z)
        glVertex3f(x, -y, 0)
        glEnd()

    def basket_floor(x,y):
        glBegin(GL_QUADS)
        glVertex3f(-x, -y, 0)
        glVertex3f(x, -y, 0)
        glVertex3f(x, y, 0)
        glVertex3f(-x, y, 0)
        glEnd()

    def handle(handle_color,slide_x, side_w, side_h, side_z0, side_z1,  side_y):
        # Left Handle 
        glColor3f(*handle_color)
        glBegin(GL_QUADS)
        glVertex3f(-slide_x, side_y - side_w//2, side_z0)
        glVertex3f(-slide_x, side_y + side_w//2, side_z0)
        glVertex3f(-slide_x, side_y + side_w//2, side_z1)
        glVertex3f(-slide_x, side_y - side_w//2, side_z1)
        glEnd()

        # Right Handle
        glBegin(GL_QUADS)
        glVertex3f(slide_x, side_y - side_w//2, side_z0)
        glVertex3f(slide_x, side_y + side_w//2, side_z0)
        glVertex3f(slide_x, side_y + side_w//2, side_z1)
        glVertex3f(slide_x, side_y - side_w//2, side_z1)
        glEnd()

        # Top Bridge 
        bridge_len = 80 
        bridge_w = 4
        bridge_z = side_z1
        glBegin(GL_QUADS)
        glVertex3f(-slide_x, side_y - bridge_w//2, bridge_z)
        glVertex3f(slide_x, side_y - bridge_w//2, bridge_z)
        glVertex3f(slide_x, side_y + bridge_w//2, bridge_z)
        glVertex3f(-slide_x, side_y + bridge_w//2, bridge_z)
        glEnd()


    
    glColor3f(0.5, 0.3, 0.11)  
    glPushMatrix()
    glTranslatef(x, y, z)
    
    basket_floor(40,40)

    glColor3f(0.2784313725490196, 0.16470588235294117, 0.03529411764705882) 
    basket_walls(40,40,30)
    handle((0.9215686274509803, 0.3215686274509804, 0.8235294117647058), 40,4,30,30,60,0)

    # Fruit inside basket
    for i, fruit in enumerate(fruits):
        glPushMatrix()
        glTranslatef(-25 + (i%4)*16, -5 + (i//4)*18, 35)
        draw_fruit(fruit)
        glPopMatrix()
    glPopMatrix()


# Tic Tac Toe cheat mode
ttt_grid = [0] * 9  
ttt_turn = 1        
ttt_winner = 0     
ttt_cheatcode_given = False
ttt_cheatcode_used = False
ttt_mode = False

def setup_ttt():
    global ttt_grid, ttt_turn, ttt_winner, ttt_cheatcode_given, ttt_cheatcode_used
    ttt_grid[:] = [0]*9
    ttt_turn = 1
    ttt_winner = 0
    ttt_cheatcode_given = False
    ttt_cheatcode_used = False

def draw_ttt():
    base_x = 590
    base_y = 200
    cell = 85
    glColor3f(1,1,1)
    glLineWidth(3)
    for i in range(1,3):
        glBegin(GL_LINES)
        glVertex3f(base_x + i*cell, base_y, 0)
        glVertex3f(base_x + i*cell, base_y + 3*cell, 0)
        glEnd()
        glBegin(GL_LINES)
        glVertex3f(base_x, base_y + i*cell, 0)
        glVertex3f(base_x + 3*cell, base_y + i*cell, 0)
        glEnd()
    for idx in range(9):
        row = idx // 3
        col = idx % 3
        display_number = row * 3 + col + 1
        cx = base_x + col*cell + cell//2
        cy = base_y + row*cell + cell//2
        if ttt_grid[idx] == 1:
            glColor3f(1,0.2,0.2)
            glLineWidth(2)
            glBegin(GL_LINES)
            glVertex3f(cx-12, cy-12, 0)
            glVertex3f(cx+12, cy+12, 0)
            glVertex3f(cx-12, cy+12, 0)
            glVertex3f(cx+12, cy-12, 0)
            glEnd()
        elif ttt_grid[idx] == 2:
            glColor3f(0.2,0.6,1)
            for a in range(0,360,30):
                theta1 = a * pi / 180
                theta2 = (a+30) * pi / 180
                glBegin(GL_LINES)
                glVertex3f(cx + 14 * cos(theta1), cy + 14 * sin(theta1), 0)
                glVertex3f(cx + 14 * cos(theta2), cy + 14 * sin(theta2), 0)
                glEnd()
        glColor3f(0.8,0.8,0.8)
        glRasterPos2f(cx-7, cy-7)
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(str(idx+1)))
    if ttt_winner == 0:
        draw_text(base_x-450, base_y + 200, f"Tic Tac Toe: {'X' if ttt_turn==1 else 'O'}'s turn")
    elif ttt_winner == 3:
        draw_text(base_x-450, base_y + 200, "Tic Tac Toe: Draw!")
    else:
        draw_text(base_x-450, base_y + 200, f"Tic Tac Toe: {'X' if ttt_winner==1 else 'O'} wins!")
        if not ttt_cheatcode_given:
            draw_text(base_x, base_y + 120, "Winner gets a cheatcode! (Press K in fruit mode)")
        else:
            draw_text(base_x+150, base_y + 120, "Cheatcode used!")

def ttt_check_win():
   
    g = ttt_grid
    
   
    wins = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],  
        [0, 3, 6], [1, 4, 7], [2, 5, 8], 
        [0, 4, 8], [2, 4, 6]              
    ]
    
    for win_combo in wins:
        if g[win_combo[0]] == g[win_combo[1]] == g[win_combo[2]] != 0:
            return g[win_combo[0]]  # Return the winner (1 or 2)
    
   
    if all(cell != 0 for cell in g):
        return 3  
    
    return 0  

def ttt_handle_key(idx):
    global ttt_turn, ttt_winner, ttt_cheatcode_given
    
    if ttt_winner != 0:  
        return
    if ttt_grid[idx] != 0:  
        return
    
  
    ttt_grid[idx] = ttt_turn
    
    ttt_winner = ttt_check_win()
    
    if ttt_winner == 0:
        ttt_turn = 3 - ttt_turn  
    
    glutPostRedisplay()

def use_cheatcode():
    global ttt_cheatcode_given, ttt_cheatcode_used, scores, ttt_winner
    if ttt_winner in [1,2] and not ttt_cheatcode_given and not ttt_cheatcode_used:
        scores[ttt_winner - 1] += 1  # ttt_winner is 1 or 2, so index is 0 or 1
        ttt_cheatcode_given = True
        ttt_cheatcode_used = True

#Setting up the game
def setup_fruits():
    global fruit_grid, revealed, matched, removed, selected, scores, current_player
    global game_over, start_time, game_state, reveal_start_time, basket_fruits
    global matched_time, block_colors
    global paused_start, total_paused


    def reset_game_state():
        global current_player, game_over
        global paused_start, total_paused
        total_tiles = GRID_ROWS * GRID_COLS
        revealed[:] = [True] * total_tiles
        matched[:] = [False] * total_tiles
        removed[:] = [False] * total_tiles
        selected.clear()
        scores[:] = [0, 0]
        basket_fruits[0].clear()
        basket_fruits[1].clear()
        current_player = 0
        game_over = False
        paused_start = 0
        total_paused = 0


    def generate_fruit_types():
        global pairs_needed
        global matched_time
        total_tiles = GRID_ROWS * GRID_COLS
        pairs_needed = total_tiles // 2
        fruit_pairs = []
        for fruit in FRUITS:
            fruit_pairs.extend([fruit, fruit])
        while len(fruit_pairs) < total_tiles:
            additional_fruits = FRUITS * ((total_tiles - len(fruit_pairs) + len(FRUITS) - 1) // len(FRUITS))
            fruit_pairs.extend(additional_fruits[:total_tiles - len(fruit_pairs)])
        fruit_types = fruit_pairs[:total_tiles]
        random.shuffle(fruit_types)
        fruit_grid[:] = fruit_types
        matched_time = [None] * total_tiles

    def generate_block_colors():
        global block_colors  
        total_tiles = GRID_ROWS * GRID_COLS
        block_colors = []  
        for _ in range(total_tiles):
            base_r = random.uniform(0.3, 0.8)
            base_g = random.uniform(0.3, 0.8)
            base_b = random.uniform(0.3, 0.8)
            pastel_r = 0.6 * base_r + 0.4 * 1.0
            pastel_g = 0.6 * base_g + 0.4 * 1.0
            pastel_b = 0.6 * base_b + 0.4 * 1.0
            block_colors.append((pastel_r, pastel_g, pastel_b))

    def initialize_timing():
        global start_time, reveal_start_time, game_state
        start_time = time.time()
        reveal_start_time = time.time()
        game_state = "initial_reveal"

    reset_game_state()
    generate_fruit_types()
    generate_block_colors()
    initialize_timing()
    setup_platform_colors()
    setup_ttt()


def generate_vertex_colors(base_color):
    def rgb_to_hsv(r, g, b):
        max_val = max(r, g, b)
        min_val = min(r, g, b)
        diff = max_val - min_val
        
        if max_val == min_val:
            h = 0
        elif max_val == r:
            h = (60 * ((g - b) / diff) + 360) % 360
        elif max_val == g:
            h = (60 * ((b - r) / diff) + 120) % 360
        else:
            h = (60 * ((r - g) / diff) + 240) % 360
        
        s = 0 if max_val == 0 else (diff / max_val)
        v = max_val
        return h, s, v

    def hsv_to_rgb(h, s, v):
        h = h % 360
        c = v * s
        x = c * (1 - abs((h / 60) % 2 - 1))
        m = v - c
        
        if 0 <= h < 60:
            r, g, b = c, x, 0
        elif 60 <= h < 120:
            r, g, b = x, c, 0
        elif 120 <= h < 180:
            r, g, b = 0, c, x
        elif 180 <= h < 240:
            r, g, b = 0, x, c
        elif 240 <= h < 300:
            r, g, b = x, 0, c
        else:
            r, g, b = c, 0, x
        
        return r + m, g + m, b + m


    r, g, b = base_color
    h, s, v = rgb_to_hsv(r, g, b)
    
    vertex_colors = [
        hsv_to_rgb((h + 0) % 360, min(s * 1.2, 1.0), min(v * 1.1, 1.0)),
        hsv_to_rgb((h + 30) % 360, min(s * 1.3, 1.0), min(v * 0.9, 1.0)),
        hsv_to_rgb((h + 60) % 360, min(s * 1.1, 1.0), min(v * 1.2, 1.0)),
        hsv_to_rgb((h + 90) % 360, min(s * 1.4, 1.0), min(v * 0.8, 1.0)),
        hsv_to_rgb((h + 120) % 360, min(s * 0.9, 1.0), min(v * 1.3, 1.0)),
        hsv_to_rgb((h + 180) % 360, min(s * 1.5, 1.0), min(v * 0.7, 1.0)),
        hsv_to_rgb((h + 240) % 360, min(s * 0.8, 1.0), min(v * 1.4, 1.0)),
        hsv_to_rgb((h + 300) % 360, min(s * 1.6, 1.0), min(v * 0.6, 1.0))
    ]
    
    return vertex_colors

def draw_gradient_cube(size, base_color): #pastel gradient coloured cubes    
    s = size / 2
    vertices = [
        [-s, -s, -s],
        [ s, -s, -s],
        [ s,  s, -s],
        [-s,  s, -s],
        [-s, -s,  s],
        [ s, -s,  s],
        [ s,  s,  s],
        [-s,  s,  s],
    ]
    #defining 6 faces of the cube
    faces = [
        [0, 1, 2, 3], # back
        [4, 5, 6, 7], # front
        [0, 1, 5, 4], # bottom
        [2, 3, 7, 6], # top
        [1, 2, 6, 5], # right
        [0, 3, 7, 4], # left
    ]
   
    
    vertex_colors = generate_vertex_colors(base_color)
    for face in faces:
        glBegin(GL_QUADS)
        for vi in face:
            glColor3f(*vertex_colors[vi])
            glVertex3f(*vertices[vi])
        glEnd()



def draw_grid():
    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            idx = row * GRID_COLS + (GRID_COLS - 1 - col)

            if removed[idx]:
                continue
            x = (col - GRID_COLS/2 + 0.5) * (TILE_SIZE + TILE_MARGIN)
            y = (row - GRID_ROWS/2 + 0.5) * (TILE_SIZE + TILE_MARGIN)
            glPushMatrix()
            glTranslatef(x, y, 0)
            if matched[idx]:
                draw_gradient_cube(TILE_SIZE, (0.2, 0.8, 0.2))
            elif idx in selected:
                draw_gradient_cube(TILE_SIZE, (1, 1, 0))
            else:
                color = block_colors[idx] #random gradient pastel
                draw_gradient_cube(TILE_SIZE, color)


            if revealed[idx] or matched[idx]:
                glTranslatef(0, 0, TILE_SIZE/2 + 10)
                draw_fruit(fruit_grid[idx])

            
            glColor3f(1, 1, 1)
            glRasterPos3f(0, 0, TILE_SIZE/2 + 35)
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(str(idx+1)))
            glPopMatrix()

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1,1,1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
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

def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, 1.25, 0.1, 1500)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    x, y, z = camera_pos
    gluLookAt(x, y, z, 0, 0, 0, 0, 0, 1)

def select_tile(idx):
    global selected, revealed, matched, removed, current_player, scores, game_over
    global checking_match, match_check_start_time

    if matched[idx] or revealed[idx] or removed[idx]:
        return
    if idx in selected:
        return
    if len(selected) < 2:
        selected.append(idx)
        revealed[idx] = True
        glutPostRedisplay()
    
    if len(selected) == 2 and not checking_match:
        checking_match = True
        match_check_start_time = time.time()


def check_match(value):
    global selected, revealed, matched, removed, current_player, scores, game_over, basket_fruits
    if len(selected) < 2:
        return
    i1, i2 = selected
    if fruit_grid[i1] == fruit_grid[i2]:
        matched[i1] = True
        matched[i2] = True
        
        matched_time[i1] = time.time()
        matched_time[i2] = time.time()
        scores[current_player] += 1
        
    else:
        revealed[i1] = False
        revealed[i2] = False
        current_player = (current_player + 1) % 2
    selected.clear()
    if matched.count(True) == len(matched) - 1:
        game_over = True
    glutPostRedisplay()

def get_idx_from_rc(row,col):
    if 0 <= row < GRID_ROWS and 0 <= col < GRID_COLS:
        if row==0:
            if col==0:
                return 6
            elif col==2:
                return 8
            else:
                return 7
        elif row==2:
            return col
        
        else:
            return 3+col
        
    return None
    
    

def tile_from_mouse(x, y):
    wx = (x / 1000.0) * GRID_COLS
    wy = ((800 - y) / 800.0) * GRID_ROWS
    col = int(wx)
    row = int(wy)
    return get_idx_from_rc(row,col)
   
    
        

def keyboardListener(key, x, y):
    global ttt_mode, game_over, paused, paused_start, total_paused, start_time

    if key in [b'q', b'Q']: 
        if not paused:
            paused = True
            paused_start = time.time()
        else:
            paused = False
            total_paused += time.time() - paused_start
        glutPostRedisplay()
        return

    if paused:  
        return 
    
    if key == b't':
        ttt_mode = not ttt_mode
        glutPostRedisplay()
        return
    if ttt_mode:
        if key in [b'1',b'2',b'3',b'4',b'5',b'6',b'7',b'8',b'9']:
            idx = int(key.decode()) - 1
            if 0 <= idx < 9:
                ttt_handle_key(idx)
        return
    if game_over:
        if key == b'r':
            setup_fruits()
        return
    if key == b'r':
        setup_fruits()
    if key == b'c':
        global camera_pos
        camera_pos = [0, 500, 500] if camera_pos != [0, 500, 500] else [0, 0, 100]
        glutPostRedisplay()
    if key == b'k':
        use_cheatcode()
    if key in [b'1',b'2',b'3',b'4',b'5',b'6',b'7',b'8',b'9']:
        idx = int(key.decode()) - 1
        if idx < GRID_ROWS * GRID_COLS:
            select_tile(idx)

    glutPostRedisplay()

def specialKeyListener(key, x, y):
    global camera_pos
    if paused:  
        return 
    x, y, z = camera_pos
    if key == GLUT_KEY_LEFT:
        x -= 50
    elif key == GLUT_KEY_RIGHT:
        x += 50
    elif key == GLUT_KEY_UP:
        z += 50
    elif key == GLUT_KEY_DOWN:
        z -= 50
    camera_pos[:] = [x, y, z]
    glutPostRedisplay()

def mouseListener(button, state, x, y):
    if paused:  
        return 
    if ttt_mode:
        return
    if game_over:
        return
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        idx = tile_from_mouse(x, y)
        if idx is not None:
            select_tile(idx)
    glutPostRedisplay()

def idle():
    global game_over, game_state, revealed, reveal_start_time, paused, matched, removed
    global matched_time, basket_fruits, fruit_grid, current_player
    global checking_match, match_check_start_time

    if paused:  
        return 

    now = time.time()

    def handle_initial_reveal():
        global game_state, revealed, reveal_start_time
        if game_state == "initial_reveal":
            if now - reveal_start_time > 2.0:
                revealed[:] = [False] * (GRID_ROWS * GRID_COLS)
                game_state = "playing"

    def check_game_timer():
        global game_over
        if not game_over and now - start_time > timer_limit:
            game_over = True

    def process_matched_fruits():
        global matched, removed, matched_time, basket_fruits, current_player
        for idx in range(GRID_ROWS * GRID_COLS):
            if matched[idx] and not removed[idx] and matched_time[idx] is not None:
                if now - matched_time[idx] > 1.0:
                    removed[idx] = True
                    basket_fruits[current_player].append(fruit_grid[idx])

    def handle_match_check():
        global selected, revealed, matched, removed, current_player, scores
        global checking_match, match_check_start_time, matched_time, game_over

        if checking_match and now - match_check_start_time >= 1.0:
            checking_match = False
            if len(selected) < 2:
                return
            i1, i2 = selected
            if fruit_grid[i1] == fruit_grid[i2]:
                matched[i1] = True
                matched[i2] = True
                matched_time[i1] = now
                matched_time[i2] = now
                scores[current_player] += 1
            else:
                revealed[i1] = False
                revealed[i2] = False
                current_player = (current_player + 1) % 2
            selected.clear()
            if matched.count(True) == len(matched) - 1:
                game_over = True

    handle_initial_reveal()
    check_game_timer()
    process_matched_fruits()
    handle_match_check()

    glutPostRedisplay()


def get_game_result_message(): #message is shown when player wins
    p1 = scores[0]
    p2 = scores[1]
    if p1 ==  p2:
        return "Draw!"
    elif p1 > p2:
        return "Player 1 wins!"
    elif p1 < p2:
        return "Player 2 wins!"
    else:
        return "Draw!"

def showScreen():
    global paused
    
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)
    setupCamera()
    
    def draw_game_elements():
        draw_platform_grid()
        draw_grid()
        draw_basket(-350, 400, 0, basket_fruits[0])
        draw_text(90, 60, "Player 2 Basket")
        draw_basket(350, 400, 0, basket_fruits[1])
        draw_text(780, 60, "Player 1 Basket")
        draw_ttt()

    def draw_game_ui():
        if ttt_mode:
            draw_text(10, 770, "Tic Tac Toe Mode (T to toggle, 1-9 to play, K for cheat)")
        else:
            draw_text(10, 770, f"Fruit Matching Mode (T to toggle, 1-9 to play, K for cheat)")
            draw_text(10, 740, f"Player {current_player+1}'s turn")
            draw_text(10, 710, f"Scores: P1={scores[0]}  P2={scores[1]}")

    def draw_timer():
        if not game_over:
            now = time.time()
            elapsed = now - start_time - total_paused
            time_left = max(0, int(timer_limit - elapsed))
            mins, secs = divmod(time_left, 60)
            timer_str = f"Time Left: {mins:02d}:{secs:02d}"
            draw_text(800, 770, timer_str, GLUT_BITMAP_HELVETICA_18)


    def draw_game_over():
        if game_over:
            result_message = get_game_result_message()
            draw_text(400, 400, f"Game Over! {result_message}", GLUT_BITMAP_TIMES_ROMAN_24)
            draw_text(400, 370, "Press R to restart.", GLUT_BITMAP_HELVETICA_18)

    def draw_pause():
        if paused:
            draw_text(420, 650, "PAUSED", GLUT_BITMAP_TIMES_ROMAN_24)

    draw_game_elements()
    draw_game_ui()
    draw_timer()
    draw_game_over()
    draw_pause()

    glutSwapBuffers()
def main():
    setup_fruits()
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"Fruit Basket Brawl")
    glEnable(GL_DEPTH_TEST)
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)
    glutMainLoop()

if __name__ == "__main__":
    main()
