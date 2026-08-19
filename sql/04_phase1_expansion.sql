ALTER TABLE stocks ADD COLUMN isin VARCHAR(12) NULL UNIQUE AFTER ticker;
ALTER TABLE stocks ADD COLUMN active BOOLEAN NOT NULL DEFAULT TRUE AFTER is_fo_enabled;
ALTER TABLE stocks ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP AFTER active;

CREATE TABLE IF NOT EXISTS data_sync_log (
    sync_id INT AUTO_INCREMENT PRIMARY KEY,
    job_name VARCHAR(100) NOT NULL,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    status ENUM('RUNNING','SUCCESS','PARTIAL','FAILED') NOT NULL DEFAULT 'RUNNING',
    records_processed INT DEFAULT 0,
    records_failed INT DEFAULT 0,
    error_message TEXT NULL,
    INDEX idx_job_started (job_name, started_at)
);

CREATE TABLE IF NOT EXISTS predictions (
    prediction_id INT AUTO_INCREMENT PRIMARY KEY,
    stock_id INT NOT NULL,
    prediction_date DATE NOT NULL,
    model VARCHAR(50) NOT NULL,
    prediction ENUM('UP','DOWN','NEUTRAL') NOT NULL,
    up_probability DECIMAL(5,2) NOT NULL,
    down_probability DECIMAL(5,2) NOT NULL,
    confidence DECIMAL(5,2) NOT NULL,
    `signal` ENUM('BUY','SELL','HOLD') NOT NULL,
    feature_version VARCHAR(20) DEFAULT 'v1',
    actual_outcome ENUM('UP','DOWN') NULL,
    correct BOOLEAN NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (stock_id) REFERENCES stocks(stock_id) ON DELETE CASCADE,
    UNIQUE (stock_id, prediction_date, model),
    INDEX idx_pred_date (prediction_date)
);

CREATE TABLE IF NOT EXISTS model_metrics (
    metric_id INT AUTO_INCREMENT PRIMARY KEY,
    model VARCHAR(50) NOT NULL,
    version VARCHAR(20) NOT NULL DEFAULT 'v1',
    training_period_start DATE,
    training_period_end DATE,
    validation_period_start DATE,
    validation_period_end DATE,
    accuracy DECIMAL(6,4),
    precision_score DECIMAL(6,4),
    recall_score DECIMAL(6,4),
    f1_score DECIMAL(6,4),
    roc_auc DECIMAL(6,4),
    sample_count INT,
    feature_count INT DEFAULT 19,
    evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_model_version (model, version)
);

