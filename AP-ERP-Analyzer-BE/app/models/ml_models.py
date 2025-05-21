from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any, Union

class SalesForecastResponse(BaseModel):
    """Model for sales forecast response"""
    forecast_periods: List[str]
    forecast_values: List[float]
    historical_periods: List[str]
    historical_values: List[float]

class AnomalyDetectionResponse(BaseModel):
    """Model for anomaly detection response"""
    periods: List[str]
    net_flow: List[float]
    is_anomaly: List[bool]
    anomaly_score: List[float]
    anomalies: List[Dict[str, Any]]
    anomaly_count: int

class ModelTrainingResponse(BaseModel):
    """Model for model training response"""
    message: str
    model_type: Optional[str] = None
    periods_used: Optional[int] = None
    error: Optional[str] = None
