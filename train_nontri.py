from ultralytics import YOLO
import sys
import torch

# --- Configuration for S Package (10GB GPU) ---
MODEL_NAME = 'yolov8n.pt'
EPOCHS = 60              # Reduced epochs for 1 hour limit
IMG_SIZE = 640
BATCH_SIZE = 16          # IMPORTANT: 10GB GPU supports max ~16-32 batch size
PATIENCE = 15
PROJECT_path = 'runs/detect' 
NAME = 'fish_model_S'    # Renamed output folder

def main():
    # เช็คก่อนว่าเห็น GPU ไหม
    print(f"🔥 GPU Available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"🔥 GPU Name: {torch.cuda.get_device_name(0)}")

    # รับ Path data จาก Argument
    if len(sys.argv) > 1:
        DATA_PATH = sys.argv[1]
    else:
        DATA_PATH = 'dataset/data.yaml'

    print(f"🚀 Starting MAX POWER training on Nontri AI...")
    print(f"📂 Data Path: {DATA_PATH}")

    model = YOLO(MODEL_NAME)

    results = model.train(
        data=DATA_PATH,
        epochs=EPOCHS,
        imgsz=IMG_SIZE,
        batch=BATCH_SIZE,
        device=0,
        project=PROJECT_path,
        name=NAME,
        patience=PATIENCE,
        
        # --- ปรับจูนความเสถียร (Stability Tuning) ---
        workers=4,         # ลดเหลือ 4 (เพราะเราขอ CPU แค่ 8 Core)
        cache=False,       # ปิด Cache RAM ป้องกันค้างตอนเริ่ม (อ่านจาก Disk แทน)
        exist_ok=True,
        verbose=True,
        save_period=1      # เซฟทุกรอบ กันหลุด
    )

    print("\n✅ Training Complete!")

if __name__ == '__main__':
    main()