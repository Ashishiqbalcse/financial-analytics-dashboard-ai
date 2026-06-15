-- Sample data insertion for testing
-- This will be replaced by real data ingestion

-- Insert sample OHLCV data for AAPL
INSERT INTO ohlcv (symbol, timestamp, open, high, low, close, volume) VALUES
('AAPL', '2024-01-01 09:30:00+00', 185.50, 186.20, 185.10, 186.00, 50000000),
('AAPL', '2024-01-01 09:31:00+00', 186.00, 186.50, 185.80, 186.30, 48000000),
('AAPL', '2024-01-01 09:32:00+00', 186.30, 187.00, 186.20, 186.80, 52000000),
('AAPL', '2024-01-01 09:33:00+00', 186.80, 187.50, 186.70, 187.20, 49000000),
('AAPL', '2024-01-01 09:34:00+00', 187.20, 187.80, 187.00, 187.60, 51000000);

-- Insert sample OHLCV data for TSLA
INSERT INTO ohlcv (symbol, timestamp, open, high, low, close, volume) VALUES
('TSLA', '2024-01-01 09:30:00+00', 248.50, 250.20, 247.80, 249.50, 45000000),
('TSLA', '2024-01-01 09:31:00+00', 249.50, 251.00, 249.00, 250.30, 42000000),
('TSLA', '2024-01-01 09:32:00+00', 250.30, 252.50, 250.00, 251.80, 48000000),
('TSLA', '2024-01-01 09:33:00+00', 251.80, 253.20, 251.50, 252.60, 46000000),
('TSLA', '2024-01-01 09:34:00+00', 252.60, 254.00, 252.30, 253.50, 47000000);

-- Insert sample technical indicators
INSERT INTO technical_indicators (symbol, timestamp, indicator_type, value, metadata) VALUES
('AAPL', '2024-01-01 09:34:00+00', 'RSI', 65.5, '{"period": 14}'),
('AAPL', '2024-01-01 09:34:00+00', 'MACD', 1.25, '{"signal": 1.15, "histogram": 0.10}'),
('AAPL', '2024-01-01 09:34:00+00', 'SMA', 185.75, '{"period": 20}'),
('TSLA', '2024-01-01 09:34:00+00', 'RSI', 72.3, '{"period": 14}'),
('TSLA', '2024-01-01 09:34:00+00', 'MACD', 2.45, '{"signal": 2.30, "histogram": 0.15}'),
('TSLA', '2024-01-01 09:34:00+00', 'SMA', 248.90, '{"period": 20}');
