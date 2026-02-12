from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# ========== LOAD ENV ==========
# พยายามโหลดจากโฟลเดอร์ root
load_dotenv(os.path.join(os.path.dirname(__file__), "../../.env"))

# ========== DATABASE SETUP ==========
DB_USER = os.getenv("DB_USER", "admin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "supaporn2026")
DB_NAME = os.getenv("DB_NAME", "underwater_db")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5433") # ใช้ 5433 ตามที่ตั้งไว้ใน Local

SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

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