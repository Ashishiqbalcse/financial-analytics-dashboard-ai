from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.market_data import Alert

router = APIRouter()


@router.post("/alerts")
def create_alert(
    alert_data: dict,
    db: Session = Depends(get_db)
):
    try:
        alert = Alert(
            user_id=alert_data.get(
                "user_id",
                "demo_user"
            ),
            symbol=alert_data["symbol"].upper(),
            condition=alert_data["condition"],
            target_price=alert_data["target_price"]
        )

        db.add(alert)
        db.commit()
        db.refresh(alert)

        return {
            "message": "Alert created",
            "alert_id": alert.id
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/alerts")
def get_alerts(
    db: Session = Depends(get_db)
):
    alerts = db.query(Alert).all()

    return [
        {
            "id": a.id,
            "symbol": a.symbol,
            "condition": a.condition,
            "target_price": a.target_price,
            "active": a.is_active,
            "triggered": a.triggered
        }
        for a in alerts
    ]


@router.delete("/alerts/{alert_id}")
def delete_alert(
    alert_id: int,
    db: Session = Depends(get_db)
):
    alert = (
        db.query(Alert)
        .filter(Alert.id == alert_id)
        .first()
    )

    if not alert:
        raise HTTPException(
            status_code=404,
            detail="Alert not found"
        )

    db.delete(alert)
    db.commit()

    return {
        "message": "Alert deleted"
    }