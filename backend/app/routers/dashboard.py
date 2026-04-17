from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import Optional, Any
from .. import models
from ..database import get_db

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)

@router.get("/{session_id}")
def get_dashboard_summary(session_id: str, db: Session = Depends(get_db)) -> dict[str, Any]:
    """
    Get aggregated dashboard data.
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
    # FIX: Use .is_not(None) for SQLAlchemy filters to satisfy Ruff/Mypy
    unique_fish_count = db.query(func.count(func.distinct(models.FishDetection.track_id)))\
        .filter(models.FishDetection.session_id == session_id)\
        .filter(models.FishDetection.track_id.is_not(None))\
        .scalar() or 0
        
    # --- Image URL Processing ---
    # FIX: Explicitly type image_url as Optional[str] to prevent Mypy 
    # from confusing it with a SQLAlchemy Column type.
    image_url: Optional[str] = None
    
    if latest_detection and latest_detection.raw_image_path:
        # Cast to str to ensure Mypy treats it as a value, not a Column object
        path: str = str(latest_detection.raw_image_path)
        
        if path.startswith("http"):
             image_url = path
        else:
             from ..core.config import settings
             clean_path = path.lstrip("/")
             image_url = f"{settings.STORAGE_PUBLIC_URL}/{clean_path}"

    return {
        "session_id": session_id,
        "system_status": "ONLINE",
        "telemetry": {
            # Safely handle potential None values from the query
            "depth": float(telemetry.depth) if telemetry else 0.0,
            "temp": float(telemetry.temp) if telemetry else 0.0,
            "ph": float(telemetry.ph) if telemetry else 0.0,
            "do": float(telemetry.do_level) if telemetry else 0.0,
            "turbidity": float(telemetry.turbidity) if telemetry else 0.0,
        },
        "ai_vision": {
            "fish_count": int(unique_fish_count), 
            "latest_detection_type": str(latest_detection.fish_type) if latest_detection else "unknown",
            "last_seen": latest_detection.timestamp if latest_detection else None,
            "image_url": image_url
        }
    }