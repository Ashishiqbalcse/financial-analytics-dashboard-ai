import prophet

print("==========")
print("PROPHET VERSION:", prophet.__version__)
print("==========")
import pandas as pd
import numpy as np
from prophet import Prophet
# from prophet.diagnostics import cross_validation, performance_metrics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
import pickle
import os
from pathlib import Path
from sqlalchemy.orm import Session
from app.models.market_data import OHLCV, Prediction
from app.core.redis_client import redis_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ForecastingService:
    """Service for ML-based price forecasting using Prophet"""
    
    def __init__(self):
        self.model_cache_dir = Path("backend/data/models")
        self.model_cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_ttl = 3600  # Cache models for 1 hour
        
    def prepare_data(self, ohlcv_data: List[OHLCV]) -> pd.DataFrame:
        """Prepare OHLCV data for Prophet training"""
        data = []
        for record in ohlcv_data:
            data.append({
                'ds': record.timestamp,
                'y': record.close
            })
        
        df = pd.DataFrame(data)
        df = df.sort_values('ds')
        df = df.drop_duplicates(subset=['ds'])
        
        return df
    
    def train_model(self, symbol: str, periods: int = 7) -> Dict:
        """Train a Prophet model for a symbol"""
        try:
            cache_key = f"model:{symbol}"
            
            # Check if model exists in cache
            cached_model = redis_client.get(cache_key)
            if cached_model:
                logger.info(f"Using cached model for {symbol}")
                return cached_model
            
            # This would normally fetch from database, but for now we'll use mock data
            # In production, fetch from OHLCV table
            df = self._generate_mock_data(symbol)
            
            if len(df) < 30:
                raise ValueError(f"Insufficient data for {symbol}. Need at least 30 data points.")
            
            # Initialize and train Prophet model
            logger.info(f"Creating Prophet model for {symbol}")
            
            import prophet
            import cmdstanpy

            logger.info(f"PROPHET VERSION = {prophet.__version__}")
            logger.info(f"CMDSTANPY VERSION = {cmdstanpy.__version__}")

            try:
                model = Prophet()

                logger.info(
                f"Model attributes: {dir(model)}"
            )

                logger.info("Prophet model created")

                model.fit(df)

                logger.info("Prophet training completed")

            except Exception as e:
                logger.exception(f"Prophet failed: {e}")
                raise

            logger.info(f"Generating {periods}-day forecast")

            future = model.make_future_dataframe(
                periods=periods
            )

            forecast = model.predict(future)

            logger.info("Forecast generated successfully")
            
            # Extract forecast results
            forecast_results = self._extract_forecast_results(forecast, periods)
            
            # Calculate model metrics
            metrics = self._calculate_metrics(df, forecast, periods)
            
            # Cache the model
            model_data = {
                'symbol': symbol,
                'forecast': forecast_results,
                'metrics': metrics,
                'trained_at': datetime.utcnow().isoformat(),
                'periods': periods
            }
            
            redis_client.set(cache_key, model_data, ttl=self.cache_ttl)
            
            # Save model to disk
            logger.info("Skipping model pickle storage")
            
            logger.info(f"Successfully trained model for {symbol}")
            
            return model_data
            
        except Exception as e:
            logger.error(f"Error training model for {symbol}: {e}")
            raise
    
    def _generate_mock_data(self, symbol: str) -> pd.DataFrame:
        """Generate mock historical data for testing (in production, fetch from database)"""
        # Generate 90 days of mock data
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=90)
        
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # Simulate price data with trend and noise
        np.random.seed(hash(symbol) % 1000)  # Consistent random data per symbol
        base_price = 100 + hash(symbol) % 50
        trend = np.linspace(0, 10, len(dates))
        noise = np.random.normal(0, 2, len(dates))
        prices = base_price + trend + noise
        
        data = []
        for date, price in zip(dates, prices):
            data.append({
                'ds': date,
                'y': max(price, 1)  # Ensure positive prices
            })
        
        return pd.DataFrame(data)
    
    def _extract_forecast_results(self, forecast: pd.DataFrame, periods: int) -> Dict:
        """Extract forecast results from Prophet output"""
        # Get the forecasted period
        forecast_period = forecast.tail(periods)
        
        results = {
            'predictions': [],
            'current_price': forecast.iloc[-periods-1]['yhat'] if len(forecast) > periods else forecast.iloc[0]['yhat'],
            'forecast_start': forecast_period.iloc[0]['ds'].isoformat(),
            'forecast_end': forecast_period.iloc[-1]['ds'].isoformat()
        }
        
        for _, row in forecast_period.iterrows():
            results['predictions'].append({
                'date': row['ds'].isoformat(),
                'predicted_price': float(row['yhat']),
                'lower_bound': float(row['yhat_lower']),
                'upper_bound': float(row['yhat_upper']),
                'trend': float(row['trend'])
            })
        
        return results
    
    def _calculate_metrics(self, historical: pd.DataFrame, forecast: pd.DataFrame, periods: int) -> Dict:
        """Calculate forecast accuracy metrics"""
        try:
            # Merge historical data with forecast for the overlapping period
            merged = historical.merge(forecast, on='ds', how='inner')
            
            if len(merged) < 2:
                return {
                    'mae': None,
                    'rmse': None,
                    'mape': None,
                    'coverage': None
                }
            
            # Calculate metrics
            actual = merged['y'].values
            predicted = merged['yhat'].values
            
            mae = np.mean(np.abs(actual - predicted))
            rmse = np.sqrt(np.mean((actual - predicted) ** 2))
            
            # MAPE (Mean Absolute Percentage Error) - avoid division by zero
            mape = np.mean(np.abs((actual - predicted) / np.where(actual != 0, actual, 1))) * 100
            
            # Coverage - how often actual values fall within confidence intervals
            within_bounds = ((actual >= merged['yhat_lower'].values) & 
                            (actual <= merged['yhat_upper'].values)).sum()
            coverage = (within_bounds / len(merged)) * 100 if len(merged) > 0 else 0
            
            return {
                'mae': float(mae),
                'rmse': float(rmse),
                'mape': float(mape),
                'coverage': float(coverage),
                'sample_size': len(merged)
            }
            
        except Exception as e:
            logger.error(f"Error calculating metrics: {e}")
            return {
                'mae': None,
                'rmse': None,
                'mape': None,
                'coverage': None
            }
    
    def get_forecast(self, symbol: str, periods: int = 7) -> Dict:
        """Get forecast for a symbol (cached if available)"""
        try:
            cache_key = f"forecast:{symbol}:{periods}"
            
            # Check cache first
            cached_forecast = redis_client.get(cache_key)
            if cached_forecast:
                logger.info(f"Returning cached forecast for {symbol}")
                return cached_forecast
            
            # Generate new forecast
            model_data = self.train_model(symbol, periods)
            
            forecast_data = {
                'symbol': symbol,
                'generated_at': datetime.utcnow().isoformat(),
                'forecast': model_data['forecast'],
                'metrics': model_data['metrics'],
                'model_type': 'prophet',
                'periods': periods
            }
            
            # Cache the forecast
            redis_client.set(cache_key, forecast_data, ttl=1800)  # Cache for 30 minutes
            
            return forecast_data
            
        except Exception as e:
            logger.error(f"Error getting forecast for {symbol}: {e}")
            raise
    
    def save_forecast_to_db(self, db: Session, symbol: str, forecast_data: Dict):
        """Save forecast results to database"""
        try:
            for prediction in forecast_data['forecast']['predictions']:
                db_prediction = Prediction(
                    symbol=symbol,
                    prediction_date=datetime.fromisoformat(prediction['date'].replace('Z', '+00:00')),
                    predicted_close=prediction['predicted_price'],
                    confidence_lower=prediction['lower_bound'],
                    confidence_upper=prediction['upper_bound'],
                    model_type='prophet'
                )
                db.add(db_prediction)
            
            db.commit()
            logger.info(f"Saved {len(forecast_data['forecast']['predictions'])} predictions for {symbol}")
            
        except Exception as e:
            logger.error(f"Error saving forecast to database: {e}")
            db.rollback()
            raise
    
    def get_forecast_history(self, db: Session, symbol: str, limit: int = 10) -> List[Dict]:
        """Get historical forecasts for a symbol"""
        try:
            forecasts = db.query(Prediction).filter(
                Prediction.symbol == symbol.upper()
            ).order_by(
                Prediction.prediction_date.desc()
            ).limit(limit).all()
            
            return [
                {
                    'id': f.id,
                    'prediction_date': f.prediction_date.isoformat(),
                    'predicted_close': f.predicted_close,
                    'confidence_lower': f.confidence_lower,
                    'confidence_upper': f.confidence_upper,
                    'model_type': f.model_type,
                    'created_at': f.created_at.isoformat()
                }
                for f in forecasts
            ]
            
        except Exception as e:
            logger.error(f"Error fetching forecast history for {symbol}: {e}")
            return []
    
    def get_model_metrics(self, symbol: str) -> Dict:
        """Get model performance metrics"""
        try:
            model_data = self.train_model(symbol)
            return model_data['metrics']
        except Exception as e:
            logger.error(f"Error getting model metrics for {symbol}: {e}")
            return {}


# Global forecasting service instance
forecasting_service = ForecastingService()
