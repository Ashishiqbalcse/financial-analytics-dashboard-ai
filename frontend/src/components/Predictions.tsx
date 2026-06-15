import React from 'react';
import { Box, Typography, Paper } from '@mui/material';

const Predictions: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ color: '#00bcd4' }}>
        AI Predictions
      </Typography>
      <Paper sx={{ p: 3, backgroundColor: '#1a1f35' }}>
        <Typography variant="body1" sx={{ color: '#8892b0' }}>
          Prophet forecasting engine will be implemented in Phase 7 with 7-day forecasts and confidence bands.
        </Typography>
      </Paper>
    </Box>
  );
};

export default Predictions;
