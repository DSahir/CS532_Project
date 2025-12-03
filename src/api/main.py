#!/usr/bin/env python3
"""
FastAPI Application - Milestone 4
API layer for cryptocurrency data with visualizations
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import os
import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent.parent
sys.path.insert(0, str(src_path))

from api.routes import ohlc, volatility, visualizations

app = FastAPI(
    title="Cryptocurrency Data API",
    description="Real-time cryptocurrency OHLC and volatility data API",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(ohlc.router)
app.include_router(volatility.router)
app.include_router(visualizations.router)


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve dashboard HTML"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Crypto Dashboard</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #1e1e1e; color: #fff; }
            .container { max-width: 1400px; margin: 0 auto; }
            .header { text-align: center; margin-bottom: 30px; }
            .controls { background: #2d2d2d; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
            .controls input, .controls select, .controls button {
                padding: 10px; margin: 5px; border-radius: 4px; border: 1px solid #444;
                background: #1e1e1e; color: #fff;
            }
            .controls button { background: #00d4ff; color: #000; cursor: pointer; }
            .controls button:hover { background: #00b8e6; }
            .chart-container { background: #2d2d2d; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 Cryptocurrency Real-Time Dashboard</h1>
                <p>OHLC Data & Volatility Analytics</p>
            </div>
            
            <div class="controls">
                <label>Symbol:</label>
                <select id="symbolSelect">
                    <option value="BTCUSD">BTCUSD</option>
                    <option value="ETHUSD">ETHUSD</option>
                    <option value="USDTUSD">USDTUSD</option>
                </select>
                
                <label>Chart Type:</label>
                <select id="chartType">
                    <option value="candlestick">Candlestick</option>
                    <option value="price-line">Price Line</option>
                    <option value="volatility">Volatility</option>
                    <option value="volume">Volume</option>
                </select>
                
                <label>Limit:</label>
                <input type="number" id="limit" value="500" min="100" max="5000">
                
                <button onclick="loadChart()">Load Chart</button>
                <button onclick="loadMultiSymbol()">Compare Symbols</button>
            </div>
            
            <div class="chart-container">
                <div id="chart"></div>
            </div>
        </div>
        
        <script>
            async function loadChart() {
                const symbol = document.getElementById('symbolSelect').value;
                const chartType = document.getElementById('chartType').value;
                const limit = document.getElementById('limit').value;
                
                let endpoint = `/api/viz/${chartType}?symbol=${symbol}&limit=${limit}`;
                
                try {
                    const response = await fetch(endpoint);
                    const data = await response.json();
                    Plotly.newPlot('chart', data.data, data.layout);
                } catch (error) {
                    console.error('Error loading chart:', error);
                    document.getElementById('chart').innerHTML = '<p style="color: red;">Error loading chart. Make sure data exists for this symbol.</p>';
                }
            }
            
            async function loadMultiSymbol() {
                const symbols = 'BTCUSD,ETHUSD,USDTUSD';
                const limit = document.getElementById('limit').value;
                
                try {
                    const response = await fetch(`/api/viz/multi-symbol?symbols=${symbols}&limit=${limit}`);
                    const data = await response.json();
                    Plotly.newPlot('chart', data.data, data.layout);
                } catch (error) {
                    console.error('Error loading multi-symbol chart:', error);
                }
            }
            
            // Load default chart on page load
            window.onload = () => loadChart();
        </script>
    </body>
    </html>
    """
    return html_content


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "service": "crypto-api"}


@app.get("/api/symbols")
async def get_symbols():
    """Get available symbols"""
    from api.data_loader import DataLoader
    # Get OUTPUT_DIR from environment or use relative path from project root
    output_dir = os.getenv("OUTPUT_DIR")
    if not output_dir:
        # Default to data/outputs relative to project root
        project_root = Path(__file__).parent.parent.parent
        output_dir = str(project_root / "data" / "outputs")
    loader = DataLoader(output_dir)
    return {"symbols": loader.get_available_symbols()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

