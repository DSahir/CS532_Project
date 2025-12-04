#!/usr/bin/env python3
"""
Data Loader - Reads OHLC and Volatility data from Parquet files
"""

import os
import glob
from pathlib import Path
from typing import Optional, List
from datetime import datetime, date
import pandas as pd


class DataLoader:
    """Loads OHLC and volatility data from parquet files"""
    
    def __init__(self, output_dir: str = "./data/outputs"):
        self.output_dir = Path(output_dir)
        self.ohlc_dir = self.output_dir / "ohlc"
        self.vol_dir = self.output_dir / "volatility"
    
    def _find_parquet_files(self, data_type: str, symbol: Optional[str] = None, 
                           date_filter: Optional[str] = None) -> List[Path]:
        """Find parquet files matching criteria"""
        if data_type == "ohlc":
            base_dir = self.ohlc_dir
        elif data_type == "volatility":
            base_dir = self.vol_dir
        else:
            return []
        
        pattern = "**/*.parquet"
        files = list(base_dir.glob(pattern))
        
        # Filter by symbol
        if symbol:
            files = [f for f in files if f"symbol={symbol}" in str(f)]
        
        # Filter by date
        if date_filter:
            files = [f for f in files if f"date={date_filter}" in str(f)]
        
        return sorted(files)
    
    def load_ohlc(self, symbol: Optional[str] = None, 
                   start_date: Optional[str] = None,
                   end_date: Optional[str] = None,
                   limit: Optional[int] = None) -> pd.DataFrame:
        """Load OHLC data"""
        files = self._find_parquet_files("ohlc", symbol=symbol)
        
        if not files:
            return pd.DataFrame()
        
        # Load all matching files
        dfs = []
        for file in files:
            # Extract date from path
            file_date = None
            for part in file.parts:
                if part.startswith("date="):
                    file_date = part.split("=")[1]
                    break
            
            # Apply date filters
            if start_date and file_date and file_date < start_date:
                continue
            if end_date and file_date and file_date > end_date:
                continue
            
            try:
                df = pd.read_parquet(file)
                dfs.append(df)
            except Exception as e:
                print(f"Error reading {file}: {e}")
        
        if not dfs:
            return pd.DataFrame()
        
        # Combine and sort
        result = pd.concat(dfs, ignore_index=True)
        result['timestamp'] = pd.to_datetime(result['timestamp'], utc=True)
        result = result.sort_values('timestamp')
        
        # Apply symbol filter if needed
        if symbol:
            result = result[result['symbol'] == symbol]
        
        # Limit results
        if limit:
            result = result.tail(limit)
        
        return result
    
    def load_volatility(self, symbol: Optional[str] = None,
                       start_date: Optional[str] = None,
                       end_date: Optional[str] = None,
                       limit: Optional[int] = None) -> pd.DataFrame:
        """Load volatility data"""
        files = self._find_parquet_files("volatility", symbol=symbol)
        
        if not files:
            return pd.DataFrame()
        
        dfs = []
        for file in files:
            file_date = None
            for part in file.parts:
                if part.startswith("date="):
                    file_date = part.split("=")[1]
                    break
            
            if start_date and file_date and file_date < start_date:
                continue
            if end_date and file_date and file_date > end_date:
                continue
            
            try:
                df = pd.read_parquet(file)
                dfs.append(df)
            except Exception as e:
                print(f"Error reading {file}: {e}")
        
        if not dfs:
            return pd.DataFrame()
        
        result = pd.concat(dfs, ignore_index=True)
        result['timestamp'] = pd.to_datetime(result['timestamp'], utc=True)
        result = result.sort_values('timestamp')
        
        if symbol:
            result = result[result['symbol'] == symbol]
        
        if limit:
            result = result.tail(limit)
        
        return result
    
    def get_available_symbols(self) -> List[str]:
        """Get list of available symbols"""
        symbols = set()
        for pattern in ["ohlc/symbol=*", "volatility/symbol=*"]:
            for path in self.output_dir.glob(pattern):
                if path.is_dir():
                    symbol = path.name.split("=")[1]
                    symbols.add(symbol)
        return sorted(list(symbols))
    
    def get_available_dates(self, symbol: Optional[str] = None) -> List[str]:
        """Get list of available dates"""
        dates = set()
        base_dir = self.ohlc_dir if symbol else self.output_dir
        pattern = f"ohlc/symbol={symbol}/date=*" if symbol else "ohlc/symbol=*/date=*"
        
        for path in base_dir.glob(pattern):
            if path.is_dir():
                date_str = path.name.split("=")[1]
                dates.add(date_str)
        
        return sorted(list(dates))

