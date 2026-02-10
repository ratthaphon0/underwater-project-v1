from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
import torch

from database import get_db
from models import Sensor, UnderwaterData
from schemas import SensorCreate, SensorResponse, ReadingCreate, ReadingResponse

router = APIRouter()

# ========== HEALTH CHECK ==========
@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {
            "status": "✓ OK",
            "database": "Connected",
            "gpu": "Available" if torch.cuda.is_available() else "Not Available"
        }
    except Exception as e:
        return {
            "status": "✗ Error",
            "error": str(e)
        }

# ========== SENSOR ROUTES ==========
@router.post("/sensors", response_model=dict)
def create_sensor(sensor: SensorCreate, db: Session = Depends(get_db)):
    db_sensor = Sensor(**sensor.dict())
    db.add(db_sensor)
    db.commit()
    db.refresh(db_sensor)
    return {"id": db_sensor.id, "message": "✓ Sensor created"}

@router.get("/sensors", response_model=list[SensorResponse])
def get_sensors(db: Session = Depends(get_db)):
    return db.query(Sensor).all()

# ========== READING ROUTES ==========
@router.post("/readings", response_model=ReadingResponse)
def create_reading(reading: ReadingCreate, db: Session = Depends(get_db)):
    db_reading = UnderwaterData(**reading.dict())
    db.add(db_reading)
    db.commit()
    db.refresh(db_reading)
    return db_reading

@router.get("/readings", response_model=list[ReadingResponse])
def get_readings(db: Session = Depends(get_db), limit: int = 100):
    return db.query(UnderwaterData).order_by(
        UnderwaterData.timestamp.desc()
    ).limit(limit).all()

@router.get("/readings/{sensor_id}", response_model=list[ReadingResponse])
def get_readings_by_sensor(sensor_id: str, db: Session = Depends(get_db)):
    return db.query(UnderwaterData).filter(
        UnderwaterData.sensor_id == sensor_id
    ).order_by(UnderwaterData.timestamp.desc()).all()
