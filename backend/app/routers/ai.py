from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db
import json

router = APIRouter(
    prefix="/ai",
    tags=["AI & Vision"]
)

@router.post("/detect", response_model=schemas.FishDetectionResponse)
def create_detection(detection: schemas.FishDetectionCreate, db: Session = Depends(get_db)):
    """
    Receive detection data from AI Service.
    Includes track_id to prevent double counting.
    """
    # Check if Session ID exists
    session = db.query(models.MonitoringSession).filter(models.MonitoringSession.id == detection.session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Prepare data for database
    db_detection = models.FishDetection(
        session_id=detection.session_id,
        fish_count=detection.fish_count,
        track_id=detection.track_id,
        confidence=detection.confidence,
        fish_type=detection.fish_type,
        detection_metadata=detection.detection_metadata, # SQLAlchemy JSONB handles list/dict automatically
        # image_path handling can be added here if we save base64 to file
    )
    
    db.add(db_detection)
    db.commit()
    db.refresh(db_detection)
    return db_detection
