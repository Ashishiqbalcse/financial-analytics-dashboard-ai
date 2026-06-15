from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from app.core.database import get_async_db
from app.models.market_data import OHLCV
from app.models.schemas import OHLCVResponse, MarketDataResponse
from app.services.market_data import market_data_service
from app.services.technical_indicators import technical_indicators
from app.core.redis_client import redis_client
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/prices/{symbol}", response_model=List[OHLCVResponse])
async def get_prices(
    symbol: str,
    limit: int = Query(100, ge=1, le=1000),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_async_db)
):
    """Get price data for a symbol"""
    try:
        cache_key = f"prices:{symbol}:{limit}:{start_date}:{end_date}"
        cached_data = redis_client.get(cache_key)
        if cached_data:
            logger.debug(f"Returning cached prices for {symbol}")
            return cached_data
        
        query = db.query(OHLCV).filter(OHLCV.symbol == symbol.upper())
        
        if start_date:
            query = query.filter(OHLCV.timestamp >= start_date)
        if end_date:
            query = query.filter(OHLCV.timestamp <= end_date)
        
        prices = query.order_by(OHLCV.timestamp.desc()).limit(limit).all()
        prices = list(reversed(prices))  # Return in chronological order
        
        # Cache for 5 minutes
        redis_client.set(cache_key, [p.__dict__ for p in prices], ttl=300)
        
        return prices
        
    except Exception as e:
        logger.error(f"Error fetching prices for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/prices/{symbol}/latest", response_model=MarketDataResponse)
async def get_latest_price(symbol: str):
    """Get the latest price for a symbol"""
    try:
        cache_key = f"latest_price:{symbol}"
        cached_data = redis_client.get(cache_key)
        if cached_data:
            logger.debug(f"Returning cached latest price for {symbol}")
            return cached_data
        
        price_data = await market_data_service.get_realtime_price(symbol.upper())
        
        if not price_data:
            raise HTTPException(status_code=404, detail=f"No data found for symbol {symbol}")
        
        # Cache for 30 seconds
        redis_client.set(cache_key, price_data, ttl=30)
        
        return price_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching latest price for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/prices/{symbol}/historical")
async def get_historical_prices(
    symbol: str,
    period: str = Query("1mo", description="Time period: 1mo, 3mo, 6mo, 1y, max"),
    interval: str = Query("1d", description="Data interval: 1d, 1wk, 1mo")
):
    """Get historical price data from external API"""
    try:
        cache_key = f"hist_external:{symbol}:{period}:{interval}"
        cached_data = redis_client.get(cache_key)
        if cached_data:
            logger.debug(f"Returning cached historical data for {symbol}")
            return cached_data
        
        historical_data = await market_data_service.get_historical_data(symbol.upper(), period, interval)
        
        if not historical_data:
            raise HTTPException(status_code=404, detail=f"No historical data found for symbol {symbol}")
        
        # Cache for 10 minutes
        redis_client.set(cache_key, historical_data, ttl=600)
        
        return historical_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching historical prices for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/prices/{symbol}/range")
async def get_prices_by_range(
    symbol: str,
    start_date: datetime,
    end_date: datetime,
    db: Session = Depends(get_async_db)
):
    """Get prices within a specific date range"""
    try:
        cache_key = f"range:{symbol}:{start_date}:{end_date}"
        cached_data = redis_client.get(cache_key)
        if cached_data:
            logger.debug(f"Returning cached range data for {symbol}")
            return cached_data
        
        query = db.query(OHLCV).filter(
            OHLCV.symbol == symbol.upper(),
            OHLCV.timestamp >= start_date,
            OHLCV.timestamp <= end_date
        ).order_by(OHLCV.timestamp.asc()).all()
        
        result = [p.__dict__ for p in query]
        
        # Cache for 5 minutes
        redis_client.set(cache_key, result, ttl=300)
        
        return result
        
    except Exception as e:
        logger.error(f"Error fetching price range for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/prices/symbols")
async def get_available_symbols(db: Session = Depends(get_async_db)):
    """Get list of available symbols"""
    try:
        symbols = db.query(OHLCV.symbol).distinct().all()
        return [symbol[0] for symbol in symbols]
    except Exception as e:
        logger.error(f"Error fetching available symbols: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/prices/compare")
async def compare_symbols(
    symbols: List[str] = Query(..., description="List of symbols to compare"),
    db: Session = Depends(get_async_db)
):
    """Compare current prices of multiple symbols"""
    try:
        results = {}
        for symbol in symbols:
            latest = db.query(OHLCV).filter(
                OHLCV.symbol == symbol.upper()
            ).order_by(OHLCV.timestamp.desc()).first()
            
            if latest:
                results[symbol.upper()] = {
                    'current_price': latest.close,
                    'timestamp': latest.timestamp,
                    'volume': latest.volume
                }
        
        return results
        
    except Exception as e:
        logger.error(f"Error comparing symbols: {e}")
        raise HTTPException(status_code=500, detail=str(e))
