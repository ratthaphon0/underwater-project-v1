from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, BigInteger
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from database import Base

# ========== ORM MODELS ==========

class MonitoringSession(Base):
    __tablename__ = "monitoring_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=True)
    location_name = Column(String(255), nullable=False)
    weather_type = Column(String(50), nullable=True)
    activity_type = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    telemetry = relationship("WaterTelemetry", back_populates="session")
    detections = relationship("FishDetection", back_populates="session")
    predictions = relationship("WaterPrediction", back_populates="session")

class WaterTelemetry(Base):
    __tablename__ = "water_telemetry"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey("monitoring_sessions.id"), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Location Info
    lat = Column(Float, nullable=True)
    lng = Column(Float, nullable=True)
    depth = Column(Float, nullable=True)
    
    # Water Quality
    temp = Column(Float, nullable=True)
    ph = Column(Float, nullable=True)
    do_level = Column(Float, nullable=True)
    ec_value = Column(Float, nullable=True)
    turbidity = Column(Float, nullable=True)
    
    # Relationships
    session = relationship("MonitoringSession", back_populates="telemetry")

class FishDetection(Base):
    __tablename__ = "fish_detections"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey("monitoring_sessions.id"), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    
    raw_image_path = Column(String, nullable=True)
    enhanced_image_path = Column(String, nullable=True)
    fish_count = Column(Integer, default=0)
    detection_metadata = Column(JSONB, nullable=True)
    health_status = Column(String(100), nullable=True)
    
    # Relationships
    session = relationship("MonitoringSession", back_populates="detections")

class WaterPrediction(Base):
    __tablename__ = "water_predictions"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey("monitoring_sessions.id"), nullable=False, index=True)
    base_timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    predict_for_timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    
    parameter_name = Column(String(50), nullable=False)
    predicted_value = Column(Float, nullable=False)
    confidence_interval = Column(Float, nullable=True)
    model_version = Column(String(50), nullable=True)
    
    # Relationships
    session = relationship("MonitoringSession", back_populates="predictions")

class TilapiaLifecycleStandard(Base):
    __tablename__ = "tilapia_lifecycle_standards"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    stage_name = Column(String(100), nullable=False)
    
    min_temp = Column(Float, nullable=True)
    max_temp = Column(Float, nullable=True)
    min_do = Column(Float, nullable=True)
    ph_range_min = Column(Float, nullable=True)
    ph_range_max = Column(Float, nullable=True)
    ideal_turbidity_max = Column(Float, nullable=True)
    alert_threshold = Column(JSONB, nullable=True)
