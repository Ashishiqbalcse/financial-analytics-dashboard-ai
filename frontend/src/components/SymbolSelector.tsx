import React, { useState, useEffect } from 'react';
import {
  Box,
  TextField,
  MenuItem,
  Paper,
  Typography,
  Chip,
  Autocomplete
} from '@mui/material';
import { Search } from '@mui/icons-material';
import api from '../services/api';

interface SymbolSelectorProps {
  selectedSymbol: string;
  onSymbolChange: (symbol: string) => void;
}

const POPULAR_SYMBOLS = [
  'AAPL',
  'TSLA', 
  'GOOGL',
  'MSFT',
  'AMZN',
  'META',
  'NVDA',
  'JPM',
  'BAC',
  'WMT'
];

const SymbolSelector: React.FC<SymbolSelectorProps> = ({ selectedSymbol, onSymbolChange }) => {
  const [availableSymbols, setAvailableSymbols] = useState<string[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchSymbols = async () => {
      try {
        setLoading(true);
        const response = await api.get('/prices/symbols');
        setAvailableSymbols(response.data || POPULAR_SYMBOLS);
      } catch (error) {
        console.error('Error fetching symbols:', error);
        setAvailableSymbols(POPULAR_SYMBOLS);
      } finally {
        setLoading(false);
      }
    };

    fetchSymbols();
  }, []);

  const handleSymbolSelect = (symbol: string) => {
    onSymbolChange(symbol.toUpperCase());
    setSearchTerm('');
  };

  const filteredSymbols = availableSymbols.filter(symbol =>
    symbol.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <Box sx={{ mb: 3 }}>
      <Typography variant="h6" gutterBottom sx={{ color: '#00bcd4', mb: 2 }}>
        Select Symbol
      </Typography>
      
      <Paper sx={{ p: 2, backgroundColor: '#1a1f35', border: '1px solid rgba(0, 188, 212, 0.2)' }}>
        <Box sx={{ mb: 2 }}>
          <Autocomplete
            freeSolo
            options={availableSymbols}
            value={selectedSymbol}
            onChange={(event, newValue) => {
              if (newValue) {
                handleSymbolSelect(typeof newValue === 'string' ? newValue : '');
              }
            }}
            onInputChange={(event, newInputValue) => {
              setSearchTerm(newInputValue);
            }}
            renderInput={(params) => (
              <TextField
                {...params}
                placeholder="Search or enter symbol..."
                variant="outlined"
                fullWidth
                size="small"
                InputProps={{
                  ...params.InputProps,
                  startAdornment: <Search sx={{ mr: 1, color: '#00bcd4' }} />,
                  sx: {
                    color: '#00bcd4',
                    '& .MuiOutlinedInput-notchedOutline': {
                      borderColor: 'rgba(0, 188, 212, 0.3)'
                    },
                    '&:hover .MuiOutlinedInput-notchedOutline': {
                      borderColor: '#00bcd4'
                    },
                    '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                      borderColor: '#00bcd4'
                    }
                  }
                }}
              />
            )}
            renderOption={(props, option) => (
              <MenuItem {...props} sx={{ color: '#8892b0' }}>
                {option}
              </MenuItem>
            )}
            sx={{
              '& .MuiAutocomplete-inputRoot': {
                color: '#00bcd4'
              }
            }}
          />
        </Box>

        <Box>
          <Typography variant="caption" sx={{ color: '#8892b0', mb: 1, display: 'block' }}>
            Popular Symbols:
          </Typography>
          <Box display="flex" flexWrap="wrap" gap={1}>
            {POPULAR_SYMBOLS.map((symbol) => (
              <Chip
                key={symbol}
                label={symbol}
                onClick={() => handleSymbolSelect(symbol)}
                clickable
                size="small"
                sx={{
                  backgroundColor: selectedSymbol === symbol 
                    ? '#00bcd4' 
                    : 'rgba(0, 188, 212, 0.1)',
                  color: selectedSymbol === symbol ? '#1a1f35' : '#00bcd4',
                  border: selectedSymbol === symbol 
                    ? 'none' 
                    : '1px solid rgba(0, 188, 212, 0.3)',
                  '&:hover': {
                    backgroundColor: selectedSymbol === symbol 
                      ? '#00bcd4' 
                      : 'rgba(0, 188, 212, 0.2)',
                  }
                }}
              />
            ))}
          </Box>
        </Box>
      </Paper>
    </Box>
  );
};

export default SymbolSelector;
