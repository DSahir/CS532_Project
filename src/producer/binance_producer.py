#!/usr/bin/env python3
"""
Binance WebSocket Producer - Milestone 1
Connects to Binance API and streams raw trade data to Kafka.
"""

import json
import os
import time
import logging
from datetime import datetime
import websocket
from kafka import KafkaProducer
from kafka.errors import KafkaError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BinanceProducer:
    """Producer for streaming Binance trade data to Kafka"""
    
    def __init__(self):
        self.bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092')
        self.topic = os.getenv('KAFKA_TOPIC', 'crypto-trades')
        self.symbols = os.getenv('SYMBOLS', 'BTCUSDT,ETHUSDT,USDTUSDT').split(',')
        self.batch_size = int(os.getenv('BATCH_SIZE', '1'))
        self.replay_speed = float(os.getenv('REPLAY_SPEED', '1'))
        
        self.producer = None
        self.ws = None
        self.message_count = 0
        self.start_time = time.time()
        
        logger.info(f"Initializing BinanceProducer")
        logger.info(f"Symbols: {self.symbols}")
        logger.info(f"Batch size: {self.batch_size}, Replay speed: {self.replay_speed}x")
        
    def connect_kafka(self):
        """Initialize Kafka producer with retry logic"""
        max_retries = 10
        retry_delay = 5
        
        for attempt in range(max_retries):
            try:
                self.producer = KafkaProducer(
                    bootstrap_servers=self.bootstrap_servers,
                    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                    key_serializer=lambda k: k.encode('utf-8') if k else None,
                    acks='all',
                    retries=3,
                    compression_type='gzip'
                )
                logger.info("✓ Successfully connected to Kafka")
                return True
            except Exception as e:
                logger.error(f"Attempt {attempt + 1}/{max_retries} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    raise
        return False
    
    def on_message(self, ws, message):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(message)
            
            # Extract trade information from Binance aggTrade stream
            if 'e' in data and data['e'] == 'aggTrade':
                # Normalize trade data
                trade_data = {
                    'symbol': data['s'],           # Trading symbol
                    'price': float(data['p']),     # Trade price
                    'quantity': float(data['q']),  # Trade quantity
                    'timestamp': data['T'],        # Trade timestamp (ms)
                    'is_buyer_maker': data['m'],   # Buyer is maker?
                    'trade_id': data['a']          # Aggregate trade ID
                }
                
                self.send_to_kafka(trade_data)
                
                # Apply replay speed throttling (for future stress testing)
                if self.replay_speed < 1:
                    time.sleep(1.0 / self.replay_speed)
                    
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    def send_to_kafka(self, trade_data):
        """Send trade data to Kafka"""
        try:
            # Use symbol as key for partitioning
            key = trade_data['symbol']
            
            future = self.producer.send(self.topic, key=key, value=trade_data)
            future.get(timeout=10)
            
            self.message_count += 1
            
            # Log progress every 100 messages
            if self.message_count % 100 == 0:
                elapsed = time.time() - self.start_time
                rate = self.message_count / elapsed
                logger.info(f"Sent {self.message_count} messages | Rate: {rate:.2f} msg/sec")
                
        except KafkaError as e:
            logger.error(f"Kafka error: {e}")
        except Exception as e:
            logger.error(f"Error sending message: {e}")
    
    def on_error(self, ws, error):
        """Handle WebSocket errors"""
        logger.error(f"WebSocket error: {error}")
    
    def on_close(self, ws, close_status_code, close_msg):
        """Handle WebSocket closure"""
        logger.info(f"WebSocket closed: {close_status_code}")
    
    def on_open(self, ws):
        """Handle WebSocket connection opening"""
        logger.info(f"✓ WebSocket connected for symbols: {self.symbols}")
    
    def start(self):
        """Start the producer"""
        logger.info("="*80)
        logger.info("STARTING BINANCE PRODUCER - MILESTONE 1")
        logger.info("="*80)
        
        # Connect to Kafka
        self.connect_kafka()
        
        # Build WebSocket URL for multiple symbols
        streams = [f"{symbol.lower()}@aggTrade" for symbol in self.symbols]
        stream_names = '/'.join(streams)
        ws_url = f"wss://stream.binance.com:9443/stream?streams={stream_names}"
        
        logger.info(f"Connecting to Binance WebSocket...")
        logger.info(f"Streaming: {', '.join(self.symbols)}")
        
        # Create WebSocket connection
        websocket.enableTrace(False)
        self.ws = websocket.WebSocketApp(
            ws_url,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
            on_open=self.on_open
        )
        
        # Run forever with automatic reconnection
        while True:
            try:
                self.ws.run_forever()
                logger.info("WebSocket disconnected, reconnecting in 5 seconds...")
                time.sleep(5)
            except KeyboardInterrupt:
                logger.info("Shutting down producer...")
                break
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                time.sleep(5)
        
        # Cleanup
        if self.producer:
            self.producer.flush()
            self.producer.close()


def main():
    """Main entry point"""
    producer = BinanceProducer()
    producer.start()


if __name__ == '__main__':
    main()