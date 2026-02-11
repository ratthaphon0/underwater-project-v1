from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import desc
import os

# Import โมดูลภายในที่เราสร้างไว้
from . import database, models, schemas, crud
# Import routes.py ที่คุณทำไว้
from . import routes 

# ==========================================
# 1. การตั้งค่า App และความปลอดภัย (CORS)
# ==========================================
app = FastAPI(
    title="Project Submarine AI Backend ⚓",
    description="API สำหรับเรือดำน้ำอัตโนมัติ ตรวจจับปลานิลและวัดคุณภาพน้ำ",
    version="1.0.0"
)

# ตั้งค่า CORS ให้ Frontend (React/Vue) เข้าถึงได้
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ใน Production ควรเปลี่ยนเป็น domain ของ frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# 2. การจัดการไฟล์รูปภาพ (Static Files)
# ==========================================
# สร้างโฟลเดอร์เก็บรูป AI ถ้ายังไม่มี
os.makedirs("static/detections", exist_ok=True)

# Mount โฟลเดอร์เพื่อให้เข้าถึงรูปภาพผ่าน URL ได้ (เช่น http://host/static/detections/img.jpg)
app.mount("/static", StaticFiles(directory="static"), name="static")

# ==========================================
# 3. เชื่อมต่อ Router (routes.py)
# ==========================================
# ดึง API Health Check และ Telemetry มาจากไฟล์ routes.py ของคุณ
app.include_router(routes.router, prefix="/api/v1", tags=["System & Telemetry"])

# ==========================================
# 4. API หลักสำหรับ Session และ Dashboard
# (ส่วนนี้ routes.py ยังไม่มี ผมเติมให้ตรงนี้เลย)
# ==========================================

# Dependency สำหรับเชื่อมต่อ DB
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- [POST] เริ่มภารกิจใหม่ (Start Session) ---
@app.post("/api/v1/sessions", response_model=schemas.SessionResponse, tags=["Mission Control"])
def start_new_session(session_data: schemas.SessionCreate, db: Session = Depends(get_db)):
    """
    กดปุ่ม Start ที่ Frontend -> ยิงมาที่นี่เพื่อสร้าง Session ID
    """
    return crud.create_session(db=db, session_data=session_data)

# --- [GET] ข้อมูล Dashboard รวม (Real-time) ---
@app.get("/api/v1/dashboard/{session_id}", tags=["Dashboard"])
def get_dashboard_summary(session_id: str, db: Session = Depends(get_db)):
    """
    ดึงค่าทุกอย่างมาโชว์หน้าจอ: ค่าเซนเซอร์ล่าสุด + จำนวนปลาล่าสุด
    """
    # 1. ดึงค่าเซนเซอร์ล่าสุดจาก routes/telemetry
    telemetry = db.query(models.WaterTelemetry)\
        .filter(models.WaterTelemetry.session_id == session_id)\
        .order_by(desc(models.WaterTelemetry.timestamp)).first()
    
    # 2. ดึงค่า AI ล่าสุด
    detection = db.query(models.FishDetection)\
        .filter(models.FishDetection.session_id == session_id)\
        .order_by(desc(models.FishDetection.timestamp)).first()
        
    return {
        "session_id": session_id,
        "system_status": "ONLINE",
        "telemetry": {
            "depth": telemetry.depth if telemetry else 0.0,
            "temp": telemetry.temp if telemetry else 0.0,
            "ph": telemetry.ph if telemetry else 0.0,
            "do": telemetry.do_level if telemetry else 0.0,
            "turbidity": telemetry.turbidity if telemetry else 0.0,
        },
        "ai_vision": {
            "fish_count": detection.fish_count if detection else 0,
            "last_seen": detection.timestamp if detection else None,
            "image_url": detection.raw_image_path if detection else None
        }
    }

# ==========================================
# 5. Root Endpoint
# ==========================================
@app.get("/")
def read_root():
    return {
        "project": "Submarine AI",
        "status": "Ready to dive! 🌊",
        "docs_url": "/docs"
    }

# ⚠️ หมายเหตุ: เราลบคำสั่ง create_all ออกแล้วตามที่คุณขอ
# เพราะคุณมีตารางใน Database อยู่แล้ว