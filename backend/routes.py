from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from backend.database import get_db
from backend.models import MonitoringSession, WaterTelemetry, FishDetection
from backend.schemas import (
    MonitoringSessionCreate, MonitoringSessionResponse,
    WaterTelemetryCreate, WaterTelemetryResponse,
    FishDetectionCreate, FishDetectionResponse
)
from typing import List
from uuid import UUID

router = APIRouter()

# ===============================
# HEALTH CHECK
# ===============================
@router.get("/health")
def health_check():
    return {"status": "OK"}

# ===============================
# SESSION ROUTES
# ===============================
@router.post("/sessions", response_model=MonitoringSessionResponse)
def create_session(session: MonitoringSessionCreate, db: Session = Depends(get_db)):
    db_session = MonitoringSession(**session.model_dump())
    try:
        db.add(db_session)
        db.commit()
        db.refresh(db_session)
        return db_session
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/sessions", response_model=List[MonitoringSessionResponse])
def get_sessions(db: Session = Depends(get_db)):
    return db.query(MonitoringSession).all()

# ===============================
# TELEMETRY ROUTES
# ===============================
@router.post("/telemetry", response_model=WaterTelemetryResponse)
def create_telemetry(data: WaterTelemetryCreate, db: Session = Depends(get_db)):
    # Check if session exists
    session = db.query(MonitoringSession).filter(MonitoringSession.id == data.session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    db_telemetry = WaterTelemetry(**data.model_dump())
    try:
        db.add(db_telemetry)
        db.commit()
        db.refresh(db_telemetry)
        return db_telemetry
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/telemetry/{session_id}", response_model=List[WaterTelemetryResponse])
def get_telemetry_by_session(session_id: UUID, db: Session = Depends(get_db)):
    return db.query(WaterTelemetry).filter(WaterTelemetry.session_id == session_id).all()

# ===============================
# FISH DETECTION ROUTES
# ===============================
@router.post("/detections", response_model=FishDetectionResponse)
def create_detection(detection: FishDetectionCreate, db: Session = Depends(get_db)):
    db_detection = FishDetection(**detection.model_dump())
    try:
        db.add(db_detection)
        db.commit()
        db.refresh(db_detection)
        return db_detection
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
