from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# อ่านค่าจาก Environment Variable (ถ้าไม่มีจะใช้ค่า Default สำหรับ Dev)
# รูปแบบ: postgresql://user:password@host:port/dbname
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:password@localhost:5432/submarine_db"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency สำหรับให้ API ยืม Session ไปใช้แล้วคืน
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()