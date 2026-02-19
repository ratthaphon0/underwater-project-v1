from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import desc
import os
import contextlib

# [NEW] Import Core Modules
from app.core.config import settings
from app.core.security import setup_security
from app.core.logging import setup_logging

# Import โมดูลภายในที่เราสร้างไว้
from app import database, models, schemas, crud
# Import routes.py ที่คุณทำไว้
from app import routes 

# --- 0. Setup Logging ---
setup_logging()

# ==========================================
# 1. การตั้งค่า App และความปลอดภัย
# ==========================================
@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: สามารถเพิ่ม logic connect DB/Redis ตรงนี้ได้
    yield
    # Shutdown

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API สำหรับเรือดำน้ำอัตโนมัติ ตรวจจับปลานิลและวัดคุณภาพน้ำ",
    version=settings.VERSION,
    lifespan=lifespan
)

# [NEW] Setup Security (Failed CORS & Trusted Host)
app = setup_security(app)

# ==========================================
# 2. การจัดการไฟล์รูปภาพ (Static Files)
# ==========================================
# สร้างโฟลเดอร์เก็บรูป AI ถ้ายังไม่มี
os.makedirs(settings.IMAGE_STORAGE_PATH, exist_ok=True)

# Mount โฟลเดอร์เพื่อให้เข้าถึงรูปภาพผ่าน URL ได้
app.mount("/static", StaticFiles(directory="static"), name="static")

# ==========================================
# 3. เชื่อมต่อ Router (routes.py)
# ==========================================
app.include_router(routes.router, prefix=settings.API_V1_STR, tags=["System & Telemetry"])

# ==========================================
# 4. API หลักสำหรับ Session และ Dashboard
# (ส่วนนี้ routes.py ยังไม่มี ผมเติมให้ตรงนี้เลย)
# ==========================================

# Dependency สำหรับเชื่อมต่อ DB
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- [POST] เริ่มภารกิจใหม่ (Start Session) ---
@app.post(f"{settings.API_V1_STR}/sessions", response_model=schemas.SessionResponse, tags=["Mission Control"])
def start_new_session(session_data: schemas.SessionCreate, db: Session = Depends(get_db)):
    """
    กดปุ่ม Start ที่ Frontend -> ยิงมาที่นี่เพื่อสร้าง Session ID
    """
    return crud.create_session(db=db, session_data=session_data)

# --- [GET] ข้อมูล Dashboard รวม (Real-time) ---
@app.get(f"{settings.API_V1_STR}/dashboard/{{session_id}}", tags=["Dashboard"])
def get_dashboard_summary(session_id: str, db: Session = Depends(get_db)):
    """
    ดึงค่าทุกอย่างมาโชว์หน้าจอ: ค่าเซนเซอร์ล่าสุด + จำนวนปลาล่าสุด
    """
    # 1. ดึงค่าเซนเซอร์ล่าสุดจาก routes/telemetry
    telemetry = db.query(models.WaterTelemetry)\
        .filter(models.WaterTelemetry.session_id == session_id)\
        .order_by(desc(models.WaterTelemetry.timestamp)).first()
    
    # 2. ดึงค่า AI ล่าสุด
    detection = db.query(models.FishDetection)\
        .filter(models.FishDetection.session_id == session_id)\
        .order_by(desc(models.FishDetection.timestamp)).first()
        
    # [Use Public Storage URL for Image]
    image_url = None
    if detection and detection.raw_image_path:
        # สมมติ path ใน db คือ "static/detections/abc.jpg"
        # เราตัด static/ ออก หรือต่อ URL ให้ถูกต้อง
        # ถ้าใน DB เก็บแค่ filename ก็ใช้ง่ายเลย
        if detection.raw_image_path.startswith("http"):
             image_url = detection.raw_image_path
        else:
             # กรณีเก็บ relative path
             image_url = f"{settings.STORAGE_PUBLIC_URL}/{detection.raw_image_path}"

    return {
        "session_id": session_id,
        "system_status": "ONLINE",
        "telemetry": {
            "depth": telemetry.depth if telemetry else 0.0,
            "temp": telemetry.temp if telemetry else 0.0,
            "ph": telemetry.ph if telemetry else 0.0,
            "do": telemetry.do_level if telemetry else 0.0,
            "turbidity": telemetry.turbidity if telemetry else 0.0,
        },
        "ai_vision": {
            "fish_count": detection.fish_count if detection else 0,
            "last_seen": detection.timestamp if detection else None,
            "image_url": image_url
        }
    }

# ==========================================
# 5. Root Endpoint
# ==========================================
@app.get("/")
def read_root():
    return {
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "docs_url": "/docs"
    }

# ⚠️ หมายเหตุ: เราลบคำสั่ง create_all ออกแล้วตามที่คุณขอ
# เพราะคุณมีตารางใน Database อยู่แล้ว