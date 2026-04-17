# import logging
# import sys
# import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

# เราจะใช้ config ที่เราเพิ่งสร้าง
from app.core.config import settings

def setup_security(app: FastAPI):
    """
    ตั้งค่าความปลอดภัย Security Middlewares
    """
    # 1. Trusted Host Middleware
    # ป้องกัน Host Header Attack 
    # อนุญาตเฉพาะ Domain ของเรา และ localhost (สำหรับ Tunnel)
    app.add_middleware(
        TrustedHostMiddleware, 
        allowed_hosts=[
            "submarines.app", 
            "api.submarines.app", 
            "localhost", 
            "127.0.0.1",
            "*.submarines.app" # อนุญาต Subdomain ทั้งหมด
        ]
    )

    # 2. CORS Middleware
    # อนุญาตเฉพาะ Frontend ที่เรารู้จัก
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app
