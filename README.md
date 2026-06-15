# Real-Time Financial Analytics Dashboard with Predictive AI

A comprehensive full-stack financial analytics platform featuring real-time market data ingestion, technical indicators, ML forecasting, and natural language querying.

## Tech Stack

### Backend
- Python 3.11
- FastAPI
- PostgreSQL + TimescaleDB
- Redis
- APScheduler
- Pandas / NumPy
- Scikit-learn + Prophet
- WebSocket
- Alpha Vantage / Yahoo Finance API

### Frontend
- React + TypeScript
- Recharts / D3.js
- Material-UI
- Socket.io-client

### Infrastructure
- Docker
- Docker Compose

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── api/           # API endpoints
│   │   ├── core/          # Configuration and database
│   │   ├── models/        # Database models and schemas
│   │   ├── services/      # Business logic
│   │   ├── utils/         # Utility functions
│   │   ├── scheduler/     # Background job scheduling
│   │   └── websocket/     # WebSocket handlers
│   ├── tests/             # Test suite
│   ├── requirements.txt   # Python dependencies
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── hooks/         # Custom React hooks
│   │   ├── services/      # API services
│   │   ├── types/         # TypeScript types
│   │   └── utils/         # Utility functions
│   ├── package.json       # Node dependencies
│   └── Dockerfile
├── docker/
│   ├── postgres/
│   │   └── init/          # Database initialization scripts
│   └── redis/
│       └── redis.conf     # Redis configuration
├── docker-compose.yml     # Multi-container orchestration
└── README.md
```

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Git

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd "2. Real-Time Financial Analytics Dashboard with AI"
```

2. Configure environment variables:
```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
- `ALPHA_VANTAGE_API_KEY`: Get from [Alpha Vantage](https://www.alphavantage.co/support/#api-key)
- `OPENAI_API_KEY`: Get from [OpenAI](https://platform.openai.com/api-keys)

3. Start all services:
```bash
docker-compose up -d
```

4. Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Local Development

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

#### Database (Local)
Ensure PostgreSQL with TimescaleDB is running, then run:
```bash
psql -U finance_user -d finance_db -f docker/postgres/init/01-init.sql
```

## Features

### Phase 1 (✓ Complete)
- Complete folder structure
- FastAPI backend configuration
- React + TypeScript frontend setup
- PostgreSQL + TimescaleDB schema
- Redis configuration
- Docker orchestration

### Phase 2 (Next)
- Market data ingestion pipeline
- APScheduler for automated data fetching
- OHLCV data storage in TimescaleDB

### Phase 3
- Technical indicators: RSI, MACD, Bollinger Bands, SMA, EMA

### Phase 4
- REST APIs for prices, indicators, and historical data

### Phase 5
- WebSocket live price streaming

### Phase 6
- React dashboard with live charts and stat cards

### Phase 7
- Prophet forecasting engine with 7-day forecasts

### Phase 8
- Portfolio tracker with P&L calculations

### Phase 9
- Alerts engine with price threshold monitoring

### Phase 10
- Natural language query interface using OpenAI API

## API Endpoints

- `GET /health` - Health check
- `GET /api/v1/prices/{symbol}` - Get price data
- `GET /api/v1/indicators/{symbol}` - Get technical indicators
- `POST /api/v1/predict` - Get ML predictions
- `GET /api/v1/portfolio/{user_id}` - Get portfolio data
- `POST /api/v1/alerts` - Create price alert

## Database Schema

### Tables
- `ohlcv` - OHLCV market data (hypertable)
- `technical_indicators` - Pre-calculated indicators (hypertable)
- `predictions` - ML model predictions (hypertable)
- `portfolios` - User portfolio holdings
- `alerts` - Price alerts and notifications

## Architecture

```
Market Data API (Alpha Vantage)
    ↓
Data Ingestion Service (APScheduler)
    ↓
TimescaleDB (time-series storage)
    ↓
ML Model (Prophet/LSTM)
    ↓
Prediction Cache (Redis)
    ↓
FastAPI REST + WebSocket
    ↓
React Dashboard (Recharts)
```

## License

MIT

## Contributing

Contributions are welcome! Please read our contributing guidelines before submitting PRs.
