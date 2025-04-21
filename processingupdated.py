import os
import math
from p5 import *

WIDTH, HEIGHT = 1920, 1080
FPS = 60
STEM_FRAMES = 140
LEAF_FRAMES = 80
FLOWER_FRAMES = 140
TOTAL_FRAMES = STEM_FRAMES + LEAF_FRAMES + FLOWER_FRAMES
FRAMES_DIR = 'flower_frames'

GROUND_Y = int(HEIGHT * 0.82)
STEM_X = WIDTH // 2
STEM_TOP_Y_TARGET = int(HEIGHT * 0.38)
STEM_WIDTH = 14

LEAF_LENGTH = 200
LEAF_WIDTH = 110
LEAF_OFFSET_Y = int(HEIGHT * 0.58)

PETAL_COUNT = 12
PETAL_LENGTH = 180
PETAL_WIDTH = 90
CENTER_RADIUS = 70

frame_idx = 0

def ease_in_out_cubic(u):
    return 4*u*u*u if u < 0.5 else 1 - pow(-2*u + 2, 3) / 2

def draw_gradient_sky():
    steps = 80
    for i in range(steps):
        t = i / (steps - 1)
        r = int(120 + (180 - 120) * t)
        g = int(170 + (210 - 170) * t)
        b = int(230 + (255 - 230) * t)
        no_stroke()
        fill(r, g, b)
        y0 = int((HEIGHT * 0.0) + t * (GROUND_Y - HEIGHT * 0.0))
        rect((0, y0), WIDTH, int((GROUND_Y - 0) / steps + 2))

def draw_ground():
    no_stroke()
    fill(92, 122, 78)
    rect((0, GROUND_Y), WIDTH, HEIGHT - GROUND_Y)
    fill(78, 56, 42)
    rect((0, GROUND_Y), WIDTH, 18)

def draw_stem(stem_top_y):
    stroke(46, 120, 60)
    stroke_weight(STEM_WIDTH)
    line((STEM_X, GROUND_Y), (STEM_X, stem_top_y))

def leaf_shape(cx, cy, angle, scale_):
    push_matrix()
    translate(cx, cy)
    rotate(angle)
    scale(scale_)
    no_stroke()
    fill(64, 158, 74)
    begin_shape()
    vertex(0, 0)
    bezier_vertex(LEAF_LENGTH*0.25, -LEAF_WIDTH*0.9, LEAF_LENGTH*0.75, -LEAF_WIDTH*0.4, LEAF_LENGTH, 0)
    bezier_vertex(LEAF_LENGTH*0.75, LEAF_WIDTH*0.4, LEAF_LENGTH*0.25, LEAF_WIDTH*0.9, 0, 0)
    end_shape(CLOSE)
    pop_matrix()

def draw_flower(center_x, center_y, petal_open_t):
    no_stroke()
    push_matrix()
    translate(center_x, center_y)
    for i in range(PETAL_COUNT):
        a = (2*math.pi / PETAL_COUNT) * i
        open_scale = 0.2 + 0.8 * petal_open_t
        px = math.cos(a) * CENTER_RADIUS * 0.4
        py = math.sin(a) * CENTER_RADIUS * 0.4
        push_matrix()
        translate(px, py)
        rotate(a)
        fill(248, 208, 76)
        ellipse((PETAL_LENGTH*0.5*open_scale, 0), PETAL_LENGTH*open_scale, PETAL_WIDTH*open_scale)
        pop_matrix()
    fill(120, 82, 48)
    circle((0, 0), CENTER_RADIUS*2)
    pop_matrix()

def setup():
    size(WIDTH, HEIGHT)
    os.makedirs(FRAMES_DIR, exist_ok=True)
    no_smooth()

def draw():
    global frame_idx
    background(180, 210, 255)
    draw_gradient_sky()
    draw_ground()

    if frame_idx < STEM_FRAMES:
        t = ease_in_out_cubic(frame_idx / STEM_FRAMES)
        stem_top_y = int(GROUND_Y - t * (GROUND_Y - STEM_TOP_Y_TARGET))
        draw_stem(stem_top_y)
    else:
        stem_top_y = STEM_TOP_Y_TARGET
        draw_stem(stem_top_y)

    if frame_idx <= STEM_FRAMES:
        leaf_t = 0.0
    elif frame_idx <= STEM_FRAMES + LEAF_FRAMES:
        leaf_t = ease_in_out_cubic((frame_idx - STEM_FRAMES) / LEAF_FRAMES)
    else:
        leaf_t = 1.0

    if leaf_t > 0:
        leaf_shape(STEM_X - 10, LEAF_OFFSET_Y, -0.9, leaf_t)
        leaf_shape(STEM_X + 10, LEAF_OFFSET_Y + 40, 0.9, leaf_t*0.95)

    if frame_idx <= STEM_FRAMES + LEAF_FRAMES:
        flower_t = 0.0
    else:
        flower_phase = (frame_idx - STEM_FRAMES - LEAF_FRAMES) / FLOWER_FRAMES
        flower_t = ease_in_out_cubic(min(max(flower_phase, 0.0), 1.0))

    if flower_t > 0:
        draw_flower(STEM_X, STEM_TOP_Y_TARGET, flower_t)

    save_frame(f'{FRAMES_DIR}/frame_{frame_idx:05d}.png')
    frame_idx += 1
    if frame_idx > TOTAL_FRAMES:
        no_loop()
        exit()

run(frame_rate=FPS)
