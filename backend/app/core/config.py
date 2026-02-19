from pydantic_settings import BaseSettings
from typing import List, Union
from pydantic import AnyHttpUrl, validator

class Settings(BaseSettings):
    # --- Project Info ---
    PROJECT_NAME: str = "Project Submarine API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # --- Environment ---
    ENVIRONMENT: str = "production"  # development, production
    
    # --- Security ---
    SECRET_KEY: str
    # ⚠️ Default to specific domains for security
    CORS_ORIGINS: List[AnyHttpUrl] = [
        "https://submarines.app", 
        "https://www.submarines.app",
        "https://storage.submarines.app",
        "https://db.submarines.app",
        "http://localhost:5173",  # For local dev
        "http://localhost:8000",  # For local swagger
    ]
    
    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # --- Database ---
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: str = "5432"
    
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # --- AI & Storage ---
    MODEL_PATH: str = "models/best.pt"
    AI_CONF_THRESHOLD: float = 0.25
    IMAGE_STORAGE_PATH: str = "static/detections"
    
    # URL ที่จะใช้ Generate Link รูปภาพกลับไปให้ Frontend
    # กรณี Cloud Tunnel ต้องใช้ Public URL (https://storage.submarines.app)
    # กรณี Localhost ก็ใช้ http://localhost:9000
    STORAGE_PUBLIC_URL: str = "https://storage.submarines.app"

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
