from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, BigInteger
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from .database import Base

# 1. ตารางรอบการเดินเรือ (Monitoring Sessions)
class MonitoringSession(Base):
    __tablename__ = "monitoring_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    start_time = Column(DateTime(timezone=True), server_default=func.now())
    end_time = Column(DateTime(timezone=True), nullable=True)
    location_name = Column(String) # เช่น 'บ่อที่ 1'
    notes = Column(Text)           # เช่น 'ฝนตก น้ำขุ่น'

    # ความสัมพันธ์
    telemetry_logs = relationship("WaterTelemetry", back_populates="session")
    detections = relationship("FishDetection", back_populates="session")

# 2. ตารางข้อมูลเซนเซอร์ (Water Telemetry)
class WaterTelemetry(Base):
    __tablename__ = "water_telemetry"

    id = Column(BigInteger, primary_key=True, index=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey("monitoring_sessions.id"))
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Location
    lat = Column(Float, nullable=True)
    lng = Column(Float, nullable=True)
    depth = Column(Float)

    # Water Quality
    temp = Column(Float)
    ph = Column(Float)
    do_level = Column(Float)
    turbidity = Column(Float) # ความขุ่น

    session = relationship("MonitoringSession", back_populates="telemetry_logs")

# 3. ตารางผลจาก AI (Fish Detections)
class FishDetection(Base):
    __tablename__ = "fish_detections"

    id = Column(BigInteger, primary_key=True, index=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey("monitoring_sessions.id"))
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    raw_image_path = Column(String)
    enhanced_image_path = Column(String, nullable=True)
    fish_count = Column(Integer)
    
    # New fields for Tracking & Classification
    track_id = Column(String, nullable=True, index=True) # Unique ID from AI Tracker
    confidence = Column(Float, nullable=True)
    fish_type = Column(String, default="unknown")

    # เก็บ Bounding Box (x, y, w, h, conf) เป็น JSON
    detection_metadata = Column(JSONB)  
    health_status = Column(String, default="unknown")

    session = relationship("MonitoringSession", back_populates="detections")

# 4. ตารางพยากรณ์ (Water Predictions) - สำหรับ Data Science
class WaterPrediction(Base):
    __tablename__ = "water_predictions"
    id = Column(BigInteger, primary_key=True, index=True)
    base_timestamp = Column(DateTime(timezone=True))
    predict_for_timestamp = Column(DateTime(timezone=True))
    parameter_name = Column(String) # 'DO', 'pH'
    predicted_value = Column(Float)
    confidence_interval = Column(Float)
    model_version = Column(String)

# 5. ตารางเกณฑ์มาตรฐาน (Lifecycle Standards)
class LifecycleStandard(Base):
    __tablename__ = "tilapia_lifecycle_standards"
    id = Column(Integer, primary_key=True, index=True)
    stage_name = Column(String) # 'ลูกปลา', 'ตัวเต็มวัย'
    min_temp = Column(Float)
    max_temp = Column(Float)
    min_do = Column(Float)
    ph_range_min = Column(Float)
    ph_range_max = Column(Float)
    alert_threshold = Column(JSONB)