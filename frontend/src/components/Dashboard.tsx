import { useState, useEffect } from "react";
import { Box, Grid, Typography } from "@mui/material";

import SymbolSelector from "./SymbolSelector";
import StatCards from "./StatCards";
import PriceChart from "./PriceChart";
import IndicatorPanel from "./IndicatorPanel";
import ForecastOverlay from "./ForecastOverlay";

import { useWebSocket } from "../hooks/useWebSocket";

const Dashboard = () => {
  const [selectedSymbol, setSelectedSymbol] =
    useState("AAPL");

  const [livePrice, setLivePrice] =
    useState<number | null>(null);

  const { isConnected } =
  useWebSocket(
    `ws://localhost:7777/ws/${selectedSymbol}`,
    {
      onMessage: (message) => {
        if (
          message.type === "price_update" &&
          message.data
        ) {
          setLivePrice(
            message.data.current_price
          );
        }
      },
    }
  );

  useEffect(() => {
  if (!isConnected) return;

  console.log(
    `Connected to ${selectedSymbol} websocket`
  );
}, [
  selectedSymbol,
  isConnected,
]);

  const handleSymbolChange = (
    symbol: string
  ) => {
    setSelectedSymbol(symbol);
    setLivePrice(null);
  };

  return (
    <Box>
      <Typography
        variant="h4"
        gutterBottom
        sx={{
          color: "#00bcd4",
          mb: 3,
        }}
      >
        Financial Analytics Dashboard
      </Typography>

      <Box mb={2}>
        <Typography
          variant="caption"
          sx={{
            color: "#8892b0",
          }}
        >
          WebSocket Status:{" "}
          {isConnected
            ? "🟢 Connected"
            : "🔴 Disconnected"}
        </Typography>

        {livePrice !== null && (
          <Typography
            variant="caption"
            sx={{
              color: "#00bcd4",
              ml: 2,
            }}
          >
            Live Price: $
            {livePrice.toFixed(2)}
          </Typography>
        )}
      </Box>

      <SymbolSelector
        selectedSymbol={selectedSymbol}
        onSymbolChange={
          handleSymbolChange
        }
      />

      <Grid
        container
        spacing={2}
      >
        <Grid item xs={12}>
          <StatCards
            symbol={selectedSymbol}
          />
        </Grid>

        <Grid item xs={12} lg={8}>
          <PriceChart
            symbol={selectedSymbol}
          />
        </Grid>

        <Grid item xs={12} lg={4}>
          <IndicatorPanel
            symbol={selectedSymbol}
          />
        </Grid>

        <Grid item xs={12}>
          <ForecastOverlay
            symbol={selectedSymbol}
          />
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;