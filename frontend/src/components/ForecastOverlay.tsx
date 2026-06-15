import React, { useEffect, useState } from 'react';
import {
  Paper,
  Typography,
  Box,
  Button,
  Chip,
  LinearProgress,
  Grid,
  CircularProgress
} from '@mui/material';
import {
  ShowChart,
  Timeline,
  Warning,
  Refresh,
  TrendingUp,
  TrendingDown
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Area,
  AreaChart
} from 'recharts';
import api from '../services/api';

interface ForecastOverlayProps {
  symbol: string;
}

const ForecastOverlay: React.FC<ForecastOverlayProps> = ({ symbol }) => {
  const [forecastData, setForecastData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchForecast = async (forceRefresh = false) => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await api.get(`/forecast/${symbol}?periods=7&force_refresh=${forceRefresh}`);
      setForecastData(response.data);
    } catch (err) {
      console.error('Error fetching forecast:', err);
      setError('Failed to fetch forecast data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchForecast();
  }, [symbol]);

  const handleRefresh = () => {
    fetchForecast(true);
  };

  if (loading && !forecastData) {
    return (
      <Paper sx={{ p: 3, backgroundColor: '#1a1f35', height: '100%' }}>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight={300}>
          <CircularProgress />
        </Box>
      </Paper>
    );
  }

  if (error) {
    return (
      <Paper sx={{ p: 3, backgroundColor: '#1a1f35', height: '100%' }}>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight={300}>
          <Typography color="error">{error}</Typography>
        </Box>
      </Paper>
    );
  }

  // Prepare chart data
  const prepareChartData = () => {
    if (!forecastData || !forecastData.forecast) return [];

    const historicalData = [];
    const forecastDataPoints = [];
    
    // Add historical data point
    if (forecastData.forecast.current_price) {
      historicalData.push({
        date: 'Current',
        price: forecastData.forecast.current_price,
        type: 'historical'
      });
    }
    
    // Add forecast predictions
    forecastData.forecast.predictions.forEach((pred: any) => {
      forecastDataPoints.push({
        date: new Date(pred.date).toLocaleDateString(),
        price: pred.predicted_price,
        upper: pred.upper_bound,
        lower: pred.lower_bound,
        type: 'forecast'
      });
    });
    
    return [...historicalData, ...forecastDataPoints];
  };

  const chartData = prepareChartData();

  return (
    <Paper sx={{ p: 3, backgroundColor: '#1a1f35', height: '100%' }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h6" sx={{ color: '#00bcd4', display: 'flex', alignItems: 'center' }}>
          <Timeline sx={{ mr: 1 }} />
          AI Price Forecast
        </Typography>
        <Box display="flex" alignItems="center" gap={2}>
          <Chip
            label={forecastData?.model_type || 'Prophet'}
            color="primary"
            variant="outlined"
            size="small"
          />
          <Button
            size="small"
            startIcon={<Refresh />}
            onClick={handleRefresh}
            disabled={loading}
            sx={{
              color: '#00bcd4',
              border: '1px solid #00bcd4',
              '&:hover': {
                backgroundColor: 'rgba(0, 188, 212, 0.1)'
              }
            }}
          >
            Refresh
          </Button>
        </Box>
      </Box>

      {forecastData && (
        <>
          {/* Metrics Grid */}
          <Grid container spacing={2} mb={3}>
            <Grid item xs={6} sm={3}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="caption" sx={{ color: '#8892b0' }}>MAE</Typography>
                <Typography variant="h6" sx={{ color: '#00bcd4' }}>
                  ${forecastData.metrics?.mae?.toFixed(2) || 'N/A'}
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={6} sm={3}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="caption" sx={{ color: '#8892b0' }}>RMSE</Typography>
                <Typography variant="h6" sx={{ color: '#00bcd4' }}>
                  ${forecastData.metrics?.rmse?.toFixed(2) || 'N/A'}
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={6} sm={3}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="caption" sx={{ color: '#8892b0' }}>MAPE</Typography>
                <Typography variant="h6" sx={{ color: '#00bcd4' }}>
                  {forecastData.metrics?.mape?.toFixed(1) || 'N/A'}%
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={6} sm={3}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="caption" sx={{ color: '#8892b0' }}>Coverage</Typography>
                <Typography variant="h6" sx={{ color: '#00bcd4' }}>
                  {forecastData.metrics?.coverage?.toFixed(1) || 'N/A'}%
                </Typography>
              </Box>
            </Grid>
          </Grid>

          {/* Forecast Chart */}
          {chartData.length > 0 && (
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={chartData}>
                <defs>
                  <linearGradient id="colorForecast" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#ff4081" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#ff4081" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorConfidence" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#00bcd4" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#00bcd4" stopOpacity={0.1}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#8892b0" strokeOpacity={0.3} />
                <XAxis 
                  dataKey="date" 
                  stroke="#8892b0"
                  tick={{ fill: '#8892b0' }}
                />
                <YAxis 
                  stroke="#8892b0"
                  tick={{ fill: '#8892b0' }}
                  domain={['auto', 'auto']}
                />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#1a1f35', 
                    border: '1px solid #00bcd4',
                    borderRadius: '8px'
                  }}
                  itemStyle={{ color: '#00bcd4' }}
                />
                <Legend />
                <Area 
                  type="monotone" 
                  dataKey="price" 
                  stroke="#ff4081" 
                  fillOpacity={1} 
                  fill="url(#colorForecast)"
                  name="Predicted Price"
                />
                {chartData.some(d => d.upper) && chartData.some(d => d.lower) && (
                  <>
                    <Line 
                      type="monotone" 
                      dataKey="upper" 
                      stroke="#00bcd4" 
                      strokeDasharray="5 5"
                      dot={false}
                      name="Upper Bound"
                    />
                    <Line 
                      type="monotone" 
                      dataKey="lower" 
                      stroke="#00bcd4" 
                      strokeDasharray="5 5"
                      dot={false}
                      name="Lower Bound"
                    />
                  </>
                )}
              </AreaChart>
            </ResponsiveContainer>
          )}

          {/* Forecast Summary */}
          <Box mt={3} p={2} sx={{ backgroundColor: 'rgba(0, 188, 212, 0.1)', borderRadius: 2 }}>
            <Typography variant="caption" sx={{ color: '#00bcd4', fontWeight: 500 }}>
              Forecast Summary: {forecastData.forecast?.prediction_count || 0} day forecast generated at {new Date(forecastData.generated_at).toLocaleString()}
            </Typography>
          </Box>

          {/* Warning */}
          <Box mt={2} p={2} sx={{ backgroundColor: 'rgba(255, 152, 0, 0.1)', borderRadius: 2 }}>
            <Box display="flex" alignItems="center">
              <Warning sx={{ color: '#ff9800', mr: 1, fontSize: 16 }} />
              <Typography variant="caption" sx={{ color: '#ff9800', fontStyle: 'italic' }}>
                ⚠️ Forecasting results are for illustrative purposes only and should not be used for trading decisions.
              </Typography>
            </Box>
          </Box>
        </>
      )}
    </Paper>
  );
};

export default ForecastOverlay;
