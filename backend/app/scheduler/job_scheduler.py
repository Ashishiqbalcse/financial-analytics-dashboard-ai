from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.services.data_ingestion import DataIngestionService
from app.services.market_data import market_data_service
from app.services.forecasting import forecasting_service
from app.websocket.connection_manager import manager
from app.core.config import settings
from datetime import datetime
import logging
from typing import List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataIngestionScheduler:
    """Scheduler for automated market data ingestion"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler(timezone=settings.SCHEDULER_TIMEZONE)
        # Default symbols to track
        self.symbols_to_track = [
            "AAPL",  # Apple
            "TSLA",  # Tesla
            "GOOGL", # Google
            "MSFT",  # Microsoft
            "AMZN",  # Amazon
            "META",  # Meta
            "NVDA",  # NVIDIA
            "JPM",   # JPMorgan
        ]
        
    def start(self):
        """Start the scheduler"""
        try:
            # Schedule data ingestion every minute
            self.scheduler.add_job(
                self.ingest_all_symbols,
                trigger=IntervalTrigger(minutes=1),
                id='ingest_all_symbols',
                name='Ingest data for all tracked symbols',
                replace_existing=True
            )
            
            # Schedule historical data ingestion every hour
            self.scheduler.add_job(
                self.ingest_historical_data,
                trigger=IntervalTrigger(hours=1),
                id='ingest_historical',
                name='Ingest historical data',
                replace_existing=True
            )
            
            # Schedule data cleanup daily
            self.scheduler.add_job(
                self.cleanup_old_data,
                trigger=IntervalTrigger(hours=24),
                id='cleanup_data',
                name='Clean up old data',
                replace_existing=True
            )
            
            # Schedule model retraining every 6 hours
            self.scheduler.add_job(
                self.retrain_forecast_models,
                trigger=IntervalTrigger(hours=6),
                id='retrain_models',
                name='Retrain forecast models',
                replace_existing=True
            )
            
            self.scheduler.start()
            logger.info("Data ingestion scheduler started successfully")
            
        except Exception as e:
            logger.error(f"Error starting scheduler: {e}")
    
    def stop(self):
        """Stop the scheduler"""
        try:
            self.scheduler.shutdown()
            logger.info("Data ingestion scheduler stopped")
        except Exception as e:
            logger.error(f"Error stopping scheduler: {e}")
    
    async def ingest_all_symbols(self):
        """Ingest real-time data for all tracked symbols"""
        db = SessionLocal()
        try:
            ingestion_service = DataIngestionService(db)
            results = await ingestion_service.ingest_multiple_symbols(self.symbols_to_track)
            
            logger.info(f"Data ingestion completed: {len(results['success'])} success, {len(results['failed'])} failed")
            
            # Broadcast price updates via WebSocket for successful ingestions
            for symbol in results['success']:
                try:
                    price_data = await market_data_service.get_realtime_price(symbol)
                    if price_data:
                        await manager.broadcast_price(symbol, price_data)
                        logger.info(f"Broadcasted price update for {symbol}")
                except Exception as e:
                    logger.error(f"Error broadcasting price for {symbol}: {e}")
            
            if results['failed']:
                logger.warning(f"Failed symbols: {results['failed']}")
                
        except Exception as e:
            logger.error(f"Error in ingest_all_symbols job: {e}")
        finally:
            db.close()
    
    async def ingest_historical_data(self):
        """Ingest historical data for all tracked symbols"""
        db = SessionLocal()
        try:
            ingestion_service = DataIngestionService(db)
            
            for symbol in self.symbols_to_track:
                records = await ingestion_service.ingest_historical_data(symbol, period="1mo")
                logger.info(f"Added {records} historical records for {symbol}")
                
        except Exception as e:
            logger.error(f"Error in ingest_historical_data job: {e}")
        finally:
            db.close()
    
    def cleanup_old_data(self):
        """Clean up old data (older than 30 days)"""
        db = SessionLocal()
        try:
            ingestion_service = DataIngestionService(db)
            
            for symbol in self.symbols_to_track:
                deleted = ingestion_service.delete_old_data(symbol, days_to_keep=30)
                logger.info(f"Deleted {deleted} old records for {symbol}")
                
        except Exception as e:
            logger.error(f"Error in cleanup_old_data job: {e}")
        finally:
            db.close()
    
    async def retrain_forecast_models(self):
        """Retrain forecast models for all tracked symbols"""
        try:
            logger.info("Starting forecast model retraining")
            
            for symbol in self.symbols_to_track:
                try:
                    # Retrain model
                    model_data = forecasting_service.train_model(symbol, periods=7)
                    logger.info(f"Retrained forecast model for {symbol}")
                    
                    # Broadcast model update via WebSocket
                    await manager.broadcast_price(symbol, {
                        'type': 'model_update',
                        'symbol': symbol,
                        'metrics': model_data['metrics'],
                        'timestamp': datetime.utcnow().isoformat()
                    })
                    
                except Exception as e:
                    logger.error(f"Error retraining model for {symbol}: {e}")
            
            logger.info("Forecast model retraining completed")
            
        except Exception as e:
            logger.error(f"Error in retrain_forecast_models job: {e}")
    
    def add_symbol(self, symbol: str):
        """Add a symbol to the tracking list"""
        if symbol not in self.symbols_to_track:
            self.symbols_to_track.append(symbol)
            logger.info(f"Added {symbol} to tracking list")
        else:
            logger.warning(f"{symbol} is already being tracked")
    
    def remove_symbol(self, symbol: str):
        """Remove a symbol from the tracking list"""
        if symbol in self.symbols_to_track:
            self.symbols_to_track.remove(symbol)
            logger.info(f"Removed {symbol} from tracking list")
        else:
            logger.warning(f"{symbol} is not being tracked")
    
    def get_tracked_symbols(self) -> List[str]:
        """Get list of tracked symbols"""
        return self.symbols_to_track.copy()
    
    def set_symbols(self, symbols: List[str]):
        """Set the list of symbols to track"""
        self.symbols_to_track = symbols
        logger.info(f"Updated tracked symbols to: {symbols}")


# Global scheduler instance
scheduler = DataIngestionScheduler()
