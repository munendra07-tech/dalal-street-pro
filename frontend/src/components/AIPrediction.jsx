import { useState, useEffect, useCallback } from "react";
import { api } from "../services/api";

// initialTicker: optional -- when provided (e.g. opened from the Stock
// Detail panel or AI Screener), auto-runs analysis on mount instead of
// waiting for the user to type a ticker and press Analyze.
export default function AIPrediction({ initialTicker }) {
  const [ticker, setTicker] = useState(initialTicker || "RELIANCE.NS");
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const predict = useCallback(async (t) => {
    const target = (t || ticker).trim().toUpperCase();
    setLoading(true);
    setError("");

    try {
      const result = await api.aiPrediction(target);
      setData(result);
    } catch (err) {
      setError(err.message || "Prediction failed");
      setData(null);
    } finally {
      setLoading(false);
    }
  }, [ticker]);

  useEffect(() => {
    if (initialTicker) {
      setTicker(initialTicker);
      predict(initialTicker);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [initialTicker]);

  const signalClass = signal => {
    if (signal === "BUY") return "ai-buy";
    if (signal === "SELL") return "ai-sell";
    return "ai-hold";
  };

  return (
    <section className="ai-card">

      <div className="ai-header">
        <div>
          <h2>🤖 AI Stock Intelligence</h2>
          <p>
            Multi-model market prediction powered by
            Random Forest, XGBoost and Logistic Regression.
          </p>
        </div>

        <div className="ai-search">
          <input
            value={ticker}
            onChange={e => setTicker(e.target.value)}
            placeholder="RELIANCE.NS"
          />

          <button
            onClick={() => predict()}
            disabled={loading || !ticker.trim()}
          >
            {loading ? "Analyzing..." : "Analyze"}
          </button>
        </div>
      </div>

      {error && (
        <div className="ai-error">
          {error}
        </div>
      )}

      {loading && (
        <div className="ai-loading">
          Training AI models and analyzing market data...
        </div>
      )}

      {data && !loading && (
        <>
          <div className="ai-main-grid">

            <div className="ai-prediction-box">
              <span>AI Prediction</span>

              <strong>
                {data.prediction}
              </strong>

              <div
                className={signalClass(data.signal)}
              >
                {data.signal}
              </div>

              <small>
                Confidence: {data.confidence}%
              </small>
            </div>

            <div className="ai-stat">
              <span>Current Price</span>
              <strong>
                ₹{Number(data.current_price).toFixed(2)}
              </strong>
            </div>

            <div className="ai-stat">
              <span>UP Probability</span>
              <strong>
                {data.up_probability}%
              </strong>
            </div>

            <div className="ai-stat">
              <span>DOWN Probability</span>
              <strong>
                {data.down_probability}%
              </strong>
            </div>

          </div>

          <div className="ai-section">
            <h3>Model Predictions</h3>

            <div className="model-grid">
              {Object.entries(
                data.models || {}
              ).map(([model, probability]) => (
                <div
                  className="model-card"
                  key={model}
                >
                  <span>{model}</span>

                  <strong>
                    {probability}%
                  </strong>

                  <div className="probability-bar">
                    <div
                      style={{
                        width: `${probability}%`
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="ai-section">
            <h3>Technical Indicators</h3>

            <div className="indicator-grid">

              <Indicator
                name="RSI"
                value={data.indicators?.rsi}
              />

              <Indicator
                name="MACD"
                value={data.indicators?.macd}
              />

              <Indicator
                name="MACD Signal"
                value={data.indicators?.macd_signal}
              />

              <Indicator
                name="SMA 20"
                value={data.indicators?.sma20}
              />

              <Indicator
                name="SMA 50"
                value={data.indicators?.sma50}
              />

              <Indicator
                name="SMA 200"
                value={data.indicators?.sma200}
              />

              <Indicator
                name="Volatility"
                value={data.indicators?.volatility_20}
              />

              <Indicator
                name="ATR"
                value={data.indicators?.atr}
              />

            </div>
          </div>

          <div className="ai-bottom-grid">

            <div className="ai-section">
              <h3>🧠 AI Explanation</h3>

              {data.explanation?.reasons?.map(
                (reason, index) => (
                  <div
                    className="ai-reason"
                    key={index}
                  >
                    ✓ {reason}
                  </div>
                )
              )}

              {data.explanation?.warnings?.map(
                (warning, index) => (
                  <div
                    className="ai-warning"
                    key={index}
                  >
                    ⚠ {warning}
                  </div>
                )
              )}

              <p>
                {data.explanation?.summary}
              </p>
            </div>

            <div className="ai-section">
              <h3>⚠ Risk Assessment</h3>

              <div className="risk-score">
                {data.risk?.score}
                <small>/100</small>
              </div>

              <strong>
                {data.risk?.level}
              </strong>

              {data.risk?.factors?.map(
                (factor, index) => (
                  <div
                    className="ai-reason"
                    key={index}
                  >
                    • {factor}
                  </div>
                )
              )}
            </div>

          </div>

          <div className="ai-disclaimer">
            AI predictions are estimates based on historical
            market data and technical indicators. They are
            not guaranteed future returns or financial advice.
          </div>
        </>
      )}
    </section>
  );
}


function Indicator({ name, value }) {
  const number = Number(value);

  return (
    <div className="indicator">
      <span>{name}</span>
      <strong>
        {Number.isFinite(number)
          ? number.toFixed(2)
          : "--"}
      </strong>
    </div>
  );
}