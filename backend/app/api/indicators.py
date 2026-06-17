from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
import math
import logging

from app.core.database import get_db
from app.models.market_data import OHLCV
from app.services.technical_indicators import technical_indicators

logger = logging.getLogger(__name__)

router = APIRouter()


def safe_float(value):
    """
    Convert NaN/Infinity to None
    so FastAPI can serialize JSON safely.
    """
    try:
        if value is None:
            return None

        if isinstance(value, float):
            if math.isnan(value) or math.isinf(value):
                return None

        return float(value)

    except Exception:
        return None


def get_price_data(
    db: Session,
    symbol: str,
    limit: int = 500
):
    return (
        db.query(OHLCV)
        .filter(
            OHLCV.symbol == symbol.upper()
        )
        .order_by(
            OHLCV.timestamp.asc()
        )
        .limit(limit)
        .all()
    )


@router.get("/indicators/{symbol}")
async def get_indicators(
    symbol: str,
    indicator_type: Optional[str] = Query(
        default="RSI",
        description="RSI, SMA, EMA, MACD, BB"
    ),
    period: int = Query(
        default=20,
        ge=5,
        le=200
    ),
    db: Session = Depends(get_db)
):
    try:

        symbol = symbol.upper()
        indicator_type = indicator_type.upper()

        prices = get_price_data(
            db,
            symbol,
            500
        )

        if not prices:
            raise HTTPException(
                status_code=404,
                detail=f"No price data found for {symbol}"
            )

        close_prices = [
            float(row.close)
            for row in prices
        ]

        timestamps = [
            row.timestamp.isoformat()
            for row in prices
        ]

        data = []

        # =========================
        # RSI
        # =========================

        if indicator_type == "RSI":

            values = technical_indicators.calculate_rsi(
                close_prices,
                period
            )

            data = [
                {
                    "timestamp": ts,
                    "value": safe_float(val)
                }
                for ts, val in zip(
                    timestamps,
                    values
                )
            ]

        # =========================
        # SMA
        # =========================

        elif indicator_type == "SMA":

            values = technical_indicators.calculate_sma(
                close_prices,
                period
            )

            data = [
                {
                    "timestamp": ts,
                    "value": safe_float(val)
                }
                for ts, val in zip(
                    timestamps,
                    values
                )
            ]

        # =========================
        # EMA
        # =========================

        elif indicator_type == "EMA":

            values = technical_indicators.calculate_ema(
                close_prices,
                period
            )

            data = [
                {
                    "timestamp": ts,
                    "value": safe_float(val)
                }
                for ts, val in zip(
                    timestamps,
                    values
                )
            ]

        # =========================
        # MACD
        # =========================

        elif indicator_type == "MACD":

            macd = technical_indicators.calculate_macd(
                close_prices
            )

            for i in range(
                len(macd["macd"])
            ):
                data.append(
                    {
                        "timestamp": timestamps[i],
                        "macd": safe_float(
                            macd["macd"][i]
                        ),
                        "signal": safe_float(
                            macd["signal"][i]
                        ),
                        "histogram": safe_float(
                            macd["histogram"][i]
                        )
                    }
                )

        # =========================
        # Bollinger Bands
        # =========================

        elif indicator_type in ["BB", "BOLLINGER"]:

            bb = technical_indicators.calculate_bollinger_bands(
                close_prices,
                period
            )

            for i in range(
                len(bb["upper"])
            ):
                data.append(
                    {
                        "timestamp": timestamps[i],
                        "upper": safe_float(
                            bb["upper"][i]
                        ),
                        "middle": safe_float(
                            bb["middle"][i]
                        ),
                        "lower": safe_float(
                            bb["lower"][i]
                        )
                    }
                )

        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported indicator: {indicator_type}"
            )

        return {
            "symbol": symbol,
            "indicator": indicator_type,
            "period": period,
            "records": len(data),
            "data": data
        }

    except HTTPException:
        raise

    except Exception as e:

        logger.exception(
            f"Indicator calculation failed for {symbol}"
        )

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/indicators/{symbol}/rsi")
async def get_rsi(
    symbol: str,
    period: int = 14,
    db: Session = Depends(get_db)
):
    return await get_indicators(
        symbol=symbol,
        indicator_type="RSI",
        period=period,
        db=db
    )


@router.get("/indicators/{symbol}/sma")
async def get_sma(
    symbol: str,
    period: int = 20,
    db: Session = Depends(get_db)
):
    return await get_indicators(
        symbol=symbol,
        indicator_type="SMA",
        period=period,
        db=db
    )


@router.get("/indicators/{symbol}/ema")
async def get_ema(
    symbol: str,
    period: int = 20,
    db: Session = Depends(get_db)
):
    return await get_indicators(
        symbol=symbol,
        indicator_type="EMA",
        period=period,
        db=db
    )


@router.get("/indicators/{symbol}/macd")
async def get_macd(
    symbol: str,
    db: Session = Depends(get_db)
):
    return await get_indicators(
        symbol=symbol,
        indicator_type="MACD",
        period=20,
        db=db
    )


@router.get("/indicators/{symbol}/bollinger")
async def get_bollinger(
    symbol: str,
    period: int = 20,
    db: Session = Depends(get_db)
):
    return await get_indicators(
        symbol=symbol,
        indicator_type="BB",
        period=period,
        db=db
    )