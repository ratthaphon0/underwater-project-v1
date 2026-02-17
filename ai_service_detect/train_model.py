from ultralytics import YOLO
import os
import shutil
import yaml


# --- 1. ตั้งค่า Path ---
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(CURRENT_DIR, 'datasets')
DATA_YAML_PATH = os.path.join(DATASET_DIR, 'data.yaml')

# ปลายทางเก็บโมเดล (ที่ทีมจะเรียกใช้)
DEST_MODEL_DIR = os.path.join(CURRENT_DIR, 'models')
DEST_MODEL_PATH = os.path.join(DEST_MODEL_DIR, 'best.pt')

def force_fix_yaml():
    """ฟังก์ชันแก้ data.yaml (เหมือนเดิม เพราะทำงานดีแล้ว)"""
    print("🔧 กำลังตรวจสอบไฟล์ data.yaml...")
    if not os.path.exists(DATA_YAML_PATH):
        print(f"❌ หาไฟล์ไม่เจอ: {DATA_YAML_PATH}")
        return False

    with open(DATA_YAML_PATH, 'r', encoding='utf-8') as f:
        try:
            old_data = yaml.safe_load(f)
        except yaml.YAMLError:
            old_data = {}

    if os.path.exists(os.path.join(DATASET_DIR, 'valid')):
        val_dir_name = 'valid'
    else:
        val_dir_name = 'val'
    
    # บังคับเขียน Path เต็ม
    new_data = {
        'path': DATASET_DIR,
        'train': os.path.join(DATASET_DIR, 'train', 'images'),
        'val': os.path.join(DATASET_DIR, val_dir_name, 'images'),
        'test': os.path.join(DATASET_DIR, 'test', 'images'),
    }

    if 'names' in old_data:
        new_data['names'] = old_data['names']
    else:
        new_data['names'] = {0: 'Tilapia'}
    
    if 'nc' in old_data:
        new_data['nc'] = old_data['nc']

    with open(DATA_YAML_PATH, 'w', encoding='utf-8') as f:
        yaml.dump(new_data, f, default_flow_style=False, allow_unicode=True)

    print("✅ Config พร้อมใช้งาน!")
    return True

def find_latest_best_model():
    """
    ฟังก์ชันค้นหาไฟล์ best.pt ที่ 'ใหม่ที่สุด' ในโฟลเดอร์ runs ทั้งหมด
    ไม่ว่าจะซ่อนอยู่ลึกแค่ไหนก็ตาม
    """
    search_dir = os.path.join(CURRENT_DIR, 'runs')
    best_file = None
    latest_time = 0

    # เดินหาไฟล์ best.pt ทุกซอกทุกมุม
    print(f"🔍 กำลังสแกนหาไฟล์ best.pt ล่าสุดใน {search_dir} ...")
    
    for root, dirs, files in os.walk(search_dir):
        for file in files:
            if file == 'best.pt':
                full_path = os.path.join(root, file)
                # เช็คเวลาไฟล์
                file_time = os.path.getmtime(full_path)
                if file_time > latest_time:
                    latest_time = file_time
                    best_file = full_path

    return best_file

def main():
    # 1. แก้ Config
    if not force_fix_yaml():
        return

    print("🚀 กำลังเริ่มเทรนโมเดล...")

    # 2. เริ่มเทรน
    model = YOLO('yolov8n.pt') 
    
    # หมายเหตุ: การใช้ project='runs/detect' บางครั้งทำให้เกิดโฟลเดอร์ซ้อน
    # แต่ฟังก์ชัน copy ใหม่ของเราจะจัดการปัญหานี้ได้ครับ
    try:
        model.train(
            data=DATA_YAML_PATH,
            epochs=50,
            imgsz=640,
            batch=8,
            device=0,
            project='runs/detect',
            name='tilapia_model',
            patience=10,
            workers=1,
            exist_ok=True 
        )
    except Exception as e:
        print(f"⚠️ เกิดข้อผิดพลาดขณะเทรน (อาจเป็น Bug ของ YOLO ในการสร้างโฟลเดอร์): {e}")
        # ถึงเทรน Error ตอนจบ แต่ถ้าได้ไฟล์ best.pt แล้ว เราก็จะพยายาม copy อยู่ดี

    # 3. ระบบ Auto-Copy อัจฉริยะ (Smart Copy)
    print("\n" + "="*50)
    print("📦 ระบบจัดการไฟล์อัตโนมัติกำลังทำงาน...")

    latest_model = find_latest_best_model()

    if latest_model:
        print(f"✅ เจอไฟล์ล่าสุดที่: {latest_model}")
        
        # สร้างโฟลเดอร์ปลายทางถ้ายังไม่มี
        os.makedirs(DEST_MODEL_DIR, exist_ok=True)
        
        # ก๊อปปี้และเขียนทับทันที
        try:
            shutil.copy(latest_model, DEST_MODEL_PATH)
            print(f"🎉 อัปเดตสำเร็จ! ทีมสามารถใช้ไฟล์นี้ได้เลย: {DEST_MODEL_PATH}")
        except Exception as e:
            print(f"❌ ก๊อปปี้ไม่สำเร็จ: {e}")
    else:
        print("❌ ไม่พบไฟล์ best.pt ในโฟลเดอร์ runs เลย")
    
    print("="*50 + "\n")

if __name__ == '__main__':
    main()