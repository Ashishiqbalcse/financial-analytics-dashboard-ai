import React, { useEffect, useState } from "react";
import {
  Paper,
  Typography,
  Box,
  Button,
  Chip,
  Grid,
  CircularProgress,
} from "@mui/material";
import {
  Timeline,
  Warning,
  Refresh,
} from "@mui/icons-material";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from "recharts";

import api from "../services/api";

interface ForecastOverlayProps {
  symbol: string;
}

interface Prediction {
  date: string;
  predicted_price: number;
  lower_bound: number;
  upper_bound: number;
  trend: number;
}

interface ForecastResponse {
  status: string;
  symbol: string;
  generated_at: string;
  model_type: string;
  periods: number;
  metrics: {
    mae: number;
    rmse: number;
    mape: number;
    coverage: number;
    sample_size: number;
  };
  forecast: {
    current_price: number;
    forecast_start: string;
    forecast_end: string;
    predictions: Prediction[];
  };
}

const ForecastOverlay: React.FC<ForecastOverlayProps> = ({ symbol }) => {
  const [forecastData, setForecastData] =
    useState<ForecastResponse | null>(null);

  const [loading, setLoading] = useState(false);

  const [error, setError] =
    useState<string | null>(null);

  const fetchForecast = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await api.get(
        `/forecast/${symbol}`
      );

      setForecastData(response.data);
    } catch (err) {
      console.error(
        "Error fetching forecast:",
        err
      );

      setError(
        "Failed to fetch forecast data"
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchForecast();
  }, [symbol]);

  const handleRefresh = () => {
    fetchForecast();
  };

  const chartData =
    forecastData?.forecast?.predictions
      ? [
          {
            date: "Today",
            price:
              forecastData.forecast.current_price,
          },
          ...forecastData.forecast.predictions.map(
            (prediction) => ({
              date: new Date(
                prediction.date
              ).toLocaleDateString(),
              price:
                prediction.predicted_price,
              upper:
                prediction.upper_bound,
              lower:
                prediction.lower_bound,
            })
          ),
        ]
      : [];

  const currentPrice =
    forecastData?.forecast?.current_price ?? 0;

  const finalForecast =
    forecastData?.forecast?.predictions?.[
      (forecastData?.forecast?.predictions?.length ?? 1) - 1
    ]?.predicted_price ?? 0;

  const bullish =
    finalForecast > currentPrice;

  if (loading && !forecastData) {
    return (
      <Paper sx={{ p: 3 }}>
        <Box
          display="flex"
          justifyContent="center"
          alignItems="center"
          minHeight={300}
        >
          <CircularProgress />
        </Box>
      </Paper>
    );
  }

  if (error) {
    return (
      <Paper sx={{ p: 3 }}>
        <Typography color="error">
          {error}
        </Typography>
      </Paper>
    );
  }

  return (
    <Paper
      sx={{
        p: 3,
        backgroundColor: "#1a1f35",
      }}
    >
      <Box
        display="flex"
        justifyContent="space-between"
        alignItems="center"
        mb={3}
      >
        <Typography
          variant="h6"
          sx={{
            color: "#00bcd4",
            display: "flex",
            alignItems: "center",
          }}
        >
          <Timeline sx={{ mr: 1 }} />
          AI Forecast
        </Typography>

        <Box display="flex" gap={1}>
          <Chip
            label={
              forecastData?.model_type ??
              "Prophet"
            }
            color="primary"
            variant="outlined"
            size="small"
          />

          <Chip
            label={
              bullish
                ? "Bullish"
                : "Bearish"
            }
            color={
              bullish
                ? "success"
                : "error"
            }
            size="small"
          />

          <Button
            size="small"
            startIcon={<Refresh />}
            onClick={handleRefresh}
          >
            Refresh
          </Button>
        </Box>
      </Box>

      {forecastData && (
        <>
          <Grid container spacing={2} mb={3}>
            <Grid item xs={6} md={3}>
              <Typography variant="caption">
                MAE
              </Typography>

              <Typography
                variant="h6"
                color="primary"
              >
                ${forecastData.metrics.mae.toFixed(2)}
              </Typography>
            </Grid>

            <Grid item xs={6} md={3}>
              <Typography variant="caption">
                RMSE
              </Typography>

              <Typography
                variant="h6"
                color="primary"
              >
                ${forecastData.metrics.rmse.toFixed(2)}
              </Typography>
            </Grid>

            <Grid item xs={6} md={3}>
              <Typography variant="caption">
                MAPE
              </Typography>

              <Typography
                variant="h6"
                color="primary"
              >
                {forecastData.metrics.mape.toFixed(2)}%
              </Typography>
            </Grid>

            <Grid item xs={6} md={3}>
              <Typography variant="caption">
                Coverage
              </Typography>

              <Typography
                variant="h6"
                color="primary"
              >
                {forecastData.metrics.coverage.toFixed(1)}%
              </Typography>
            </Grid>
          </Grid>

          <ResponsiveContainer
            width="100%"
            height={350}
          >
            <AreaChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />

              <Area
                type="monotone"
                dataKey="price"
                stroke="#ff4081"
                fill="#ff4081"
                fillOpacity={0.25}
                name="Forecast"
              />

              <Line
                type="monotone"
                dataKey="upper"
                stroke="#00bcd4"
                dot={false}
                name="Upper Bound"
              />

              <Line
                type="monotone"
                dataKey="lower"
                stroke="#00bcd4"
                dot={false}
                name="Lower Bound"
              />
            </AreaChart>
          </ResponsiveContainer>

          <Box mt={3}>
            <Typography
              variant="body2"
              sx={{ color: "#00bcd4" }}
            >
              Generated:{" "}
              {new Date(
                forecastData.generated_at
              ).toLocaleString()}
            </Typography>
          </Box>

          <Box
            mt={2}
            p={2}
            sx={{
              backgroundColor:
                "rgba(255,152,0,0.1)",
              borderRadius: 2,
            }}
          >
            <Box
              display="flex"
              alignItems="center"
            >
              <Warning
                sx={{
                  color: "#ff9800",
                  mr: 1,
                }}
              />

              <Typography
                variant="caption"
                sx={{
                  color: "#ff9800",
                }}
              >
                Forecasts are for educational purposes only and are not investment advice.
              </Typography>
            </Box>
          </Box>
        </>
      )}
    </Paper>
  );
};

export default ForecastOverlay;