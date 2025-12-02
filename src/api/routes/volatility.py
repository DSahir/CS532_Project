"""
Volatility data endpoints
"""

from fastapi import APIRouter, Query, HTTPException
from typing import Optional
import sys
import os
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from api.data_loader import DataLoader
from api.models import VolatilityResponse, VolatilityData

router = APIRouter(prefix="/api/volatility", tags=["Volatility"])

OUTPUT_DIR = os.getenv("OUTPUT_DIR", "./data/outputs")
loader = DataLoader(OUTPUT_DIR)


@router.get("/", response_model=VolatilityResponse)
async def get_volatility(
    symbol: Optional[str] = Query(None, description="Cryptocurrency symbol"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    limit: Optional[int] = Query(1000, description="Maximum number of records")
):
    """Get volatility data"""
    try:
        df = loader.load_volatility(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )
        
        if df.empty:
            return VolatilityResponse(data=[], count=0, symbol=symbol)
        
        data = []
        for _, row in df.iterrows():
            data.append(VolatilityData(
                timestamp=row['timestamp'],
                volatility=float(row['volatility']) if pd.notna(row['volatility']) else 0.0,
                symbol=row['symbol']
            ))
        
        return VolatilityResponse(data=data, count=len(data), symbol=symbol)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

