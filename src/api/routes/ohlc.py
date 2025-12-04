"""
OHLC data endpoints
"""

from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from api.data_loader import DataLoader
from api.models import OHLCResponse, OHLCData

router = APIRouter(prefix="/api/ohlc", tags=["OHLC"])

# Initialize data loader
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "./data/outputs")
loader = DataLoader(OUTPUT_DIR)


@router.get("/", response_model=OHLCResponse)
async def get_ohlc(
    symbol: Optional[str] = Query(None, description="Cryptocurrency symbol (e.g., BTCUSD)"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    limit: Optional[int] = Query(1000, description="Maximum number of records to return")
):
    """Get OHLC (Open, High, Low, Close) data"""
    try:
        df = loader.load_ohlc(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )
        
        if df.empty:
            return OHLCResponse(data=[], count=0, symbol=symbol)
        
        # Convert to list of dicts
        data = []
        for _, row in df.iterrows():
            data.append(OHLCData(
                timestamp=row['timestamp'],
                open=float(row['open']),
                high=float(row['high']),
                low=float(row['low']),
                close=float(row['close']),
                volume=float(row['volume']),
                symbol=row['symbol']
            ))
        
        return OHLCResponse(data=data, count=len(data), symbol=symbol)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/latest")
async def get_latest_ohlc(
    symbol: Optional[str] = Query(None, description="Cryptocurrency symbol")
):
    """Get latest OHLC data point for each symbol"""
    try:
        symbols = [symbol] if symbol else loader.get_available_symbols()
        
        if not symbols:
            return {"data": []}
        
        result = []
        for sym in symbols:
            df = loader.load_ohlc(symbol=sym, limit=1)
            if not df.empty:
                row = df.iloc[-1]
                result.append({
                    "symbol": sym,
                    "timestamp": row['timestamp'].isoformat(),
                    "open": float(row['open']),
                    "high": float(row['high']),
                    "low": float(row['low']),
                    "close": float(row['close']),
                    "volume": float(row['volume'])
                })
        
        return {"data": result}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

