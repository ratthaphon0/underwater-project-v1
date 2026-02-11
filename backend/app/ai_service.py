#ตัวเชื่อมต่อระหว่าง YOLO กับ Database (แปลงจาก test_video.py มาเป็น Service)
from ultralytics import YOLO
import cv2
from datetime import datetime
import os
from sqlalchemy.orm import Session
from . import crud
import uuid

# โหลดโมเดล (แก้ Path ให้ตรงกับ Docker หรือ Local)
MODEL_PATH = "models/best.pt" # หรือ path ที่ mount เข้ามา
OUTPUT_DIR = "static/detections" # โฟลเดอร์เก็บรูป

# ตรวจสอบว่ามีโฟลเดอร์ไหม
os.makedirs(OUTPUT_DIR, exist_ok=True)

class AIProcessor:
    def __init__(self):
        # โหลดโมเดลครั้งเดียวตอนเริ่ม App
        try:
            self.model = YOLO(MODEL_PATH)
        except Exception as e:
            print(f"Warning: Could not load model at {MODEL_PATH}. {e}")
            self.model = None

    def process_frame_and_save(self, db: Session, session_id: uuid.UUID, frame, conf_threshold=0.25):
        if not self.model:
            return {"status": "model_not_loaded"}

        # 1. ให้ YOLO ทำนาย
        results = self.model.predict(frame, conf=conf_threshold, verbose=False)
        result = results[0]
        
        fish_count = len(result.boxes)
        
        # 2. ถ้าเจอเป้าหมาย ให้บันทึก
        if fish_count > 0:
            # วาดกรอบลงภาพ (Optional: ถ้าอยากเก็บภาพ Raw ก็ไม่ต้อง plot)
            plot_img = result.plot()
            
            # สร้างชื่อไฟล์
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            filename = f"detect_{timestamp}.jpg"
            filepath = os.path.join(OUTPUT_DIR, filename)
            
            # บันทึกรูป
            cv2.imwrite(filepath, plot_img)
            
            # เตรียม Metadata (JSON)
            metadata = []
            for box in result.boxes:
                metadata.append({
                    "class": int(box.cls),
                    "conf": float(box.conf),
                    "bbox": box.xywh.tolist()[0] # [x, y, w, h]
                })

            # 3. เรียก CRUD เพื่อบันทึกลง Database
            crud.create_detection(
                db=db,
                session_id=session_id,
                fish_count=fish_count,
                image_path=f"/static/detections/{filename}", # Path สำหรับ Frontend
                metadata=metadata
            )
            
            return {"saved": True, "count": fish_count}
        
        return {"saved": False, "count": 0}