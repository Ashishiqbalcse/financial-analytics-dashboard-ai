from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.portfolio import PortfolioHolding
from app.models.market_data import OHLCV

router = APIRouter()


@router.get("/portfolio/analytics")
def get_portfolio_analytics(
    db: Session = Depends(get_db)
):
    holdings = db.query(
        PortfolioHolding
    ).all()

    total_holdings = len(holdings)

    total_investment = 0.0
    current_value = 0.0

    portfolio_details = []

    for holding in holdings:

        latest_price = (
            db.query(OHLCV)
            .filter(
                OHLCV.symbol == holding.symbol
            )
            .order_by(
                OHLCV.timestamp.desc()
            )
            .first()
        )

        current_price = (
            latest_price.close
            if latest_price
            else holding.avg_buy_price
        )

        invested = (
            holding.quantity
            * holding.avg_buy_price
        )

        value = (
            holding.quantity
            * current_price
        )

        profit = value - invested

        total_investment += invested
        current_value += value

        portfolio_details.append({
            "symbol": holding.symbol,
            "quantity": holding.quantity,
            "buy_price": holding.avg_buy_price,
            "current_price": current_price,
            "investment": invested,
            "current_value": value,
            "profit_loss": profit
        })

    profit_loss = (
        current_value
        - total_investment
    )

    profit_percent = (
        (profit_loss / total_investment) * 100
        if total_investment > 0
        else 0
    )

    return {
        "total_holdings": total_holdings,
        "total_investment": round(
            total_investment, 2
        ),
        "current_value": round(
            current_value, 2
        ),
        "profit_loss": round(
            profit_loss, 2
        ),
        "profit_percent": round(
            profit_percent, 2
        ),
        "holdings": portfolio_details
    }