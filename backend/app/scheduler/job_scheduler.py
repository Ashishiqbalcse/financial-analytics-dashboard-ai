import asyncio
import logging
from datetime import datetime
from typing import List

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.market_data import Alert
from app.services.data_ingestion import DataIngestionService
from app.services.market_data import market_data_service
from app.services.forecasting import forecasting_service
from app.websocket.connection_manager import manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataIngestionScheduler:
    """Scheduler for market ingestion, forecasting and alerts"""

    def __init__(self):
        self.scheduler = AsyncIOScheduler(
            timezone=settings.SCHEDULER_TIMEZONE
        )

        self.symbols_to_track = [
            "AAPL",
            "TSLA",
            "GOOGL",
            "MSFT",
            "AMZN",
            "META",
            "NVDA",
            "JPM",
        ]

    def start(self):
        """Start scheduler"""

        try:
            self.scheduler.add_job(
                self.ingest_all_symbols,
                trigger=IntervalTrigger(minutes=30),
                id="ingest_all_symbols",
                replace_existing=True,
            )

            self.scheduler.add_job(
                self.ingest_historical_data,
                trigger=IntervalTrigger(hours=1),
                id="ingest_historical",
                replace_existing=True,
            )

            self.scheduler.add_job(
                self.cleanup_old_data,
                trigger=IntervalTrigger(hours=24),
                id="cleanup_data",
                replace_existing=True,
            )

            self.scheduler.add_job(
                self.retrain_forecast_models,
                trigger=IntervalTrigger(hours=6),
                id="retrain_models",
                replace_existing=True,
            )

            self.scheduler.start()

            asyncio.create_task(
                self.ingest_historical_data()
            )

            logger.info(
                "Scheduler started successfully"
            )

        except Exception as e:
            logger.error(
                f"Scheduler startup failed: {e}"
            )

    def stop(self):
        """Stop scheduler"""

        try:
            self.scheduler.shutdown(wait=False)
            logger.info("Scheduler stopped")

        except Exception as e:
            logger.error(
                f"Scheduler shutdown failed: {e}"
            )

    async def ingest_all_symbols(self):
        """Realtime market ingestion"""

        db = SessionLocal()

        try:
            service = DataIngestionService(db)

            results = await service.ingest_multiple_symbols(
                self.symbols_to_track
            )

            logger.info(
                f"Ingestion completed | "
                f"Success={len(results['success'])} "
                f"Failed={len(results['failed'])}"
            )

            await self.check_alerts()

            for symbol in results["success"]:

                try:
                    price_data = (
                        await market_data_service
                        .get_realtime_price(symbol)
                    )

                    if price_data:
                        await manager.broadcast_price(
                            symbol,
                            price_data
                        )

                except Exception as e:
                    logger.error(
                        f"Broadcast failed for "
                        f"{symbol}: {e}"
                    )

        except Exception as e:
            logger.error(
                f"Realtime ingestion failed: {e}"
            )

        finally:
            db.close()

    async def ingest_historical_data(self):
        """Historical ingestion"""

        db = SessionLocal()

        try:
            service = DataIngestionService(db)

            for symbol in self.symbols_to_track:

                try:
                    records = (
                        await service
                        .ingest_historical_data(
                            symbol,
                            period="1mo"
                        )
                    )

                    logger.info(
                        f"{symbol}: "
                        f"{records} rows added"
                    )

                except Exception as e:
                    logger.error(
                        f"Historical ingestion "
                        f"failed for {symbol}: {e}"
                    )

        except Exception as e:
            logger.error(
                f"Historical job failed: {e}"
            )

        finally:
            db.close()

    def cleanup_old_data(self):
        """Cleanup old OHLCV records"""

        db = SessionLocal()

        try:
            service = DataIngestionService(db)

            for symbol in self.symbols_to_track:

                deleted = service.delete_old_data(
                    symbol,
                    days_to_keep=30
                )

                logger.info(
                    f"{symbol}: "
                    f"{deleted} records deleted"
                )

        except Exception as e:
            logger.error(
                f"Cleanup failed: {e}"
            )

        finally:
            db.close()

    async def retrain_forecast_models(self):
        """Retrain forecasting models"""

        try:
            logger.info(
                "Starting model retraining"
            )

            for symbol in self.symbols_to_track:

                try:
                    model_data = (
                        forecasting_service
                        .train_model(
                            symbol,
                            periods=7
                        )
                    )

                    await manager.broadcast_price(
                        symbol,
                        {
                            "type": "model_update",
                            "symbol": symbol,
                            "metrics": model_data.get(
                                "metrics",
                                {}
                            ),
                            "timestamp":
                                datetime.utcnow()
                                .isoformat()
                        }
                    )

                    logger.info(
                        f"Model retrained: {symbol}"
                    )

                except Exception as e:
                    logger.error(
                        f"Retraining failed "
                        f"for {symbol}: {e}"
                    )

        except Exception as e:
            logger.error(
                f"Retraining job failed: {e}"
            )

    async def check_alerts(self):
        """Check alert conditions"""

        db = SessionLocal()

        try:
            alerts = (
                db.query(Alert)
                .filter(
                    Alert.is_active == True,
                    Alert.triggered == False
                )
                .all()
            )

            for alert in alerts:

                try:
                    price_data = (
                        await market_data_service
                        .get_realtime_price(
                            alert.symbol
                        )
                    )

                    if not price_data:
                        continue

                    current_price = (
                        price_data.get(
                            "current_price"
                        )
                    )

                    if current_price is None:
                        continue

                    triggered = False

                    if (
                        alert.condition == "above"
                        and current_price >= alert.target_price
                    ):
                        triggered = True

                    elif (
                        alert.condition == "below"
                        and current_price <= alert.target_price
                    ):
                        triggered = True

                    if triggered:

                        alert.triggered = True
                        alert.is_active = False

                        if hasattr(
                            alert,
                            "triggered_at"
                        ):
                            alert.triggered_at = (
                                datetime.utcnow()
                            )

                        db.commit()

                        logger.info(
                            f"ALERT TRIGGERED | "
                            f"{alert.symbol}"
                        )

                        await manager.broadcast_alert(
                            "system",
                            {
                                "symbol": alert.symbol,
                                "condition": alert.condition,
                                "target_price": alert.target_price,
                                "current_price": current_price,
                            }
                        )

                except Exception as e:
                    logger.error(
                        f"Alert processing error: {e}"
                    )

        except Exception as e:
            logger.error(
                f"Alert scan failed: {e}"
            )

        finally:
            db.close()

    def add_symbol(self, symbol: str):
        symbol = symbol.upper()

        if symbol not in self.symbols_to_track:
            self.symbols_to_track.append(symbol)

    def remove_symbol(self, symbol: str):
        symbol = symbol.upper()

        if symbol in self.symbols_to_track:
            self.symbols_to_track.remove(symbol)

    def get_tracked_symbols(self) -> List[str]:
        return self.symbols_to_track.copy()

    def set_symbols(self, symbols: List[str]):
        self.symbols_to_track = [
            s.upper()
            for s in symbols
        ]


scheduler = DataIngestionScheduler()