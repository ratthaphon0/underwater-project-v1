from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import timedelta
from .. import models, schemas
from ..database import get_db
from ..services.model_engine import model_engine

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

    # 1. Save raw data to WaterTelemetry
    db_telemetry = models.WaterTelemetry(**reading.dict())
    db.add(db_telemetry)
    db.commit()
    db.refresh(db_telemetry)
    
    # 2. Real-time Prediction using Model Engine
    predictions = model_engine.predict_water_quality(reading.dict())
    
    # Assuming prediction is for 1 hour in the future
    predict_for_time = db_telemetry.timestamp + timedelta(hours=1)
    
    # 3. Save predictions to WaterPrediction table
    for param_name, pred_data in predictions.items():
        db_prediction = models.WaterPrediction(
            base_timestamp=db_telemetry.timestamp,
            predict_for_timestamp=predict_for_time,
            parameter_name=param_name,
            predicted_value=pred_data["predicted_value"],
            confidence_interval=pred_data["confidence_interval"],
            model_version=model_engine.model_version
        )
        db.add(db_prediction)
        
    db.commit()

    return db_telemetry

@router.get("/{session_id}")
def get_telemetry_by_session(session_id: str, db: Session = Depends(get_db), limit: int = 100):
    readings = db.query(models.WaterTelemetry)\
        .filter(models.WaterTelemetry.session_id == session_id)\
        .order_by(models.WaterTelemetry.timestamp.desc())\
        .limit(limit)\
        .all()
    return readings
