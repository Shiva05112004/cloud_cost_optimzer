"""API routes for Phase A ML inference."""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional

from app.routes.auth import get_current_user
from app.ml.phase_a.inference import get_inference_service

router = APIRouter()


class SinglePredictionRequest(BaseModel):
    """Request body for single prediction."""
    features: dict = Field(..., description="Feature dict with cpu, memory, etc.")


class BatchPredictionRequest(BaseModel):
    """Request body for batch predictions."""
    features_list: List[dict] = Field(..., description="List of feature dicts")


class PredictionResponse(BaseModel):
    """Response with prediction results."""
    prediction: Optional[int] = None
    probability: Optional[float] = None
    confidence: Optional[float] = None
    model: Optional[str] = None
    status: str
    error: Optional[str] = None


class BatchPredictionResponse(BaseModel):
    """Response with batch prediction results."""
    predictions: Optional[List[int]] = None
    probabilities: Optional[List[float]] = None
    confidences: Optional[List[float]] = None
    model: Optional[str] = None
    count: Optional[int] = None
    status: str
    error: Optional[str] = None


class ModelInfoResponse(BaseModel):
    """Response with model metadata."""
    timestamp: Optional[str] = None
    best_model: Optional[str] = None
    rf_test_f1: Optional[float] = None
    xgb_test_f1: Optional[float] = None
    class_imbalance_ratio: Optional[float] = None
    feature_names: Optional[List[str]] = None
    num_features: Optional[int] = None
    status: str
    error: Optional[str] = None


@router.get("/info", response_model=ModelInfoResponse)
def get_model_info():
    """Get Phase A model metadata and information."""
    service = get_inference_service()
    info = service.get_model_info()
    return ModelInfoResponse(**info)


@router.post("/predict", response_model=PredictionResponse)
def predict_single(request: SinglePredictionRequest, user=Depends(get_current_user)):
    """
    Make a single prediction using Phase A models.
    
    Example request:
    ```json
    {
        "features": {
            "cpu": 45.2,
            "memory": 60.1,
            "connections": 120,
            "cpu_velocity": 2.1,
            "memory_velocity": 1.5,
            "connections_velocity": 5,
            "rolling_cpu": 44.8,
            "rolling_memory": 59.2,
            "rolling_connections": 118
        }
    }
    ```
    """
    service = get_inference_service()
    
    if not service.is_ready():
        raise HTTPException(status_code=503, detail="Models not loaded or trained yet")
    
    result = service.predict_single(request.features)
    
    if 'error' in result:
        raise HTTPException(status_code=400, detail=result['error'])
    
    return PredictionResponse(**result)


@router.post("/predict-batch", response_model=BatchPredictionResponse)
def predict_batch(request: BatchPredictionRequest, user=Depends(get_current_user)):
    """
    Make batch predictions using Phase A models.
    
    Example request:
    ```json
    {
        "features_list": [
            {
                "cpu": 45.2,
                "memory": 60.1,
                ...
            },
            {
                "cpu": 50.0,
                "memory": 70.0,
                ...
            }
        ]
    }
    ```
    """
    service = get_inference_service()
    
    if not service.is_ready():
        raise HTTPException(status_code=503, detail="Models not loaded or trained yet")
    
    result = service.predict_batch(request.features_list)
    
    if 'error' in result:
        raise HTTPException(status_code=400, detail=result['error'])
    
    return BatchPredictionResponse(**result)
