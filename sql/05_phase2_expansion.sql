ALTER TABLE market_news ADD COLUMN url VARCHAR(500) NULL AFTER source;
ALTER TABLE market_news ADD COLUMN sentiment_label ENUM('POSITIVE','NEUTRAL','NEGATIVE') NULL AFTER category;
ALTER TABLE market_news ADD COLUMN sentiment_score DECIMAL(5,2) NULL AFTER sentiment_label;

CREATE TABLE IF NOT EXISTS fundamentals (
    fundamental_id INT AUTO_INCREMENT PRIMARY KEY,
    stock_id INT NOT NULL,
    pe_ratio DECIMAL(10,2),
    pb_ratio DECIMAL(10,2),
    eps DECIMAL(12,2),
    revenue BIGINT,
    net_profit BIGINT,
    profit_growth_pct DECIMAL(6,2),
    debt_to_equity DECIMAL(8,2),
    roe DECIMAL(6,2),
    roce DECIMAL(6,2),
    dividend_yield DECIMAL(5,2),
    market_cap BIGINT,
    book_value DECIMAL(12,2),
    fundamental_score DECIMAL(5,2),
    source VARCHAR(50) DEFAULT 'Yahoo Finance',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (stock_id) REFERENCES stocks(stock_id) ON DELETE CASCADE,
    UNIQUE (stock_id)
);

CREATE TABLE IF NOT EXISTS market_regime_log (
    regime_id INT AUTO_INCREMENT PRIMARY KEY,
    regime ENUM('BULLISH','BEARISH','SIDEWAYS','HIGH_VOLATILITY') NOT NULL,
    confidence DECIMAL(5,2) NOT NULL,
    nifty_trend VARCHAR(20),
    volatility_20d DECIMAL(8,4),
    breadth_score DECIMAL(6,2),
    evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_evaluated (evaluated_at)
);

