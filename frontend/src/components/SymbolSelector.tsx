
import React, { useEffect, useState } from "react";
import {
  Box,
  TextField,
  MenuItem,
  Paper,
  Typography,
  Chip,
  Autocomplete,
} from "@mui/material";

import { Search } from "@mui/icons-material";
import api from "../services/api";

interface SymbolSelectorProps {
  selectedSymbol: string;
  onSymbolChange: (symbol: string) => void;
}

const POPULAR_SYMBOLS = [
  "AAPL",
  "TSLA",
  "GOOGL",
  "MSFT",
  "AMZN",
  "META",
  "NVDA",
  "JPM",
  "BAC",
  "WMT",
];

const SymbolSelector: React.FC<SymbolSelectorProps> = ({
  selectedSymbol,
  onSymbolChange,
}) => {
  const [availableSymbols, setAvailableSymbols] =
    useState<string[]>([]);

  const [searchTerm, setSearchTerm] =
    useState("");

  useEffect(() => {
    const fetchSymbols = async () => {
      try {
        const response =
          await api.get(
            "/prices/symbols"
          );

        setAvailableSymbols(
          response.data ||
            POPULAR_SYMBOLS
        );
      } catch (error) {
        console.error(
          "Error fetching symbols:",
          error
        );

        setAvailableSymbols(
          POPULAR_SYMBOLS
        );
      }
    };

    fetchSymbols();
  }, []);

  const handleSymbolSelect = (
    symbol: string
  ) => {
    onSymbolChange(
      symbol.toUpperCase()
    );

    setSearchTerm("");
  };

  return (
    <Box sx={{ mb: 3 }}>
      <Typography
        variant="h6"
        gutterBottom
        sx={{
          color: "#00bcd4",
          mb: 2,
        }}
      >
        Select Symbol
      </Typography>

      <Paper
        sx={{
          p: 2,
          backgroundColor:
            "#1a1f35",
          border:
            "1px solid rgba(0,188,212,0.2)",
        }}
      >
        <Box sx={{ mb: 2 }}>
          <Autocomplete
            freeSolo
            options={
              availableSymbols
            }
            value={
              selectedSymbol
            }
            inputValue={
              searchTerm
            }
            onChange={(
              _,
              newValue
            ) => {
              if (newValue) {
                handleSymbolSelect(
                  String(newValue)
                );
              }
            }}
            onInputChange={(
              _,
              newInputValue
            ) => {
              setSearchTerm(
                newInputValue
              );
            }}
            renderInput={(
              params
            ) => (
              <TextField
                {...params}
                placeholder="Search Symbol..."
                variant="outlined"
                fullWidth
                size="small"
                InputProps={{
                  ...params.InputProps,
                  startAdornment: (
                    <Search
                      sx={{
                        mr: 1,
                        color:
                          "#00bcd4",
                      }}
                    />
                  ),
                }}
              />
            )}
            renderOption={(
              props,
              option
            ) => (
              <MenuItem
                {...props}
              >
                {option}
              </MenuItem>
            )}
          />
        </Box>

        <Typography
          variant="caption"
          sx={{
            color: "#8892b0",
            display: "block",
            mb: 1,
          }}
        >
          Popular Symbols
        </Typography>

        <Box
          display="flex"
          flexWrap="wrap"
          gap={1}
        >
          {POPULAR_SYMBOLS.map(
            (symbol) => (
              <Chip
                key={symbol}
                label={symbol}
                clickable
                onClick={() =>
                  handleSymbolSelect(
                    symbol
                  )
                }
                sx={{
                  backgroundColor:
                    selectedSymbol ===
                    symbol
                      ? "#00bcd4"
                      : "rgba(0,188,212,0.1)",

                  color:
                    selectedSymbol ===
                    symbol
                      ? "#1a1f35"
                      : "#00bcd4",
                }}
              />
            )
          )}
        </Box>
      </Paper>
    </Box>
  );
};

export default SymbolSelector;
