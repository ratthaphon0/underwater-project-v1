import os
import contextlib
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.security import setup_security
from app.core.logging import setup_logging

# Import Routers
from app.routers import system, telemetry, ai, dashboard, session, prediction

# --- 0. Setup Logging ---
setup_logging()

# ==========================================
# 1. Lifespan (Startup/Shutdown)
# ==========================================
@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: สามารถเพิ่ม logic connect DB/Redis ตรงนี้ได้
    yield
    # Shutdown

# ==========================================
# 2. App Initialization
# ==========================================
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API for Autonomous Underwater Drone & AI Analysis (v2.0 Refactored)",
    version=settings.VERSION,
    lifespan=lifespan
)

# ==========================================
# 3. Security (CORS & Trusted Host)
# ==========================================
app = setup_security(app)

# ==========================================
# 4. Static Files
# ==========================================
# สร้างโฟลเดอร์เก็บรูป AI ถ้ายังไม่มี
os.makedirs(settings.IMAGE_STORAGE_PATH, exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# ==========================================
# 5. Router Registration
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
# 6. Root Endpoint
# ==========================================
@app.get("/")
def read_root():
    return {
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "status": "Ready to dive! 🌊",
        "docs_url": "/docs"
    }
