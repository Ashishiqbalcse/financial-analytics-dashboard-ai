import yfinance as yf
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.foreignexchange import ForeignExchange
import pandas as pd
import asyncio
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from app.core.config import settings
from app.core.redis_client import redis_client
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MarketDataService:
    """Service for fetching market data from multiple sources"""
    
    def __init__(self):
        self.alpha_vantage_api_key = settings.ALPHA_VANTAGE_API_KEY
        self.cache_ttl = 60  # 60 seconds cache TTL
        
    async def get_yahoo_data(self, symbol: str, period: str = "1mo", interval: str = "1d") -> Optional[pd.DataFrame]:
        """Fetch data from Yahoo Finance"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period, interval=interval)
            
            if data.empty:
                logger.warning(f"No data returned from Yahoo Finance for {symbol}")
                return None
            
            # Rename columns to match our schema
            data.columns = data.columns.str.lower()
            data = data.reset_index()
            
            # Standardize column names
            if 'adj close' in data.columns:
                data = data.rename(columns={'adj close': 'adj_close'})
            
            return data
        except Exception as e:
            logger.error(f"Error fetching Yahoo data for {symbol}: {e}")
            return None
    
    async def get_alpha_vantage_data(self, symbol: str, outputsize: str = "compact") -> Optional[pd.DataFrame]:
        """Fetch data from Alpha Vantage"""
        if not self.alpha_vantage_api_key:
            logger.warning("Alpha Vantage API key not configured")
            return None
        
        try:
            ts = TimeSeries(key=self.alpha_vantage_api_key, output_format='pandas')
            
            # Get intraday data (1-minute intervals)
            data, meta_data = ts.get_intraday(
                symbol=symbol,
                interval='1min',
                outputsize=outputsize
            )
            
            if data is None or data.empty:
                logger.warning(f"No data returned from Alpha Vantage for {symbol}")
                return None
            
            # Rename columns to match our schema
            data.columns = [col.split('. ')[1].lower() for col in data.columns]
            data = data.reset_index()
            data = data.rename(columns={'date': 'timestamp'})
            
            return data
        except Exception as e:
            logger.error(f"Error fetching Alpha Vantage data for {symbol}: {e}")
            return None
    
    async def get_realtime_price(self, symbol: str) -> Optional[Dict]:
        """Get current real-time price with caching"""
        cache_key = f"price:{symbol}"
        
        # Check cache first
        cached_data = redis_client.get(cache_key)
        if cached_data:
            logger.debug(f"Returning cached price for {symbol}")
            return cached_data
        
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            if not info:
                return None
            
            price_data = {
                'symbol': symbol,
                'current_price': info.get('currentPrice') or info.get('regularMarketPrice'),
                'change': info.get('regularMarketChange'),
                'change_percent': info.get('regularMarketChangePercent'),
                'volume': info.get('regularMarketVolume'),
                'high_52w': info.get('fiftyTwoWeekHigh'),
                'low_52w': info.get('fiftyTwoWeekLow'),
                'market_cap': info.get('marketCap'),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Cache for 60 seconds
            redis_client.set(cache_key, price_data, ttl=self.cache_ttl)
            
            return price_data
        except Exception as e:
            logger.error(f"Error fetching realtime price for {symbol}: {e}")
            return None
    
    async def get_historical_data(self, symbol: str, period: str = "1mo", interval: str = "1d") -> Optional[List[Dict]]:
        """Get historical OHLCV data"""
        cache_key = f"hist:{symbol}:{period}:{interval}"
        
        # Check cache first
        cached_data = redis_client.get(cache_key)
        if cached_data:
            logger.debug(f"Returning cached historical data for {symbol}")
            return cached_data
        
        try:
            data = await self.get_yahoo_data(symbol, period, interval)
            
            if data is None:
                return None
            
            # Convert to list of dictionaries
            records = []
            for _, row in data.iterrows():
                record = {
                    'symbol': symbol,
                    'timestamp': row['date'].isoformat() if 'date' in row else row['timestamp'].isoformat(),
                    'open': float(row['open']),
                    'high': float(row['high']),
                    'low': float(row['low']),
                    'close': float(row['close']),
                    'volume': float(row['volume'])
                }
                records.append(record)
            
            # Cache for 5 minutes
            redis_client.set(cache_key, records, ttl=300)
            
            return records
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {e}")
            return None
    
    async def get_multiple_prices(self, symbols: List[str]) -> Dict[str, Optional[Dict]]:
        """Get real-time prices for multiple symbols"""
        results = {}
        
        # Fetch all prices concurrently
        tasks = [self.get_realtime_price(symbol) for symbol in symbols]
        prices = await asyncio.gather(*tasks)
        
        for symbol, price in zip(symbols, prices):
            results[symbol] = price
        
        return results
    
    def format_ohlcv_for_db(self, data: Dict) -> Dict:
        """Format OHLCV data for database insertion"""
        return {
            'symbol': data['symbol'],
            'timestamp': datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00')),
            'open': data['open'],
            'high': data['high'],
            'low': data['low'],
            'close': data['close'],
            'volume': data['volume']
        }


# Global market data service instance
market_data_service = MarketDataService()
