from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# ใช้ Connection String จาก Config ที่รวมรวบมาจาก Env Vars แล้ว
SQLALCHEMY_DATABASE_URL = settings.SQLALCHEMY_DATABASE_URI

# [NEW] Connection Pooling for Production
# - pool_size: จำนวน connection ที่เปิดค้างไว้รอ (default 5)
# - max_overflow: จำนวน connection ที่เปิดเพิ่มได้ถ้า pool เต็ม (default 10)
# - pool_pre_ping: เช็คว่า connection ยังมีชีวิตอยู่ไหมก่อนใช้ (กัน error "server closed the connection unexpectedly")
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency สำหรับให้ API ยืม Session ไปใช้แล้วคืน
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()