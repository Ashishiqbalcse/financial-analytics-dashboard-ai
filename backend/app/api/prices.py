from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.models.market_data import OHLCV
from app.models.schemas import OHLCVResponse, MarketDataResponse
from app.services.market_data import market_data_service
from app.core.redis_client import redis_client

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


# =====================================================
# STATIC ROUTES FIRST
# =====================================================

@router.get("/prices/symbols")
async def get_available_symbols(
    db: Session = Depends(get_db)
):
    """Get all available symbols"""

    try:
        symbols = (
            db.query(OHLCV.symbol)
            .distinct()
            .order_by(OHLCV.symbol)
            .all()
        )

        return [row[0] for row in symbols]

    except Exception as e:
        logger.error(f"Error fetching symbols: {e}")

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/prices/compare")
async def compare_symbols(
    symbols: List[str] = Query(...),
    db: Session = Depends(get_db),
):
    """Compare multiple symbols"""

    try:
        results = {}

        for symbol in symbols:

            latest = (
                db.query(OHLCV)
                .filter(
                    OHLCV.symbol == symbol.upper()
                )
                .order_by(
                    OHLCV.timestamp.desc()
                )
                .first()
            )

            if latest:
                results[symbol.upper()] = {
                    "current_price": latest.close,
                    "volume": latest.volume,
                    "timestamp": latest.timestamp,
                }

        return results

    except Exception as e:
        logger.error(f"Error comparing symbols: {e}")

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# =====================================================
# DYNAMIC ROUTES AFTER STATIC ROUTES
# =====================================================

@router.get("/prices/{symbol}", response_model=List[OHLCVResponse])
async def get_prices(
    symbol: str,
    limit: int = Query(100, ge=1, le=1000),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
):
    """Get price data for a symbol"""

    try:
        query = db.query(OHLCV).filter(
            OHLCV.symbol == symbol.upper()
        )

        if start_date:
            query = query.filter(
                OHLCV.timestamp >= start_date
            )

        if end_date:
            query = query.filter(
                OHLCV.timestamp <= end_date
            )

        prices = (
            query.order_by(
                OHLCV.timestamp.desc()
            )
            .limit(limit)
            .all()
        )

        prices.reverse()

        return prices

    except Exception as e:
        logger.error(f"Error fetching prices: {e}")

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get(
    "/prices/{symbol}/latest",
    response_model=MarketDataResponse
)
async def get_latest_price(symbol: str):
    """Get latest market price"""

    try:
        cache_key = f"latest_price:{symbol}"

        cached = redis_client.get(cache_key)
        if cached:
            return cached

        data = await market_data_service.get_realtime_price(
            symbol.upper()
        )

        if not data:
            raise HTTPException(
                status_code=404,
                detail=f"No data found for {symbol}"
            )

        redis_client.set(
            cache_key,
            data,
            ttl=30
        )

        return data

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Error fetching latest price: {e}")

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/prices/{symbol}/historical")
async def get_historical_prices(
    symbol: str,
    period: str = Query("1mo"),
    interval: str = Query("1d"),
):
    """Get historical data from Yahoo Finance"""

    try:
        data = await market_data_service.get_historical_data(
            symbol.upper(),
            period,
            interval
        )

        if not data:
            raise HTTPException(
                status_code=404,
                detail=f"No historical data found for {symbol}"
            )

        return data

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Error fetching historical prices: {e}")

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/prices/{symbol}/range")
async def get_prices_by_range(
    symbol: str,
    start_date: datetime,
    end_date: datetime,
    db: Session = Depends(get_db),
):
    """Get prices within date range"""

    try:
        prices = (
            db.query(OHLCV)
            .filter(
                OHLCV.symbol == symbol.upper(),
                OHLCV.timestamp >= start_date,
                OHLCV.timestamp <= end_date,
            )
            .order_by(
                OHLCV.timestamp.asc()
            )
            .all()
        )

        return prices

    except Exception as e:
        logger.error(f"Error fetching range prices: {e}")

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )