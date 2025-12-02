"""
Plotly visualization endpoints
"""

from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import HTMLResponse
from typing import Optional
import plotly.graph_objects as go
import plotly.express as px
from plotly.utils import PlotlyJSONEncoder
import json
import sys
import os
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from api.data_loader import DataLoader

router = APIRouter(prefix="/api/viz", tags=["Visualizations"])

OUTPUT_DIR = os.getenv("OUTPUT_DIR", "./data/outputs")
loader = DataLoader(OUTPUT_DIR)


@router.get("/candlestick")
async def candlestick_chart(
    symbol: str = Query(..., description="Cryptocurrency symbol"),
    limit: int = Query(500, description="Number of data points")
):
    """Generate candlestick chart for OHLC data"""
    try:
        df = loader.load_ohlc(symbol=symbol, limit=limit)
        
        if df.empty:
            raise HTTPException(status_code=404, detail=f"No data found for symbol {symbol}")
        
        # Create candlestick chart
        fig = go.Figure(data=[go.Candlestick(
            x=df['timestamp'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name=symbol
        )])
        
        fig.update_layout(
            title=f"{symbol} Price Chart (Candlestick)",
            xaxis_title="Time",
            yaxis_title="Price (USD)",
            template="plotly_dark",
            height=600
        )
        
        return json.loads(json.dumps(fig.to_dict(), cls=PlotlyJSONEncoder))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/price-line")
async def price_line_chart(
    symbol: str = Query(..., description="Cryptocurrency symbol"),
    limit: int = Query(500, description="Number of data points")
):
    """Generate line chart for closing prices"""
    try:
        df = loader.load_ohlc(symbol=symbol, limit=limit)
        
        if df.empty:
            raise HTTPException(status_code=404, detail=f"No data found for symbol {symbol}")
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['close'],
            mode='lines',
            name='Close Price',
            line=dict(color='#00d4ff', width=2)
        ))
        
        fig.update_layout(
            title=f"{symbol} Closing Price Over Time",
            xaxis_title="Time",
            yaxis_title="Price (USD)",
            template="plotly_dark",
            height=500
        )
        
        return json.loads(json.dumps(fig.to_dict(), cls=PlotlyJSONEncoder))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/volatility")
async def volatility_chart(
    symbol: str = Query(..., description="Cryptocurrency symbol"),
    limit: int = Query(500, description="Number of data points")
):
    """Generate volatility chart"""
    try:
        df = loader.load_volatility(symbol=symbol, limit=limit)
        
        if df.empty:
            raise HTTPException(status_code=404, detail=f"No data found for symbol {symbol}")
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['volatility'],
            mode='lines',
            name='Volatility',
            fill='tozeroy',
            line=dict(color='#ff6b6b', width=2)
        ))
        
        fig.update_layout(
            title=f"{symbol} Volatility Over Time",
            xaxis_title="Time",
            yaxis_title="Volatility",
            template="plotly_dark",
            height=500
        )
        
        return json.loads(json.dumps(fig.to_dict(), cls=PlotlyJSONEncoder))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/multi-symbol")
async def multi_symbol_chart(
    symbols: str = Query(..., description="Comma-separated symbols (e.g., BTCUSD,ETHUSD)"),
    limit: int = Query(500, description="Number of data points per symbol")
):
    """Compare multiple symbols on one chart"""
    try:
        symbol_list = [s.strip() for s in symbols.split(",")]
        fig = go.Figure()
        
        colors = ['#00d4ff', '#ff6b6b', '#4ecdc4', '#ffe66d', '#a8e6cf']
        
        for i, symbol in enumerate(symbol_list):
            df = loader.load_ohlc(symbol=symbol, limit=limit)
            if not df.empty:
                fig.add_trace(go.Scatter(
                    x=df['timestamp'],
                    y=df['close'],
                    mode='lines',
                    name=symbol,
                    line=dict(color=colors[i % len(colors)], width=2)
                ))
        
        fig.update_layout(
            title="Multi-Symbol Price Comparison",
            xaxis_title="Time",
            yaxis_title="Price (USD)",
            template="plotly_dark",
            height=600
        )
        
        return json.loads(json.dumps(fig.to_dict(), cls=PlotlyJSONEncoder))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/volume")
async def volume_chart(
    symbol: str = Query(..., description="Cryptocurrency symbol"),
    limit: int = Query(500, description="Number of data points")
):
    """Generate volume chart"""
    try:
        df = loader.load_ohlc(symbol=symbol, limit=limit)
        
        if df.empty:
            raise HTTPException(status_code=404, detail=f"No data found for symbol {symbol}")
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df['timestamp'],
            y=df['volume'],
            name='Volume',
            marker_color='#4ecdc4'
        ))
        
        fig.update_layout(
            title=f"{symbol} Trading Volume",
            xaxis_title="Time",
            yaxis_title="Volume",
            template="plotly_dark",
            height=400
        )
        
        return json.loads(json.dumps(fig.to_dict(), cls=PlotlyJSONEncoder))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

