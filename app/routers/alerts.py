from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Literal
from app.database import query
from app.auth import get_current_user

router = APIRouter(prefix="/alerts", tags=["Alerts"])

class AlertCreate(BaseModel):
    ticker: str
    alert_type: Literal["PRICE_ABOVE", "PRICE_BELOW", "PCT_CHANGE", "VOLUME_SPIKE"]
    target_value: float
    notify_via: str = "APP"
    is_recurring: bool = False

@router.get("/")
def get_alerts(user: dict = Depends(get_current_user)):
    return query("""
        SELECT a.*, s.ticker, s.company, s.current_price,
               CASE WHEN a.alert_type='PRICE_ABOVE' AND s.current_price>=a.target_value THEN 'TRIGGERED'
                    WHEN a.alert_type='PRICE_BELOW' AND s.current_price<=a.target_value THEN 'TRIGGERED'
                    ELSE 'PENDING' END AS live_status
        FROM alerts a JOIN stocks s ON a.stock_id=s.stock_id
        WHERE a.user_id=%s ORDER BY a.created_at DESC
    """, (user["user_id"],), fetch=True)

@router.post("/")
def create_alert(body: AlertCreate, user: dict = Depends(get_current_user)):
    s = query("SELECT stock_id FROM stocks WHERE ticker=%s", (body.ticker.upper(),), fetch=True)
    if not s:
        raise HTTPException(404, "Stock not found")
    query(
        "INSERT INTO alerts (user_id, stock_id, alert_type, target_value, notify_via, is_recurring) VALUES (%s,%s,%s,%s,%s,%s)",
        (user["user_id"], s[0]["stock_id"], body.alert_type, body.target_value, body.notify_via, body.is_recurring)
    )
    return {"message": f"Alert set: {body.ticker.upper()} {body.alert_type} Rs{body.target_value}"}

@router.delete("/{alert_id}")
def delete_alert(alert_id: int, user: dict = Depends(get_current_user)):
    if not query("DELETE FROM alerts WHERE alert_id=%s AND user_id=%s", (alert_id, user["user_id"])):
        raise HTTPException(404, "Alert not found")
    return {"message": "Alert deleted"}
