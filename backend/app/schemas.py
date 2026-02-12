from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime
from uuid import UUID

# --- Schemas สำหรับ Telemetry (Sensor) ---
class TelemetryCreate(BaseModel):
    session_id: UUID
    lat: Optional[float] = None
    lng: Optional[float] = None
    depth: float
    temp: float
    ph: float
    do_level: float
    turbidity: float

class TelemetryResponse(TelemetryCreate):
    id: int
    timestamp: datetime
    class Config:
        from_attributes = True

# --- Schemas สำหรับ Session ---
class SessionCreate(BaseModel):
    location_name: str
    notes: Optional[str] = None

class SessionResponse(SessionCreate):
    id: UUID
    start_time: datetime
    end_time: Optional[datetime]
    class Config:
        from_attributes = True

# --- Schemas สำหรับ Dashboard ---
class DashboardResponse(BaseModel):
    session_id: UUID
    latest_telemetry: Optional[TelemetryResponse]
    total_fish_count: int
    latest_image: Optional[str]
    system_status: str

# --- Schemas สำหรับ Fish Detection (AI) ---
class FishDetectionCreate(BaseModel):
    session_id: UUID
    fish_count: int
    track_id: Optional[str] = None
    confidence: Optional[float] = None
    fish_type: Optional[str] = "unknown"
    detection_metadata: Optional[List[dict]] = None
    image_base64: Optional[str] = None # กรณีส่งรูปมาเป็น Base64 (ถ้ามี)

class FishDetectionResponse(BaseModel):
    id: int
    session_id: UUID
    track_id: Optional[str]
    fish_type: str
    timestamp: datetime
    
    class Config:
        from_attributes = True