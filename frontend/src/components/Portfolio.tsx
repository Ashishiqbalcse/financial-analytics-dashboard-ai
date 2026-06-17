import React, { useEffect, useState } from "react";
import {
  Box,
  Typography,
  Paper,
  Grid,
  CircularProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow
} from "@mui/material";

import api from "../services/api";

interface Holding {
  symbol: string;
  quantity: number;
  buy_price: number;
  current_price: number;
  investment: number;
  current_value: number;
  profit_loss: number;
}

interface PortfolioAnalytics {
  total_holdings: number;
  total_investment: number;
  current_value: number;
  profit_loss: number;
  profit_percent: number;
  holdings: Holding[];
}

const Portfolio: React.FC = () => {
  const [data, setData] =
    useState<PortfolioAnalytics | null>(null);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState<string | null>(null);

  useEffect(() => {
    fetchPortfolio();
  }, []);

  const fetchPortfolio = async () => {
    try {
      setLoading(true);

      const response =
        await api.get(
          "/portfolio/analytics"
        );

      setData(response.data);
    } catch (err) {
      console.error(err);
      setError(
        "Failed to load portfolio analytics"
      );
    } finally {
      setLoading(false);
    }
  };

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

  if (error || !data) {
    return (
      <Typography color="error">
        {error}
      </Typography>
    );
  }

  return (
    <Box>
      <Typography
        variant="h4"
        gutterBottom
        sx={{
          color: "#00bcd4",
          mb: 3
        }}
      >
        Portfolio Dashboard
      </Typography>

      <Grid
        container
        spacing={2}
        mb={3}
      >
        <Grid item xs={12} md={4}>
          <Paper
            sx={{
              p: 3,
              backgroundColor:
                "#1a1f35"
            }}
          >
            <Typography
              variant="subtitle2"
              color="gray"
            >
              Total Investment
            </Typography>

            <Typography
              variant="h5"
              sx={{
                color: "#00bcd4"
              }}
            >
              $
              {data.total_investment.toFixed(
                2
              )}
            </Typography>
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper
            sx={{
              p: 3,
              backgroundColor:
                "#1a1f35"
            }}
          >
            <Typography
              variant="subtitle2"
              color="gray"
            >
              Current Value
            </Typography>

            <Typography
              variant="h5"
              sx={{
                color: "#4caf50"
              }}
            >
              $
              {data.current_value.toFixed(
                2
              )}
            </Typography>
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper
            sx={{
              p: 3,
              backgroundColor:
                "#1a1f35"
            }}
          >
            <Typography
              variant="subtitle2"
              color="gray"
            >
              Profit / Loss
            </Typography>

            <Typography
              variant="h5"
              sx={{
                color:
                  data.profit_loss >= 0
                    ? "#4caf50"
                    : "#f44336"
              }}
            >
              $
              {data.profit_loss.toFixed(
                2
              )}
              {" ("}
              {data.profit_percent.toFixed(
                2
              )}
              %)
            </Typography>
          </Paper>
        </Grid>
      </Grid>

      <Paper
        sx={{
          p: 2,
          backgroundColor:
            "#1a1f35"
        }}
      >
        <Typography
          variant="h6"
          gutterBottom
          sx={{
            color: "#00bcd4"
          }}
        >
          Holdings
        </Typography>

        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>
                  Symbol
                </TableCell>

                <TableCell>
                  Qty
                </TableCell>

                <TableCell>
                  Buy Price
                </TableCell>

                <TableCell>
                  Current
                </TableCell>

                <TableCell>
                  Investment
                </TableCell>

                <TableCell>
                  Value
                </TableCell>

                <TableCell>
                  P/L
                </TableCell>
              </TableRow>
            </TableHead>

            <TableBody>
              {data.holdings.map(
                (holding) => (
                  <TableRow
                    key={
                      holding.symbol
                    }
                  >
                    <TableCell>
                      {
                        holding.symbol
                      }
                    </TableCell>

                    <TableCell>
                      {
                        holding.quantity
                      }
                    </TableCell>

                    <TableCell>
                      $
                      {holding.buy_price.toFixed(
                        2
                      )}
                    </TableCell>

                    <TableCell>
                      $
                      {holding.current_price.toFixed(
                        2
                      )}
                    </TableCell>

                    <TableCell>
                      $
                      {holding.investment.toFixed(
                        2
                      )}
                    </TableCell>

                    <TableCell>
                      $
                      {holding.current_value.toFixed(
                        2
                      )}
                    </TableCell>

                    <TableCell
                      sx={{
                        color:
                          holding.profit_loss >=
                          0
                            ? "#4caf50"
                            : "#f44336"
                      }}
                    >
                      $
                      {holding.profit_loss.toFixed(
                        2
                      )}
                    </TableCell>
                  </TableRow>
                )
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>
    </Box>
  );
};

export default Portfolio;