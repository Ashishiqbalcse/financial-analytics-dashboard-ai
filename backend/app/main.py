
from contextlib import asynccontextmanager
import logging
from app.api import alerts
from fastapi import FastAPI
from app.api import ai_assistant
from fastapi.middleware.cors import CORSMiddleware
from app.api import portfolio_analytics
from app.core.config import settings
from app.core.database import Base, engine
from app.core.redis_client import redis_client
from app.scheduler.job_scheduler import scheduler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Financial Analytics Dashboard...")

    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized")
    except Exception as e:
        logger.error(f"Database error: {e}")

    try:
        redis_ok = await redis_client.ping()
        if redis_ok:
            logger.info("Redis connected")
        else:
            logger.warning("Redis unavailable")
    except Exception as e:
        logger.error(f"Redis error: {e}")

    try:
        scheduler.start()
        logger.info("Scheduler started")
    except Exception as e:
        logger.error(f"Scheduler error: {e}")

    yield

    logger.info("Shutting down application")

    try:
        scheduler.stop()
    except Exception:
        pass

    try:
        redis_client.close()
    except Exception:
        pass


app = FastAPI(
    title="Financial Analytics Dashboard",
    description="Real-Time Financial Analytics Dashboard with Predictive AI",
    version="1.0.0",
    lifespan=lifespan,
)

# ---------------------------------------------------
# CORS CONFIGURATION
# ---------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://localhost:3003",
        "http://localhost:3004",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3002",
        "http://127.0.0.1:3003",
        "http://127.0.0.1:3004",

        # Vercel Production
        "https://financial-analytics-dashboard-ai.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------
# ROUTERS
# ---------------------------------------------------

from app.api import (
    prices,
    indicators,
    websocket,
    forecast,
    portfolio
)

app.include_router(
    prices.router,
    prefix=settings.API_V1_STR,
    tags=["Prices"],
)

app.include_router(
    indicators.router,
    prefix=settings.API_V1_STR,
    tags=["Indicators"],
)

app.include_router(
    forecast.router,
    prefix=settings.API_V1_STR,
    tags=["Forecast"],
)

app.include_router(
    portfolio.router,
    prefix=settings.API_V1_STR,
    tags=["portfolio"]
)

app.include_router(
    portfolio_analytics.router,
    prefix=settings.API_V1_STR,
    tags=["portfolio-analytics"]
)

app.include_router(
    alerts.router,
    prefix=settings.API_V1_STR,
    tags=["alerts"]
)

app.include_router(
    ai_assistant.router,
    prefix=settings.API_V1_STR,
    tags=["AI Assistant"]
)

app.include_router(
    websocket.router,
    tags=["WebSocket"],
)

# ---------------------------------------------------
# ROOT
# ---------------------------------------------------

@app.get("/")
async def root():
    return {
        "message": "Financial Analytics Dashboard API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


# ---------------------------------------------------
# HEALTH CHECK
# ---------------------------------------------------

@app.get("/health")
async def health_check():
    try:
        redis_ok = await redis_client.ping()
        redis_status = (
            "connected"
            if redis_ok
            else "disconnected"
        )
    except Exception:
        redis_status = "error"

    scheduler_running = (
        scheduler.scheduler.running
        if scheduler.scheduler
        else False
    )

    return {
        "status": "healthy",
        "database": "connected",
        "redis": redis_status,
        "scheduler": (
            "running"
            if scheduler_running
            else "stopped"
        ),
        "tracked_symbols":
            scheduler.get_tracked_symbols(),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=7777,
        reload=True,
    )
