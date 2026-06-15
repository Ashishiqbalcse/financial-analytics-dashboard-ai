from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class OHLCVBase(BaseModel):
    symbol: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


class OHLCVCreate(OHLCVBase):
    pass


class OHLCVResponse(OHLCVBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class TechnicalIndicatorBase(BaseModel):
    symbol: str
    timestamp: datetime
    indicator_type: str
    value: float
    metadata: Optional[str] = None


class TechnicalIndicatorCreate(TechnicalIndicatorBase):
    pass


class TechnicalIndicatorResponse(TechnicalIndicatorBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class IndicatorData(BaseModel):
    """Response format for indicator data"""
    timestamp: datetime
    value: float
    signal: Optional[str] = None  # buy, sell, neutral
    metadata: Optional[Dict[str, Any]] = None


class IndicatorResponse(BaseModel):
    symbol: str
    indicator_type: str
    data: List[IndicatorData]


class PredictionBase(BaseModel):
    symbol: str
    prediction_date: datetime
    predicted_close: float
    confidence_lower: float
    confidence_upper: float
    model_type: str = "prophet"


class PredictionCreate(PredictionBase):
    pass


class PredictionResponse(PredictionBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class ForecastResponse(BaseModel):
    symbol: str
    forecast: List[Dict[str, Any]]
    model_type: str
    generated_at: datetime


class PortfolioBase(BaseModel):
    user_id: str
    symbol: str
    shares: float
    average_cost: float


class PortfolioCreate(PortfolioBase):
    pass


class PortfolioResponse(PortfolioBase):
    id: int
    current_price: Optional[float] = None
    current_value: Optional[float] = None
    profit_loss: Optional[float] = None
    profit_loss_percent: Optional[float] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class AlertBase(BaseModel):
    user_id: str
    symbol: str
    condition: str  # above, below
    target_price: float


class AlertCreate(AlertBase):
    pass


class AlertResponse(AlertBase):
    id: int
    is_active: bool
    triggered: bool
    triggered_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class MarketDataResponse(BaseModel):
    symbol: str
    current_price: float
    change: float
    change_percent: float
    volume: float
    high_52w: Optional[float] = None
    low_52w: Optional[float] = None
    market_cap: Optional[float] = None


class NaturalLanguageQuery(BaseModel):
    query: str


class NaturalLanguageResponse(BaseModel):
    query: str
    interpretation: str
    symbols: List[str]
    timeframe: Optional[str] = None
    indicators: Optional[List[str]] = None
    sql_query: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


class WebSocketMessage(BaseModel):
    type: str  # price, indicator, alert, etc.
    symbol: str
    data: Dict[str, Any]
    timestamp: datetime


class HealthResponse(BaseModel):
    status: str
    database: str
    redis: str
    scheduler: str
