from pydantic import BaseModel
from datetime import datetime

# ========== REQUEST/RESPONSE MODELS ==========
class SensorCreate(BaseModel):
    sensor_id: str
    location: str
    sensor_type: str

class SensorResponse(BaseModel):
    id: int
    sensor_id: str
    location: str
    sensor_type: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class ReadingCreate(BaseModel):
    sensor_id: str
    temperature: float
    pressure: float
    salinity: float = None
    depth: float = None

class ReadingResponse(BaseModel):
    id: int
    sensor_id: str
    temperature: float
    pressure: float
    salinity: float = None
    depth: float = None
    timestamp: datetime
    
    class Config:
        from_attributes = True
