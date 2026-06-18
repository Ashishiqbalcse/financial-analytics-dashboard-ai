import yfinance as yf
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.foreignexchange import ForeignExchange
import pandas as pd
import asyncio
from typing import List, Dict, Optional
from datetime import datetime
from app.core.config import settings
from app.core.redis_client import redis_client
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MarketDataService:
    """Service for fetching market data from multiple sources"""

    def __init__(self):
        self.alpha_vantage_api_key = settings.ALPHA_VANTAGE_API_KEY
        self.cache_ttl = 60

    async def get_yahoo_data(
        self,
        symbol: str,
        period: str = "1mo",
        interval: str = "1d"
    ) -> Optional[pd.DataFrame]:
        """Fetch data from Yahoo Finance"""

        try:
            ticker = yf.Ticker(symbol)

            data = ticker.history(
                period=period,
                interval=interval
            )

            if data.empty:
                logger.warning(
                    f"No data returned from Yahoo Finance for {symbol}"
                )
                return None

            data = data.reset_index()

            # Standardize timestamp column
            if "Date" in data.columns:
                data = data.rename(
                    columns={"Date": "timestamp"}
                )

            if "Datetime" in data.columns:
                data = data.rename(
                    columns={"Datetime": "timestamp"}
                )

            # Lowercase all columns
            data.columns = [
                str(col).lower()
                for col in data.columns
            ]

            if "adj close" in data.columns:
                data = data.rename(
                    columns={
                        "adj close": "adj_close"
                    }
                )

            logger.info(
                f"Yahoo returned {len(data)} rows for {symbol}"
            )

            return data

        except Exception as e:
            logger.error(
                f"Error fetching Yahoo data for {symbol}: {e}"
            )
            return None

    async def get_alpha_vantage_data(
        self,
        symbol: str,
        outputsize: str = "compact"
    ) -> Optional[pd.DataFrame]:
        """Fetch data from Alpha Vantage"""

        if not self.alpha_vantage_api_key:
            logger.warning(
                "Alpha Vantage API key not configured"
            )
            return None

        try:
            ts = TimeSeries(
                key=self.alpha_vantage_api_key,
                output_format="pandas"
            )

            data, meta_data = ts.get_intraday(
                symbol=symbol,
                interval="1min",
                outputsize=outputsize
            )

            if data is None or data.empty:
                logger.warning(
                    f"No data returned from Alpha Vantage for {symbol}"
                )
                return None

            data.columns = [
                col.split(". ")[1].lower()
                for col in data.columns
            ]

            data = data.reset_index()

            if "date" in data.columns:
                data = data.rename(
                    columns={"date": "timestamp"}
                )

            return data

        except Exception as e:
            logger.error(
                f"Error fetching Alpha Vantage data for {symbol}: {e}"
            )
            return None

    async def get_realtime_price(
        self,
        symbol: str
    ) -> Optional[Dict]:
        """Get current real-time price"""

        cache_key = f"price:{symbol}"

        cached_data = redis_client.get(cache_key)
        if cached_data:
            return cached_data

        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            if not info:
                return None

            price_data = {
                "symbol": symbol,
                "current_price": info.get("currentPrice")
                or info.get("regularMarketPrice"),
                "change": info.get("regularMarketChange"),
                "change_percent": info.get(
                    "regularMarketChangePercent"
                ),
                "volume": info.get(
                    "regularMarketVolume"
                ),
                "high_52w": info.get(
                    "fiftyTwoWeekHigh"
                ),
                "low_52w": info.get(
                    "fiftyTwoWeekLow"
                ),
                "market_cap": info.get(
                    "marketCap"
                ),
                "timestamp": datetime.utcnow().isoformat()
            }

            redis_client.set(
                cache_key,
                price_data,
                ttl=self.cache_ttl
            )

            return price_data

        except Exception as e:
            logger.error(
                f"Error fetching realtime price for {symbol}: {e}"
            )
            return None

    async def get_historical_data(
        self,
        symbol: str,
        period: str = "1mo",
        interval: str = "1d"
    ) -> Optional[List[Dict]]:
        """Get historical OHLCV data"""

        cache_key = f"hist:{symbol}:{period}:{interval}"

        cached_data = redis_client.get(cache_key)
        if cached_data:
            return cached_data

        try:
            data = await self.get_yahoo_data(
                symbol,
                period,
                interval
            )

            # Fallback to Alpha Vantage
            if data is None or data.empty:
                logger.warning(
                    f"Yahoo failed for {symbol}, trying Alpha Vantage..."
                )

                data = await self.get_alpha_vantage_data(symbol)

            if data is None or data.empty:
                logger.error(
                    f"All providers failed for {symbol}"
                )
                return None

            records = []

            for _, row in data.iterrows():

                timestamp = row["timestamp"]

                if hasattr(timestamp, "isoformat"):
                    timestamp = timestamp.isoformat()
                else:
                    timestamp = str(timestamp)

                records.append({
                    "symbol": symbol,
                    "timestamp": timestamp,
                    "open": float(row["open"]),
                    "high": float(row["high"]),
                    "low": float(row["low"]),
                    "close": float(row["close"]),
                    "volume": float(row["volume"])
                })

            redis_client.set(
                cache_key,
                records,
                ttl=300
            )

            logger.info(
                f"Generated {len(records)} records for {symbol}"
            )

            return records

        except Exception as e:
            logger.error(
                f"Error fetching historical data for {symbol}: {e}"
            )
            return None

    async def get_multiple_prices(
        self,
        symbols: List[str]
    ) -> Dict[str, Optional[Dict]]:
        """Get prices for multiple symbols"""

        results = {}

        tasks = [
            self.get_realtime_price(symbol)
            for symbol in symbols
        ]

        prices = await asyncio.gather(*tasks)

        for symbol, price in zip(symbols, prices):
            results[symbol] = price

        return results

    def format_ohlcv_for_db(
        self,
        data: Dict
    ) -> Dict:
        """Format data for DB insert"""

        return {
            "symbol": data["symbol"],
            "timestamp": datetime.fromisoformat(
                data["timestamp"].replace(
                    "Z",
                    "+00:00"
                )
            ),
            "open": data["open"],
            "high": data["high"],
            "low": data["low"],
            "close": data["close"],
            "volume": data["volume"]
        }


# Global service instance
market_data_service = MarketDataService()