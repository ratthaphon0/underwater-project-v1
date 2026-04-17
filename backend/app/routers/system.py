from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
import torch
from ..database import get_db

router = APIRouter(
    prefix="/system",
    tags=["System"]
)

@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        # Check Database
        db.execute(text("SELECT 1"))
        
        # Check GPU for AI
        gpu_status = "Available" if torch.cuda.is_available() else "Not Available"
        gpu_name = torch.cuda.get_device_name(0) if torch.cuda.is_available() else "None"

        return {
            "status": "OK",
            "database": "Connected",
            "ai_engine": {
                "gpu": gpu_status,
                "device": gpu_name
            }
        }
    except Exception as e:
        return {
            "status": "Error",
            "error": str(e)
        }
