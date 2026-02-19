from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os
import contextlib

# [NEW] Import Core Modules
from app.core.config import settings
from app.core.security import setup_security
from app.core.logging import setup_logging

# [NEW] Import Modular Routers (New Structure from Dev Branch)
from app.routers import system, telemetry, ai, dashboard, session, prediction

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

# [NEW] Setup Security (CORS & Trusted Host)
app = setup_security(app)

# ==========================================
# 2. การจัดการไฟล์รูปภาพ (Static Files)
# ==========================================
# สร้างโฟลเดอร์เก็บรูป AI ถ้ายังไม่มี
os.makedirs(settings.IMAGE_STORAGE_PATH, exist_ok=True)

# Mount โฟลเดอร์เพื่อให้เข้าถึงรูปภาพผ่าน URL ได้
app.mount("/static", StaticFiles(directory="static"), name="static")

# ==========================================
# 3. Router Registration (Modular Logic)
# ==========================================
# System & Health
app.include_router(system.router, prefix=settings.API_V1_STR)

# Core Features
app.include_router(session.router, prefix=settings.API_V1_STR)    # /api/v1/sessions
app.include_router(telemetry.router, prefix=settings.API_V1_STR)  # /api/v1/telemetry
app.include_router(ai.router, prefix=settings.API_V1_STR)         # /api/v1/ai
app.include_router(dashboard.router, prefix=settings.API_V1_STR)  # /api/v1/dashboard
app.include_router(prediction.router, prefix=settings.API_V1_STR) # /api/v1/predict

# ==========================================
# 4. Root Endpoint
# ==========================================
@app.get("/")
def read_root():
    return {
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "docs_url": "/docs"
    }
