import React from 'react';
import { Box, Typography, Paper } from '@mui/material';

const Portfolio: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ color: '#00bcd4' }}>
        Portfolio Tracker
      </Typography>
      <Paper sx={{ p: 3, backgroundColor: '#1a1f35' }}>
        <Typography variant="body1" sx={{ color: '#8892b0' }}>
          Portfolio tracker will be implemented in Phase 8 with holdings, P&L, allocation breakdown, and risk score.
        </Typography>
      </Paper>
    </Box>
  );
};

export default Portfolio;
