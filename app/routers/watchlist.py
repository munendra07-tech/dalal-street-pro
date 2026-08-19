from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.database import query
from app.auth import get_current_user

router = APIRouter(prefix="/watchlist", tags=["Watchlist"])

class WatchlistAdd(BaseModel):
    ticker: str
    notes: str = ""

@router.get("/")
def get_watchlist(user: dict = Depends(get_current_user)):
    return query("""
        SELECT w.watchlist_id, s.ticker, s.company, s.exchange, s.sector,
               s.current_price, s.prev_close, s.pe_ratio, s.pb_ratio,
               s.week_52_high, s.week_52_low, s.dividend_yield, s.market_cap_cat,
               ROUND((s.current_price-s.prev_close)/s.prev_close*100,2) AS change_pct,
               w.notes, w.added_at
        FROM watchlist w JOIN stocks s ON w.stock_id=s.stock_id
        WHERE w.user_id=%s ORDER BY w.added_at DESC
    """, (user["user_id"],), fetch=True)

@router.post("/")
def add_to_watchlist(body: WatchlistAdd, user: dict = Depends(get_current_user)):
    s = query("SELECT stock_id FROM stocks WHERE ticker=%s", (body.ticker.upper(),), fetch=True)
    if not s:
        raise HTTPException(404, "Stock not found")
    try:
        query("INSERT INTO watchlist (user_id, stock_id, notes) VALUES (%s,%s,%s)", (user["user_id"], s[0]["stock_id"], body.notes))
    except Exception:
        raise HTTPException(400, "Already in watchlist")
    return {"message": f"{body.ticker.upper()} added to watchlist"}

@router.delete("/{watchlist_id}")
def remove(watchlist_id: int, user: dict = Depends(get_current_user)):
    if not query("DELETE FROM watchlist WHERE watchlist_id=%s AND user_id=%s", (watchlist_id, user["user_id"])):
        raise HTTPException(404, "Not found")
    return {"message": "Removed from watchlist"}
