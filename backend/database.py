import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base

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
