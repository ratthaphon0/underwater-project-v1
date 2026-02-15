#ฟังก์ชันสำหรับบันทึกและดึงข้อมูล (Logic ของ Database)
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app import models, schemas
import uuid

# 1. สร้าง Session ใหม่
def create_session(db: Session, session_data: schemas.SessionCreate):
    db_session = models.MonitoringSession(
        location_name=session_data.location_name,
        notes=session_data.notes
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

# 2. บันทึกค่า Sensor (Telemetry)
def create_telemetry(db: Session, telemetry: schemas.TelemetryCreate):
    db_item = models.WaterTelemetry(**telemetry.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

# 3. บันทึกผล AI (Detection) - ฟังก์ชันนี้ AI Service จะเรียกใช้
def create_detection(db: Session, session_id: uuid.UUID, fish_count: int, image_path: str, metadata: list):
    db_detection = models.FishDetection(
        session_id=session_id,
        fish_count=fish_count,
        raw_image_path=image_path,
        detection_metadata=metadata, # รองรับ JSONB
        health_status="analyzing"
    )
    db.add(db_detection)
    db.commit()
    db.refresh(db_detection)
    return db_detection

# 4. ดึงข้อมูลล่าสุดสำหรับ Dashboard
def get_latest_dashboard_data(db: Session, session_id: uuid.UUID):
    telemetry = db.query(models.WaterTelemetry)\
        .filter(models.WaterTelemetry.session_id == session_id)\
        .order_by(desc(models.WaterTelemetry.timestamp)).first()
    
    latest_detection = db.query(models.FishDetection)\
        .filter(models.FishDetection.session_id == session_id)\
        .order_by(desc(models.FishDetection.timestamp)).first()

    return {
        "telemetry": telemetry,
        "latest_detection": latest_detection
    }