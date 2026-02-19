from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from .. import models, schemas
from ..database import get_db

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)

@router.get("/{session_id}")
def get_dashboard_summary(session_id: str, db: Session = Depends(get_db)):
    """
    Get aggregated dashboard data.
    Calculates total unique fish count based on track_id.
    """
    # 1. Get latest Telemetry
    telemetry = db.query(models.WaterTelemetry)\
        .filter(models.WaterTelemetry.session_id == session_id)\
        .order_by(desc(models.WaterTelemetry.timestamp)).first()
    
    # 2. Get latest Detection for display
    latest_detection = db.query(models.FishDetection)\
        .filter(models.FishDetection.session_id == session_id)\
        .order_by(desc(models.FishDetection.timestamp)).first()
        
    # 3. Calculate Unique Fish Count using track_id
    # Count unique track_ids that are not null
    unique_fish_count = db.query(func.count(func.distinct(models.FishDetection.track_id)))\
        .filter(models.FishDetection.session_id == session_id)\
        .filter(models.FishDetection.track_id != None)\
        .scalar()
        
    # If no track_ids are used, might fall back to sum of counts (optional, but sticking to track_id for now)
    if unique_fish_count == 0:
        # Fallback: just use the latest count if available, or 0? 
        # User wants "Unique Count", so if no track_id, maybe 0 is correct or we take max of fish_count seen?
        # Let's stick to unique track_id as requested.
        pass

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
            "fish_count": unique_fish_count, # Use the unique count
            "latest_detection_type": latest_detection.fish_type if latest_detection else "unknown",
            "last_seen": latest_detection.timestamp if latest_detection else None,
            "image_url": latest_detection.raw_image_path if latest_detection else None
        }
    }
