from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Literal, Optional
from app.database import query
from app.auth import get_current_user

router = APIRouter(prefix="/portfolio", tags=["Portfolio"])

class TradeRequest(BaseModel):
    ticker: str
    trade_type: Literal["BUY", "SELL"]
    product_type: Literal["CNC", "MIS", "NRML"] = "CNC"
    order_type: Literal["MARKET", "LIMIT", "SL", "SL-M"] = "MARKET"
    quantity: float
    price: float
    notes: Optional[str] = None

class SIPRequest(BaseModel):
    ticker: str
    amount: float
    frequency: Literal["DAILY", "WEEKLY", "MONTHLY", "QUARTERLY"] = "MONTHLY"
    start_date: str

@router.get("/all")
def all_portfolios(user: dict = Depends(get_current_user)):
    return query(
        "SELECT p.*, COUNT(h.holding_id) AS holdings_count FROM portfolios p "
        "LEFT JOIN holdings h ON p.portfolio_id=h.portfolio_id WHERE p.user_id=%s "
        "GROUP BY p.portfolio_id ORDER BY p.is_default DESC",
        (user["user_id"],), fetch=True
    )

@router.get("/{portfolio_id}")
def get_portfolio(portfolio_id: int, user: dict = Depends(get_current_user)):
    holdings = query("SELECT * FROM v_portfolio_pnl WHERE portfolio_id=%s ORDER BY current_value DESC", (portfolio_id,), fetch=True)
    ti = sum(float(h["cost_basis"] or 0) for h in holdings)
    tv = sum(float(h["current_value"] or 0) for h in holdings)
    tp = sum(float(h["unrealized_pnl"] or 0) for h in holdings)
    dp = sum(float(h["day_pnl"] or 0) for h in holdings)
    return {
        "portfolio_id": portfolio_id, "holdings": holdings,
        "summary": {
            "total_invested": round(ti, 2), "current_value": round(tv, 2),
            "unrealized_pnl": round(tp, 2), "pnl_pct": round(tp / ti * 100, 2) if ti else 0,
            "day_pnl": round(dp, 2), "holdings_count": len(holdings)
        }
    }

@router.post("/{portfolio_id}/trade")
def execute_trade(portfolio_id: int, trade: TradeRequest, user: dict = Depends(get_current_user)):
    stocks = query("SELECT * FROM stocks WHERE ticker=%s", (trade.ticker.upper(),), fetch=True)
    if not stocks:
        raise HTTPException(404, f"Stock '{trade.ticker}' not found")
    stock = stocks[0]
    total = round(trade.quantity * trade.price, 2)
    brokerage = min(round(total * 0.0003, 2), 20.0)
    stt = round(total * 0.001, 2)

    if trade.trade_type == "BUY":
        existing = query("SELECT * FROM holdings WHERE portfolio_id=%s AND stock_id=%s", (portfolio_id, stock["stock_id"]), fetch=True)
        if existing:
            h = existing[0]
            new_qty = float(h["quantity"]) + trade.quantity
            new_avg = (float(h["quantity"]) * float(h["avg_buy_price"]) + total) / new_qty
            query("UPDATE holdings SET quantity=%s, avg_buy_price=%s WHERE portfolio_id=%s AND stock_id=%s",
                  (new_qty, round(new_avg, 2), portfolio_id, stock["stock_id"]))
        else:
            query("INSERT INTO holdings (portfolio_id, stock_id, quantity, avg_buy_price) VALUES (%s,%s,%s,%s)",
                  (portfolio_id, stock["stock_id"], trade.quantity, trade.price))
    else:
        existing = query("SELECT * FROM holdings WHERE portfolio_id=%s AND stock_id=%s", (portfolio_id, stock["stock_id"]), fetch=True)
        if not existing or float(existing[0]["quantity"]) < trade.quantity:
            raise HTTPException(400, "Insufficient shares to sell")
        new_qty = float(existing[0]["quantity"]) - trade.quantity
        if new_qty == 0:
            query("DELETE FROM holdings WHERE portfolio_id=%s AND stock_id=%s", (portfolio_id, stock["stock_id"]))
        else:
            query("UPDATE holdings SET quantity=%s WHERE portfolio_id=%s AND stock_id=%s", (new_qty, portfolio_id, stock["stock_id"]))

    query(
        "INSERT INTO trades (portfolio_id, stock_id, trade_type, product_type, order_type, quantity, price, brokerage, stt, notes) "
        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
        (portfolio_id, stock["stock_id"], trade.trade_type, trade.product_type, trade.order_type,
         trade.quantity, trade.price, brokerage, stt, trade.notes)
    )
    query(
        "UPDATE alerts SET is_triggered=TRUE, triggered_at=NOW() WHERE stock_id=%s AND is_triggered=FALSE "
        "AND ((alert_type='PRICE_ABOVE' AND %s>=target_value) OR (alert_type='PRICE_BELOW' AND %s<=target_value))",
        (stock["stock_id"], trade.price, trade.price)
    )
    return {"message": f"{trade.trade_type} {trade.quantity} {trade.ticker.upper()} @ Rs{trade.price}",
            "total": total, "brokerage": brokerage, "stt": stt}

@router.get("/{portfolio_id}/trades")
def trade_history(portfolio_id: int, user: dict = Depends(get_current_user)):
    return query(
        "SELECT t.*, s.ticker, s.company, s.exchange FROM trades t JOIN stocks s ON t.stock_id=s.stock_id "
        "WHERE t.portfolio_id=%s ORDER BY t.traded_at DESC",
        (portfolio_id,), fetch=True
    )

@router.get("/{portfolio_id}/pnl")
def pnl_report(portfolio_id: int, user: dict = Depends(get_current_user)):
    unrealized = query("SELECT * FROM v_portfolio_pnl WHERE portfolio_id=%s", (portfolio_id,), fetch=True)
    realized = query(
        "SELECT s.ticker, t.trade_type, t.quantity, t.price, t.total_value, t.brokerage, t.stt, t.traded_at, "
        "CASE WHEN DATEDIFF(NOW(),t.traded_at)<365 THEN 'STCG' ELSE 'LTCG' END AS tax_type "
        "FROM trades t JOIN stocks s ON t.stock_id=s.stock_id "
        "WHERE t.portfolio_id=%s AND t.trade_type='SELL' ORDER BY t.traded_at DESC",
        (portfolio_id,), fetch=True
    )
    stcg = sum(float(r["total_value"] or 0) for r in realized if r["tax_type"] == "STCG")
    ltcg = sum(float(r["total_value"] or 0) for r in realized if r["tax_type"] == "LTCG")
    return {
        "unrealized": unrealized, "realized": realized,
        "tax_summary": {"stcg": round(stcg, 2), "ltcg": round(ltcg, 2),
                        "stcg_tax": round(stcg * 0.15, 2), "ltcg_tax": round(ltcg * 0.10, 2)}
    }

@router.post("/{portfolio_id}/sip")
def create_sip(portfolio_id: int, sip: SIPRequest, user: dict = Depends(get_current_user)):
    stocks = query("SELECT * FROM stocks WHERE ticker=%s", (sip.ticker.upper(),), fetch=True)
    if not stocks:
        raise HTTPException(404, "Stock not found")
    query(
        "INSERT INTO sip_plans (portfolio_id, stock_id, amount, frequency, start_date, next_due) VALUES (%s,%s,%s,%s,%s,%s)",
        (portfolio_id, stocks[0]["stock_id"], sip.amount, sip.frequency, sip.start_date, sip.start_date)
    )
    return {"message": f"SIP of Rs{sip.amount} created for {sip.ticker.upper()} ({sip.frequency})"}

@router.get("/{portfolio_id}/sip")
def get_sips(portfolio_id: int, user: dict = Depends(get_current_user)):
    return query("SELECT * FROM v_sip_performance WHERE portfolio_id=%s ORDER BY sip_return_pct DESC", (portfolio_id,), fetch=True)
