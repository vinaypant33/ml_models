import os
from p5 import *

# HD resolution
WIDTH, HEIGHT = 1920, 1080

# Animation config
GROW_FRAMES = 120
MOVE_FRAMES = 240
TOTAL_FRAMES = GROW_FRAMES + MOVE_FRAMES
START_RADIUS = 20
MAX_RADIUS = 250
GROW_PER_FRAME = (MAX_RADIUS - START_RADIUS) / GROW_FRAMES

frame_idx = 0

def ease_in_out_quad(u):
    return 2*u*u if u < 0.5 else -1 + (4 - 2*u)*u

def setup():
    size(WIDTH, HEIGHT)
    os.makedirs('frames_hd', exist_ok=True)

def draw():
    global frame_idx
    background(30)

    if frame_idx < GROW_FRAMES:
        radius = START_RADIUS + GROW_PER_FRAME * frame_idx
        cx = WIDTH // 2
    else:
        radius = MAX_RADIUS
        t = frame_idx - GROW_FRAMES
        cx = int(ease_in_out_quad(t / MOVE_FRAMES) * (WIDTH - 2*MAX_RADIUS) + MAX_RADIUS)

    cy = HEIGHT // 2
    fill(255)
    circle((cx, cy), radius * 2)

    save_frame(f'frames_hd/frame_{frame_idx:05d}.png')

    frame_idx += 1
    if frame_idx > TOTAL_FRAMES:
        no_loop()
        exit()

run(frame_rate=60)
