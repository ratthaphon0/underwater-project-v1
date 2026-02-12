from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os

from . import database
from .routers import system, telemetry, ai, dashboard, session, prediction

# ==========================================
# 1. App Configuration & Security (CORS)
# ==========================================
app = FastAPI(
    title="Project Submarine AI Backend ⚓",
    description="API for Autonomous Underwater Drone & AI Analysis",
    version="2.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# 2. Static Files (Images)
# ==========================================
os.makedirs("static/detections", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# ==========================================
# 3. Router Registration
# ==========================================
# System & Health
app.include_router(system.router, prefix="/api/v1")

# Core Features
app.include_router(session.router, prefix="/api/v1")    # /api/v1/sessions
app.include_router(telemetry.router, prefix="/api/v1")  # /api/v1/telemetry
app.include_router(ai.router, prefix="/api/v1")         # /api/v1/ai
app.include_router(dashboard.router, prefix="/api/v1")  # /api/v1/dashboard
app.include_router(prediction.router, prefix="/api/v1") # /api/v1/predict

# ==========================================
# 4. Root Endpoint
# ==========================================
@app.get("/")
def read_root():
    return {
        "project": "Submarine AI",
        "status": "Ready to dive! 🌊",
        "version": "v2.0 (Refactored)",
        "docs_url": "/docs"
    }
