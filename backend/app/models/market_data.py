from sqlalchemy import Column, Integer, String, Float, DateTime, Index, Boolean
from sqlalchemy.sql import func
from app.core.database import Base


class OHLCV(Base):
    """OHLCV (Open, High, Low, Close, Volume) market data"""

    __tablename__ = "ohlcv"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), index=True, nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)

    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)

    volume = Column(Float, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    __table_args__ = (
        Index("idx_symbol_timestamp", "symbol", "timestamp"),
        Index("idx_timestamp", "timestamp"),
    )


class TechnicalIndicator(Base):
    """Pre-calculated technical indicators"""

    __tablename__ = "technical_indicators"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), index=True, nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)

    indicator_type = Column(
        String(20),
        nullable=False
    )  # RSI, MACD, SMA, EMA, BB

    value = Column(Float, nullable=False)

    # Renamed from 'metadata' because SQLAlchemy reserves that name
    indicator_metadata = Column(
        String(500),
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    __table_args__ = (
        Index(
            "idx_symbol_indicator_timestamp",
            "symbol",
            "indicator_type",
            "timestamp"
        ),
    )


class Prediction(Base):
    """ML model predictions"""

    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), index=True, nullable=False)

    prediction_date = Column(
        DateTime(timezone=True),
        nullable=False
    )

    predicted_close = Column(Float, nullable=False)

    confidence_lower = Column(
        Float,
        nullable=False
    )

    confidence_upper = Column(
        Float,
        nullable=False
    )

    model_type = Column(
        String(50),
        default="prophet"
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    __table_args__ = (
        Index(
            "idx_symbol_prediction_date",
            "symbol",
            "prediction_date"
        ),
    )


class Portfolio(Base):
    """User portfolio holdings"""

    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        String(100),
        index=True,
        nullable=False
    )

    symbol = Column(
        String(10),
        nullable=False
    )

    shares = Column(
        Float,
        nullable=False
    )

    average_cost = Column(
        Float,
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    __table_args__ = (
        Index(
            "idx_user_symbol",
            "user_id",
            "symbol"
        ),
    )


class Alert(Base):
    """Price alerts"""

    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        String(100),
        index=True,
        nullable=False
    )

    symbol = Column(
        String(10),
        nullable=False
    )

    condition = Column(
        String(10),
        nullable=False
    )  # above, below

    target_price = Column(
        Float,
        nullable=False
    )

    is_active = Column(
        Boolean,
        default=True
    )

    triggered = Column(
        Boolean,
        default=False
    )

    triggered_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    __table_args__ = (
        Index(
            "idx_user_active",
            "user_id",
            "is_active"
        ),
    )