from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Optional, Any
from uuid import UUID

# ========== MONITORING SESSION ==========
class MonitoringSessionBase(BaseModel):
    start_time: datetime
    location_name: str
    weather_type: Optional[str] = None
    activity_type: Optional[str] = None
    notes: Optional[str] = None

class MonitoringSessionCreate(MonitoringSessionBase):
    pass

class MonitoringSessionResponse(MonitoringSessionBase):
    id: UUID
    end_time: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

# ========== WATER TELEMETRY ==========
class WaterTelemetryBase(BaseModel):
    session_id: UUID
    timestamp: datetime
    lat: Optional[float] = None
    lng: Optional[float] = None
    depth: Optional[float] = None
    temperature: Optional[float] = None
    ph: Optional[float] = None
    dissolved_oxygen: Optional[float] = None
    ec_tds: Optional[float] = None
    turbidity: Optional[float] = None

class WaterTelemetryCreate(WaterTelemetryBase):
    pass

class WaterTelemetryResponse(WaterTelemetryBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# ========== FISH DETECTION ==========
class FishDetectionBase(BaseModel):
    session_id: UUID
    timestamp: datetime
    raw_image_path: Optional[str] = None
    enhanced_image_path: Optional[str] = None
    fish_count: int = 0
    detection_metadata: Optional[Any] = None
    health_status: Optional[str] = None

class FishDetectionCreate(FishDetectionBase):
    pass

class FishDetectionResponse(FishDetectionBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
