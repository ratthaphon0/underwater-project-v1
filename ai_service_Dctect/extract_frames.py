import cv2
import os
import numpy as np # ต้องใช้ numpy ช่วยแก้เรื่องภาษาไทย

# --- 1. ตั้งค่า Path ---
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
VIDEO_FILENAME = 'fish_video.mp4' 
VIDEO_PATH = os.path.join(CURRENT_DIR, VIDEO_FILENAME)
OUTPUT_DIR = os.path.join(CURRENT_DIR, 'datasets', 'new_raw_data')
EVERY_N_FRAME = 30 

def imread_unicode(path):
    """อ่านไฟล์ภาพ/วิดีโอ จาก Path ที่มีภาษาไทย"""
    stream = open(path, "rb")
    bytes = bytearray(stream.read())
    numpyarray = np.asarray(bytes, dtype=np.uint8)
    return cv2.imdecode(numpyarray, cv2.IMREAD_UNCHANGED)

def imwrite_unicode(path, img):
    """บันทึกไฟล์ภาพ ลง Path ที่มีภาษาไทย"""
    try:
        is_success, im_buf_arr = cv2.imencode(".jpg", img)
        im_buf_arr.tofile(path)
        return True
    except Exception as e:
        print(f"Error saving: {e}")
        return False

def main():
    print(f"📂 โฟลเดอร์ทำงาน: {CURRENT_DIR}")
    
    # เช็คว่ามีไฟล์วิดีโอไหม
    if not os.path.exists(VIDEO_PATH):
        print(f"❌ หาไฟล์ไม่เจอ: {VIDEO_FILENAME}")
        return

    # สร้างโฟลเดอร์ปลายทาง
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # เปิดวิดีโอ
    cap = cv2.VideoCapture(VIDEO_PATH)
    
    if not cap.isOpened():
        print("❌ เปิดวิดีโอไม่สำเร็จ (อาจเป็นเพราะ Path ภาษาไทย)")
        print("💡 ลองเปลี่ยนชื่อโฟลเดอร์ 'Project เรือดำน้ำ' เป็นภาษาอังกฤษดูครับ")
        return

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"🎥 พบวิดีโอ! ความยาว {total_frames} เฟรม")
    print(f"💾 กำลังบันทึกรูปลง: {OUTPUT_DIR}")

    saved_count = 0
    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % EVERY_N_FRAME == 0:
            image_name = f"tilapia_add_{saved_count:04d}.jpg"
            save_path = os.path.join(OUTPUT_DIR, image_name)
            
            # ใช้ฟังก์ชันพิเศษที่รองรับภาษาไทย
            success = imwrite_unicode(save_path, frame)
            
            if success:
                print(f"📸 Saved ({saved_count}): {image_name}")
                saved_count += 1
            else:
                print(f"❌ Failed to save: {image_name}")

        frame_count += 1

    cap.release()
    print(f"\n✅ เสร็จสิ้น! ได้รูปทั้งหมด {saved_count} รูป")

if __name__ == "__main__":
    main()