import os
from math import sin, cos, pi
from p5 import *


os.environ["VISPY_BACKEND"] = "osmesa"
os.environ["VISPY_BACKEND"] = "egl"

WIDTH, HEIGHT = 1920, 1080
FPS = 60

STEM_FRAMES = 180
LEAF_FRAMES = 150
BLOOM_FRAMES = 180
HOLD_FRAMES = 60
TOTAL_FRAMES = STEM_FRAMES + LEAF_FRAMES + BLOOM_FRAMES + HOLD_FRAMES

GROUND_H = int(HEIGHT * 0.18)
STEM_MAX = int(HEIGHT * 0.55)
STEM_X = WIDTH // 2
STEM_Y0 = HEIGHT - GROUND_H
STEM_WIDTH = 10

LEAF_SIZE = int(HEIGHT * 0.12)
LEAF_OFFSET_Y = int(HEIGHT * 0.25)

BUD_RADIUS = int(HEIGHT * 0.03)
PETAL_LENGTH = int(HEIGHT * 0.12)
PETAL_WIDTH = int(HEIGHT * 0.06)
PETAL_COUNT = 8
CENTER_RADIUS = int(HEIGHT * 0.035)

frame_idx = 0

def ease_in_out_cubic(u):
    return 4*u*u*u if u < 0.5 else 1 - pow(-2*u + 2, 3)/2

def ease_out_quad(u):
    return 1 - (1 - u)*(1 - u)

def lerp(a, b, t):
    return a + (b - a) * t

def sky():
    background(135, 206, 235)
    no_stroke()
    fill(120, 180, 90)
    rect((0, HEIGHT - GROUND_H), WIDTH, GROUND_H)
    stroke(34, 139, 34)
    stroke_weight(2)
    for x in range(0, WIDTH, 20):
        h = 10 + int(8 * sin(x * 0.05))
        line((x, HEIGHT - GROUND_H), (x, HEIGHT - GROUND_H - h))

def draw_stem(g):
    stroke(34, 139, 34)
    stroke_weight(STEM_WIDTH)
    x0, y0 = STEM_X, STEM_Y0
    y1 = y0 - int(STEM_MAX * g)
    line((x0, y0), (x0, y1))
    return x0, y1

def draw_leaves(cx, cy, f):
    no_stroke()
    fill(46, 139, 87)
    a = lerp(0.0, pi/6, ease_in_out_cubic(f))
    s = lerp(0.2, 1.0, ease_in_out_cubic(f))
    lx = cx - int(LEAF_SIZE * 0.9)
    rx = cx + int(LEAF_SIZE * 0.9)
    ly = cy + LEAF_OFFSET_Y
    push_matrix()
    translate(lx, ly)
    rotate(-a)
    ellipse((0, 0), LEAF_SIZE * s, int(LEAF_SIZE * 0.55 * s))
    pop_matrix()
    push_matrix()
    translate(rx, ly - int(LEAF_SIZE * 0.15))
    rotate(a)
    ellipse((0, 0), LEAF_SIZE * s, int(LEAF_SIZE * 0.55 * s))
    pop_matrix()

def draw_flower(cx, cy, t):
    o = ease_in_out_cubic(min(1.0, t))
    no_stroke()
    fill(255, 182, 193)
    open_amt = lerp(0.0, pi/3, o)
    for i in range(PETAL_COUNT):
        theta = 2*pi * i / PETAL_COUNT
        px = cx + int(10 * sin(theta))
        py = cy + int(10 * cos(theta))
        push_matrix()
        translate(px, py)
        rotate(theta + open_amt * 0.6)
        ellipse((0, 0), PETAL_WIDTH, PETAL_LENGTH)
        pop_matrix()
    fill(238, 213, 0)
    circle((cx, cy), CENTER_RADIUS * 2)

def setup():
    size(WIDTH, HEIGHT)
    os.makedirs('flower_frames', exist_ok=True)

def draw():
    global frame_idx
    sky()
    if frame_idx < STEM_FRAMES:
        g = ease_in_out_cubic(frame_idx / STEM_FRAMES)
        cx, cy = draw_stem(g)
    else:
        cx, cy = STEM_X, STEM_Y0 - STEM_MAX
        draw_stem(1.0)
    if frame_idx >= STEM_FRAMES:
        lf = min(1.0, (frame_idx - STEM_FRAMES) / LEAF_FRAMES)
        draw_leaves(cx, cy, lf)
    if frame_idx >= STEM_FRAMES + int(LEAF_FRAMES * 0.5):
        bf = min(1.0, (frame_idx - (STEM_FRAMES + int(LEAF_FRAMES * 0.5))) / BLOOM_FRAMES)
        sway = sin(frame_idx * 0.02) * 6
        push_matrix()
        translate(cx, cy - int(BUD_RADIUS * lerp(0.2, 1.0, bf)))
        rotate(radians(sway))
        draw_flower(0, 0, bf)
        pop_matrix()
    save_frame(f'flower_frames/frame_{frame_idx:05d}.png')
    frame_idx += 1
    if frame_idx > TOTAL_FRAMES:
        no_loop()
        exit()

run(frame_rate=FPS)
