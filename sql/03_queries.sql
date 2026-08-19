USE dalal_street_pro;

-- 1. Live portfolio P&L using VIEW
SELECT ticker, company, quantity, avg_buy_price, current_price, current_value, unrealized_pnl, pnl_pct, day_pnl
FROM v_portfolio_pnl WHERE portfolio_id = 1 ORDER BY unrealized_pnl DESC;

-- 2. Sector allocation percentage
SELECT s.sector, COUNT(DISTINCT h.stock_id) AS stocks,
       ROUND(SUM(h.quantity * s.current_price), 2) AS total_value,
       ROUND(SUM(h.quantity * s.current_price) / SUM(SUM(h.quantity * s.current_price)) OVER () * 100, 2) AS allocation_pct
FROM holdings h JOIN stocks s ON h.stock_id = s.stock_id
JOIN portfolios p ON h.portfolio_id = p.portfolio_id
WHERE p.user_id = 1 GROUP BY s.sector ORDER BY total_value DESC;

-- 3. RANK + NTILE window functions
SELECT ticker, company, pnl_pct, unrealized_pnl,
       RANK() OVER (ORDER BY pnl_pct DESC) AS pnl_rank,
       NTILE(4) OVER (ORDER BY pnl_pct DESC) AS quartile
FROM v_portfolio_pnl WHERE portfolio_id = 1;

-- 4. LAG window function for price momentum
SELECT recorded_at, close_price,
       LAG(close_price) OVER (ORDER BY recorded_at) AS prev_day,
       ROUND(close_price - LAG(close_price) OVER (ORDER BY recorded_at), 2) AS daily_change
FROM price_history WHERE stock_id = 1 ORDER BY recorded_at DESC LIMIT 30;

-- 5. CTE for sector performance ranking
WITH sector_pnl AS (
    SELECT s.sector, COUNT(*) AS holdings, ROUND(AVG(v.pnl_pct), 2) AS avg_pnl_pct
    FROM v_portfolio_pnl v JOIN stocks s ON v.ticker = s.ticker GROUP BY s.sector
)
SELECT *, RANK() OVER (ORDER BY avg_pnl_pct DESC) AS sector_rank FROM sector_pnl;

-- 6. STCG / LTCG tax classification
SELECT username, ticker, sell_price, total_value, traded_at, tax_type FROM v_tax_report ORDER BY traded_at DESC;

-- 7. SIP performance
SELECT ticker, company, total_invested, current_value, sip_pnl, sip_return_pct, next_due
FROM v_sip_performance WHERE is_active = TRUE ORDER BY sip_return_pct DESC;

-- 8. Dividend income calendar
SELECT username, ticker, shares_held, amount_per_share, income_earned, ex_date, pay_date FROM v_dividend_income ORDER BY ex_date ASC;

-- 9. Stock screener: undervalued large caps
SELECT ticker, company, sector, current_price, pe_ratio, pb_ratio, dividend_yield FROM stocks
WHERE market_cap_cat = 'LARGE_CAP' AND pe_ratio < 30 AND pe_ratio > 0 ORDER BY pe_ratio ASC;

-- 10. IPO listing gains
SELECT company_name, ticker, price_band_high, listing_price,
       ROUND((listing_price - price_band_high) / price_band_high * 100, 2) AS gain_pct, subscription_times, gmp
FROM ipos WHERE listing_price IS NOT NULL ORDER BY gain_pct DESC;

-- 11. User leaderboard with RANK and CTE
WITH user_wealth AS (
    SELECT u.user_id, u.username, u.balance,
           COALESCE(SUM(v.current_value), 0) AS holdings_value
    FROM users u LEFT JOIN portfolios p ON u.user_id = p.user_id
    LEFT JOIN v_portfolio_pnl v ON p.portfolio_id = v.portfolio_id
    GROUP BY u.user_id, u.username, u.balance
)
SELECT username, ROUND(balance + holdings_value, 2) AS total_wealth,
       RANK() OVER (ORDER BY balance + holdings_value DESC) AS rank_pos FROM user_wealth;

-- 12. Mutual fund holdings with returns
SELECT u.username, mf.fund_name, mf.category, mh.units, mh.avg_nav, mf.current_nav,
       ROUND(mh.units * mf.current_nav - mh.invested_amount, 2) AS pnl, mf.returns_1y
FROM mf_holdings mh JOIN mutual_funds mf ON mh.fund_id = mf.fund_id
JOIN portfolios p ON mh.portfolio_id = p.portfolio_id JOIN users u ON p.user_id = u.user_id;
