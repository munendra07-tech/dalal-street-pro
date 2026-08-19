import { useState, useEffect } from "react";
import { api } from "../services/api";
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import AIPrediction from "./AIPrediction";

const PERIODS = ["5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "max"];

const S = {
  overlay: { position: "fixed", inset: 0, background: "rgba(0,0,0,.6)", zIndex: 50, display: "flex", justifyContent: "flex-end" },
  panel: { width: "min(880px, 100%)", height: "100%", background: "#0a0d14", overflowY: "auto", borderLeft: "1px solid #1f2937" },
  header: { position: "sticky", top: 0, background: "#111827", borderBottom: "1px solid #1f2937", padding: "16px 20px", display: "flex", justifyContent: "space-between", alignItems: "center", zIndex: 1 },
  body: { padding: 20 },
  closeBtn: { background: "#1f2937", border: "1px solid #374151", borderRadius: 8, color: "#9ca3af", width: 32, height: 32, cursor: "pointer", fontSize: 16 },
  periodRow: { display: "flex", gap: 6, marginBottom: 14 },
  periodBtn: active => ({ padding: "5px 12px", borderRadius: 99, border: "1px solid #374151", background: active ? "#4338ca" : "#1f2937", color: active ? "#c7d2fe" : "#9ca3af", fontSize: 11, cursor: "pointer" }),
  card: { background: "#111827", border: "1px solid #1f2937", borderRadius: 12, padding: 16, marginBottom: 14 },
  statGrid: { display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 10, marginBottom: 14 },
  stat: { background: "#1f2937", borderRadius: 8, padding: "10px 12px" },
  statLabel: { fontSize: 10, color: "#6b7280", marginBottom: 3 },
  statValue: { fontSize: 15, fontWeight: 600 },
  refreshBtn: { background: "#1f2937", border: "1px solid #374151", borderRadius: 6, color: "#9ca3af", fontSize: 10, padding: "4px 10px", cursor: "pointer" },
};

const g = v => ({ color: parseFloat(v) >= 0 ? "#10b981" : "#ef4444" });

function FundamentalsAndNews({ ticker }) {
  const [fund, setFund] = useState(undefined); // undefined = not loaded, null = loaded-empty
  const [news, setNews] = useState(undefined);
  const [loadingFund, setLoadingFund] = useState(false);
  const [loadingNews, setLoadingNews] = useState(false);

  const loadFund = async (refresh = false) => {
    setLoadingFund(true);
    try {
      const r = await api.stockFundamentals(ticker, refresh);
      setFund(r.fundamentals || null);
    } catch { setFund(null); }
    finally { setLoadingFund(false); }
  };

  const loadNews = async (refresh = false) => {
    setLoadingNews(true);
    try {
      const r = await api.stockNews(ticker, refresh);
      setNews(r.news || []);
    } catch { setNews([]); }
    finally { setLoadingNews(false); }
  };

  useEffect(() => { loadFund(false); loadNews(false); }, [ticker]); // eslint-disable-line react-hooks/exhaustive-deps

  const fundFields = fund ? [
    ["P/E", fund.pe_ratio], ["P/B", fund.pb_ratio], ["EPS", fund.eps],
    ["ROE %", fund.roe], ["Debt/Equity", fund.debt_to_equity],
    ["Div Yield %", fund.dividend_yield], ["Market Cap", fund.market_cap ? `₹${(fund.market_cap/1e7).toFixed(0)}Cr` : null],
    ["Book Value", fund.book_value],
  ] : [];

  return (
    <>
      <div style={S.card}>
        <div style={{display:"flex",justifyContent:"space-between",alignItems:"center",marginBottom:10}}>
          <div style={{fontSize:13,fontWeight:600}}>Fundamentals</div>
          <button style={S.refreshBtn} onClick={()=>loadFund(true)} disabled={loadingFund}>
            {loadingFund ? "Fetching…" : "↻ Refresh from Yahoo Finance"}
          </button>
        </div>
        {fund === undefined && <div style={{color:"#6b7280",fontSize:12}}>Loading…</div>}
        {fund === null && <div style={{color:"#6b7280",fontSize:12}}>No cached fundamentals yet — click Refresh to fetch.</div>}
        {fund && (
          <>
            <div style={{display:"grid",gridTemplateColumns:"repeat(4,1fr)",gap:8}}>
              {fundFields.map(([label,val])=>(
                <div key={label} style={S.stat}>
                  <div style={S.statLabel}>{label}</div>
                  <div style={{...S.statValue,fontSize:13}}>{val ?? "N/A"}</div>
                </div>
              ))}
            </div>
            {fund.fundamental_score != null && (
              <div style={{marginTop:10,fontSize:11,color:"#9ca3af"}}>
                Fundamental score: <b style={{color:"#a5b4fc"}}>{fund.fundamental_score}/100</b>
                {" "}(heuristic, weighted from whichever of the above fields Yahoo provided)
              </div>
            )}
          </>
        )}
      </div>

      <div style={S.card}>
        <div style={{display:"flex",justifyContent:"space-between",alignItems:"center",marginBottom:10}}>
          <div style={{fontSize:13,fontWeight:600}}>News & Sentiment</div>
          <button style={S.refreshBtn} onClick={()=>loadNews(true)} disabled={loadingNews}>
            {loadingNews ? "Fetching…" : "↻ Refresh"}
          </button>
        </div>
        {news === undefined && <div style={{color:"#6b7280",fontSize:12}}>Loading…</div>}
        {news?.length === 0 && <div style={{color:"#6b7280",fontSize:12}}>No cached news yet — click Refresh to fetch.</div>}
        {news?.map((n,i)=>(
          <div key={i} style={{padding:"8px 0",borderBottom:"1px solid #1f2937"}}>
            <div style={{fontSize:12,color:"#e5e7eb",lineHeight:1.4,marginBottom:3}}>
              {n.url ? <a href={n.url} target="_blank" rel="noreferrer" style={{color:"#e5e7eb",textDecoration:"none"}}>{n.headline}</a> : n.headline}
            </div>
            <div style={{display:"flex",gap:8,alignItems:"center",fontSize:10,color:"#6b7280"}}>
              <span>{n.source}</span>
              {n.sentiment_label && (
                <span style={{
                  padding:"1px 8px",borderRadius:99,fontSize:9,fontWeight:600,
                  background: n.sentiment_label==="POSITIVE"?"#14532d":n.sentiment_label==="NEGATIVE"?"#7f1d1d":"#374151",
                  color: n.sentiment_label==="POSITIVE"?"#86efac":n.sentiment_label==="NEGATIVE"?"#fca5a5":"#d1d5db",
                }}>{n.sentiment_label}</span>
              )}
            </div>
          </div>
        ))}
      </div>
    </>
  );
}

export default function StockDetail({ ticker, onClose }) {
  const [period, setPeriod] = useState("6mo");
  const [history, setHistory] = useState(null);
  const [live, setLive] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!ticker) return;
    setLoading(true);
    setError("");
    Promise.all([
      api.livePrice(ticker).catch(() => null),
      api.stockHistory(ticker, period).catch(() => null),
    ]).then(([liveRes, histRes]) => {
      setLive(liveRes);
      setHistory(histRes);
      if (!liveRes && !histRes) setError("Data unavailable for this ticker.");
    }).finally(() => setLoading(false));
  }, [ticker, period]);

  if (!ticker) return null;

  const chartData = (history?.candles || history?.data || history || []).map(d => ({
    date: d.date || d.Date,
    close: parseFloat(d.close ?? d.Close),
  })).filter(d => d.date && !isNaN(d.close));

  return (
    <div style={S.overlay} onClick={onClose}>
      <div style={S.panel} onClick={e => e.stopPropagation()}>
        <div style={S.header}>
          <div style={{ display: "flex", alignItems: "baseline", gap: 12 }}>
            <span style={{ fontSize: 18, fontWeight: 700 }}>{ticker}</span>
            {live && (
              <>
                <span style={{ fontSize: 22, fontWeight: 700, color: "#6366f1" }}>
                  ₹{parseFloat(live.price).toFixed(2)}
                </span>
                <span style={{ fontSize: 13, fontWeight: 500, ...g(live.change) }}>
                  {parseFloat(live.change) >= 0 ? "+" : ""}{live.change} ({live.change_pct}%)
                </span>
              </>
            )}
          </div>
          <button style={S.closeBtn} onClick={onClose}>✕</button>
        </div>

        <div style={S.body}>
          {loading && <div style={{ color: "#6b7280", fontSize: 13 }}>Loading…</div>}
          {error && <div style={{ color: "#f87171", fontSize: 13, marginBottom: 12 }}>{error}</div>}

          {live && (
            <div style={S.statGrid}>
              <div style={S.stat}><div style={S.statLabel}>Open</div><div style={S.statValue}>₹{parseFloat(live.open).toFixed(2)}</div></div>
              <div style={S.stat}><div style={S.statLabel}>High</div><div style={S.statValue}>₹{parseFloat(live.high).toFixed(2)}</div></div>
              <div style={S.stat}><div style={S.statLabel}>Low</div><div style={S.statValue}>₹{parseFloat(live.low).toFixed(2)}</div></div>
              <div style={S.stat}><div style={S.statLabel}>Volume</div><div style={S.statValue}>{parseInt(live.volume).toLocaleString("en-IN")}</div></div>
            </div>
          )}

          <div style={S.card}>
            <div style={S.periodRow}>
              {PERIODS.map(p => (
                <button key={p} style={S.periodBtn(p === period)} onClick={() => setPeriod(p)}>{p.toUpperCase()}</button>
              ))}
            </div>
            {chartData.length > 1 ? (
              <ResponsiveContainer width="100%" height={260}>
                <AreaChart data={chartData}>
                  <defs>
                    <linearGradient id="closeGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#6366f1" stopOpacity={0.35} />
                      <stop offset="100%" stopColor="#6366f1" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid stroke="#1f2937" vertical={false} />
                  <XAxis dataKey="date" tick={{ fontSize: 10, fill: "#6b7280" }} minTickGap={40} />
                  <YAxis domain={["auto", "auto"]} tick={{ fontSize: 10, fill: "#6b7280" }} width={55} />
                  <Tooltip contentStyle={{ background: "#111827", border: "1px solid #1f2937", fontSize: 12 }} />
                  <Area type="monotone" dataKey="close" stroke="#6366f1" fill="url(#closeGrad)" strokeWidth={2} />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              !loading && <div style={{ color: "#6b7280", fontSize: 12, padding: "30px 0", textAlign: "center" }}>
                No chart data available for this period.
              </div>
            )}
          </div>

          {/* AI Prediction, explanation, and risk -- auto-runs for this ticker */}
          <AIPrediction initialTicker={ticker} />

          {/* Fundamentals + News/Sentiment -- lazy-loaded, refresh-on-demand */}
          <FundamentalsAndNews ticker={ticker} />
        </div>
      </div>
    </div>
  );
}
