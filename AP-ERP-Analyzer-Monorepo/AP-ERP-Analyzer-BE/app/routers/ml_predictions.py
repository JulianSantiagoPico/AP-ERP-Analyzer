from fastapi import APIRouter, Query, HTTPException, BackgroundTasks
from typing import Optional, List, Dict, Any
from app.services.ml_service import ml_service

router = APIRouter()

@router.post("/train/sales-forecast")
async def train_sales_forecast_model(
    background_tasks: BackgroundTasks,
    force_retrain: bool = Query(False, description="Force retraining of the model")
):
    """
    Train a sales forecast model
    """
    try:
        # Run training in background to avoid blocking the API
        background_tasks.add_task(ml_service.train_sales_forecast_model, force_retrain=force_retrain)
        return {"message": "Sales forecast model training started in background"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error training sales forecast model: {str(e)}")

@router.get("/sales-forecast")
async def get_sales_forecast(
    periods: int = Query(3, description="Number of periods to forecast")
):
    """
    Get sales forecast
    """
    try:
        result = ml_service.predict_sales(periods=periods)
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error predicting sales: {str(e)}")

@router.post("/train/anomaly-detection")
async def train_anomaly_detection_model(
    background_tasks: BackgroundTasks,
    force_retrain: bool = Query(False, description="Force retraining of the model")
):
    """
    Train an anomaly detection model for cash flow
    """
    try:
        # Run training in background to avoid blocking the API
        background_tasks.add_task(ml_service.train_anomaly_detection_model, force_retrain=force_retrain)
        return {"message": "Anomaly detection model training started in background"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error training anomaly detection model: {str(e)}")

@router.get("/anomaly-detection")
async def get_anomaly_detection():
    """
    Get anomaly detection results for cash flow
    """
    try:
        result = ml_service.detect_anomalies()
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error detecting anomalies: {str(e)}")
