import cv2
import glob

FRAMES_DIR = "flower_frames"
OUTPUT_VIDEO = "flower_growth_HD.mp4"
FPS = 60
WIDTH, HEIGHT = 1920, 1080

def make_video():
    files = sorted(glob.glob(f"{FRAMES_DIR}/frame_*.png"))
    if not files:
        raise RuntimeError("No frames found in directory.")

    # Try H.264 mp4, fallback to AVI if codec unavailable
    fourcc_try = [("avc1", OUTPUT_VIDEO), ("mp4v", OUTPUT_VIDEO), ("XVID", "flower_growth_HD.avi")]
    writer = None
    out_path = None

    for fourcc_str, path in fourcc_try:
        fourcc = cv2.VideoWriter_fourcc(*fourcc_str)
        vw = cv2.VideoWriter(path, fourcc, FPS, (WIDTH, HEIGHT))
        if vw.isOpened():
            writer = vw
            out_path = path
            break
        vw.release()

    if writer is None:
        raise RuntimeError("No suitable codec found. Try XVID AVI.")

    for f in files:
        img = cv2.imread(f)
        if img is None:
            continue
        if (img.shape[1], img.shape[0]) != (WIDTH, HEIGHT):
            img = cv2.resize(img, (WIDTH, HEIGHT), interpolation=cv2.INTER_AREA)
        writer.write(img)

    writer.release()
    print(f"✅ Video saved as {out_path}")

if __name__ == "__main__":
    make_video()
