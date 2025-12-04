"""
Pydantic models for API request/response
"""

from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class OHLCData(BaseModel):
    """OHLC data point"""
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    symbol: str
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class VolatilityData(BaseModel):
    """Volatility data point"""
    timestamp: datetime
    volatility: float
    symbol: str
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class MetricsResponse(BaseModel):
    """Aggregated metrics response"""
    symbol: str
    current_price: float
    price_change_24h: Optional[float] = None
    price_change_percent_24h: Optional[float] = None
    high_24h: Optional[float] = None
    low_24h: Optional[float] = None
    volume_24h: Optional[float] = None
    avg_volatility_24h: Optional[float] = None
    max_volatility_24h: Optional[float] = None


class OHLCResponse(BaseModel):
    """OHLC endpoint response"""
    data: List[OHLCData]
    count: int
    symbol: Optional[str] = None


class VolatilityResponse(BaseModel):
    """Volatility endpoint response"""
    data: List[VolatilityData]
    count: int
    symbol: Optional[str] = None

