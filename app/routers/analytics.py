from fastapi import APIRouter, Depends
from app.database import query
from app.auth import get_current_user

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/market-overview")
def market_overview():
    return {
        "indices": query("SELECT * FROM benchmarks ORDER BY recorded_at DESC LIMIT 5", fetch=True),
        "gainers": query(
            "SELECT ticker,company,sector,current_price,prev_close,"
            "ROUND((current_price-prev_close)/prev_close*100,2) AS change_pct "
            "FROM stocks WHERE prev_close>0 ORDER BY change_pct DESC LIMIT 5", fetch=True
        ),
        "losers": query(
            "SELECT ticker,company,sector,current_price,prev_close,"
            "ROUND((current_price-prev_close)/prev_close*100,2) AS change_pct "
            "FROM stocks WHERE prev_close>0 ORDER BY change_pct ASC LIMIT 5", fetch=True
        ),
        "news": query(
            "SELECT n.*,s.ticker FROM market_news n LEFT JOIN stocks s ON n.stock_id=s.stock_id "
            "ORDER BY n.published_at DESC LIMIT 8", fetch=True
        ),
    }

@router.get("/leaderboard")
def leaderboard():
    return query("""
        WITH uw AS (
            SELECT u.user_id, u.username, u.risk_profile, u.balance,
                   COALESCE(SUM(v.current_value),0) AS hv,
                   COALESCE(SUM(v.unrealized_pnl),0) AS tp
            FROM users u
            LEFT JOIN portfolios p ON u.user_id=p.user_id
            LEFT JOIN v_portfolio_pnl v ON p.portfolio_id=v.portfolio_id
            GROUP BY u.user_id, u.username, u.risk_profile, u.balance
        )
        SELECT username, risk_profile, ROUND(balance,2) AS cash, ROUND(hv,2) AS holdings,
               ROUND(balance+hv,2) AS total_wealth, ROUND(tp,2) AS unrealized_pnl,
               RANK() OVER (ORDER BY balance+hv DESC) AS rank_pos
        FROM uw ORDER BY total_wealth DESC
    """, fetch=True)

@router.get("/sector-breakdown/{portfolio_id}")
def sector_breakdown(portfolio_id: int, user: dict = Depends(get_current_user)):
    return query("""
        SELECT s.sector, COUNT(*) AS stocks,
               ROUND(SUM(v.current_value),2) AS total_value,
               ROUND(SUM(v.unrealized_pnl),2) AS total_pnl,
               ROUND(AVG(v.pnl_pct),2) AS avg_pnl_pct,
               ROUND(SUM(v.current_value)/SUM(SUM(v.current_value)) OVER()*100,2) AS allocation_pct
        FROM v_portfolio_pnl v JOIN stocks s ON v.ticker=s.ticker
        WHERE v.portfolio_id=%s GROUP BY s.sector ORDER BY total_value DESC
    """, (portfolio_id,), fetch=True)

@router.get("/benchmark/{portfolio_id}")
def benchmark(portfolio_id: int, user: dict = Depends(get_current_user)):
    h = query("SELECT * FROM v_portfolio_pnl WHERE portfolio_id=%s", (portfolio_id,), fetch=True)
    ti = sum(float(x["cost_basis"] or 0) for x in h)
    tv = sum(float(x["current_value"] or 0) for x in h)
    pr = round((tv - ti) / ti * 100, 2) if ti else 0
    b = query("SELECT * FROM benchmarks ORDER BY recorded_at DESC LIMIT 5", fetch=True)
    nc = float(b[0]["change_pct"] or 0) if b else 0
    return {"portfolio_return_pct": pr, "alpha_vs_nifty": round(pr - nc, 2), "benchmarks": b}

@router.get("/breadth")
def market_breadth():
    """
    Section 21: market-wide advance/decline based on the `stocks` table's
    current_price vs prev_close, which is kept fresh by the
    update_stock_quotes sync job. Real counts from real data -- no
    fabricated breadth numbers.
    """
    rows = query(
        """
        SELECT
            SUM(CASE WHEN current_price > prev_close THEN 1 ELSE 0 END) AS advancing,
            SUM(CASE WHEN current_price < prev_close THEN 1 ELSE 0 END) AS declining,
            SUM(CASE WHEN current_price = prev_close THEN 1 ELSE 0 END) AS unchanged,
            SUM(CASE WHEN current_price >= week_52_high THEN 1 ELSE 0 END) AS new_52w_highs,
            SUM(CASE WHEN current_price <= week_52_low THEN 1 ELSE 0 END) AS new_52w_lows,
            SUM(CASE WHEN current_price > prev_close THEN volume ELSE 0 END) AS advancing_volume,
            SUM(CASE WHEN current_price < prev_close THEN volume ELSE 0 END) AS declining_volume
        FROM stocks WHERE active = TRUE AND prev_close > 0
        """,
        fetch=True,
    )
    r = rows[0] if rows else {}
    adv, dec = r.get("advancing") or 0, r.get("declining") or 0
    r["advance_decline_ratio"] = round(adv / dec, 2) if dec else None
    return r


@router.get("/sectors")
def sector_performance():
    """
    Section 22: market-wide (not per-portfolio) sector analytics --
    return, momentum proxy, breadth, and top/weakest stock per sector.
    """
    sectors = query(
        """
        SELECT
            sector,
            COUNT(*) AS stock_count,
            ROUND(AVG((current_price - prev_close) / NULLIF(prev_close, 0) * 100), 2) AS avg_change_pct,
            SUM(CASE WHEN current_price > prev_close THEN 1 ELSE 0 END) AS advancing,
            SUM(CASE WHEN current_price < prev_close THEN 1 ELSE 0 END) AS declining
        FROM stocks
        WHERE active = TRUE AND prev_close > 0 AND sector IS NOT NULL
        GROUP BY sector
        ORDER BY avg_change_pct DESC
        """,
        fetch=True,
    )
    for s in sectors:
        top = query(
            """
            SELECT ticker, ROUND((current_price-prev_close)/NULLIF(prev_close,0)*100,2) AS change_pct
            FROM stocks WHERE sector=%s AND active=TRUE AND prev_close>0
            ORDER BY change_pct DESC LIMIT 1
            """, (s["sector"],), fetch=True,
        )
        weak = query(
            """
            SELECT ticker, ROUND((current_price-prev_close)/NULLIF(prev_close,0)*100,2) AS change_pct
            FROM stocks WHERE sector=%s AND active=TRUE AND prev_close>0
            ORDER BY change_pct ASC LIMIT 1
            """, (s["sector"],), fetch=True,
        )
        s["top_stock"] = top[0] if top else None
        s["weakest_stock"] = weak[0] if weak else None
    return sectors


@router.get("/dividends/{user_id}")
def dividends(user_id: int, user: dict = Depends(get_current_user)):
    d = query("SELECT * FROM v_dividend_income WHERE user_id=%s ORDER BY ex_date ASC", (user_id,), fetch=True)
    return {"dividends": d, "total_projected_income": round(sum(float(x["income_earned"] or 0) for x in d), 2)}
