"""
extract_frames.py — ดึง frame จากวิดีโอเพื่อเพิ่ม training dataset

ดึงจากทุกวิดีโอที่มีในโฟลเดอร์ CURRENT_DIR โดยอัตโนมัติ
ผลลัพธ์บันทึกลง datasets/new_raw_data/ พร้อม label

วิธีใช้:
    python extract_frames.py

หลังรันแล้ว ต้อง label รูปใน new_raw_data/ ด้วย LabelImg หรือ Roboflow
แล้วย้ายมาไว้ใน datasets/train/ และ datasets/valid/
"""

import cv2
import os
import numpy as np

# ─── Config ───────────────────────────────────────────────────────────────────

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR  = os.path.join(CURRENT_DIR, "datasets", "new_raw_data")

# รายการวิดีโอทั้งหมดที่ต้องการดึง frame
# key = ชื่อไฟล์, value = ดึงทุกกี่ frame (ปรับตาม fps ของแต่ละวิดีโอ)
VIDEO_CONFIGS = {
    "fish_video.mp4":   60,   # 60fps  → ดึงทุก 60f = ~1 รูป/วินาที
    "fish_video_2.mp4": 25,   # 25fps  → ดึงทุก 25f = ~1 รูป/วินาที
    "fish_video_3.mp4": 30,   # 30fps  → ดึงทุก 30f = ~1 รูป/วินาที  (วิดีโอใหญ่สุด)
    "fish_video_4.mp4": 30,   # 30fps  → ดึงทุก 30f = ~1 รูป/วินาที
}


# ─── Helpers ──────────────────────────────────────────────────────────────────

def imwrite_safe(path: str, img: np.ndarray) -> bool:
    """บันทึกภาพรองรับ path ที่มีภาษาไทย"""
    try:
        ok, buf = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 95])
        if ok:
            buf.tofile(path)
        return ok
    except Exception as e:
        print(f"  [Error] Cannot save {path}: {e}")
        return False


def next_index(output_dir: str) -> int:
    """หา index ถัดไปที่ยังไม่ซ้ำในโฟลเดอร์ output"""
    existing = [
        f for f in os.listdir(output_dir)
        if f.startswith("goldfish_") and f.endswith(".jpg")
    ]
    if not existing:
        return 0
    nums = []
    for name in existing:
        try:
            nums.append(int(name.replace("goldfish_", "").replace(".jpg", "")))
        except ValueError:
            pass
    return max(nums) + 1 if nums else 0


# ─── Main ─────────────────────────────────────────────────────────────────────

def extract_from_video(
    video_path: str,
    output_dir: str,
    every_n: int,
    start_index: int,
) -> int:
    """
    ดึง frame จากวิดีโอ 1 ไฟล์

    Returns:
        จำนวนรูปที่บันทึกได้
    """
    name = os.path.basename(video_path)

    if not os.path.exists(video_path):
        print(f"  [Skip] ไม่พบไฟล์: {name}")
        return 0

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"  [Skip] เปิดวิดีโอไม่สำเร็จ: {name}")
        return 0

    total  = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps    = cap.get(cv2.CAP_PROP_FPS)
    expect = total // every_n
    print(f"\n  {name}")
    print(f"    {total} frames @ {fps:.0f}fps  |  extract every {every_n}f  |  expect ~{expect} images")

    saved      = 0
    frame_idx  = 0
    save_idx   = start_index

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_idx % every_n == 0:
            filename  = f"goldfish_{save_idx:05d}.jpg"
            save_path = os.path.join(output_dir, filename)
            if imwrite_safe(save_path, frame):
                saved    += 1
                save_idx += 1
                if saved % 20 == 0:
                    print(f"    ... {saved} images saved")

        frame_idx += 1

    cap.release()
    print(f"    Done: {saved} images saved")
    return saved


def main():
    print(f"\nOutput dir: {OUTPUT_DIR}")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # หา index เริ่มต้น (ต่อจากรูปที่มีอยู่แล้ว ไม่ทับ)
    start = next_index(OUTPUT_DIR)
    print(f"Starting from index: {start}")

    total_saved = 0
    current_idx = start

    for filename, every_n in VIDEO_CONFIGS.items():
        video_path = os.path.join(CURRENT_DIR, filename)
        n = extract_from_video(video_path, OUTPUT_DIR, every_n, current_idx)
        total_saved  += n
        current_idx  += n

    print(f"\n{'='*50}")
    print(f"Finished! Total new images: {total_saved}")
    print(f"Output: {OUTPUT_DIR}")
    print(f"\nNext step: label these images with LabelImg or Roboflow,")
    print(f"then move to datasets/train/ and datasets/valid/")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    main()
