import os, math
os.environ["VISPY_BACKEND"] = "egl"
from p5 import *

WIDTH, HEIGHT = 1920, 1080
FPS = 60
STEM_FRAMES = 160
LEAF_FRAMES = 100
BUD_FRAMES = 60
BLOOM_FRAMES = 160
TOTAL_FRAMES = STEM_FRAMES + LEAF_FRAMES + BUD_FRAMES + BLOOM_FRAMES
FRAMES_DIR = 'flower_frames'

GROUND_FRAC = 0.82
STEM_X = 0.50
STEM_TOP_Y_FRAC = 0.35
STEM_WIDTH = 14
STEM_CURVE = 0.08
WIND_SWAY_PIX = 18
WIND_SPEED = 0.9

LEAF_LENGTH = 220
LEAF_WIDTH = 120
LEAF_Y_FRAC_1 = 0.60
LEAF_Y_FRAC_2 = 0.66
LEAF_ANGLE = 0.95

PETAL_COUNT = 12
PETAL_LENGTH = 200
PETAL_WIDTH = 100
CENTER_RADIUS = 78
PETAL_BASE_RGB = (238, 184, 65)
CENTER_RGB = (120, 82, 48)
STEM_RGB = (46, 120, 60)
LEAF_RGB = (64, 158, 74)
GROUND_RGB = (92, 122, 78)
EDGE_SOIL_RGB = (78, 56, 42)

SKY_TOP = (120, 170, 230)
SKY_BOTTOM = (180, 210, 255)

frame_idx = 0

def ease_in_out_cubic(u):
    return 4*u*u*u if u < 0.5 else 1 - pow(-2*u + 2, 3) / 2

def ease_out_back(u, k=1.5):
    t = u - 1
    return t*t*((k+1)*t + k) + 1

def clamp01(x):
    return 0 if x < 0 else 1 if x > 1 else x

def lerp(a,b,t):
    return a + (b-a)*t

def lerp3(c1,c2,t):
    return (int(lerp(c1[0],c2[0],t)), int(lerp(c1[1],c2[1],t)), int(lerp(c1[2],c2[2],t)))

def draw_gradient_sky(gy):
    steps = 120
    h = gy
    for i in range(steps):
        t = i/(steps-1)
        c = lerp3(SKY_TOP, SKY_BOTTOM, t)
        no_stroke()
        fill(*c)
        rect((0, int(t*h)), WIDTH, int(h/steps + 2))

def draw_ground(gy):
    no_stroke()
    fill(*GROUND_RGB)
    rect((0, gy), WIDTH, HEIGHT - gy)
    fill(*EDGE_SOIL_RGB)
    rect((0, gy), WIDTH, 18)

def stem_x_at(y0, y1, y):
    h = y1 - y0
    u = (y - y0)/h if h != 0 else 0
    base = WIDTH * STEM_X
    curve = (u - 0.5) * STEM_CURVE * WIDTH
    return base + curve

def draw_stem(y0, y1, sway_phase, width_px):
    steps = 90
    stroke(*STEM_RGB)
    stroke_weight(width_px)
    lastx = stem_x_at(y0,y1,y0)
    lasty = y0
    for i in range(1, steps+1):
        t = i/steps
        yy = lerp(y0, y1, t)
        sway = math.sin((sway_phase + yy*0.01) * WIND_SPEED) * WIND_SWAY_PIX * (0.3 + 0.7*t)
        xx = stem_x_at(y0,y1,yy) + sway
        line((lastx, lasty), (xx, yy))
        lastx, lasty = xx, yy

def leaf_shape(cx, cy, angle, scale_):
    push_matrix()
    translate(cx, cy)
    rotate(angle)
    scale(scale_)
    no_stroke()
    fill(*LEAF_RGB)
    begin_shape()
    vertex(0, 0)
    bezier_vertex(LEAF_LENGTH*0.25, -LEAF_WIDTH*0.9, LEAF_LENGTH*0.75, -LEAF_WIDTH*0.4, LEAF_LENGTH, 0)
    bezier_vertex(LEAF_LENGTH*0.75, LEAF_WIDTH*0.4, LEAF_LENGTH*0.25, LEAF_WIDTH*0.9, 0, 0)
    end_shape(CLOSE)
    pop_matrix()

def draw_flower(cx, cy, open_t):
    no_stroke()
    push_matrix()
    translate(cx, cy)
    for i in range(PETAL_COUNT):
        a = (2*math.pi / PETAL_COUNT) * i
        s = 0.18 + 0.82 * ease_out_back(clamp01(open_t))
        px = math.cos(a) * CENTER_RADIUS * 0.35
        py = math.sin(a) * CENTER_RADIUS * 0.35
        push_matrix()
        translate(px, py)
        rotate(a)
        k = 0.75 + 0.25*math.sin(i*1.7)
        c = lerp3(PETAL_BASE_RGB, (255, 220, 120), 0.35*k)
        fill(*c)
        ellipse((PETAL_LENGTH*0.5*s, 0), PETAL_LENGTH*s, PETAL_WIDTH*s)
        pop_matrix()
    fill(*CENTER_RGB)
    circle((0,0), CENTER_RADIUS*2)
    pop_matrix()

def setup():
    size(WIDTH, HEIGHT)
    os.makedirs(FRAMES_DIR, exist_ok=True)
    try:
        smooth()
    except Exception:
        pass

def draw():
    global frame_idx
    gy = int(HEIGHT * GROUND_FRAC)
    background(*SKY_BOTTOM)
    draw_gradient_sky(gy)
    draw_ground(gy)

    if frame_idx < STEM_FRAMES:
        t = ease_in_out_cubic(frame_idx / STEM_FRAMES)
        y0 = gy
        y1 = int(lerp(gy, int(HEIGHT*STEM_TOP_Y_FRAC), t))
    else:
        y0 = gy
        y1 = int(HEIGHT*STEM_TOP_Y_FRAC)

    sway_phase = frame_idx * (2*math.pi/FPS) * 0.5
    draw_stem(y0, y1, sway_phase, STEM_WIDTH)

    if frame_idx <= STEM_FRAMES:
        leaf_t = 0.0
    elif frame_idx <= STEM_FRAMES + LEAF_FRAMES:
        leaf_t = ease_in_out_cubic((frame_idx - STEM_FRAMES) / LEAF_FRAMES)
    else:
        leaf_t = 1.0

    if leaf_t > 0:
        cx1 = stem_x_at(gy, y1, int(HEIGHT*LEAF_Y_FRAC_1)) - 10
        cy1 = int(HEIGHT*LEAF_Y_FRAC_1)
        cx2 = stem_x_at(gy, y1, int(HEIGHT*LEAF_Y_FRAC_2)) + 10
        cy2 = int(HEIGHT*LEAF_Y_FRAC_2)
        leaf_shape(cx1, cy1, -LEAF_ANGLE, leaf_t)
        leaf_shape(cx2, cy2, LEAF_ANGLE, leaf_t*0.96)

    if frame_idx <= STEM_FRAMES + LEAF_FRAMES:
        bud_t = 0.0
    elif frame_idx <= STEM_FRAMES + LEAF_FRAMES + BUD_FRAMES:
        bud_t = ease_in_out_cubic((frame_idx - STEM_FRAMES - LEAF_FRAMES) / BUD_FRAMES)
    else:
        bud_t = 1.0

    if frame_idx <= STEM_FRAMES + LEAF_FRAMES + BUD_FRAMES:
        open_t = 0.0
    else:
        open_t = ease_in_out_cubic((frame_idx - STEM_FRAMES - LEAF_FRAMES - BUD_FRAMES) / BLOOM_FRAMES)

    cx_top = stem_x_at(gy, y1, y1)
    cy_top = y1
    if bud_t > 0:
        r = CENTER_RADIUS * (0.6 + 0.4*bud_t)
        no_stroke()
        fill(*CENTER_RGB)
        circle((cx_top, cy_top), r*2)

    if open_t > 0:
        draw_flower(cx_top, cy_top, open_t)

    save_frame(f'{FRAMES_DIR}/frame_{frame_idx:05d}.png')
    frame_idx += 1
    if frame_idx > TOTAL_FRAMES:
        no_loop()
        exit()

run(frame_rate=FPS)
