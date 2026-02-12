from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from database import get_db
from models import Sensor, UnderwaterData
from schemas import SensorCreate, SensorResponse, ReadingCreate, ReadingResponse
from typing import List

router = APIRouter()

# ===============================
# HEALTH CHECK
# ===============================
@router.get("/health")
def health_check():
    return {"status": "OK"}

# ===============================
# SENSOR ROUTES
# ===============================
@router.post("/sensors", response_model=SensorResponse)
def create_sensor(sensor: SensorCreate, db: Session = Depends(get_db)):
    db_sensor = Sensor(**sensor.dict())

    try:
        db.add(db_sensor)
        db.commit()
        db.refresh(db_sensor)
        return db_sensor
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error")


@router.get("/sensors", response_model=List[SensorResponse])
def get_sensors(db: Session = Depends(get_db)):
    return db.query(Sensor).all()


# ===============================
# READING ROUTES
# ===============================
@router.post("/readings", response_model=ReadingResponse)
def create_reading(reading: ReadingCreate, db: Session = Depends(get_db)):

    # เช็คก่อนว่า sensor มีจริงไหม
    sensor = db.query(Sensor).filter(Sensor.sensor_id == reading.sensor_id).first()
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")

    db_reading = UnderwaterData(**reading.dict())

    try:
        db.add(db_reading)
        db.commit()
        db.refresh(db_reading)
        return db_reading
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error")


@router.get("/readings", response_model=List[ReadingResponse])
def get_readings(limit: int = 100, db: Session = Depends(get_db)):
    return (
        db.query(UnderwaterData)
        .order_by(UnderwaterData.timestamp.desc())
        .limit(limit)
        .all()
    )


@router.get("/readings/{sensor_id}", response_model=List[ReadingResponse])
def get_readings_by_sensor(sensor_id: str, db: Session = Depends(get_db)):
    return (
        db.query(UnderwaterData)
        .filter(UnderwaterData.sensor_id == sensor_id)
        .order_by(UnderwaterData.timestamp.desc())
        .all()
    )
