import React, { useEffect, useState } from "react";
import {
  Box,
  Typography,
  Paper,
  Grid,
  TextField,
  Button,
  MenuItem,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  CircularProgress,
} from "@mui/material";
import DeleteIcon from "@mui/icons-material/Delete";
import api from "../services/api";

interface Alert {
  id: number;
  symbol: string;
  condition: string;
  target_price: number;
  active: boolean;
  triggered: boolean;
}

const Alerts: React.FC = () => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(false);

  const [symbol, setSymbol] = useState("AAPL");
  const [condition, setCondition] = useState("above");
  const [targetPrice, setTargetPrice] = useState("");

  const fetchAlerts = async () => {
    try {
      setLoading(true);

      const response = await api.get("/alerts");

      setAlerts(response.data || []);
    } catch (error) {
      console.error("Failed to fetch alerts", error);
    } finally {
      setLoading(false);
    }
  };

  const createAlert = async () => {
    try {
      await api.post("/alerts", {
        symbol,
        condition,
        target_price: Number(targetPrice),
      });

      setTargetPrice("");

      fetchAlerts();
    } catch (error) {
      console.error("Failed to create alert", error);
    }
  };

  const deleteAlert = async (id: number) => {
    try {
      await api.delete(`/alerts/${id}`);

      fetchAlerts();
    } catch (error) {
      console.error("Failed to delete alert", error);
    }
  };

  useEffect(() => {
  fetchAlerts();

  const interval = setInterval(
    fetchAlerts,
    10000
  );

  return () =>
    clearInterval(interval);
}, []);

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
        Price Alerts
      </Typography>

      <Paper
        sx={{
          p: 3,
          mb: 3,
          backgroundColor: "#1a1f35",
        }}
      >
        <Typography
          variant="h6"
          gutterBottom
          sx={{
            color: "#00bcd4",
          }}
        >
          Create Alert
        </Typography>

        <Grid container spacing={2}>
          <Grid item xs={12} md={3}>
            <TextField
              fullWidth
              label="Symbol"
              value={symbol}
              onChange={(e) =>
                setSymbol(e.target.value.toUpperCase())
              }
            />
          </Grid>

          <Grid item xs={12} md={3}>
            <TextField
              select
              fullWidth
              label="Condition"
              value={condition}
              onChange={(e) =>
                setCondition(e.target.value)
              }
            >
              <MenuItem value="above">
                Above
              </MenuItem>

              <MenuItem value="below">
                Below
              </MenuItem>
            </TextField>
          </Grid>

          <Grid item xs={12} md={3}>
            <TextField
              fullWidth
              type="number"
              label="Target Price"
              value={targetPrice}
              onChange={(e) =>
                setTargetPrice(e.target.value)
              }
            />
          </Grid>

          <Grid item xs={12} md={3}>
            <Button
              variant="contained"
              fullWidth
              sx={{
                height: "56px",
              }}
              onClick={createAlert}
            >
              Create Alert
            </Button>
          </Grid>
        </Grid>
      </Paper>

      <Paper
        sx={{
          p: 3,
          backgroundColor: "#1a1f35",
        }}
      >
        <Typography
          variant="h6"
          gutterBottom
          sx={{
            color: "#00bcd4",
          }}
        >
          Active Alerts
        </Typography>

        {loading ? (
          <Box textAlign="center">
            <CircularProgress />
          </Box>
        ) : (
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>ID</TableCell>
                  <TableCell>Symbol</TableCell>
                  <TableCell>Condition</TableCell>
                  <TableCell>Target Price</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Delete</TableCell>
                </TableRow>
              </TableHead>

              <TableBody>
                {alerts.map((alert) => (
                  <TableRow key={alert.id}>
                    <TableCell>
                      {alert.id}
                    </TableCell>

                    <TableCell>
                      {alert.symbol}
                    </TableCell>

                    <TableCell>
                      {alert.condition}
                    </TableCell>

                    <TableCell>
                      ${alert.target_price}
                    </TableCell>

                    <TableCell>
  {alert.triggered
    ? "🟢 Triggered"
    : alert.active
    ? "🔵 Active"
    : "⚪ Closed"}
</TableCell>

                    <TableCell>
                      <IconButton
                        color="error"
                        onClick={() =>
                          deleteAlert(alert.id)
                        }
                      >
                        <DeleteIcon />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </Paper>
    </Box>
  );
};

export default Alerts;