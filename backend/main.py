from fastapi import FastAPI
import torch

from backend.database import engine, Base
from backend.routes import router


# ========== CREATE TABLES ==========
Base.metadata.create_all(bind=engine)

# ========== FASTAPI APP ==========
app = FastAPI(title="Underwater AI Backend", version="1.0.0")

# Include routes
app.include_router(router)

# ========== ROOT ENDPOINT ==========
@app.get("/")
def read_root():
    gpu_status = torch.cuda.is_available()
    return {
        "message": "Underwater AI Backend is Running!",
        "gpu_available": gpu_status,
        "gpu_name": torch.cuda.get_device_name(0) if gpu_status else "CPU",
        "database": "Connected ✓"
    }

# ========== STARTUP/SHUTDOWN ==========
@app.on_event("startup")
async def startup():
    print("✓ Database connected and tables created")

@app.on_event("shutdown")
async def shutdown():
    engine.dispose()
    print("✓ Database connection closed")