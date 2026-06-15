import React, { useEffect, useState } from 'react';
import {
  Grid,
  Paper,
  Typography,
  Box,
  CircularProgress
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  VolumeUp,
  ShowChart
} from '@mui/icons-material';
import api from '../services/api';
import { MarketData } from '../types';

interface StatCardsProps {
  symbol: string;
}

const StatCard: React.FC<{
  title: string;
  value: string | number;
  change?: number;
  icon: React.ReactNode;
}> = ({ title, value, change, icon }) => {
  const isPositive = change !== undefined && change >= 0;

  return (
    <Paper
      sx={{
        p: 3,
        background: 'linear-gradient(135deg, #1a1f35 0%, #2a2f45 100%)',
        borderRadius: '12px',
        border: '1px solid rgba(0, 188, 212, 0.2)',
        height: '100%'
      }}
    >
      <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
        <Typography variant="body2" sx={{ color: '#8892b0', textTransform: 'uppercase', letterSpacing: 1 }}>
          {title}
        </Typography>
        <Box sx={{ color: '#00bcd4' }}>
          {icon}
        </Box>
      </Box>
      <Typography variant="h4" sx={{ color: '#00bcd4', fontWeight: 'bold', mb: 1 }}>
        {typeof value === 'number' ? value.toFixed(2) : value}
      </Typography>
      {change !== undefined && (
        <Box display="flex" alignItems="center">
          {isPositive ? (
            <TrendingUp sx={{ color: '#4caf50', mr: 0.5, fontSize: 16 }} />
          ) : (
            <TrendingDown sx={{ color: '#f44336', mr: 0.5, fontSize: 16 }} />
          )}
          <Typography
            variant="body2"
            sx={{
              color: isPositive ? '#4caf50' : '#f44336',
              fontWeight: 500
            }}
          >
            {change >= 0 ? '+' : ''}{change.toFixed(2)}%
          </Typography>
        </Box>
      )}
    </Paper>
  );
};

const StatCards: React.FC<StatCardsProps> = ({ symbol }) => {
  const [marketData, setMarketData] = useState<MarketData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const response = await api.get(`/prices/${symbol}/latest`);
        setMarketData(response.data);
      } catch (err) {
        console.error('Error fetching market data:', err);
        setError('Failed to fetch market data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    
    // Refresh every 30 seconds
    const interval = setInterval(fetchData, 30000);
    
    return () => clearInterval(interval);
  }, [symbol]);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" p={3}>
        <CircularProgress />
      </Box>
    );
  }

  if (error || !marketData) {
    return (
      <Box display="flex" justifyContent="center" p={3}>
        <Typography color="error">{error || 'No data available'}</Typography>
      </Box>
    );
  }

  return (
    <Grid container spacing={2}>
      <Grid item xs={12} sm={6} md={3}>
        <StatCard
          title="Current Price"
          value={marketData.current_price}
          change={marketData.change_percent}
          icon={<ShowChart />}
        />
      </Grid>
      <Grid item xs={12} sm={6} md={3}>
        <StatCard
          title="Daily Change"
          value={marketData.change}
          change={marketData.change_percent}
          icon={marketData.change >= 0 ? <TrendingUp /> : <TrendingDown />}
        />
      </Grid>
      <Grid item xs={12} sm={6} md={3}>
        <StatCard
          title="Volume"
          value={marketData.volume ? (marketData.volume / 1000000).toFixed(2) + 'M' : 'N/A'}
          icon={<VolumeUp />}
        />
      </Grid>
      <Grid item xs={12} sm={6} md={3}>
        <StatCard
          title="52W High"
          value={marketData.high_52w || 'N/A'}
          icon={<TrendingUp />}
        />
      </Grid>
    </Grid>
  );
};

export default StatCards;
