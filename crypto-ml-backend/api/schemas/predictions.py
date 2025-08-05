"""
Schemas for prediction requests and responses.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class PredictionRequest(BaseModel):
    """Base prediction request schema"""
    symbol: str = Field(..., description="Cryptocurrency symbol")
    model_type: str = Field("ensemble", description="Model type to use")
    
class PredictionResponse(BaseModel):
    """Base prediction response schema"""
    symbol: str
    model_type: str
    timestamp: datetime
    
class PricePredictionRequest(PredictionRequest):
    """Price prediction specific request"""
    horizon: int = Field(24, description="Prediction horizon in hours", ge=1, le=168)
    include_confidence: bool = Field(True, description="Include confidence intervals")
    features: Optional[Dict[str, Any]] = Field(None, description="Additional features")
    
class PricePredictionResponse(PredictionResponse):
    """Price prediction response"""
    predictions: List[Dict[str, Any]]
    confidence_intervals: Optional[List[Dict[str, float]]]
    model_metrics: Dict[str, float]
    feature_importance: Optional[Dict[str, float]]
    
class SentimentPredictionRequest(PredictionRequest):
    """Sentiment prediction request"""
    text_data: List[str] = Field(..., description="Texts to analyze")
    sources: Optional[List[str]] = Field(None, description="Data sources")
    
class SentimentPredictionResponse(PredictionResponse):
    """Sentiment prediction response"""
    sentiment_scores: List[Dict[str, Any]]
    aggregate_sentiment: Dict[str, float]
    confidence: float
