from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.database import engine, Base, async_engine
from app.core.redis_client import redis_client
from app.scheduler.job_scheduler import scheduler
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle event handler"""
    # Startup
    logger.info("Starting up Financial Analytics Dashboard...")
    
    # Create database tables
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
    
    # Check Redis connection
    try:
        redis_status = await redis_client.ping()
        if redis_status:
            logger.info("Redis connection established")
        else:
            logger.warning("Redis connection failed")
    except Exception as e:
        logger.error(f"Redis connection error: {e}")
    
    # Start data ingestion scheduler
    try:
        scheduler.start()
        logger.info("Data ingestion scheduler started")
    except Exception as e:
        logger.error(f"Error starting scheduler: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Financial Analytics Dashboard...")
    scheduler.stop()
    redis_client.close()


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Real-Time Financial Analytics Dashboard with Predictive AI",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        redis_status = await redis_client.ping()
        redis_status_str = "connected" if redis_status else "disconnected"
    except Exception:
        redis_status_str = "error"
    
    scheduler_running = scheduler.scheduler.running if scheduler.scheduler else False
    
    return {
        "status": "healthy",
        "database": "connected",
        "redis": redis_status_str,
        "scheduler": "running" if scheduler_running else "stopped",
        "tracked_symbols": scheduler.get_tracked_symbols()
    }


# Include routers
from app.api import prices, indicators, websocket, forecast
# from app.api import predictions, portfolio, alerts, nlp
app.include_router(prices.router, prefix=settings.API_V1_STR, tags=["prices"])
app.include_router(indicators.router, prefix=settings.API_V1_STR, tags=["indicators"])
app.include_router(websocket.router, tags=["websocket"])
app.include_router(forecast.router, prefix=settings.API_V1_STR, tags=["forecast"])
# app.include_router(predictions.router, prefix=settings.API_V1_STR, tags=["predictions"])
# app.include_router(portfolio.router, prefix=settings.API_V1_STR, tags=["portfolio"])
# app.include_router(alerts.router, prefix=settings.API_V1_STR, tags=["alerts"])
# app.include_router(nlp.router, prefix=settings.API_V1_STR, tags=["nlp"])


@app.get("/")
async def root():
    return {
        "message": "Financial Analytics Dashboard API",
        "version": "1.0.0",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
