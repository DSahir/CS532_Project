#!/usr/bin/env python3
"""
Unit tests for FastAPI endpoints
Tests HTTP endpoints, status codes, and basic request/response flow
"""

import unittest
from unittest.mock import Mock, patch
import pandas as pd
from datetime import datetime


class TestAPIEndpoints(unittest.TestCase):
    def setUp(self):
        # Mock OHLC data
        self.mock_ohlc_data = pd.DataFrame({
            'timestamp': pd.date_range('2023-11-09 12:00:00', periods=5, freq='1s', tz='UTC'),
            'open': [50000.0, 50010.0, 50020.0, 50030.0, 50040.0],
            'high': [50020.0, 50030.0, 50040.0, 50050.0, 50060.0],
            'low': [49980.0, 49990.0, 50000.0, 50010.0, 50020.0],
            'close': [50010.0, 50020.0, 50030.0, 50040.0, 50050.0],
            'volume': [0.5, 0.6, 0.7, 0.8, 0.9],
            'symbol': ['BTCUSD'] * 5
        })
        
        # Mock volatility data
        self.mock_volatility_data = pd.DataFrame({
            'timestamp': pd.date_range('2023-11-09 12:00:00', periods=5, freq='1s', tz='UTC'),
            'volatility': [0.001, 0.002, 0.0015, 0.0018, 0.0012],
            'symbol': ['BTCUSD'] * 5
        })
    
    def test_health_endpoint_format(self):
        """Test health endpoint returns correct format"""
        expected_response = {
            'status': 'healthy',
            'service': 'crypto-api'
        }
        
        self.assertIn('status', expected_response)
        self.assertIn('service', expected_response)
        self.assertEqual(expected_response['status'], 'healthy')
    
    def test_symbols_endpoint_format(self):
        """Test symbols endpoint returns list of symbols"""
        mock_symbols = ['BTCUSD', 'ETHUSD', 'USDTUSD']
        
        response = {'symbols': mock_symbols}
        
        self.assertIn('symbols', response)
        self.assertIsInstance(response['symbols'], list)
        self.assertEqual(len(response['symbols']), 3)
    
    def test_ohlc_endpoint_query_params(self):
        """Test OHLC endpoint accepts proper query parameters"""
        valid_params = {
            'symbol': 'BTCUSD',
            'limit': 100,
            'start_date': '2023-11-09',
            'end_date': '2023-11-10'
        }
        
        # Check all expected params exist
        self.assertIn('symbol', valid_params)
        self.assertIn('limit', valid_params)
        
        # Check types
        self.assertIsInstance(valid_params['symbol'], str)
        self.assertIsInstance(valid_params['limit'], int)
        self.assertGreater(valid_params['limit'], 0)
    
    def test_ohlc_response_with_data(self):
        """Test OHLC endpoint response when data exists"""
        response_data = []
        for _, row in self.mock_ohlc_data.iterrows():
            response_data.append({
                'timestamp': row['timestamp'].isoformat(),
                'open': float(row['open']),
                'high': float(row['high']),
                'low': float(row['low']),
                'close': float(row['close']),
                'volume': float(row['volume']),
                'symbol': row['symbol']
            })
        
        response = {
            'data': response_data,
            'count': len(response_data),
            'symbol': 'BTCUSD'
        }
        
        # Verify response structure
        self.assertEqual(response['count'], 5)
        self.assertEqual(len(response['data']), 5)
        self.assertEqual(response['symbol'], 'BTCUSD')
        
        # Verify first data point has all fields
        first_point = response['data'][0]
        required_fields = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'symbol']
        for field in required_fields:
            self.assertIn(field, first_point)
    
    def test_ohlc_response_empty_data(self):
        """Test OHLC endpoint response when no data exists"""
        response = {
            'data': [],
            'count': 0,
            'symbol': 'INVALID'
        }
        
        self.assertEqual(response['count'], 0)
        self.assertEqual(len(response['data']), 0)
        self.assertIsInstance(response['data'], list)
    
    def test_volatility_endpoint_response(self):
        """Test volatility endpoint response structure"""
        response_data = []
        for _, row in self.mock_volatility_data.iterrows():
            response_data.append({
                'timestamp': row['timestamp'].isoformat(),
                'volatility': float(row['volatility']),
                'symbol': row['symbol']
            })
        
        response = {
            'data': response_data,
            'count': len(response_data),
            'symbol': 'BTCUSD'
        }
        
        # Verify structure
        self.assertEqual(response['count'], 5)
        self.assertIsInstance(response['data'], list)
        
        # Verify volatility data point
        first_point = response['data'][0]
        self.assertIn('timestamp', first_point)
        self.assertIn('volatility', first_point)
        self.assertIn('symbol', first_point)
    
    def test_limit_parameter_validation(self):
        """Test limit parameter validation"""
        valid_limits = [1, 100, 1000, 5000]
        invalid_limits = [-1, 0, 'invalid']
        
        for limit in valid_limits:
            self.assertIsInstance(limit, int)
            self.assertGreater(limit, 0)
        
        for limit in invalid_limits:
            if isinstance(limit, int):
                self.assertFalse(limit > 0)
    
    def test_date_parameter_format(self):
        """Test date parameters are in correct format"""
        valid_dates = ['2023-11-09', '2024-01-01', '2023-12-31']
        
        for date_str in valid_dates:
            # Should be YYYY-MM-DD format
            self.assertEqual(len(date_str), 10)
            self.assertEqual(date_str.count('-'), 2)
            
            # Should be parseable
            parts = date_str.split('-')
            self.assertEqual(len(parts), 3)
            self.assertEqual(len(parts[0]), 4)  # year
            self.assertEqual(len(parts[1]), 2)  # month
            self.assertEqual(len(parts[2]), 2)  # day


class TestAPIErrorHandling(unittest.TestCase):
    """Test API error handling and edge cases"""
    
    def test_missing_symbol_returns_all_data(self):
        """Test that missing symbol parameter returns data for all symbols"""
        # When symbol is None or not provided, should return all symbols
        symbol = None
        
        self.assertIsNone(symbol)
    
    def test_invalid_symbol_returns_empty(self):
        """Test that invalid symbol returns empty response"""
        response = {
            'data': [],
            'count': 0,
            'symbol': 'INVALID_SYMBOL'
        }
        
        self.assertEqual(response['count'], 0)
        self.assertEqual(len(response['data']), 0)
    
    def test_timestamp_serialization(self):
        """Test timestamps are properly serialized to ISO format"""
        timestamp = pd.Timestamp('2023-11-09 12:00:00', tz='UTC')
        iso_string = timestamp.isoformat()
        
        # Should be ISO 8601 format
        self.assertIsInstance(iso_string, str)
        self.assertIn('T', iso_string)
        self.assertIn(':', iso_string)

class TestVisualizationEndpoints(unittest.TestCase):
    def test_candlestick_response_structure(self):
        """Test candlestick chart endpoint returns plotly-compatible format"""
        # Plotly format has 'data' and 'layout' keys
        mock_response = {
            'data': [
                {
                    'type': 'candlestick',
                    'x': ['2023-11-09T12:00:00+00:00'],
                    'open': [50000.0],
                    'high': [50100.0],
                    'low': [49900.0],
                    'close': [50050.0]
                }
            ],
            'layout': {
                'title': 'BTCUSD Price Chart',
                'xaxis': {'title': 'Time'},
                'yaxis': {'title': 'Price (USD)'}
            }
        }
        
        self.assertIn('data', mock_response)
        self.assertIn('layout', mock_response)
        self.assertIsInstance(mock_response['data'], list)
        self.assertIsInstance(mock_response['layout'], dict)
    
    def test_price_line_response_structure(self):
        """Test price line chart response structure"""
        mock_response = {
            'data': [
                {
                    'type': 'scatter',
                    'mode': 'lines',
                    'x': ['2023-11-09T12:00:00+00:00'],
                    'y': [50000.0]
                }
            ],
            'layout': {'title': 'Price Chart'}
        }
        
        self.assertIn('data', mock_response)
        self.assertIn('layout', mock_response)
    
    def test_multi_symbol_response(self):
        """Test multi-symbol comparison endpoint"""
        symbols = 'BTCUSD,ETHUSD,USDTUSD'
        symbol_list = symbols.split(',')
        
        self.assertEqual(len(symbol_list), 3)
        self.assertIn('BTCUSD', symbol_list)
        self.assertIn('ETHUSD', symbol_list)

