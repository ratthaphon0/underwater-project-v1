from ultralytics import YOLO
import os
import glob


# --- 1. ตั้งค่า Path อัตโนมัติ (เพื่อนโหลดไป รันได้เลย ไม่ต้องแก้ Path) ---
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# ชี้ไปที่ models/best.pt (ตามโครงสร้างใน Git ของคุณเป๊ะๆ)
MODEL_PATH = os.path.join(CURRENT_DIR, 'models', 'best.pt')

# โฟลเดอร์รูปภาพสำหรับทดสอบ (datasets/test/images)
TEST_IMAGES_DIR = os.path.join(CURRENT_DIR, 'datasets', 'test', 'images')
# โฟลเดอร์สำหรับเก็บผลลัพธ์
OUTPUT_DIR = os.path.join(CURRENT_DIR, 'runs', 'predict')

def main():
    print(f"📂 กำลังทำงานอยู่ที่: {CURRENT_DIR}")

    # 1. เช็คว่ามีไฟล์โมเดลไหม
    if not os.path.exists(MODEL_PATH):
        print(f"❌ ไม่พบไฟล์โมเดลที่: {MODEL_PATH}")
        print("💡 คำแนะนำ: ลองสั่ง git pull ล่าสุด หรือเช็คว่าในโฟลเดอร์ models มีไฟล์ best.pt ไหม")
        return

    # 2. โหลดโมเดล
    print(f"🚀 กำลังโหลดโมเดลจาก: {MODEL_PATH}")
    try:
        model = YOLO(MODEL_PATH)
    except Exception as e:
        print(f"❌ โหลดโมเดลไม่สำเร็จ: {e}")
        return

    # 3. หารูปภาพทดสอบ (รองรับ .jpg, .png, .jpeg)
    image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.JPG']
    image_files = []
    for ext in image_extensions:
        image_files.extend(glob.glob(os.path.join(TEST_IMAGES_DIR, ext)))

    if not image_files:
        print(f"⚠️ ไม่พบรูปภาพในโฟลเดอร์: {TEST_IMAGES_DIR}")
        print("💡 ลองหาเอารูปปลามาใส่ใน datasets/test/images สักรูปนะครับ")
        return

    # เลือกรูปแรกมาเทส (หรือจะวนลูปทุกรูปก็ได้)
    test_image = image_files[0] 
    print(f"📸 กำลังทดสอบกับรูป: {os.path.basename(test_image)}")

    # 4. สั่ง AI ตรวจจับ!
    # save=True จะบันทึกผลลัพธ์ลงโฟลเดอร์ runs/predict/exp...
    # conf=0.5 คือต้องมั่นใจเกิน 50% ถึงจะตีกรอบ
    model.predict(source=test_image, save=True, conf=0.5, project='runs', name='predict', exist_ok=True)

    print("\n" + "="*50)
    print(f"✅ เรียบร้อย! ผลลัพธ์ถูกบันทึกไว้ที่: {os.path.join(OUTPUT_DIR)}")
    print("="*50)

    # (Optional) ถ้าอยากให้เด้งโชว์รูปขึ้นมาเลย (เฉพาะ Windows/Desktop)
    # result_img_path = os.path.join(OUTPUT_DIR, os.path.basename(test_image))
    # if os.path.exists(result_img_path):
    #     img = cv2.imread(result_img_path)
    #     cv2.imshow("Detection Result", img)
    #     cv2.waitKey(0)
    #     cv2.destroyAllWindows()

if __name__ == "__main__":
    main()