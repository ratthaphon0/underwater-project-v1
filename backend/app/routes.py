from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
import torch

# import ให้ตรงกับโครงสร้างใหม่
from app.database import get_db
from app import models, schemas 

router = APIRouter()

# ========== 🏥 HEALTH CHECK (เก็บส่วนนี้ไว้ ดีมาก!) ==========
@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        # เช็ค Database
        db.execute(text("SELECT 1"))
        
        # เช็ค GPU สำหรับ AI
        gpu_status = "Available" if torch.cuda.is_available() else "Not Available"
        gpu_name = torch.cuda.get_device_name(0) if torch.cuda.is_available() else "None"

        return {
            "status": "✓ OK",
            "database": "Connected",
            "ai_engine": {
                "gpu": gpu_status,
                "device": gpu_name
            }
        }
    except Exception as e:
        return {
            "status": "✗ Error",
            "error": str(e)
        }

# ========== 📡 TELEMETRY ROUTES (แก้ให้ตรงกับตารางใหม่) ==========

# รับค่าจาก Sensor (เดิมคือ /readings)
@router.post("/telemetry", response_model=schemas.TelemetryResponse)
def create_telemetry_reading(reading: schemas.TelemetryCreate, db: Session = Depends(get_db)):
    # เช็คว่า Session ID นี้มีจริงไหม
    session = db.query(models.MonitoringSession).filter(models.MonitoringSession.id == reading.session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # บันทึกลงตาราง water_telemetry
    db_telemetry = models.WaterTelemetry(**reading.dict())
    db.add(db_telemetry)
    db.commit()
    db.refresh(db_telemetry)
    return db_telemetry

# ดึงค่า Sensor ล่าสุดของ Session นั้นๆ
@router.get("/telemetry/{session_id}")
def get_telemetry_by_session(session_id: str, db: Session = Depends(get_db), limit: int = 100):
    readings = db.query(models.WaterTelemetry)\
        .filter(models.WaterTelemetry.session_id == session_id)\
        .order_by(models.WaterTelemetry.timestamp.desc())\
        .limit(limit)\
        .all()
    return readings