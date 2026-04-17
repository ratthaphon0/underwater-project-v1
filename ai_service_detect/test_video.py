import cv2
from ultralytics import YOLO
import os

# --- 1. ตั้งค่า Path แบบอัตโนมัติ  ---
# หาตำแหน่งโฟลเดอร์ปัจจุบันที่ไฟล์นี้อยู่
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# ชี้เป้าไปที่ Model (ตามโครงสร้าง Git ของคุณ)
MODEL_PATH = os.path.join(CURRENT_DIR, 'models', 'best.pt')

# ชี้เป้าไปที่ Video (เลือกไฟล์ที่มีอยู่ในโฟลเดอร์เดียวกัน)
# จากภาพคุณมี fish_video.mp4, fish_video_2.mp4 เลือกมาสักอันครับ
VIDEO_PATH = os.path.join(CURRENT_DIR, 'fish_video.mp4') 

# โฟลเดอร์สำหรับเก็บผลลัพธ์
OUTPUT_DIR = os.path.join(CURRENT_DIR, 'runs', 'detect', 'video_result')


def has_display():
    """ตรวจว่ามี GUI (หน้าจอ) หรือไม่ — ถ้ารันใน Docker จะไม่มี"""
    display = os.environ.get('DISPLAY', '')
    if not display:
        return False
    try:
        cv2.namedWindow("__test__", cv2.WINDOW_NORMAL)
        cv2.destroyWindow("__test__")
        return True
    except Exception:
        return False


def main():
    print(f"📂 โฟลเดอร์ทำงาน: {CURRENT_DIR}")

    # --- เช็คความพร้อมของไฟล์ ---
    if not os.path.exists(MODEL_PATH):
        print(f"❌ ไม่พบไฟล์โมเดลที่: {MODEL_PATH}")
        print("💡 อย่าลืม git pull หรือก๊อปปี้ไฟล์ best.pt ใส่โฟลเดอร์ models นะครับ")
        return

    if not os.path.exists(VIDEO_PATH):
        print(f"❌ ไม่พบไฟล์วิดีโอที่: {VIDEO_PATH}")
        print("💡 ลองเช็คชื่อไฟล์วิดีโอในโค้ดอีกทีครับ ว่าตรงกับที่มีไหม")
        return

    # --- โหลดโมเดล ---
    print(f"🚀 กำลังโหลดโมเดล: {os.path.basename(MODEL_PATH)}")
    try:
        model = YOLO(MODEL_PATH)
    except Exception as e:
        print(f"❌ โหลดโมเดลไม่ได้: {e}")
        return

    # --- เปิดวิดีโอ ---
    print(f"🎥 กำลังเปิดวิดีโอ: {os.path.basename(VIDEO_PATH)}")
    cap = cv2.VideoCapture(VIDEO_PATH)

    if not cap.isOpened():
        print("❌ เปิดไฟล์วิดีโอไม่สำเร็จ")
        return

    # ดึงข้อมูลวิดีโอ
    fps = int(cap.get(cv2.CAP_PROP_FPS)) or 30
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # ตรวจว่ามีหน้าจอไหม
    use_gui = has_display()

    # เตรียม VideoWriter (บันทึกผลลัพธ์เป็นไฟล์เสมอ)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, 'output.mp4')
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    if use_gui:
        # มี GUI — แสดงหน้าต่างด้วย
        cv2.namedWindow("Goldfish Detection", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Goldfish Detection", 800, 600)
        print("🟢 กำลังทำงาน (GUI mode)... กด 'q' เพื่อออก")
    else:
        # ไม่มี GUI (Docker) — บันทึกอย่างเดียว
        print(f"🟢 กำลังทำงาน (Headless mode)... บันทึกผลลัพธ์ไปที่ {output_path}")

    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            print("🎬 วิดีโอจบแล้ว")
            break

        frame_count += 1

        # ให้ AI ตรวจจับ
        results = model.predict(frame, conf=0.25, verbose=False)

        # วาดกรอบลงบนภาพ
        annotated_frame = results[0].plot()

        # บันทึกลงไฟล์
        writer.write(annotated_frame)

        if use_gui:
            # แสดงผลบนหน้าจอ
            cv2.imshow("Goldfish Detection", annotated_frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            # แสดง progress ทุก 50 frames
            if frame_count % 50 == 0:
                progress = (frame_count / total_frames * 100) if total_frames > 0 else 0
                print(f"   ⏳ Processing: {frame_count}/{total_frames} frames ({progress:.1f}%)")

    cap.release()
    writer.release()
    if use_gui:
        cv2.destroyAllWindows()

    print(f"✅ จบการทำงาน — ประมวลผล {frame_count} frames")
    print(f"📁 ผลลัพธ์บันทึกที่: {output_path}")

if __name__ == "__main__":
    main()