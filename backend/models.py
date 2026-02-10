# from sqlalchemy import Column, Integer, String, Float, DateTime
# from datetime import datetime
# from database import Base

# # ========== ORM MODELS ==========
# class Sensor(Base):
#     __tablename__ = "sensors"
    
#     id = Column(Integer, primary_key=True)
#     sensor_id = Column(String(50), unique=True, nullable=False)
#     location = Column(String(100), nullable=False)
#     sensor_type = Column(String(50), nullable=False)
#     created_at = Column(DateTime, default=datetime.utcnow)

# class UnderwaterData(Base):
#     __tablename__ = "underwater_data"
    
#     id = Column(Integer, primary_key=True)
#     sensor_id = Column(String(50), nullable=False)
#     temperature = Column(Float, nullable=False)
#     pressure = Column(Float, nullable=False)
#     salinity = Column(Float, nullable=True)
#     depth = Column(Float, nullable=True)
#     timestamp = Column(DateTime, default=datetime.utcnow)
