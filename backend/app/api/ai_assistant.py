from fastapi import APIRouter
from pydantic import BaseModel
import httpx

router = APIRouter()


class AIQueryRequest(BaseModel):
    query: str


class AIQueryResponse(BaseModel):
    query: str
    answer: str


@router.post(
    "/ai/query",
    response_model=AIQueryResponse
)
async def ai_query(
    request: AIQueryRequest
):
    query = request.query.strip().lower()

    try:

        # Forecast queries
        if "forecast" in query:

            symbol = "AAPL"

            for stock in [
                "aapl",
                "tsla",
                "msft",
                "googl",
                "amzn",
                "meta",
                "nvda",
                "jpm",
            ]:
                if stock in query:
                    symbol = stock.upper()
                    break

            async with httpx.AsyncClient() as client:

                response = await client.get(
                    f"http://127.0.0.1:7777/api/v1/forecast/{symbol}",
                    timeout=10
                )

                if response.status_code == 200:

                    forecast_data = response.json()

                    metrics = forecast_data.get(
                        "metrics",
                        {}
                    )

                    mae = metrics.get(
                        "mae",
                        "N/A"
                    )

                    rmse = metrics.get(
                        "rmse",
                        "N/A"
                    )

                    answer = (
                        f"{symbol} forecast generated successfully. "
                        f"Model MAE: {mae}. "
                        f"RMSE: {rmse}. "
                        f"The stock is expected to follow the "
                        f"predicted trend over the next "
                        f"{forecast_data.get('periods', 7)} days."
                    )

                else:
                    answer = (
                        f"Unable to retrieve forecast "
                        f"for {symbol}."
                    )

        elif "portfolio" in query:

            answer = (
                "Portfolio analytics indicate that "
                "your holdings are being tracked successfully. "
                "Visit the Portfolio page for detailed "
                "profit and loss metrics."
            )

        elif "rsi" in query:

            answer = (
                "RSI measures momentum. "
                "Above 70 indicates overbought conditions. "
                "Below 30 indicates oversold conditions."
            )

        elif "macd" in query:

            answer = (
                "MACD helps identify trend changes. "
                "A bullish crossover may signal upward momentum."
            )

        elif "buy" in query or "sell" in query:

            answer = (
                "This platform provides analytics and forecasts "
                "only. Investment decisions should be based on "
                "your own research and risk tolerance."
            )

        elif (
            "hello" in query
            or "hi" in query
        ):

            answer = (
                "Hello! I can help with forecasts, "
                "technical indicators, portfolio analytics, "
                "and market insights."
            )

        else:

            answer = (
                f"I received your query: '{request.query}'. "
                f"Try asking things like:\n"
                f"- Show AAPL forecast\n"
                f"- Explain RSI\n"
                f"- Explain MACD\n"
                f"- Portfolio summary"
            )

    except Exception as e:

        answer = (
            f"AI Assistant encountered an error: {str(e)}"
        )

    return AIQueryResponse(
        query=request.query,
        answer=answer
    )