import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TechnicalIndicators:
    """Calculate technical indicators for market data"""
    
    @staticmethod
    def calculate_rsi(prices: List[float], period: int = 14) -> List[Optional[float]]:
        """Calculate Relative Strength Index (RSI)"""
        if len(prices) < period + 1:
            return [None] * len(prices)
        
        prices_series = pd.Series(prices)
        delta = prices_series.diff()
        
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        result = rsi.tolist()
        # Pad with None for the first period values
        result = [None] * period + result[period:]
        
        return result
    
    @staticmethod
    def calculate_macd(prices: List[float], fast_period: int = 12, slow_period: int = 26, signal_period: int = 9) -> Dict[str, List[Optional[float]]]:
        """Calculate MACD (Moving Average Convergence Divergence)"""
        if len(prices) < slow_period + signal_period:
            return {
                'macd': [None] * len(prices),
                'signal': [None] * len(prices),
                'histogram': [None] * len(prices)
            }
        
        prices_series = pd.Series(prices)
        
        # Calculate EMAs
        ema_fast = prices_series.ewm(span=fast_period, adjust=False).mean()
        ema_slow = prices_series.ewm(span=slow_period, adjust=False).mean()
        
        # MACD line
        macd = ema_fast - ema_slow
        
        # Signal line
        signal = macd.ewm(span=signal_period, adjust=False).mean()
        
        # Histogram
        histogram = macd - signal
        
        return {
            'macd': macd.tolist(),
            'signal': signal.tolist(),
            'histogram': histogram.tolist()
        }
    
    @staticmethod
    def calculate_sma(prices: List[float], period: int = 20) -> List[Optional[float]]:
        """Calculate Simple Moving Average (SMA)"""
        if len(prices) < period:
            return [None] * len(prices)
        
        prices_series = pd.Series(prices)
        sma = prices_series.rolling(window=period).mean()
        
        result = sma.tolist()
        # Pad with None for the first period-1 values
        result = [None] * (period - 1) + result[period - 1:]
        
        return result
    
    @staticmethod
    def calculate_ema(prices: List[float], period: int = 20) -> List[Optional[float]]:
        """Calculate Exponential Moving Average (EMA)"""
        if len(prices) < period:
            return [None] * len(prices)
        
        prices_series = pd.Series(prices)
        ema = prices_series.ewm(span=period, adjust=False).mean()
        
        return ema.tolist()
    
    @staticmethod
    def calculate_bollinger_bands(prices: List[float], period: int = 20, std_dev: float = 2.0) -> Dict[str, List[Optional[float]]]:
        """Calculate Bollinger Bands"""
        if len(prices) < period:
            return {
                'upper': [None] * len(prices),
                'middle': [None] * len(prices),
                'lower': [None] * len(prices)
            }
        
        prices_series = pd.Series(prices)
        
        # Middle band (SMA)
        sma = prices_series.rolling(window=period).mean()
        
        # Standard deviation
        std = prices_series.rolling(window=period).std()
        
        # Upper and lower bands
        upper = sma + (std * std_dev)
        lower = sma - (std * std_dev)
        
        return {
            'upper': upper.tolist(),
            'middle': sma.tolist(),
            'lower': lower.tolist()
        }
    
    @staticmethod
    def calculate_all_indicators(ohlcv_data: List[Dict]) -> Dict[str, List]:
        """Calculate all technical indicators for OHLCV data"""
        if not ohlcv_data:
            return {}
        
        # Extract close prices
        close_prices = [data['close'] for data in ohlcv_data]
        
        # Calculate all indicators
        rsi = TechnicalIndicators.calculate_rsi(close_prices)
        macd = TechnicalIndicators.calculate_macd(close_prices)
        sma = TechnicalIndicators.calculate_sma(close_prices)
        ema = TechnicalIndicators.calculate_ema(close_prices)
        bollinger = TechnicalIndicators.calculate_bollinger_bands(close_prices)
        
        return {
            'rsi': rsi,
            'macd': macd,
            'sma': sma,
            'ema': ema,
            'bollinger_bands': bollinger
        }
    
    @staticmethod
    def generate_signals(prices: List[float], indicators: Dict) -> List[Optional[str]]:
        """Generate buy/sell signals based on indicators"""
        if not prices or len(prices) < 20:
            return [None] * len(prices)
        
        signals = []
        rsi = indicators.get('rsi', [])
        macd = indicators.get('macd', {})
        bollinger = indicators.get('bollinger_bands', {})
        
        for i in range(len(prices)):
            if i >= 20:  # Only generate signals when we have enough data
                signal = "neutral"
                buy_signals = 0
                sell_signals = 0
                
                # RSI signals
                if len(rsi) > i and rsi[i] is not None:
                    if rsi[i] < 30:
                        buy_signals += 1
                    elif rsi[i] > 70:
                        sell_signals += 1
                
                # MACD signals
                if len(macd.get('macd', [])) > i and len(macd.get('signal', [])) > i:
                    macd_val = macd['macd'][i]
                    signal_val = macd['signal'][i]
                    if macd_val is not None and signal_val is not None:
                        if macd_val > signal_val and macd_val > 0:
                            buy_signals += 1
                        elif macd_val < signal_val and macd_val < 0:
                            sell_signals += 1
                
                # Bollinger Band signals
                upper = bollinger.get('upper', [])
                lower = bollinger.get('lower', [])
                if len(upper) > i and len(lower) > i:
                    if upper[i] is not None and lower[i] is not None:
                        if prices[i] < lower[i]:
                            buy_signals += 1
                        elif prices[i] > upper[i]:
                            sell_signals += 1
                
                # Determine overall signal
                if buy_signals > sell_signals:
                    signal = "buy"
                elif sell_signals > buy_signals:
                    signal = "sell"
                
                signals.append(signal)
            else:
                signals.append(None)
        
        return signals
    
    @staticmethod
    def format_indicator_data(indicators: Dict, timestamps: List) -> Dict[str, List[Dict]]:
        """Format indicator data for API response"""
        result = {}
        
        for indicator_name, values in indicators.items():
            if isinstance(values, dict):
                # Handle nested indicators like MACD and Bollinger Bands
                for sub_name, sub_values in values.items():
                    key = f"{indicator_name}_{sub_name}"
                    result[key] = []
                    for i, timestamp in enumerate(timestamps):
                        if i < len(sub_values):
                            result[key].append({
                                'timestamp': timestamp,
                                'value': sub_values[i]
                            })
            else:
                # Handle simple indicators like RSI, SMA, EMA
                result[indicator_name] = []
                for i, timestamp in enumerate(timestamps):
                    if i < len(values):
                        result[indicator_name].append({
                            'timestamp': timestamp,
                            'value': values[i]
                        })
        
        return result


# Global technical indicators instance
technical_indicators = TechnicalIndicators()
