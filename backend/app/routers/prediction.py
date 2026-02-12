from fastapi import APIRouter, Depends
from ..services.model_engine import model_engine
from .. import schemas

router = APIRouter(
    prefix="/predict",
    tags=["Prediction & Analytics"]
)

@router.post("/water-quality")
def predict_water_quality(data: dict):
    """
    Endpoint for Data Science model predictions.
    Calls the ModelEngine service.
    """
    return model_engine.predict_water_quality(data)
