import React, { useState } from 'react';
import { Box, Grid, Typography } from '@mui/material';
import SymbolSelector from './SymbolSelector';
import StatCards from './StatCards';
import PriceChart from './PriceChart';
import IndicatorPanel from './IndicatorPanel';
import ForecastOverlay from './ForecastOverlay';
import { useWebSocket } from '../hooks/useWebSocket';

const Dashboard: React.FC = () => {
  const [selectedSymbol, setSelectedSymbol] = useState('AAPL');
  const [livePrice, setLivePrice] = useState<number | null>(null);

  // WebSocket connection for real-time updates
  const { isConnected, lastMessage, subscribe } = useWebSocket(
    `ws://localhost:3004/ws/${selectedSymbol.toLowerCase()}`,
    {
      onMessage: (message) => {
        if (message.type === 'price_update' && message.data) {
          setLivePrice(message.data.current_price);
        }
      }
    }
  );

  // Subscribe to symbol updates when symbol changes
  React.useEffect(() => {
    if (isConnected) {
      subscribe(selectedSymbol);
    }
  }, [selectedSymbol, isConnected, subscribe]);

  const handleSymbolChange = (symbol: string) => {
    setSelectedSymbol(symbol);
    setLivePrice(null);
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ color: '#00bcd4', mb: 3 }}>
        Financial Analytics Dashboard
      </Typography>

      {/* Connection Status */}
      <Box mb={2}>
        <Typography variant="caption" sx={{ color: '#8892b0' }}>
          WebSocket Status: {isConnected ? '🟢 Connected' : '🔴 Disconnected'}
        </Typography>
        {livePrice && (
          <Typography variant="caption" sx={{ color: '#00bcd4', ml: 2 }}>
            Live Price: ${livePrice?.toFixed(2)}
          </Typography>
        )}
      </Box>

      <SymbolSelector 
        selectedSymbol={selectedSymbol}
        onSymbolChange={handleSymbolChange}
      />

      <Grid container spacing={2}>
        {/* Stat Cards */}
        <Grid item xs={12}>
          <StatCards symbol={selectedSymbol} />
        </Grid>

        {/* Price Chart */}
        <Grid item xs={12} lg={8}>
          <PriceChart symbol={selectedSymbol} />
        </Grid>

        {/* Technical Indicators */}
        <Grid item xs={12} lg={4}>
          <IndicatorPanel symbol={selectedSymbol} />
        </Grid>

        {/* Forecast Overlay */}
        <Grid item xs={12}>
          <ForecastOverlay symbol={selectedSymbol} />
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;
