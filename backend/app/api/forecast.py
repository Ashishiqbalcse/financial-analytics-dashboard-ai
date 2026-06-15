from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.core.database import get_async_db
from app.services.forecasting import forecasting_service
from app.models.schemas import ForecastResponse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/forecast/train/{symbol}")
async def train_forecast_model(
    symbol: str,
    periods: int = Query(7, ge=1, le=30, description="Number of days to forecast"),
    db: Session = Depends(get_async_db)
):
    """Train a Prophet forecasting model for a symbol"""
    try:
        symbol = symbol.upper()
        
        logger.info(f"Training forecast model for {symbol} with {periods} periods")
        
        # Train the model
        model_data = forecasting_service.train_model(symbol, periods)
        
        # Save forecast to database
        forecasting_service.save_forecast_to_db(db, symbol, model_data)
        
        return {
            "status": "success",
            "message": f"Model trained successfully for {symbol}",
            "symbol": symbol,
            "periods": periods,
            "trained_at": model_data['trained_at'],
            "metrics": model_data['metrics'],
            "forecast_summary": {
                "current_price": model_data['forecast']['current_price'],
                "forecast_start": model_data['forecast']['forecast_start'],
                "forecast_end": model_data['forecast']['forecast_end'],
                "prediction_count": len(model_data['forecast']['predictions'])
            }
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error training model for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/forecast/{symbol}")
async def get_forecast(
    symbol: str,
    periods: int = Query(7, ge=1, le=30, description="Number of days to forecast"),
    force_refresh: bool = Query(False, description="Force model retraining")
):
    """Get price forecast for a symbol"""
    try:
        symbol = symbol.upper()
        
        logger.info(f"Getting forecast for {symbol} with {periods} periods")
        
        # Force refresh if requested
        if force_refresh:
            # Clear cache
            from app.core.redis_client import redis_client
            cache_key = f"forecast:{symbol}:{periods}"
            redis_client.delete(cache_key)
            model_cache_key = f"model:{symbol}"
            redis_client.delete(model_cache_key)
        
        # Get forecast
        forecast_data = forecasting_service.get_forecast(symbol, periods)
        
        return {
            "status": "success",
            "symbol": symbol,
            "generated_at": forecast_data['generated_at'],
            "model_type": forecast_data['model_type'],
            "periods": periods,
            "metrics": forecast_data['metrics'],
            "forecast": forecast_data['forecast']
        }
        
    except Exception as e:
        logger.error(f"Error getting forecast for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/forecast/history/{symbol}")
async def get_forecast_history(
    symbol: str,
    limit: int = Query(10, ge=1, le=100, description="Number of historical forecasts to return"),
    db: Session = Depends(get_async_db)
):
    """Get historical forecast data for a symbol"""
    try:
        symbol = symbol.upper()
        
        logger.info(f"Fetching forecast history for {symbol}")
        
        history = forecasting_service.get_forecast_history(db, symbol, limit)
        
        return {
            "status": "success",
            "symbol": symbol,
            "count": len(history),
            "history": history
        }
        
    except Exception as e:
        logger.error(f"Error fetching forecast history for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/forecast/metrics/{symbol}")
async def get_forecast_metrics(
    symbol: str,
    db: Session = Depends(get_async_db)
):
    """Get model performance metrics for a symbol"""
    try:
        symbol = symbol.upper()
        
        logger.info(f"Fetching model metrics for {symbol}")
        
        metrics = forecasting_service.get_model_metrics(symbol)
        
        if not metrics or metrics.get('mae') is None:
            return {
                "status": "warning",
                "message": "No metrics available. Model may not be trained yet.",
                "symbol": symbol,
                "metrics": None
            }
        
        return {
            "status": "success",
            "symbol": symbol,
            "metrics": metrics,
            "interpretation": {
                "mae": f"Mean Absolute Error: ${metrics['mae']:.2f}",
                "rmse": f"Root Mean Square Error: ${metrics['rmse']:.2f}",
                "mape": f"Mean Absolute Percentage Error: {metrics['mape']:.2f}%",
                "coverage": f"Confidence Interval Coverage: {metrics['coverage']:.1f}%"
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching metrics for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/forecast/status")
async def get_forecast_status():
    """Get overall forecasting system status"""
    try:
        from app.core.redis_client import redis_client
        
        # Check Redis connection
        redis_status = redis_client.ping()
        
        # Get model cache directory status
        from pathlib import Path
        model_cache_dir = Path("backend/data/models")
        model_files = list(model_cache_dir.glob("*.pkl")) if model_cache_dir.exists() else []
        
        return {
            "status": "operational" if redis_status else "degraded",
            "redis_connected": redis_status,
            "cached_models": len(model_files),
            "model_files": [f.name for f in model_files],
            "model_cache_dir": str(model_cache_dir),
            "supported_models": ["prophet"],
            "max_forecast_periods": 30,
            "default_forecast_periods": 7
        }
        
    except Exception as e:
        logger.error(f"Error getting forecast status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/forecast/cache/{symbol}")
async def clear_forecast_cache(symbol: str):
    """Clear cached forecast data for a symbol"""
    try:
        symbol = symbol.upper()
        
        from app.core.redis_client import redis_client
        
        # Clear various cache keys
        cache_keys = [
            f"forecast:{symbol}:7",
            f"forecast:{symbol}:14",
            f"forecast:{symbol}:30",
            f"model:{symbol}"
        ]
        
        cleared_count = 0
        for key in cache_keys:
            if redis_client.exists(key):
                redis_client.delete(key)
                cleared_count += 1
        
        logger.info(f"Cleared {cleared_count} cache entries for {symbol}")
        
        return {
            "status": "success",
            "symbol": symbol,
            "cleared_entries": cleared_count,
            "message": f"Cache cleared for {symbol}"
        }
        
    except Exception as e:
        logger.error(f"Error clearing cache for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
