import React from 'react';
import { Box, Typography, Paper } from '@mui/material';

const Alerts: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ color: '#00bcd4' }}>
        Price Alerts
      </Typography>
      <Paper sx={{ p: 3, backgroundColor: '#1a1f35' }}>
        <Typography variant="body1" sx={{ color: '#8892b0' }}>
          Alerts engine will be implemented in Phase 9 with price thresholds and notification system.
        </Typography>
      </Paper>
    </Box>
  );
};

export default Alerts;
