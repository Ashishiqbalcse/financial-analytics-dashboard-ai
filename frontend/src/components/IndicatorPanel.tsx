import React, { useEffect, useState } from "react";
import {
  Paper,
  Typography,
  Box,
  CircularProgress,
  ToggleButton,
  ToggleButtonGroup,
  Chip,
} from "@mui/material";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";

import api from "../services/api";

interface IndicatorPanelProps {
  symbol: string;
}

type IndicatorType = "RSI" | "MACD" | "SMA" | "EMA" | "BB";

const IndicatorPanel: React.FC<IndicatorPanelProps> = ({ symbol }) => {
  const [indicatorType, setIndicatorType] =
    useState<IndicatorType>("RSI");

  const [indicatorData, setIndicatorData] =
    useState<any>(null);

  const [loading, setLoading] =
    useState<boolean>(true);

  const [error, setError] =
    useState<string | null>(null);

  useEffect(() => {
    const fetchIndicatorData = async () => {
      try {
        setLoading(true);
        setError(null);

        const endpoint =
          indicatorType === "BB"
            ? "bollinger"
            : indicatorType.toLowerCase();

        const response = await api.get(
          `/indicators/${symbol}/${endpoint}`
        );

        setIndicatorData(response.data);
      } catch (err) {
        console.error(
          "Error fetching indicator data:",
          err
        );

        setError(
          "Failed to fetch indicator data"
        );
      } finally {
        setLoading(false);
      }
    };

    fetchIndicatorData();
  }, [symbol, indicatorType]);

  const handleIndicatorChange = (
    _: React.MouseEvent<HTMLElement>,
    newIndicator: IndicatorType | null
  ) => {
    if (newIndicator) {
      setIndicatorType(newIndicator);
    }
  };

  const formatChartData = () => {
    if (!indicatorData?.data) {
      return [];
    }

    switch (indicatorType) {
      case "RSI":
        return indicatorData.data.map(
          (item: any) => ({
            time: new Date(
              item.timestamp
            ).toLocaleTimeString(),

            value: item.value,
          })
        );

      case "MACD":
        return indicatorData.data.map(
          (item: any) => ({
            time: new Date(
              item.timestamp
            ).toLocaleTimeString(),

            macd: item.macd,
            signal: item.signal,
            histogram: item.histogram,
          })
        );

      case "SMA":
      case "EMA":
        return indicatorData.data.map(
          (item: any) => ({
            time: new Date(
              item.timestamp
            ).toLocaleTimeString(),

            value: item.value,
          })
        );

      case "BB":
        return indicatorData.data.map(
          (item: any) => ({
            time: new Date(
              item.timestamp
            ).toLocaleTimeString(),

            upper: item.upper,
            middle: item.middle,
            lower: item.lower,
          })
        );

      default:
        return [];
    }
  };

  const chartData = formatChartData();

  const getIndicatorColor = () => {
    switch (indicatorType) {
      case "RSI":
        return "#00bcd4";

      case "MACD":
        return "#ff4081";

      case "SMA":
        return "#4caf50";

      case "EMA":
        return "#ff9800";

      case "BB":
        return "#9c27b0";

      default:
        return "#00bcd4";
    }
  };

  const renderChart = () => {
    const color = getIndicatorColor();

    switch (indicatorType) {
      case "RSI":
        return (
          <>
            <ReferenceLine
              y={70}
              stroke="#f44336"
              strokeDasharray="3 3"
            />

            <ReferenceLine
              y={30}
              stroke="#4caf50"
              strokeDasharray="3 3"
            />

            <Line
              type="monotone"
              dataKey="value"
              stroke={color}
              strokeWidth={2}
              dot={false}
            />
          </>
        );

      case "MACD":
        return (
          <>
            <Line
              type="monotone"
              dataKey="macd"
              stroke={color}
              strokeWidth={2}
              dot={false}
              name="MACD"
            />

            <Line
              type="monotone"
              dataKey="signal"
              stroke="#4caf50"
              strokeWidth={2}
              dot={false}
              name="Signal"
            />
          </>
        );

      case "SMA":
      case "EMA":
        return (
          <Line
            type="monotone"
            dataKey="value"
            stroke={color}
            strokeWidth={2}
            dot={false}
            name={indicatorType}
          />
        );

      case "BB":
        return (
          <>
            <Line
              type="monotone"
              dataKey="upper"
              stroke="#f44336"
              dot={false}
              name="Upper"
            />

            <Line
              type="monotone"
              dataKey="middle"
              stroke={color}
              dot={false}
              name="Middle"
            />

            <Line
              type="monotone"
              dataKey="lower"
              stroke="#4caf50"
              dot={false}
              name="Lower"
            />
          </>
        );

      default:
        return null;
    }
  };

  if (loading) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        minHeight={300}
      >
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        minHeight={300}
      >
        <Typography color="error">
          {error}
        </Typography>
      </Box>
    );
  }

  return (
    <Paper
      sx={{
        p: 3,
        backgroundColor: "#1a1f35",
        height: "100%",
      }}
    >
      <Box
        display="flex"
        justifyContent="space-between"
        alignItems="center"
        mb={2}
      >
        <Typography
          variant="h6"
          sx={{ color: "#00bcd4" }}
        >
          Technical Indicators
        </Typography>

        <ToggleButtonGroup
          value={indicatorType}
          exclusive
          onChange={handleIndicatorChange}
          size="small"
        >
          <ToggleButton value="RSI">
            RSI
          </ToggleButton>

          <ToggleButton value="MACD">
            MACD
          </ToggleButton>

          <ToggleButton value="SMA">
            SMA
          </ToggleButton>

          <ToggleButton value="EMA">
            EMA
          </ToggleButton>

          <ToggleButton value="BB">
            BB
          </ToggleButton>
        </ToggleButtonGroup>
      </Box>

      {indicatorData?.parameters && (
        <Box mb={2}>
          {Object.entries(
            indicatorData.parameters
          ).map(([key, value]) => (
            <Chip
              key={key}
              label={`${key}: ${value}`}
              size="small"
              sx={{ mr: 1, mb: 1 }}
            />
          ))}
        </Box>
      )}

      <ResponsiveContainer
        width="100%"
        height={300}
      >
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />

          <XAxis dataKey="time" />

          <YAxis />

          <Tooltip />

          {renderChart()}
        </LineChart>
      </ResponsiveContainer>
    </Paper>
  );
};

export default IndicatorPanel;