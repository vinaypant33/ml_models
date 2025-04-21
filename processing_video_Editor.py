import os
import glob
import cv2
from p5 import *

WIDTH, HEIGHT = 1920, 1080
FPS = 60
GROW_FRAMES = 120
MOVE_FRAMES = 240
TOTAL_FRAMES = GROW_FRAMES + MOVE_FRAMES
START_RADIUS = 20
MAX_RADIUS = 250
GROW_PER_FRAME = (MAX_RADIUS - START_RADIUS) / GROW_FRAMES
FRAMES_DIR = 'flower_frames'
OUTPUT_MP4 = 'circle_grow_move_HD_cv2.mp4'
OUTPUT_AVI = 'circle_grow_move_HD_cv2.avi'

frame_idx = 0

def ease_in_out_quad(u):
    return 2*u*u if u < 0.5 else -1 + (4 - 2*u)*u

def setup():
    size(WIDTH, HEIGHT)
    os.makedirs(FRAMES_DIR, exist_ok=True)

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
    save_frame(f'{FRAMES_DIR}/frame_{frame_idx:05d}.png')
    frame_idx += 1
    if frame_idx > TOTAL_FRAMES:
        no_loop()
        exit()

def assemble_video_with_opencv():
    files = sorted(glob.glob(f'{FRAMES_DIR}/frame_*.png'))
    if not files:
        raise RuntimeError('No frames found')
    probe = cv2.imread(files[0])
    h, w = probe.shape[:2]
    if (w, h) != (WIDTH, HEIGHT):
        raise RuntimeError(f'Frame size mismatch: got {(w,h)}, expected {(WIDTH,HEIGHT)}')

    fourcc_try = [('avc1', OUTPUT_MP4), ('mp4v', OUTPUT_MP4), ('XVID', OUTPUT_AVI)]
    writer = None
    out_path = None
    for fourcc_str, path in fourcc_try:
        fourcc = cv2.VideoWriter_fourcc(*fourcc_str)
        ext_path = path
        if fourcc_str == 'XVID' and path.endswith('.mp4'):
            ext_path = OUTPUT_AVI
        vw = cv2.VideoWriter(ext_path, fourcc, FPS, (WIDTH, HEIGHT))
        if vw.isOpened():
            writer = vw
            out_path = ext_path
            break
        vw.release()

    if writer is None:
        raise RuntimeError('No suitable codec found. Try installing HEVC/H.264 codecs or use .avi with XVID.')

    for f in files:
        img = cv2.imread(f)
        if img is None:
            continue
        if (img.shape[1], img.shape[0]) != (WIDTH, HEIGHT):
            img = cv2.resize(img, (WIDTH, HEIGHT), interpolation=cv2.INTER_AREA)
        writer.write(img)

    writer.release()
    print(f'Video written: {out_path}')

if __name__ == '__main__':
    run(frame_rate=FPS)
    assemble_video_with_opencv()
