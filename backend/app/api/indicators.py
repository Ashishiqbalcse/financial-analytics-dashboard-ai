from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.core.database import get_async_db
from app.models.market_data import OHLCV, TechnicalIndicator
from app.models.schemas import IndicatorResponse, IndicatorData
from app.services.technical_indicators import technical_indicators
from app.core.redis_client import redis_client
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/indicators/{symbol}", response_model=IndicatorResponse)
async def get_indicators(
    symbol: str,
    indicator_type: Optional[str] = Query(None, description="Specific indicator: RSI, MACD, SMA, EMA, BB"),
    period: int = Query(20, ge=5, le=200, description="Period for calculation"),
    db: Session = Depends(get_async_db)
):
    """Get technical indicators for a symbol"""
    try:
        symbol = symbol.upper()
        
        # Fetch price data
        prices = db.query(OHLCV).filter(
            OHLCV.symbol == symbol
        ).order_by(OHLCV.timestamp.asc()).limit(500).all()
        
        if not prices:
            raise HTTPException(status_code=404, detail=f"No price data found for {symbol}")
        
        # Extract close prices
        close_prices = [p.close for p in prices]
        timestamps = [p.timestamp.isoformat() for p in prices]
        
        # Calculate indicators
        if indicator_type:
            indicator_type = indicator_type.upper()
            if indicator_type == "RSI":
                values = technical_indicators.calculate_rsi(close_prices, period=period)
                data = [{
                    'timestamp': ts,
                    'value': val,
                    'signal': 'buy' if val and val < 30 else 'sell' if val and val > 70 else 'neutral'
                } for ts, val in zip(timestamps, values)]
            elif indicator_type == "MACD":
                macd_data = technical_indicators.calculate_macd(close_prices)
                # Return MACD line
                values = macd_data['macd']
                data = [{
                    'timestamp': ts,
                    'value': val,
                    'metadata': {'signal': macd_data['signal'][i], 'histogram': macd_data['histogram'][i]} if i < len(macd_data['signal']) else None
                } for i, (ts, val) in enumerate(zip(timestamps, values))]
            elif indicator_type == "SMA":
                values = technical_indicators.calculate_sma(close_prices, period=period)
                data = [{'timestamp': ts, 'value': val} for ts, val in zip(timestamps, values)]
            elif indicator_type == "EMA":
                values = technical_indicators.calculate_ema(close_prices, period=period)
                data = [{'timestamp': ts, 'value': val} for ts, val in zip(timestamps, values)]
            elif indicator_type == "BB":
                bb_data = technical_indicators.calculate_bollinger_bands(close_prices, period=period)
                data = [{
                    'timestamp': ts,
                    'value': bb_data['middle'][i],
                    'metadata': {
                        'upper': bb_data['upper'][i],
                        'lower': bb_data['lower'][i]
                    } if i < len(bb_data['upper']) else None
                } for i, ts in enumerate(timestamps)]
            else:
                raise HTTPException(status_code=400, detail=f"Unknown indicator type: {indicator_type}")
        else:
            # Return all indicators
            all_indicators = technical_indicators.calculate_all_indicators([
                {'close': p.close} for p in prices
            ])
            return {
                'symbol': symbol,
                'indicator_type': 'ALL',
                'data': all_indicators
            }
        
        return {
            'symbol': symbol,
            'indicator_type': indicator_type or 'ALL',
            'data': data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching indicators for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/indicators/{symbol}/all")
async def get_all_indicators(
    symbol: str,
    db: Session = Depends(get_async_db)
):
    """Get all technical indicators for a symbol"""
    try:
        symbol = symbol.upper()
        
        cache_key = f"all_indicators:{symbol}"
        cached_data = redis_client.get(cache_key)
        if cached_data:
            logger.debug(f"Returning cached indicators for {symbol}")
            return cached_data
        
        # Fetch price data
        prices = db.query(OHLCV).filter(
            OHLCV.symbol == symbol
        ).order_by(OHLCV.timestamp.asc()).limit(500).all()
        
        if not prices:
            raise HTTPException(status_code=404, detail=f"No price data found for {symbol}")
        
        # Convert to format expected by indicator calculator
        ohlcv_data = [{
            'close': p.close,
            'timestamp': p.timestamp
        } for p in prices]
        
        # Calculate all indicators
        indicators = technical_indicators.calculate_all_indicators(ohlcv_data)
        timestamps = [p.timestamp.isoformat() for p in prices]
        
        # Format for response
        formatted_indicators = technical_indicators.format_indicator_data(indicators, timestamps)
        
        # Generate signals
        close_prices = [p.close for p in prices]
        signals = technical_indicators.generate_signals(close_prices, indicators)
        
        result = {
            'symbol': symbol,
            'indicators': formatted_indicators,
            'signals': [{'timestamp': ts, 'signal': sig} for ts, sig in zip(timestamps, signals)]
        }
        
        # Cache for 5 minutes
        redis_client.set(cache_key, result, ttl=300)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching all indicators for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/indicators/{symbol}/rsi")
async def get_rsi(
    symbol: str,
    period: int = Query(14, ge=5, le=50, description="RSI period"),
    db: Session = Depends(get_async_db)
):
    """Get RSI indicator for a symbol"""
    return await get_indicators(symbol, "RSI", period, db)


@router.get("/indicators/{symbol}/macd")
async def get_macd(
    symbol: str,
    fast_period: int = Query(12, ge=5, le=50),
    slow_period: int = Query(26, ge=10, le=100),
    signal_period: int = Query(9, ge=5, le=20),
    db: Session = Depends(get_async_db)
):
    """Get MACD indicator for a symbol"""
    try:
        symbol = symbol.upper()
        
        cache_key = f"macd:{symbol}:{fast_period}:{slow_period}:{signal_period}"
        cached_data = redis_client.get(cache_key)
        if cached_data:
            return cached_data
        
        # Fetch price data
        prices = db.query(OHLCV).filter(
            OHLCV.symbol == symbol
        ).order_by(OHLCV.timestamp.asc()).limit(slow_period + signal_period + 10).all()
        
        if not prices:
            raise HTTPException(status_code=404, detail=f"No price data found for {symbol}")
        
        close_prices = [p.close for p in prices]
        timestamps = [p.timestamp.isoformat() for p in prices]
        
        # Calculate MACD
        macd_data = technical_indicators.calculate_macd(close_prices, fast_period, slow_period, signal_period)
        
        result = {
            'symbol': symbol,
            'parameters': {
                'fast_period': fast_period,
                'slow_period': slow_period,
                'signal_period': signal_period
            },
            'data': [{
                'timestamp': ts,
                'macd': macd_data['macd'][i],
                'signal': macd_data['signal'][i],
                'histogram': macd_data['histogram'][i]
            } for i, ts in enumerate(timestamps) if i < len(macd_data['macd'])]
        }
        
        # Cache for 5 minutes
        redis_client.set(cache_key, result, ttl=300)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching MACD for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/indicators/{symbol}/sma")
async def get_sma(
    symbol: str,
    period: int = Query(20, ge=5, le=200),
    db: Session = Depends(get_async_db)
):
    """Get SMA indicator for a symbol"""
    return await get_indicators(symbol, "SMA", period, db)


@router.get("/indicators/{symbol}/ema")
async def get_ema(
    symbol: str,
    period: int = Query(20, ge=5, le=200),
    db: Session = Depends(get_async_db)
):
    """Get EMA indicator for a symbol"""
    return await get_indicators(symbol, "EMA", period, db)


@router.get("/indicators/{symbol}/bollinger")
async def get_bollinger_bands(
    symbol: str,
    period: int = Query(20, ge=5, le=100),
    std_dev: float = Query(2.0, ge=0.5, le=4.0),
    db: Session = Depends(get_async_db)
):
    """Get Bollinger Bands for a symbol"""
    try:
        symbol = symbol.upper()
        
        cache_key = f"bb:{symbol}:{period}:{std_dev}"
        cached_data = redis_client.get(cache_key)
        if cached_data:
            return cached_data
        
        # Fetch price data
        prices = db.query(OHLCV).filter(
            OHLCV.symbol == symbol
        ).order_by(OHLCV.timestamp.asc()).limit(period + 10).all()
        
        if not prices:
            raise HTTPException(status_code=404, detail=f"No price data found for {symbol}")
        
        close_prices = [p.close for p in prices]
        timestamps = [p.timestamp.isoformat() for p in prices]
        
        # Calculate Bollinger Bands
        bb_data = technical_indicators.calculate_bollinger_bands(close_prices, period, std_dev)
        
        result = {
            'symbol': symbol,
            'parameters': {
                'period': period,
                'std_dev': std_dev
            },
            'data': [{
                'timestamp': ts,
                'upper': bb_data['upper'][i],
                'middle': bb_data['middle'][i],
                'lower': bb_data['lower'][i],
                'close_price': close_prices[i]
            } for i, ts in enumerate(timestamps) if i < len(bb_data['upper'])]
        }
        
        # Cache for 5 minutes
        redis_client.set(cache_key, result, ttl=300)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching Bollinger Bands for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
