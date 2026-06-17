import React, { useEffect, useState } from "react";
import {
  Grid,
  Paper,
  Typography,
  Box,
  CircularProgress,
} from "@mui/material";

import {
  TrendingUp,
  TrendingDown,
  VolumeUp,
  ShowChart,
} from "@mui/icons-material";

import api from "../services/api";

interface StatCardsProps {
  symbol: string;
}

interface MarketData {
  current_price: number;
  previous_close: number;
  change: number;
  change_percent: number;
  volume: number;
  high: number;
  low: number;
}

const StatCard = ({
  title,
  value,
  change,
  icon,
}: {
  title: string;
  value: string | number;
  change?: number;
  icon: React.ReactNode;
}) => {
  const positive = change !== undefined && change >= 0;

  return (
    <Paper
      sx={{
        p: 3,
        background:
          "linear-gradient(135deg,#1a1f35 0%,#2a2f45 100%)",
        borderRadius: 3,
        border: "1px solid rgba(0,188,212,0.2)",
      }}
    >
      <Box
        display="flex"
        justifyContent="space-between"
        mb={2}
      >
        <Typography
          variant="body2"
          sx={{ color: "#8892b0" }}
        >
          {title}
        </Typography>

        <Box sx={{ color: "#00bcd4" }}>
          {icon}
        </Box>
      </Box>

      <Typography
        variant="h5"
        sx={{
          color: "#00bcd4",
          fontWeight: "bold",
        }}
      >
        {value}
      </Typography>

      {change !== undefined && (
        <Box
          display="flex"
          alignItems="center"
          mt={1}
        >
          {positive ? (
            <TrendingUp
              sx={{
                color: "#4caf50",
                mr: 0.5,
              }}
            />
          ) : (
            <TrendingDown
              sx={{
                color: "#f44336",
                mr: 0.5,
              }}
            />
          )}

          <Typography
            variant="body2"
            sx={{
              color: positive
                ? "#4caf50"
                : "#f44336",
            }}
          >
            {change.toFixed(2)}%
          </Typography>
        </Box>
      )}
    </Paper>
  );
};

const StatCards: React.FC<StatCardsProps> = ({
  symbol,
}) => {
  const [marketData, setMarketData] =
    useState<MarketData | null>(null);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);

        const response =
          await api.get(`/prices/${symbol}`);

        const prices = response.data;

        if (
          !prices ||
          !Array.isArray(prices) ||
          prices.length === 0
        ) {
          throw new Error(
            "No price data found"
          );
        }

        const latest =
          prices[prices.length - 1];

        const previous =
          prices.length > 1
            ? prices[prices.length - 2]
            : latest;

        const change =
          latest.close -
          previous.close;

        const changePercent =
          previous.close > 0
            ? (change /
                previous.close) *
              100
            : 0;

        setMarketData({
          current_price:
            latest.close,
          previous_close:
            previous.close,
          change,
          change_percent:
            changePercent,
          volume:
            latest.volume || 0,
          high:
            latest.high || 0,
          low:
            latest.low || 0,
        });
      } catch (err) {
        console.error(err);

        setError(
          "Failed to fetch market data"
        );
      } finally {
        setLoading(false);
      }
    };

    fetchData();

    const interval =
      setInterval(
        fetchData,
        30000
      );

    return () =>
      clearInterval(interval);
  }, [symbol]);

  if (loading) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        p={4}
      >
        <CircularProgress />
      </Box>
    );
  }

  if (error || !marketData) {
    return (
      <Typography color="error">
        {error}
      </Typography>
    );
  }

  return (
    <Grid container spacing={2}>
      <Grid item xs={12} md={3}>
        <StatCard
          title="Current Price"
          value={`$${marketData.current_price.toFixed(
            2
          )}`}
          change={
            marketData.change_percent
          }
          icon={<ShowChart />}
        />
      </Grid>

      <Grid item xs={12} md={3}>
        <StatCard
          title="Daily Change"
          value={`$${marketData.change.toFixed(
            2
          )}`}
          change={
            marketData.change_percent
          }
          icon={
            marketData.change >= 0 ? (
              <TrendingUp />
            ) : (
              <TrendingDown />
            )
          }
        />
      </Grid>

      <Grid item xs={12} md={3}>
        <StatCard
          title="Volume"
          value={`${(
            marketData.volume /
            1000000
          ).toFixed(2)}M`}
          icon={<VolumeUp />}
        />
      </Grid>

      <Grid item xs={12} md={3}>
        <StatCard
          title="Day High"
          value={`$${marketData.high.toFixed(
            2
          )}`}
          icon={<TrendingUp />}
        />
      </Grid>
    </Grid>
  );
};

export default StatCards;