from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import models, schemas, crud
from ..database import get_db

router = APIRouter(
    prefix="/sessions",
    tags=["Mission Control"]
)

@router.post("/", response_model=schemas.SessionResponse)
def start_new_session(session_data: schemas.SessionCreate, db: Session = Depends(get_db)):
    """
    Start a new monitoring session.
    """
    return crud.create_session(db=db, session_data=session_data)
