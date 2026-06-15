from sqlalchemy.orm import Session
from app.models.market_data import OHLCV, TechnicalIndicator
from app.services.market_data import market_data_service
from datetime import datetime, timedelta
from typing import List, Optional
import logging
from app.core.redis_client import redis_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataIngestionService:
    """Service for ingesting market data into the database"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def ingest_realtime_data(self, symbol: str) -> bool:
        """Ingest real-time market data for a symbol"""
        try:
            # Get real-time price data
            price_data = await market_data_service.get_realtime_price(symbol)
            
            if not price_data:
                logger.error(f"Failed to fetch price data for {symbol}")
                return False
            
            # Check if data already exists for this timestamp
            existing = self.db.query(OHLCV).filter(
                OHLCV.symbol == symbol,
                OHLCV.timestamp == datetime.utcnow()
            ).first()
            
            if existing:
                logger.debug(f"Data for {symbol} already exists for current timestamp")
                return True
            
            # Create OHLCV record
            ohlcv_record = OHLCV(
                symbol=symbol,
                timestamp=datetime.utcnow(),
                open=price_data.get('current_price', 0),
                high=price_data.get('current_price', 0),
                low=price_data.get('current_price', 0),
                close=price_data.get('current_price', 0),
                volume=price_data.get('volume', 0)
            )
            
            self.db.add(ohlcv_record)
            self.db.commit()
            
            # Invalidate cache
            cache_key = f"price:{symbol}"
            redis_client.delete(cache_key)
            
            logger.info(f"Successfully ingested data for {symbol}")
            return True
            
        except Exception as e:
            logger.error(f"Error ingesting data for {symbol}: {e}")
            self.db.rollback()
            return False
    
    async def ingest_historical_data(self, symbol: str, period: str = "1mo") -> int:
        """Ingest historical market data for a symbol"""
        try:
            # Get historical data
            historical_data = await market_data_service.get_historical_data(symbol, period)
            
            if not historical_data:
                logger.error(f"Failed to fetch historical data for {symbol}")
                return 0
            
            records_added = 0
            
            for data in historical_data:
                # Check if record already exists
                existing = self.db.query(OHLCV).filter(
                    OHLCV.symbol == symbol,
                    OHLCV.timestamp == datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
                ).first()
                
                if not existing:
                    # Create OHLCV record
                    ohlcv_record = OHLCV(
                        symbol=symbol,
                        timestamp=datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00')),
                        open=data['open'],
                        high=data['high'],
                        low=data['low'],
                        close=data['close'],
                        volume=data['volume']
                    )
                    
                    self.db.add(ohlcv_record)
                    records_added += 1
            
            self.db.commit()
            
            # Invalidate cache
            cache_key = f"hist:{symbol}:{period}:1d"
            redis_client.delete(cache_key)
            
            logger.info(f"Successfully ingested {records_added} historical records for {symbol}")
            return records_added
            
        except Exception as e:
            logger.error(f"Error ingesting historical data for {symbol}: {e}")
            self.db.rollback()
            return 0
    
    async def ingest_multiple_symbols(self, symbols: List[str]) -> dict:
        """Ingest data for multiple symbols"""
        results = {
            'success': [],
            'failed': []
        }
        
        for symbol in symbols:
            success = await self.ingest_realtime_data(symbol)
            if success:
                results['success'].append(symbol)
            else:
                results['failed'].append(symbol)
        
        return results
    
    def get_latest_data(self, symbol: str, limit: int = 100) -> List[OHLCV]:
        """Get the latest data for a symbol"""
        try:
            records = self.db.query(OHLCV).filter(
                OHLCV.symbol == symbol
            ).order_by(
                OHLCV.timestamp.desc()
            ).limit(limit).all()
            
            return list(reversed(records))  # Return in chronological order
            
        except Exception as e:
            logger.error(f"Error fetching latest data for {symbol}: {e}")
            return []
    
    def get_data_by_timerange(self, symbol: str, start_time: datetime, end_time: datetime) -> List[OHLCV]:
        """Get data for a specific time range"""
        try:
            records = self.db.query(OHLCV).filter(
                OHLCV.symbol == symbol,
                OHLCV.timestamp >= start_time,
                OHLCV.timestamp <= end_time
            ).order_by(
                OHLCV.timestamp.asc()
            ).all()
            
            return records
            
        except Exception as e:
            logger.error(f"Error fetching data by timerange for {symbol}: {e}")
            return []
    
    def get_available_symbols(self) -> List[str]:
        """Get list of symbols with data"""
        try:
            symbols = self.db.query(OHLCV.symbol).distinct().all()
            return [symbol[0] for symbol in symbols]
        except Exception as e:
            logger.error(f"Error fetching available symbols: {e}")
            return []
    
    def delete_old_data(self, symbol: str, days_to_keep: int = 30) -> int:
        """Delete data older than specified days"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
            
            deleted = self.db.query(OHLCV).filter(
                OHLCV.symbol == symbol,
                OHLCV.timestamp < cutoff_date
            ).delete()
            
            self.db.commit()
            
            logger.info(f"Deleted {deleted} old records for {symbol}")
            return deleted
            
        except Exception as e:
            logger.error(f"Error deleting old data for {symbol}: {e}")
            self.db.rollback()
            return 0


def get_data_ingestion_service(db: Session) -> DataIngestionService:
    """Factory function to get data ingestion service"""
    return DataIngestionService(db)
