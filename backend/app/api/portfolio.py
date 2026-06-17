from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.portfolio import PortfolioHolding
from app.schemas.portfolio import (
    PortfolioCreate,
    PortfolioResponse,
)

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post(
    "/portfolio",
    response_model=PortfolioResponse
)
def add_holding(
    holding: PortfolioCreate,
    db: Session = Depends(get_db)
):
    new_holding = PortfolioHolding(
        symbol=holding.symbol.upper(),
        quantity=holding.quantity,
        avg_buy_price=holding.avg_buy_price
    )

    db.add(new_holding)
    db.commit()
    db.refresh(new_holding)

    return new_holding


@router.get("/portfolio")
def get_portfolio(
    db: Session = Depends(get_db)
):
    return db.query(
        PortfolioHolding
    ).all()


@router.delete("/portfolio/{holding_id}")
def delete_holding(
    holding_id: int,
    db: Session = Depends(get_db)
):
    holding = db.query(
        PortfolioHolding
    ).filter(
        PortfolioHolding.id == holding_id
    ).first()

    if holding:
        db.delete(holding)
        db.commit()

    return {
        "status": "deleted"
    }