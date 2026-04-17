from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db
from ..core.config import settings
import base64
import os
import uuid

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

    image_path = None
    if detection.image_base64:
        try:
            # Assuming base64 string might have 'data:image/jpeg;base64,' prefix or just be raw base64
            img_data = detection.image_base64
            if "," in img_data:
                img_data = img_data.split(",")[1]
            
            # Generate unique filename
            filename = f"detection_{uuid.uuid4().hex}.jpg"
            filepath = os.path.join(settings.IMAGE_STORAGE_PATH, filename)
            
            with open(filepath, "wb") as fh:
                fh.write(base64.b64decode(img_data))
                
            # Store the relative path to be served by StaticFiles
            image_path = f"/{settings.IMAGE_STORAGE_PATH}/{filename}"
        except Exception as e:
            print(f"Failed to process image: {e}")

    # Prepare data for database
    db_detection = models.FishDetection(
        session_id=detection.session_id,
        fish_count=detection.fish_count,
        track_id=detection.track_id,
        confidence=detection.confidence,
        fish_type=detection.fish_type,
        detection_metadata=detection.detection_metadata, # SQLAlchemy JSONB handles list/dict automatically
        raw_image_path=image_path
    )
    
    db.add(db_detection)
    db.commit()
    db.refresh(db_detection)
    return db_detection
