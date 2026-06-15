import React, { useEffect, useState } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  AreaChart,
  Area
} from 'recharts';
import { Box, Typography, Paper, CircularProgress } from '@mui/material';
import api from '../services/api';
import { OHLCVData } from '../types';

interface PriceChartProps {
  symbol: string;
  timeframe?: string;
}

const PriceChart: React.FC<PriceChartProps> = ({ symbol, timeframe = '1mo' }) => {
  const [data, setData] = useState<OHLCVData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const response = await api.get(`/prices/${symbol}/historical?period=${timeframe}`);
        setData(response.data);
      } catch (err) {
        console.error('Error fetching price data:', err);
        setError('Failed to fetch price data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [symbol, timeframe]);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight={400}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight={400}>
        <Typography color="error">{error}</Typography>
      </Box>
    );
  }

  const chartData = data.map((item) => ({
    time: new Date(item.timestamp).toLocaleTimeString(),
    price: item.close,
    volume: item.volume
  }));

  return (
    <Paper sx={{ p: 3, backgroundColor: '#1a1f35', height: '100%' }}>
      <Typography variant="h6" gutterBottom sx={{ color: '#00bcd4' }}>
        {symbol} Price Chart
      </Typography>
      <ResponsiveContainer width="100%" height={400}>
        <AreaChart data={chartData}>
          <defs>
            <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#00bcd4" stopOpacity={0.8}/>
              <stop offset="95%" stopColor="#00bcd4" stopOpacity={0}/>
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#8892b0" strokeOpacity={0.3} />
          <XAxis 
            dataKey="time" 
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
            stroke="#00bcd4" 
            fillOpacity={1} 
            fill="url(#colorPrice)"
            name="Price"
          />
        </AreaChart>
      </ResponsiveContainer>
    </Paper>
  );
};

export default PriceChart;
