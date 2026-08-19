from fastapi import APIRouter
from typing import Optional
from app.database import query

router = APIRouter(prefix="/ipo", tags=["IPO"])

@router.get("/")
def list_ipos(status: Optional[str] = None):
    if status:
        return query("SELECT * FROM ipos WHERE status=%s ORDER BY open_date DESC", (status.upper(),), fetch=True)
    return query("SELECT * FROM ipos ORDER BY open_date DESC", fetch=True)

@router.get("/upcoming")
def upcoming():
    return query("SELECT * FROM ipos WHERE status IN ('UPCOMING','OPEN') ORDER BY open_date ASC", fetch=True)

@router.get("/performance")
def performance():
    return query(
        "SELECT company_name,ticker,price_band_high,listing_price,"
        "ROUND((listing_price-price_band_high)/price_band_high*100,2) AS listing_gain_pct,"
        "subscription_times,gmp,status FROM ipos WHERE listing_price IS NOT NULL ORDER BY listing_gain_pct DESC",
        fetch=True
    )
