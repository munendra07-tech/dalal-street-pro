from fastapi import APIRouter, HTTPException
from typing import Optional
from app.database import query

router = APIRouter(prefix="/stocks", tags=["Stocks"])

@router.get("/")
def list_stocks(exchange: Optional[str] = None, sector: Optional[str] = None, market_cap: Optional[str] = None):
    sql = "SELECT * FROM stocks WHERE 1=1"
    params = []
    if exchange: sql += " AND exchange=%s"; params.append(exchange.upper())
    if sector: sql += " AND sector=%s"; params.append(sector)
    if market_cap: sql += " AND market_cap_cat=%s"; params.append(market_cap.upper())
    return query(sql + " ORDER BY market_cap DESC", tuple(params), fetch=True)

@router.get("/screener")
def screener(pe_max: Optional[float] = None, pe_min: Optional[float] = None,
             div_min: Optional[float] = None, pb_max: Optional[float] = None,
             sector: Optional[str] = None, market_cap: Optional[str] = None):
    sql = "SELECT * FROM stocks WHERE 1=1"
    params = []
    if pe_max: sql += " AND pe_ratio<=%s AND pe_ratio>0"; params.append(pe_max)
    if pe_min: sql += " AND pe_ratio>=%s"; params.append(pe_min)
    if div_min: sql += " AND dividend_yield>=%s"; params.append(div_min)
    if pb_max: sql += " AND pb_ratio<=%s AND pb_ratio>0"; params.append(pb_max)
    if sector: sql += " AND sector=%s"; params.append(sector)
    if market_cap: sql += " AND market_cap_cat=%s"; params.append(market_cap.upper())
    return query(sql + " ORDER BY pe_ratio ASC", tuple(params), fetch=True)

@router.get("/top-gainers")
def top_gainers():
    return query(
        "SELECT ticker,company,sector,current_price,prev_close,"
        "ROUND((current_price-prev_close)/prev_close*100,2) AS change_pct "
        "FROM stocks WHERE prev_close>0 ORDER BY change_pct DESC LIMIT 10", fetch=True
    )

@router.get("/top-losers")
def top_losers():
    return query(
        "SELECT ticker,company,sector,current_price,prev_close,"
        "ROUND((current_price-prev_close)/prev_close*100,2) AS change_pct "
        "FROM stocks WHERE prev_close>0 ORDER BY change_pct ASC LIMIT 10", fetch=True
    )

@router.get("/{ticker}")
def get_stock(ticker: str):
    rows = query("SELECT * FROM stocks WHERE ticker=%s", (ticker.upper(),), fetch=True)
    if not rows:
        raise HTTPException(404, f"Stock '{ticker}' not found")
    s = rows[0]
    s["price_history"] = query(
        "SELECT recorded_at,open_price,high_price,low_price,close_price,volume FROM price_history "
        "WHERE stock_id=%s ORDER BY recorded_at DESC LIMIT 60", (s["stock_id"],), fetch=True
    )
    s["upcoming_dividends"] = query(
        "SELECT amount_per_share,dividend_type,ex_date,pay_date FROM dividends "
        "WHERE stock_id=%s AND ex_date>=CURDATE() ORDER BY ex_date", (s["stock_id"],), fetch=True
    )
    return s

@router.get("/{ticker}/history")
def price_history(ticker: str, days: int = 30):
    rows = query("SELECT stock_id FROM stocks WHERE ticker=%s", (ticker.upper(),), fetch=True)
    if not rows:
        raise HTTPException(404, "Stock not found")
    return query(
        "SELECT recorded_at,open_price,high_price,low_price,close_price,volume,"
        "ROUND(close_price-LAG(close_price) OVER (ORDER BY recorded_at),2) AS daily_change "
        "FROM price_history WHERE stock_id=%s ORDER BY recorded_at DESC LIMIT %s",
        (rows[0]["stock_id"], days), fetch=True
    )
