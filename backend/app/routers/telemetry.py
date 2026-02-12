from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db

router = APIRouter(
    prefix="/telemetry",
    tags=["Telemetry"]
)

@router.post("/", response_model=schemas.TelemetryResponse)
def create_telemetry_reading(reading: schemas.TelemetryCreate, db: Session = Depends(get_db)):
    # Check if Session ID exists
    session = db.query(models.MonitoringSession).filter(models.MonitoringSession.id == reading.session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Save to database
    db_telemetry = models.WaterTelemetry(**reading.dict())
    db.add(db_telemetry)
    db.commit()
    db.refresh(db_telemetry)
    return db_telemetry

@router.get("/{session_id}")
def get_telemetry_by_session(session_id: str, db: Session = Depends(get_db), limit: int = 100):
    readings = db.query(models.WaterTelemetry)\
        .filter(models.WaterTelemetry.session_id == session_id)\
        .order_by(models.WaterTelemetry.timestamp.desc())\
        .limit(limit)\
        .all()
    return readings
