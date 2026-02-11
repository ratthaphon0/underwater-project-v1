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