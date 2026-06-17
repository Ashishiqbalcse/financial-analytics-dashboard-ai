import React, { useState } from "react";
import {
Box,
Typography,
Paper,
TextField,
Button,
CircularProgress,
} from "@mui/material";

import api from "../services/api";

const AIAssistant: React.FC = () => {
const [query, setQuery] = useState("");
const [answer, setAnswer] = useState("");
const [loading, setLoading] = useState(false);

const askAI = async () => {
if (!query.trim()) return;

try {
  setLoading(true);

  const response = await api.post(
    "/ai/query",
    {
      query,
    }
  );

  setAnswer(response.data.answer);
} catch (error) {
  console.error(error);
  setAnswer("Failed to get AI response.");
} finally {
  setLoading(false);
}

};

return ( <Box>
<Typography
variant="h4"
gutterBottom
sx={{ color: "#00bcd4" }}
>
AI Financial Assistant </Typography>

```
  <Paper
    sx={{
      p: 3,
      backgroundColor: "#1a1f35",
    }}
  >
    <TextField
      fullWidth
      label="Ask about forecasts, RSI, portfolio..."
      value={query}
      onChange={(e) =>
        setQuery(e.target.value)
      }
    />

    <Button
      variant="contained"
      sx={{ mt: 2 }}
      onClick={askAI}
    >
      Ask AI
    </Button>

    {loading && (
      <Box mt={2}>
        <CircularProgress />
      </Box>
    )}

    {answer && (
      <Paper
        sx={{
          mt: 3,
          p: 2,
        }}
      >
        <Typography>
          {answer}
        </Typography>
      </Paper>
    )}
  </Paper>
</Box>

);
};

export default AIAssistant;
