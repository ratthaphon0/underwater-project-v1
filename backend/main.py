import os
from fastapi import FastAPI, Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
import torch

# ========== DATABASE SETUP ==========
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://user:password@db:5432/underwater_db"
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    echo=False
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

# ========== DEPENDENCY ==========
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ========== FASTAPI APP ==========
app = FastAPI()

@app.get("/")
def read_root(db: Session = Depends(get_db)):
    gpu_status = torch.cuda.is_available()
    return {
        "message": "Underwater AI Backend is Running!",
        "gpu_available": gpu_status,
        "gpu_name": torch.cuda.get_device_name(0) if gpu_status else "CPU",
        "database": "Connected ✓"
    }

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute("SELECT 1")
        return {
            "status": "✓ OK",
            "database": "Connected",
            "gpu": "Available" if torch.cuda.is_available() else "Not Available"
        }
    except Exception as e:
        return {
            "status": "✗ Error",
            "error": str(e)
        }

@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)
    print("✓ Database connected and tables created")

@app.on_event("shutdown")
async def shutdown():
    engine.dispose()
    print("✓ Database connection closed")