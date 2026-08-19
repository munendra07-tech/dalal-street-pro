CREATE DATABASE IF NOT EXISTS dalal_street_pro CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE dalal_street_pro;

CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(150) NOT NULL UNIQUE,
    phone VARCHAR(15),
    pan_number VARCHAR(10) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    balance DECIMAL(15,2) NOT NULL DEFAULT 1000000.00,
    risk_profile ENUM('CONSERVATIVE','MODERATE','AGGRESSIVE') DEFAULT 'MODERATE',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS stocks (
    stock_id INT AUTO_INCREMENT PRIMARY KEY,
    ticker VARCHAR(20) NOT NULL UNIQUE,
    company VARCHAR(200) NOT NULL,
    exchange ENUM('NSE','BSE','MCX') NOT NULL DEFAULT 'NSE',
    sector VARCHAR(100),
    industry VARCHAR(100),
    market_cap_cat ENUM('LARGE_CAP','MID_CAP','SMALL_CAP','MICRO_CAP'),
    current_price DECIMAL(12,2) NOT NULL,
    prev_close DECIMAL(12,2),
    day_high DECIMAL(12,2),
    day_low DECIMAL(12,2),
    week_52_high DECIMAL(12,2),
    week_52_low DECIMAL(12,2),
    volume BIGINT DEFAULT 0,
    pe_ratio DECIMAL(8,2),
    pb_ratio DECIMAL(8,2),
    dividend_yield DECIMAL(5,2) DEFAULT 0,
    face_value DECIMAL(8,2) DEFAULT 10,
    market_cap BIGINT,
    is_fo_enabled BOOLEAN DEFAULT FALSE,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS portfolios (
    portfolio_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    color VARCHAR(7) DEFAULT '#6366f1',
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS holdings (
    holding_id INT AUTO_INCREMENT PRIMARY KEY,
    portfolio_id INT NOT NULL,
    stock_id INT NOT NULL,
    quantity DECIMAL(12,4) NOT NULL DEFAULT 0,
    avg_buy_price DECIMAL(12,2) NOT NULL,
    FOREIGN KEY (portfolio_id) REFERENCES portfolios(portfolio_id) ON DELETE CASCADE,
    FOREIGN KEY (stock_id) REFERENCES stocks(stock_id),
    UNIQUE (portfolio_id, stock_id)
);

CREATE TABLE IF NOT EXISTS trades (
    trade_id INT AUTO_INCREMENT PRIMARY KEY,
    portfolio_id INT NOT NULL,
    stock_id INT NOT NULL,
    trade_type ENUM('BUY','SELL') NOT NULL,
    product_type ENUM('CNC','MIS','NRML') DEFAULT 'CNC',
    order_type ENUM('MARKET','LIMIT','SL','SL-M') DEFAULT 'MARKET',
    quantity DECIMAL(12,4) NOT NULL CHECK (quantity > 0),
    price DECIMAL(12,2) NOT NULL CHECK (price > 0),
    total_value DECIMAL(15,2) GENERATED ALWAYS AS (quantity * price) STORED,
    brokerage DECIMAL(10,2) DEFAULT 0,
    stt DECIMAL(10,2) DEFAULT 0,
    notes TEXT,
    traded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (portfolio_id) REFERENCES portfolios(portfolio_id) ON DELETE CASCADE,
    FOREIGN KEY (stock_id) REFERENCES stocks(stock_id)
);

CREATE TABLE IF NOT EXISTS price_history (
    history_id INT AUTO_INCREMENT PRIMARY KEY,
    stock_id INT NOT NULL,
    open_price DECIMAL(12,2),
    high_price DECIMAL(12,2),
    low_price DECIMAL(12,2),
    close_price DECIMAL(12,2) NOT NULL,
    volume BIGINT DEFAULT 0,
    recorded_at DATE NOT NULL,
    FOREIGN KEY (stock_id) REFERENCES stocks(stock_id) ON DELETE CASCADE,
    UNIQUE (stock_id, recorded_at)
);

CREATE TABLE IF NOT EXISTS alerts (
    alert_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    stock_id INT NOT NULL,
    alert_type ENUM('PRICE_ABOVE','PRICE_BELOW','PCT_CHANGE','VOLUME_SPIKE') NOT NULL,
    target_value DECIMAL(12,2) NOT NULL,
    notify_via VARCHAR(50) DEFAULT 'APP',
    is_triggered BOOLEAN DEFAULT FALSE,
    triggered_at TIMESTAMP NULL,
    is_recurring BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (stock_id) REFERENCES stocks(stock_id)
);

CREATE TABLE IF NOT EXISTS watchlist (
    watchlist_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    stock_id INT NOT NULL,
    notes TEXT,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (stock_id) REFERENCES stocks(stock_id),
    UNIQUE (user_id, stock_id)
);

CREATE TABLE IF NOT EXISTS sip_plans (
    sip_id INT AUTO_INCREMENT PRIMARY KEY,
    portfolio_id INT NOT NULL,
    stock_id INT NOT NULL,
    amount DECIMAL(12,2) NOT NULL CHECK (amount > 0),
    frequency ENUM('DAILY','WEEKLY','MONTHLY','QUARTERLY') DEFAULT 'MONTHLY',
    start_date DATE NOT NULL,
    next_due DATE NOT NULL,
    total_invested DECIMAL(15,2) DEFAULT 0,
    units_purchased DECIMAL(12,4) DEFAULT 0,
    installments_done INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (portfolio_id) REFERENCES portfolios(portfolio_id) ON DELETE CASCADE,
    FOREIGN KEY (stock_id) REFERENCES stocks(stock_id)
);

CREATE TABLE IF NOT EXISTS mutual_funds (
    fund_id INT AUTO_INCREMENT PRIMARY KEY,
    scheme_code VARCHAR(20) NOT NULL UNIQUE,
    fund_name VARCHAR(300) NOT NULL,
    fund_house VARCHAR(150),
    category ENUM('EQUITY','DEBT','HYBRID','ELSS','INDEX','LIQUID','INTERNATIONAL'),
    sub_category VARCHAR(100),
    current_nav DECIMAL(12,4) NOT NULL,
    prev_nav DECIMAL(12,4),
    aum_cr DECIMAL(15,2),
    expense_ratio DECIMAL(5,3),
    rating TINYINT CHECK (rating BETWEEN 1 AND 5),
    returns_1y DECIMAL(7,2),
    returns_3y DECIMAL(7,2),
    returns_5y DECIMAL(7,2),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS mf_holdings (
    mf_holding_id INT AUTO_INCREMENT PRIMARY KEY,
    portfolio_id INT NOT NULL,
    fund_id INT NOT NULL,
    units DECIMAL(15,4) NOT NULL,
    avg_nav DECIMAL(12,4) NOT NULL,
    invested_amount DECIMAL(15,2) NOT NULL,
    FOREIGN KEY (portfolio_id) REFERENCES portfolios(portfolio_id) ON DELETE CASCADE,
    FOREIGN KEY (fund_id) REFERENCES mutual_funds(fund_id),
    UNIQUE (portfolio_id, fund_id)
);

CREATE TABLE IF NOT EXISTS dividends (
    dividend_id INT AUTO_INCREMENT PRIMARY KEY,
    stock_id INT NOT NULL,
    amount_per_share DECIMAL(8,2) NOT NULL,
    dividend_type ENUM('INTERIM','FINAL','SPECIAL') DEFAULT 'FINAL',
    ex_date DATE NOT NULL,
    record_date DATE,
    pay_date DATE,
    FOREIGN KEY (stock_id) REFERENCES stocks(stock_id)
);

CREATE TABLE IF NOT EXISTS ipos (
    ipo_id INT AUTO_INCREMENT PRIMARY KEY,
    company_name VARCHAR(200) NOT NULL,
    ticker VARCHAR(20),
    price_band_low DECIMAL(10,2),
    price_band_high DECIMAL(10,2),
    lot_size INT NOT NULL DEFAULT 1,
    issue_size_cr DECIMAL(12,2),
    open_date DATE,
    close_date DATE,
    listing_date DATE,
    listing_price DECIMAL(10,2),
    gmp DECIMAL(10,2) DEFAULT 0,
    subscription_times DECIMAL(8,2) DEFAULT 0,
    status ENUM('UPCOMING','OPEN','CLOSED','LISTED') DEFAULT 'UPCOMING',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS benchmarks (
    benchmark_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    value DECIMAL(12,2) NOT NULL,
    change_pct DECIMAL(7,2),
    recorded_at DATE NOT NULL
);

CREATE TABLE IF NOT EXISTS market_news (
    news_id INT AUTO_INCREMENT PRIMARY KEY,
    headline TEXT NOT NULL,
    source VARCHAR(100),
    stock_id INT,
    category VARCHAR(50),
    published_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (stock_id) REFERENCES stocks(stock_id) ON DELETE SET NULL
);

CREATE INDEX idx_trades_portfolio ON trades(portfolio_id);
CREATE INDEX idx_trades_stock ON trades(stock_id);
CREATE INDEX idx_holdings_portfolio ON holdings(portfolio_id);
CREATE INDEX idx_alerts_user ON alerts(user_id);
CREATE INDEX idx_price_history ON price_history(stock_id, recorded_at);
CREATE INDEX idx_sip_due ON sip_plans(next_due, is_active);
CREATE INDEX idx_dividends_exdate ON dividends(ex_date);
CREATE INDEX idx_ipo_status ON ipos(status, open_date);
CREATE INDEX idx_watchlist_user ON watchlist(user_id);

CREATE OR REPLACE VIEW v_portfolio_pnl AS
SELECT p.portfolio_id, p.name AS portfolio_name, u.username,
       s.ticker, s.company, s.sector, s.exchange,
       h.quantity, h.avg_buy_price, s.current_price, s.prev_close,
       ROUND(h.quantity * h.avg_buy_price, 2) AS cost_basis,
       ROUND(h.quantity * s.current_price, 2) AS current_value,
       ROUND((s.current_price - h.avg_buy_price) * h.quantity, 2) AS unrealized_pnl,
       ROUND((s.current_price - h.avg_buy_price) / h.avg_buy_price * 100, 2) AS pnl_pct,
       ROUND((s.current_price - COALESCE(s.prev_close, s.current_price)) * h.quantity, 2) AS day_pnl
FROM holdings h
JOIN portfolios p ON h.portfolio_id = p.portfolio_id
JOIN users u ON p.user_id = u.user_id
JOIN stocks s ON h.stock_id = s.stock_id;

CREATE OR REPLACE VIEW v_dividend_income AS
SELECT u.user_id, u.username, s.ticker, s.company,
       d.amount_per_share, d.ex_date, d.pay_date, d.dividend_type,
       COALESCE(h.quantity, 0) AS shares_held,
       ROUND(COALESCE(h.quantity, 0) * d.amount_per_share, 2) AS income_earned
FROM dividends d
JOIN stocks s ON d.stock_id = s.stock_id
JOIN holdings h ON h.stock_id = s.stock_id
JOIN portfolios p ON h.portfolio_id = p.portfolio_id
JOIN users u ON p.user_id = u.user_id;

CREATE OR REPLACE VIEW v_tax_report AS
SELECT u.username, s.ticker, t.trade_type, t.quantity,
       t.price AS sell_price, t.total_value, t.traded_at,
       CASE WHEN DATEDIFF(t.traded_at, MIN(t2.traded_at)) < 365 THEN 'STCG' ELSE 'LTCG' END AS tax_type
FROM trades t
JOIN trades t2 ON t.stock_id = t2.stock_id AND t2.trade_type = 'BUY'
JOIN portfolios p ON t.portfolio_id = p.portfolio_id
JOIN users u ON p.user_id = u.user_id
JOIN stocks s ON t.stock_id = s.stock_id
WHERE t.trade_type = 'SELL'
GROUP BY t.trade_id, u.username, s.ticker, t.trade_type, t.quantity, t.price, t.total_value, t.traded_at;

CREATE OR REPLACE VIEW v_sip_performance AS
SELECT sp.sip_id, sp.portfolio_id, u.username, s.ticker, s.company,
       sp.amount, sp.frequency, sp.installments_done,
       sp.total_invested, sp.units_purchased,
       ROUND(sp.units_purchased * s.current_price, 2) AS current_value,
       ROUND(sp.units_purchased * s.current_price - sp.total_invested, 2) AS sip_pnl,
       ROUND((sp.units_purchased * s.current_price - sp.total_invested) / NULLIF(sp.total_invested, 0) * 100, 2) AS sip_return_pct,
       sp.next_due, sp.is_active
FROM sip_plans sp
JOIN portfolios p ON sp.portfolio_id = p.portfolio_id
JOIN users u ON p.user_id = u.user_id
JOIN stocks s ON sp.stock_id = s.stock_id;
