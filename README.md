# Real-Time Financial Analytics Dashboard with Predictive AI

A production-ready full-stack financial analytics platform featuring real-time stock market monitoring, AI-powered forecasting, portfolio analytics, automated price alerts, technical indicators, and natural language financial insights.

---

# Features

## Real-Time Market Data

* Live stock market data ingestion using Yahoo Finance
* Automated background data collection with APScheduler
* Historical OHLCV storage in PostgreSQL
* Redis caching for high-performance data retrieval

## Technical Analysis

The platform calculates and visualizes:

* Relative Strength Index (RSI)
* Moving Average Convergence Divergence (MACD)
* Simple Moving Average (SMA)
* Exponential Moving Average (EMA)
* Bollinger Bands

## AI Forecasting Engine

* Prophet-based machine learning forecasting
* 7-day stock price prediction
* Confidence intervals
* Forecast accuracy metrics:

  * MAE
  * RMSE
  * MAPE
* Redis forecast caching

## Interactive Dashboard

* Real-time stock analytics dashboard
* Live WebSocket updates
* Interactive charts and visualizations
* Symbol search and selection
* Market statistics overview

## Portfolio Analytics

* Portfolio holdings tracking
* Investment monitoring
* Profit and loss calculations
* Portfolio performance analytics
* Current valuation tracking

## Smart Alert Engine

* Price threshold alerts
* Above price alerts
* Below price alerts
* Automatic trigger detection
* Real-time alert status updates

## AI Assistant

Natural language financial assistant capable of:

* Stock forecast explanations
* Technical indicator explanations
* Portfolio insights
* Market analytics queries
* Financial dashboard assistance

---

# Tech Stack

## Backend

* Python
* FastAPI
* PostgreSQL
* Redis
* SQLAlchemy
* APScheduler
* Pandas
* NumPy
* Prophet
* WebSockets
* Pydantic

## Frontend

* React
* TypeScript
* Material UI
* Recharts
* Axios
* React Router

## Infrastructure

* Docker
* Docker Compose

---

# Project Architecture

```text
Yahoo Finance API
        │
        ▼
Data Ingestion Service
(APScheduler)
        │
        ▼
PostgreSQL Database
        │
        ├──────────────► Technical Indicators
        │
        ├──────────────► Portfolio Analytics
        │
        └──────────────► Forecast Engine (Prophet)
                               │
                               ▼
                           Redis Cache
                               │
                               ▼
                     FastAPI REST APIs
                               │
               ┌───────────────┴───────────────┐
               ▼                               ▼
        WebSocket Server                 AI Assistant
               │
               ▼
        React Dashboard
```

---

# Project Structure

```text
.
├── backend
│   ├── app
│   │   ├── api
│   │   ├── core
│   │   ├── models
│   │   ├── scheduler
│   │   ├── services
│   │   └── websocket
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend
│   ├── src
│   │   ├── components
│   │   ├── hooks
│   │   ├── services
│   │   └── types
│   ├── package.json
│   └── Dockerfile
│
├── docker-compose.yml
└── README.md
```

---

# Screenshots

## Dashboard

Add screenshot:

```text
README/dashboard.png
```

## Portfolio

Add screenshot:

```text
README/portfolio.png
```

## Alerts

Add screenshot:

```text
README/alerts.png
```

## AI Assistant

Add screenshot:

```text
README/ai-assistant.png
```

---

# API Endpoints

## Health

```http
GET /health
```

## Prices

```http
GET /api/v1/prices/symbols
GET /api/v1/prices/{symbol}/latest
```

## Technical Indicators

```http
GET /api/v1/indicators/{symbol}
```

## Forecasting

```http
GET /api/v1/forecast/{symbol}
```

## Portfolio

```http
GET /api/v1/portfolio
GET /api/v1/portfolio/analytics
```

## Alerts

```http
GET /api/v1/alerts
POST /api/v1/alerts
DELETE /api/v1/alerts/{id}
```

## AI Assistant

```http
POST /api/v1/ai/query
```

Example:

```json
{
  "query": "Show AAPL forecast"
}
```

---

# Local Development

## Backend

```bash
cd backend

python -m venv venv

# Windows
venv\Scripts\activate

pip install -r requirements.txt

python -m uvicorn app.main:app --reload --port 7777
```

Backend URL:

```text
http://localhost:7777
```

Swagger Docs:

```text
http://localhost:7777/docs
```

---

## Frontend

```bash
cd frontend

npm install

npm run dev
```

Frontend URL:

```text
http://localhost:3001
```

---

# Database Models

## Tables

### ohlcv

Stores historical stock market OHLCV data.

### technical_indicators

Stores RSI, MACD, SMA, EMA and Bollinger Band values.

### predictions

Stores Prophet forecast results.

### portfolios

Stores portfolio holdings.

### alerts

Stores user-defined price alerts.

---

# Key Achievements

✅ Real-Time Market Data Ingestion

✅ Technical Indicators Engine

✅ Prophet Forecasting System

✅ Portfolio Analytics

✅ Price Alert Engine

✅ WebSocket Live Updates

✅ AI Assistant

✅ FastAPI REST APIs

✅ React Dashboard

✅ PostgreSQL + Redis Integration

---

# Project Status

Current Completion:

```text
98%
```

Implemented Modules:

* Real-Time Data Pipeline
* Technical Indicators
* Forecasting Engine
* Portfolio Analytics
* Alert Engine
* AI Assistant
* WebSocket Streaming
* Dashboard UI

---

# Future Enhancements

* Email Notifications
* SMS Alerts
* Push Notifications
* User Authentication
* Multi-Portfolio Support
* LSTM Forecasting Models
* News Sentiment Analysis
* Crypto Market Support

---

# Resume Highlights

Built a full-stack financial analytics platform using FastAPI, React, PostgreSQL, Redis and WebSockets with real-time market monitoring, AI-powered forecasting, portfolio analytics, automated alerts and natural language financial querying.

---

# License

MIT License

---

# Author

Ashish Iqbal

B.Tech Computer Science & Engineering

The Assam Kaziranga University
