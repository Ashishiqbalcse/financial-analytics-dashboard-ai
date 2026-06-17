from pydantic import BaseModel

class PortfolioCreate(BaseModel):
    symbol: str
    quantity: float
    avg_buy_price: float


class PortfolioResponse(PortfolioCreate):
    id: int

    class Config:
        from_attributes = True