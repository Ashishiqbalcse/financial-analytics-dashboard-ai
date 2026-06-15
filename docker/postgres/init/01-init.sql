-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Create database (will be created by Docker, but we set it up here if needed)
-- CREATE DATABASE finance_db;

-- Connect to the database
\c finance_db;

-- Create OHLCV table as hypertable
CREATE TABLE IF NOT EXISTS ohlcv (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    open FLOAT NOT NULL,
    high FLOAT NOT NULL,
    low FLOAT NOT NULL,
    close FLOAT NOT NULL,
    volume FLOAT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Convert to hypertable for time-series optimization
SELECT create_hypertable('ohlcv', 'timestamp', if_not_exists => TRUE);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_ohlcv_symbol_timestamp ON ohlcv (symbol, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_ohlcv_timestamp ON ohlcv (timestamp DESC);

-- Create technical indicators table
CREATE TABLE IF NOT EXISTS technical_indicators (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    indicator_type VARCHAR(20) NOT NULL,
    value FLOAT NOT NULL,
    metadata TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Convert to hypertable
SELECT create_hypertable('technical_indicators', 'timestamp', if_not_exists => TRUE);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_technical_symbol_indicator_timestamp 
ON technical_indicators (symbol, indicator_type, timestamp DESC);

-- Create predictions table
CREATE TABLE IF NOT EXISTS predictions (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    prediction_date TIMESTAMPTZ NOT NULL,
    predicted_close FLOAT NOT NULL,
    confidence_lower FLOAT NOT NULL,
    confidence_upper FLOAT NOT NULL,
    model_type VARCHAR(50) DEFAULT 'prophet',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Convert to hypertable
SELECT create_hypertable('predictions', 'prediction_date', if_not_exists => TRUE);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_predictions_symbol_date ON predictions (symbol, prediction_date DESC);

-- Create portfolios table
CREATE TABLE IF NOT EXISTS portfolios (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    symbol VARCHAR(10) NOT NULL,
    shares FLOAT NOT NULL,
    average_cost FLOAT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_portfolios_user_symbol ON portfolios (user_id, symbol);

-- Create alerts table
CREATE TABLE IF NOT EXISTS alerts (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    symbol VARCHAR(10) NOT NULL,
    condition VARCHAR(10) NOT NULL,
    target_price FLOAT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    triggered BOOLEAN DEFAULT FALSE,
    triggered_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_alerts_user_active ON alerts (user_id, is_active);

-- Create a view for latest prices
CREATE OR REPLACE VIEW latest_prices AS
SELECT DISTINCT ON (symbol) 
    symbol,
    close as current_price,
    timestamp,
    volume
FROM ohlcv
ORDER BY symbol, timestamp DESC;

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO finance_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO finance_user;

-- Insert some sample data for testing (optional)
-- This will be replaced by real data ingestion
