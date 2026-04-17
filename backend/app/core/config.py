from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Union, Any
from pydantic import AnyHttpUrl, field_validator, ValidationInfo

class Settings(BaseSettings):
    # --- Project Info ---
    PROJECT_NAME: str = "Project Submarine API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # --- Environment ---
    ENVIRONMENT: str = "production"  # development, production
    
    # --- Security ---
    # 1. Fix: Added a default to prevent Mypy "missing named argument" error
    SECRET_KEY: str = "temporary_secret_key_for_linting_change_me"
    
    # 2. Fix: Use List[str] instead of List[AnyHttpUrl]. 
    # FastAPI's CORSMiddleware expects plain strings; this solves the Mypy 
    # "AnyHttpUrl vs Sequence[str]" error in security.py.
    CORS_ORIGINS: List[str] = [
        "https://submarines.app", 
        "https://www.submarines.app",
        "https://storage.submarines.app",
        "https://db.submarines.app",
        "http://localhost:5173",
        "http://localhost:8000",
    ]
    
    # 3. Fix: Updated to Pydantic v2 @field_validator
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Any) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        return v

    # --- Database ---
    DATABASE_URL: Union[str, None] = None
    
    POSTGRES_SERVER: Union[str, None] = None
    POSTGRES_USER: Union[str, None] = None
    POSTGRES_PASSWORD: Union[str, None] = None
    POSTGRES_DB: Union[str, None] = None
    POSTGRES_PORT: str = "5432"
    
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        if all([self.POSTGRES_SERVER, self.POSTGRES_USER, self.POSTGRES_PASSWORD, self.POSTGRES_DB]):
            return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        # Fallback for local development if nothing is set
        return "sqlite:///./test.db"

    # --- AI & Storage ---
    MODEL_PATH: str = "models/best.pt"
    AI_CONF_THRESHOLD: float = 0.25
    IMAGE_STORAGE_PATH: str = "static/detections"
    STORAGE_PUBLIC_URL: str = "https://storage.submarines.app"

    # 4. Fix: Updated Config to Pydantic v2 style
    model_config = SettingsConfigDict(
        case_sensitive=True, 
        env_file=".env",
        extra="ignore" # Prevents crashing if extra env vars exist
    )

settings = Settings()