 import { useState, useEffect } from "react";
import { api } from "../services/api";
import StockDetail from "../components/StockDetail";
import { BarChart, Bar, PieChart, Pie, Cell, LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

const COLORS = ["#6366f1","#10b981","#f59e0b","#ef4444","#8b5cf6","#06b6d4","#f97316","#84cc16"];
const g = v => ({ color: parseFloat(v) >= 0 ? "#10b981" : "#ef4444" });
const fmt = n => parseFloat(n || 0).toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 });

const S = {
  app:   { minHeight:"100vh", background:"#0a0d14", color:"#f9fafb", fontFamily:"system-ui,sans-serif" },
  nav:   { background:"#111827", borderBottom:"1px solid #1f2937", padding:"10px 20px", display:"flex", alignItems:"center", justifyContent:"space-between" },
  tabs:  { background:"#111827", borderBottom:"1px solid #1f2937", display:"flex", overflowX:"auto", padding:"0 16px" },
  tab:   { padding:"10px 14px", border:"none", background:"transparent", cursor:"pointer", fontSize:12, fontWeight:500, borderBottom:"2px solid transparent", whiteSpace:"nowrap" },
  body:  { padding:16 },
  g4:    { display:"grid", gridTemplateColumns:"repeat(4,1fr)", gap:10, marginBottom:14 },
  g3:    { display:"grid", gridTemplateColumns:"repeat(3,1fr)", gap:10, marginBottom:12 },
  g2:    { display:"grid", gridTemplateColumns:"1fr 1fr", gap:12, marginBottom:12 },
  card:  { background:"#111827", border:"1px solid #1f2937", borderRadius:12, padding:14 },
  ct:    { fontSize:11, fontWeight:500, color:"#6b7280", textTransform:"uppercase", letterSpacing:".05em", marginBottom:10, display:"flex", alignItems:"center", justifyContent:"space-between" },
  mv:    { fontSize:20, fontWeight:600 },
  ml:    { fontSize:11, color:"#6b7280", marginBottom:3 },
  tbl:   { width:"100%", borderCollapse:"collapse", fontSize:12 },
  th:    { color:"#6b7280", fontWeight:400, padding:"5px 8px", textAlign:"left", borderBottom:"1px solid #1f2937" },
  td:    { padding:"7px 8px", borderBottom:"1px solid #0a0d14", color:"#f9fafb" },
  pill:  { display:"inline-block", fontSize:10, fontWeight:500, padding:"2px 7px", borderRadius:99, background:"#1e1b4b", color:"#a5b4fc" },
  inp:   { width:"100%", padding:"8px 10px", background:"#1f2937", border:"1px solid #374151", borderRadius:8, color:"#f9fafb", fontSize:12, boxSizing:"border-box", marginBottom:8, outline:"none" },
  sel:   { width:"100%", padding:"8px 10px", background:"#1f2937", border:"1px solid #374151", borderRadius:8, color:"#f9fafb", fontSize:12, boxSizing:"border-box", marginBottom:8, appearance:"none" },
  btnG:  { flex:1, padding:"9px", background:"#065f46", border:"none", borderRadius:8, color:"#34d399", fontWeight:600, fontSize:13, cursor:"pointer" },
  btnR:  { flex:1, padding:"9px", background:"#7f1d1d", border:"none", borderRadius:8, color:"#f87171", fontWeight:600, fontSize:13, cursor:"pointer" },
  btnP:  { width:"100%", padding:"9px", background:"#4338ca", border:"none", borderRadius:8, color:"#c7d2fe", fontWeight:500, fontSize:13, cursor:"pointer" },
};

const Met = ({ label, value, color }) => (
  <div style={S.card}><div style={S.ml}>{label}</div><div style={{ ...S.mv, color: color || "#f9fafb" }}>{value}</div></div>
);

const Card = ({ title, children, right }) => (
  <div style={S.card}><div style={S.ct}><span>{title}</span>{right}</div>{children}</div>
);

export default function Dashboard({ user, onLogout }) {
  const [tab, setTab] = useState("dashboard");
  const [portfolio, setPortfolio] = useState(null);
  const [overview, setOverview] = useState(null);
  const [watchlist, setWatchlist] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [ipos, setIpos] = useState([]);
  const [mfs, setMfs] = useState([]);
  const [sectors, setSectors] = useState([]);
  const [sips, setSips] = useState([]);
  const [trades, setTrades] = useState([]);
  const [pnl, setPnl] = useState(null);
  const [screener, setScreener] = useState([]);
  const [benchmark, setBenchmark] = useState(null);
  const [dividends, setDividends] = useState(null);
  const [liveData, setLiveData] = useState(null);
  const [msg, setMsg] = useState("");
  const [tradeForm, setTradeForm] = useState({ ticker:"RELIANCE", trade_type:"BUY", product_type:"CNC", order_type:"MARKET", quantity:"", price:"" });
  const [alertForm, setAlertForm] = useState({ ticker:"", alert_type:"PRICE_ABOVE", target_value:"", notify_via:"APP", is_recurring:false });
  const [sipForm, setSipForm] = useState({ ticker:"", amount:"", frequency:"MONTHLY", start_date:"" });
  const [liveTicker, setLiveTicker] = useState("RELIANCE");
  const [scFilter, setScFilter] = useState({ pe_max:"", div_min:"", market_cap:"" });
  const [wlTicker, setWlTicker] = useState("");
  const [selectedTicker, setSelectedTicker] = useState(null);
  const [aiScreener, setAiScreener] = useState(null); // null = not yet loaded
  const [aiScreenerLoading, setAiScreenerLoading] = useState(false);
  const [aiScreenerErr, setAiScreenerErr] = useState("");
  const [breadth, setBreadth] = useState(null);
  const [sectorPerf, setSectorPerf] = useState([]);

  const pid = user.portfolios?.[0]?.portfolio_id;
  const uid = user.user_id;

  const flash = m => { setMsg(m); setTimeout(() => setMsg(""), 3000); };

  useEffect(() => {
    api.marketOverview().then(setOverview);
    api.getWatchlist().then(setWatchlist);
    api.getAlerts().then(setAlerts);
    api.getUpcomingIpos().then(setIpos);
    api.getMFs().then(setMfs);
    api.marketBreadth().then(setBreadth).catch(() => setBreadth(null));
    api.sectorPerformance().then(setSectorPerf).catch(() => setSectorPerf([]));
    if (pid) {
      api.getPortfolio(pid).then(setPortfolio);
      api.sectorBreakdown(pid).then(setSectors);
      api.getSips(pid).then(setSips);
      api.getMFHoldings(pid).then(data => setMfs(data));
      api.getTrades(pid).then(setTrades);
      api.getPnl(pid).then(setPnl);
      api.benchmark(pid).then(setBenchmark);
      api.dividends(uid).then(setDividends);
    }
  }, [pid]);

  const doTrade = async (type) => {
    try {
      await api.executeTrade(pid, { ...tradeForm, trade_type: type, quantity: +tradeForm.quantity, price: +tradeForm.price });
      flash(`✅ ${type} ${tradeForm.ticker} executed!`);
      api.getPortfolio(pid).then(setPortfolio);
      api.getTrades(pid).then(setTrades);
    } catch(e) { flash("❌ " + e.message); }
  };

  const doAlert = async () => {
    try {
      await api.createAlert({ ...alertForm, target_value: +alertForm.target_value });
      flash("✅ Alert created!"); api.getAlerts().then(setAlerts);
    } catch(e) { flash("❌ " + e.message); }
  };

  const doSip = async () => {
    try {
      await api.createSip(pid, { ...sipForm, amount: +sipForm.amount });
      flash("✅ SIP created!"); api.getSips(pid).then(setSips);
    } catch(e) { flash("❌ " + e.message); }
  };

  const doScreener = async () => {
    const p = Object.fromEntries(Object.entries(scFilter).filter(([,v]) => v));
    api.screener(p).then(setScreener);
  };

  const doLive = async () => {
    try { setLiveData(await api.livePrice(liveTicker.toUpperCase())); }
    catch(e) { flash("❌ " + e.message); }
  };

  const loadAiScreener = async () => {
    setAiScreenerLoading(true);
    setAiScreenerErr("");
    try { setAiScreener(await api.aiScreenerTop({ limit: 25 })); }
    catch(e) { setAiScreenerErr(e.message || "Failed to load AI Screener"); setAiScreener([]); }
    finally { setAiScreenerLoading(false); }
  };

  useEffect(() => {
    if (tab === "ai-screener" && aiScreener === null && !aiScreenerLoading) loadAiScreener();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tab]);

  const [regime, setRegime] = useState(null);
  useEffect(() => { api.marketRegime().then(setRegime).catch(()=>setRegime(null)); }, []);

  const [dataHealth, setDataHealth] = useState(null);
  const [dataHealthLoading, setDataHealthLoading] = useState(false);
  const loadDataHealth = async () => {
    setDataHealthLoading(true);
    try { setDataHealth(await api.dataHealth()); } catch { setDataHealth(null); }
    finally { setDataHealthLoading(false); }
  };
  useEffect(() => {
    if (tab === "data-health" && !dataHealth && !dataHealthLoading) loadDataHealth();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tab]);

  const [researchQuery, setResearchQuery] = useState("");
  const [researchHistory, setResearchHistory] = useState([]);
  const [researchLoading, setResearchLoading] = useState(false);
  const askResearch = async () => {
    const q = researchQuery.trim();
    if (!q) return;
    setResearchLoading(true);
    try {
      const result = await api.researchAsk(q);
      setResearchHistory(h => [...h, { q, result }]);
      setResearchQuery("");
    } catch(e) {
      setResearchHistory(h => [...h, { q, result: { intent:"error", error: e.message } }]);
    } finally { setResearchLoading(false); }
  };

  const TABS = [
    { id:"dashboard", label:"📊 Dashboard" }, { id:"market", label:"🏛️ Market" },
    { id:"trade", label:"🔄 Trade" }, { id:"sip", label:"📅 SIP" },
    { id:"mf", label:"🏦 Mutual Funds" }, { id:"watchlist", label:"⭐ Watchlist" },
    { id:"alerts", label:"🔔 Alerts" }, { id:"ipo", label:"🚀 IPO" },
    { id:"screener", label:"🔍 Screener" }, { id:"ai-screener", label:"🤖 AI Screener" },
    { id:"research", label:"💬 Research Assistant" },
    { id:"analytics", label:"📈 Analytics" },
    { id:"pnl", label:"🧾 P&L / Tax" }, { id:"live", label:"📡 Live" },
    { id:"data-health", label:"🩺 Data Health" },
  ];

  const sum = portfolio?.summary || {};

  return (
    <div style={S.app}>
      {/* Navbar */}
      <div style={S.nav}>
        <div style={{fontSize:15,fontWeight:600,display:"flex",alignItems:"center",gap:8}}>
          📈 Dalal Street Pro
          <span style={{fontSize:10,padding:"2px 8px",background:"#1f2937",borderRadius:99,color:"#6b7280"}}>NSE · BSE · MCX</span>
        </div>
        <div style={{display:"flex",gap:16,alignItems:"center",fontSize:12}}>
          {overview?.indices?.slice(0,2).map(i => (
            <span key={i.name} style={{color: parseFloat(i.change_pct) >= 0 ? "#10b981" : "#ef4444"}}>
              {i.name} {parseFloat(i.value).toLocaleString("en-IN")} {parseFloat(i.change_pct) >= 0 ? "▲" : "▼"}{Math.abs(i.change_pct)}%
            </span>
          ))}
          <span style={{color:"#10b981",fontWeight:500}}>₹{parseFloat(user.balance||0).toLocaleString("en-IN")}</span>
          <span style={{color:"#6b7280"}}>👤 {user.username}</span>
          <button onClick={onLogout} style={{padding:"5px 12px",background:"#1f2937",border:"1px solid #374151",borderRadius:8,color:"#9ca3af",fontSize:11,cursor:"pointer"}}>Logout</button>
        </div>
      </div>

      {/* Tabs */}
      <div style={S.tabs}>
        {TABS.map(t => (
          <button key={t.id} onClick={() => setTab(t.id)} style={{
            ...S.tab, color: tab===t.id ? "#6366f1" : "#6b7280",
            borderBottomColor: tab===t.id ? "#6366f1" : "transparent"
          }}>{t.label}</button>
        ))}
      </div>

      <div style={S.body}>
        {msg && <div style={{background:"#1e3a5f",border:"1px solid #3b82f6",borderRadius:8,padding:"10px 14px",marginBottom:12,fontSize:13}}>{msg}</div>}

        {/* DASHBOARD */}
        {tab==="dashboard" && <>
          {regime?.regime && (
            <div style={{
              ...S.card, marginBottom:14, display:"flex", justifyContent:"space-between", alignItems:"center",
              borderLeft: `3px solid ${regime.regime==="BULLISH"?"#10b981":regime.regime==="BEARISH"?"#ef4444":regime.regime==="HIGH_VOLATILITY"?"#f59e0b":"#6b7280"}`,
            }}>
              <div>
                <div style={{fontSize:10,color:"#6b7280",marginBottom:2}}>CURRENT MARKET REGIME</div>
                <div style={{fontSize:16,fontWeight:700}}>
                  {regime.regime.replace("_"," ")} <span style={{fontSize:11,fontWeight:400,color:"#9ca3af"}}>({regime.confidence}% confidence)</span>
                </div>
              </div>
              <div style={{fontSize:11,color:"#6b7280",textAlign:"right"}}>
                {regime.nifty_trend && <div>NIFTY trend: {regime.nifty_trend}</div>}
                {regime.volatility_20d != null && <div>20d volatility: {regime.volatility_20d}%</div>}
              </div>
            </div>
          )}
          <div style={S.g4}>
            <Met label="Total Invested" value={`₹${fmt(sum.total_invested)}`} />
            <Met label="Current Value" value={`₹${fmt(sum.current_value)}`} />
            <Met label="Unrealized P&L" value={`${(sum.unrealized_pnl||0)>=0?"+":""}₹${fmt(sum.unrealized_pnl)}`} color={(sum.unrealized_pnl||0)>=0?"#10b981":"#ef4444"} />
            <Met label="Today's P&L" value={`${(sum.day_pnl||0)>=0?"+":""}₹${fmt(sum.day_pnl)}`} color={(sum.day_pnl||0)>=0?"#10b981":"#ef4444"} />
          </div>
          <Card title={`Holdings (${sum.holdings_count||0})`}>
            <table style={S.tbl}>
              <thead><tr>{["Stock","Exch","Qty","Avg Buy","LTP","Value","P&L","Day P&L","Action"].map(h=><th key={h} style={S.th}>{h}</th>)}</tr></thead>
              <tbody>{(portfolio?.holdings||[]).map(h => {
                const pnl = parseFloat(h.unrealized_pnl||0);
                const dp = parseFloat(h.day_pnl||0);
                return <tr key={h.ticker}>
                  <td style={S.td}><span style={S.pill}>{h.ticker}</span></td>
                  <td style={{...S.td,color:"#6b7280"}}>{h.exchange}</td>
                  <td style={S.td}>{h.quantity}</td>
                  <td style={S.td}>₹{fmt(h.avg_buy_price)}</td>
                  <td style={S.td}>₹{fmt(h.current_price)}</td>
                  <td style={S.td}>₹{fmt(h.current_value)}</td>
                  <td style={{...S.td,...g(pnl)}}>{pnl>=0?"+":""}₹{fmt(pnl)} ({h.pnl_pct}%)</td>
                  <td style={{...S.td,...g(dp)}}>{dp>=0?"+":""}₹{parseFloat(dp).toFixed(0)}</td>
                  <td style={S.td}><button style={{...S.btnR,padding:"3px 10px",flex:"none",fontSize:11}} onClick={()=>{setTradeForm(f=>({...f,ticker:h.ticker,price:h.current_price}));setTab("trade");}}>SELL</button></td>
                </tr>;
              })}</tbody>
            </table>
          </Card>
          {sectors.length > 0 && <div style={S.g2}>
            <Card title="Sector Allocation">
              <ResponsiveContainer width="100%" height={200}>
                <PieChart><Pie data={sectors} dataKey="allocation_pct" nameKey="sector" cx="50%" cy="50%" outerRadius={80}>
                  {sectors.map((_,i)=><Cell key={i} fill={COLORS[i%COLORS.length]}/>)}
                </Pie><Tooltip formatter={v=>`${v}%`} contentStyle={{background:"#111827",border:"1px solid #1f2937"}}/></PieChart>
              </ResponsiveContainer>
            </Card>
            <Card title="Sector P&L">
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={sectors}>
                  <XAxis dataKey="sector" stroke="#6b7280" fontSize={9}/>
                  <YAxis stroke="#6b7280" fontSize={9}/>
                  <Tooltip contentStyle={{background:"#111827",border:"1px solid #1f2937"}} formatter={v=>`₹${parseFloat(v).toFixed(0)}`}/>
                  <Bar dataKey="total_pnl" radius={[4,4,0,0]}>{sectors.map((s,i)=><Cell key={i} fill={parseFloat(s.total_pnl)>=0?"#10b981":"#ef4444"}/>)}</Bar>
                </BarChart>
              </ResponsiveContainer>
            </Card>
          </div>}
        </>}

        {/* MARKET */}
        {tab==="market" && <div style={S.g2}>
          <Card title="Market Indices">
            {(overview?.indices||[]).map(i=>(
              <div key={i.name} style={{display:"flex",justifyContent:"space-between",padding:"8px 0",borderBottom:"1px solid #1f2937"}}>
                <span style={{fontSize:13,fontWeight:500}}>{i.name}</span>
                <span style={{...g(i.change_pct),fontSize:13,fontWeight:500}}>{parseFloat(i.value).toLocaleString("en-IN")} ({i.change_pct>=0?"+":""}{i.change_pct}%)</span>
              </div>
            ))}
          </Card>
          <div>
            <Card title="🟢 Top Gainers">
              {(overview?.gainers||[]).map(s=>(
                <div key={s.ticker} onClick={()=>setSelectedTicker(s.ticker)} style={{display:"flex",justifyContent:"space-between",padding:"5px 0",borderBottom:"1px solid #1f2937",cursor:"pointer"}}>
                  <span style={S.pill}>{s.ticker}</span> <span style={{fontSize:11,color:"#6b7280"}}>{s.company?.slice(0,20)}</span>
                  <span style={{color:"#10b981",fontSize:12,fontWeight:500}}>+{s.change_pct}%</span>
                </div>
              ))}
            </Card>
            <div style={{marginTop:10}}/>
            <Card title="🔴 Top Losers">
              {(overview?.losers||[]).map(s=>(
                <div key={s.ticker} onClick={()=>setSelectedTicker(s.ticker)} style={{display:"flex",justifyContent:"space-between",padding:"5px 0",borderBottom:"1px solid #1f2937",cursor:"pointer"}}>
                  <span style={{...S.pill,background:"#450a0a",color:"#f87171"}}>{s.ticker}</span>
                  <span style={{color:"#ef4444",fontSize:12,fontWeight:500}}>{s.change_pct}%</span>
                </div>
              ))}
            </Card>
          </div>
          <Card title="Market News" right={<span style={{fontSize:10,color:"#6b7280"}}>ET · Mint · MC</span>}>
            {(overview?.news||[]).map(n=>(
              <div key={n.news_id} style={{padding:"8px 0",borderBottom:"1px solid #1f2937"}}>
                <div style={{fontSize:12,color:"#e5e7eb",lineHeight:1.4,marginBottom:3}}>{n.headline}</div>
                <div style={{display:"flex",gap:8,fontSize:10,color:"#6b7280"}}>
                  <span>{n.source}</span>
                  {n.ticker && <span style={S.pill}>{n.ticker}</span>}
                  <span>{n.category}</span>
                </div>
              </div>
            ))}
          </Card>

          {/* Market Breadth (spec section 21) */}
          <Card title="📊 NSE Market Breadth">
            {breadth ? <>
              <div style={{display:"grid",gridTemplateColumns:"1fr 1fr 1fr",gap:10,marginBottom:10}}>
                <div style={{textAlign:"center"}}>
                  <div style={{fontSize:20,fontWeight:700,color:"#10b981"}}>{breadth.advancing ?? 0}</div>
                  <div style={{fontSize:10,color:"#6b7280"}}>Advancing ▲</div>
                </div>
                <div style={{textAlign:"center"}}>
                  <div style={{fontSize:20,fontWeight:700,color:"#ef4444"}}>{breadth.declining ?? 0}</div>
                  <div style={{fontSize:10,color:"#6b7280"}}>Declining ▼</div>
                </div>
                <div style={{textAlign:"center"}}>
                  <div style={{fontSize:20,fontWeight:700,color:"#9ca3af"}}>{breadth.unchanged ?? 0}</div>
                  <div style={{fontSize:10,color:"#6b7280"}}>Unchanged</div>
                </div>
              </div>
              <div style={{fontSize:11,color:"#6b7280",display:"flex",justifyContent:"space-between"}}>
                <span>A/D Ratio: <b style={{color:"#f9fafb"}}>{breadth.advance_decline_ratio ?? "—"}</b></span>
                <span>52W Highs: <b style={{color:"#10b981"}}>{breadth.new_52w_highs ?? 0}</b></span>
                <span>52W Lows: <b style={{color:"#ef4444"}}>{breadth.new_52w_lows ?? 0}</b></span>
              </div>
            </> : <div style={{color:"#6b7280",fontSize:12}}>Breadth data unavailable — sync jobs haven't populated current_price/prev_close yet.</div>}
          </Card>

          {/* Sector Performance (spec section 22) */}
          <Card title="🏭 Sector Performance">
            {sectorPerf.length ? sectorPerf.slice(0,8).map(s=>(
              <div key={s.sector} style={{display:"flex",justifyContent:"space-between",alignItems:"center",padding:"6px 0",borderBottom:"1px solid #1f2937"}}>
                <span style={{fontSize:12}}>{s.sector}</span>
                <span style={{fontSize:10,color:"#6b7280"}}>{s.advancing}▲ {s.declining}▼</span>
                <span style={{...g(s.avg_change_pct),fontSize:12,fontWeight:500}}>{s.avg_change_pct>=0?"+":""}{s.avg_change_pct}%</span>
              </div>
            )) : <div style={{color:"#6b7280",fontSize:12}}>Sector data unavailable.</div>}
          </Card>
        </div>}

        {/* AI SCREENER (spec section 20) */}
        {tab==="ai-screener" && <>
          <Card title="🤖 Top AI Opportunities" right={
            <button style={{...S.btnP,width:"auto",padding:"5px 12px",fontSize:11}} onClick={loadAiScreener} disabled={aiScreenerLoading}>
              {aiScreenerLoading ? "Refreshing…" : "↻ Refresh"}
            </button>
          }>
            <div style={{fontSize:11,color:"#6b7280",marginBottom:12,lineHeight:1.5}}>
              Composite score blends the latest cached AI ensemble prediction (RF + XGBoost + Logistic Regression)
              with a live technical score. This is a research/screening tool, not investment advice —
              see each stock's detail page for the full model breakdown and confidence.
            </div>
            {aiScreenerErr && <div style={{color:"#f87171",fontSize:12,marginBottom:10}}>{aiScreenerErr}</div>}
            {aiScreenerLoading && !aiScreener?.length && <div style={{color:"#6b7280",fontSize:13}}>Loading…</div>}
            {aiScreener?.length === 0 && !aiScreenerLoading && !aiScreenerErr && (
              <div style={{color:"#6b7280",fontSize:12,lineHeight:1.6}}>
                No scored stocks yet. This fills in once the nightly <code>generate_predictions()</code> job
                and price sync jobs have run at least once against your stock universe.
              </div>
            )}
            {!!aiScreener?.length && (
              <table style={S.tbl}>
                <thead><tr>
                  <th style={S.th}>Ticker</th><th style={S.th}>Company</th><th style={S.th}>Sector</th>
                  <th style={S.th}>Price</th><th style={S.th}>AI Signal</th><th style={S.th}>Confidence</th>
                  <th style={S.th}>Technical</th><th style={S.th}>Composite</th>
                </tr></thead>
                <tbody>
                  {aiScreener.map(s=>(
                    <tr key={s.ticker} onClick={()=>setSelectedTicker(s.ticker)} style={{cursor:"pointer"}}>
                      <td style={S.td}><span style={S.pill}>{s.ticker}</span></td>
                      <td style={S.td}>{s.company?.slice(0,24)}</td>
                      <td style={S.td}>{s.sector||"—"}</td>
                      <td style={S.td}>{s.current_price ? `₹${fmt(s.current_price)}` : "—"}</td>
                      <td style={S.td}>
                        {s.ai_signal ? <span style={{
                          ...S.pill,
                          background: s.ai_signal==="BUY"?"#14532d":s.ai_signal==="SELL"?"#7f1d1d":"#713f12",
                          color: s.ai_signal==="BUY"?"#86efac":s.ai_signal==="SELL"?"#fca5a5":"#fde68a",
                        }}>{s.ai_signal}</span> : <span style={{color:"#6b7280",fontSize:11}}>No prediction cached</span>}
                      </td>
                      <td style={S.td}>{s.ai_confidence ? `${s.ai_confidence}%` : "—"}</td>
                      <td style={S.td}>{s.technical_score ?? "—"}</td>
                      <td style={{...S.td,fontWeight:700,color:"#a5b4fc"}}>{s.composite_score}/100</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </Card>
        </>}

        {/* TRADE */}
        {tab==="trade" && <div style={S.g2}>
          <Card title="Place Order">
            <div style={{fontSize:11,color:"#9ca3af",marginBottom:4}}>Stock Ticker</div>
            <input style={S.inp} value={tradeForm.ticker} onChange={e=>setTradeForm(f=>({...f,ticker:e.target.value.toUpperCase()}))} placeholder="RELIANCE"/>
            <div style={{fontSize:11,color:"#9ca3af",marginBottom:4}}>Quantity</div>
            <input style={S.inp} value={tradeForm.quantity} onChange={e=>setTradeForm(f=>({...f,quantity:e.target.value}))} placeholder="10"/>
            <div style={{fontSize:11,color:"#9ca3af",marginBottom:4}}>Price (₹)</div>
            <input style={S.inp} value={tradeForm.price} onChange={e=>setTradeForm(f=>({...f,price:e.target.value}))} placeholder="2850"/>
            <div style={{fontSize:11,color:"#9ca3af",marginBottom:4}}>Product Type</div>
            <select style={S.sel} value={tradeForm.product_type} onChange={e=>setTradeForm(f=>({...f,product_type:e.target.value}))}>
              <option>CNC</option><option>MIS</option><option>NRML</option>
            </select>
            <div style={{fontSize:11,color:"#9ca3af",marginBottom:4}}>Order Type</div>
            <select style={S.sel} value={tradeForm.order_type} onChange={e=>setTradeForm(f=>({...f,order_type:e.target.value}))}>
              <option>MARKET</option><option>LIMIT</option><option>SL</option><option>SL-M</option>
            </select>
            {tradeForm.quantity && tradeForm.price && (
              <div style={{fontSize:12,color:"#9ca3af",marginBottom:10}}>
                Order value: <strong style={{color:"#f9fafb"}}>₹{(+tradeForm.quantity * +tradeForm.price).toLocaleString("en-IN")}</strong>
                {" · "}STT: <strong style={{color:"#f9fafb"}}>₹{(+tradeForm.quantity * +tradeForm.price * 0.001).toFixed(2)}</strong>
              </div>
            )}
            <div style={{display:"flex",gap:8}}><button style={S.btnG} onClick={()=>doTrade("BUY")}>BUY</button><button style={S.btnR} onClick={()=>doTrade("SELL")}>SELL</button></div>
          </Card>
          <Card title="Trade History">
            <table style={S.tbl}>
              <thead><tr>{["Stock","Type","Qty","Price","Value","Date"].map(h=><th key={h} style={S.th}>{h}</th>)}</tr></thead>
              <tbody>{trades.slice(0,15).map(t=>(
                <tr key={t.trade_id}>
                  <td style={S.td}><span style={S.pill}>{t.ticker}</span></td>
                  <td style={{...S.td,color:t.trade_type==="BUY"?"#10b981":"#ef4444",fontWeight:500}}>{t.trade_type}</td>
                  <td style={S.td}>{t.quantity}</td>
                  <td style={S.td}>₹{fmt(t.price)}</td>
                  <td style={S.td}>₹{fmt(t.total_value)}</td>
                  <td style={{...S.td,color:"#6b7280",fontSize:11}}>{new Date(t.traded_at).toLocaleDateString("en-IN")}</td>
                </tr>
              ))}</tbody>
            </table>
          </Card>
        </div>}

        {/* SIP */}
        {tab==="sip" && <div style={S.g2}>
          <Card title="Create SIP">
            {[["Stock Ticker","ticker","RELIANCE"],["Monthly Amount (₹)","amount","5000"]].map(([l,k,ph])=>(
              <div key={k}><div style={{fontSize:11,color:"#9ca3af",marginBottom:4}}>{l}</div>
              <input style={S.inp} value={sipForm[k]} onChange={e=>setSipForm(f=>({...f,[k]:e.target.value}))} placeholder={ph}/></div>
            ))}
            <div style={{fontSize:11,color:"#9ca3af",marginBottom:4}}>Frequency</div>
            <select style={S.sel} value={sipForm.frequency} onChange={e=>setSipForm(f=>({...f,frequency:e.target.value}))}>
              {["DAILY","WEEKLY","MONTHLY","QUARTERLY"].map(o=><option key={o}>{o}</option>)}
            </select>
            <div style={{fontSize:11,color:"#9ca3af",marginBottom:4}}>Start Date</div>
            <input style={S.inp} type="date" value={sipForm.start_date} onChange={e=>setSipForm(f=>({...f,start_date:e.target.value}))}/>
            <button style={S.btnP} onClick={doSip}>Start SIP</button>
          </Card>
          <Card title="Active SIPs">
            <table style={S.tbl}>
              <thead><tr>{["Stock","Amount","Freq","Invested","Value","Return","Next Due"].map(h=><th key={h} style={S.th}>{h}</th>)}</tr></thead>
              <tbody>{sips.map(s=>(
                <tr key={s.sip_id}>
                  <td style={S.td}><span style={S.pill}>{s.ticker}</span></td>
                  <td style={S.td}>₹{parseFloat(s.amount).toLocaleString("en-IN")}</td>
                  <td style={{...S.td,color:"#6b7280"}}>{s.frequency}</td>
                  <td style={S.td}>₹{fmt(s.total_invested)}</td>
                  <td style={S.td}>₹{fmt(s.current_value)}</td>
                  <td style={{...S.td,...g(s.sip_return_pct)}}>{s.sip_return_pct}%</td>
                  <td style={{...S.td,fontSize:11,color:"#6b7280"}}>{s.next_due}</td>
                </tr>
              ))}</tbody>
            </table>
          </Card>
        </div>}

        {/* MUTUAL FUNDS */}
        {tab==="mf" && <Card title="Mutual Fund Holdings">
          <table style={S.tbl}>
            <thead><tr>{["Fund","House","Category","Units","Avg NAV","NAV","Value","P&L","1Y Return","Rating"].map(h=><th key={h} style={S.th}>{h}</th>)}</tr></thead>
            <tbody>{mfs.map((m,i)=>(
              <tr key={i}>
                <td style={{...S.td,fontSize:11,maxWidth:200}}>{m.fund_name}</td>
                <td style={{...S.td,fontSize:11,color:"#6b7280"}}>{m.fund_house}</td>
                <td style={S.td}><span style={{...S.pill,background:"#1e1b4b",color:"#a5b4fc"}}>{m.category}</span></td>
                <td style={S.td}>{parseFloat(m.units||0).toFixed(3)}</td>
                <td style={S.td}>₹{fmt(m.avg_nav)}</td>
                <td style={S.td}>₹{fmt(m.current_nav)}</td>
                <td style={S.td}>₹{fmt(m.current_value)}</td>
                <td style={{...S.td,...g(m.pnl)}}>₹{fmt(m.pnl)}</td>
                <td style={{...S.td,...g(m.returns_1y)}}>{m.returns_1y}%</td>
                <td style={S.td}>{"⭐".repeat(m.rating||0)}</td>
              </tr>
            ))}</tbody>
          </table>
        </Card>}

        {/* WATCHLIST */}
        {tab==="watchlist" && <Card title="My Watchlist" right={
          <div style={{display:"flex",gap:8}}>
            <input style={{...S.inp,width:110,marginBottom:0}} placeholder="Ticker" value={wlTicker} onChange={e=>setWlTicker(e.target.value.toUpperCase())}/>
            <button style={{...S.btnP,width:"auto",padding:"5px 12px"}} onClick={async()=>{if(wlTicker){await api.addWatchlist({ticker:wlTicker});api.getWatchlist().then(setWatchlist);setWlTicker("");}}}>+ Add</button>
          </div>
        }>
          <table style={S.tbl}>
            <thead><tr>{["Stock","Exch","LTP","Chg%","52W H","52W L","P/E","P/B","Div%",""].map(h=><th key={h} style={S.th}>{h}</th>)}</tr></thead>
            <tbody>{watchlist.map(w=>(
              <tr key={w.watchlist_id}>
                <td style={S.td} onClick={()=>setSelectedTicker(w.ticker)}><span style={{...S.pill,cursor:"pointer"}}>{w.ticker}</span> <span style={{fontSize:10,color:"#6b7280"}}>{w.company?.slice(0,14)}</span></td>
                <td style={{...S.td,color:"#6b7280"}}>{w.exchange}</td>
                <td style={S.td}>₹{fmt(w.current_price)}</td>
                <td style={{...S.td,...g(w.change_pct)}}>{w.change_pct>=0?"+":""}{w.change_pct}%</td>
                <td style={S.td}>₹{parseFloat(w.week_52_high||0).toFixed(0)}</td>
                <td style={S.td}>₹{parseFloat(w.week_52_low||0).toFixed(0)}</td>
                <td style={S.td}>{w.pe_ratio||"—"}</td>
                <td style={S.td}>{w.pb_ratio||"—"}</td>
                <td style={{...S.td,color:"#10b981"}}>{w.dividend_yield}%</td>
                <td style={S.td}><button style={{...S.btnR,padding:"3px 8px",flex:"none",fontSize:10}} onClick={()=>api.removeWatchlist(w.watchlist_id).then(()=>api.getWatchlist().then(setWatchlist))}>✕</button></td>
              </tr>
            ))}</tbody>
          </table>
        </Card>}

        {/* ALERTS */}
        {tab==="alerts" && <div style={S.g2}>
          <Card title="Create Alert">
            <div style={{fontSize:11,color:"#9ca3af",marginBottom:4}}>Stock Ticker</div>
            <input style={S.inp} value={alertForm.ticker} onChange={e=>setAlertForm(f=>({...f,ticker:e.target.value.toUpperCase()}))} placeholder="TSLA"/>
            <div style={{fontSize:11,color:"#9ca3af",marginBottom:4}}>Alert Type</div>
            <select style={S.sel} value={alertForm.alert_type} onChange={e=>setAlertForm(f=>({...f,alert_type:e.target.value}))}>
              {["PRICE_ABOVE","PRICE_BELOW","PCT_CHANGE","VOLUME_SPIKE"].map(o=><option key={o}>{o}</option>)}
            </select>
            <div style={{fontSize:11,color:"#9ca3af",marginBottom:4}}>Target Value (₹)</div>
            <input style={S.inp} value={alertForm.target_value} onChange={e=>setAlertForm(f=>({...f,target_value:e.target.value}))} placeholder="3000"/>
            <div style={{fontSize:11,color:"#9ca3af",marginBottom:4}}>Notify Via</div>
            <select style={S.sel} value={alertForm.notify_via} onChange={e=>setAlertForm(f=>({...f,notify_via:e.target.value}))}>
              {["APP","SMS","EMAIL","WHATSAPP"].map(o=><option key={o}>{o}</option>)}
            </select>
            <button style={S.btnP} onClick={doAlert}>Set Alert</button>
          </Card>
          <Card title="Active Alerts">
            <table style={S.tbl}>
              <thead><tr>{["Stock","Type","Target","Current","Status",""].map(h=><th key={h} style={S.th}>{h}</th>)}</tr></thead>
              <tbody>{alerts.map(a=>(
                <tr key={a.alert_id}>
                  <td style={S.td}><span style={S.pill}>{a.ticker}</span></td>
                  <td style={{...S.td,fontSize:11,color:"#9ca3af"}}>{a.alert_type}</td>
                  <td style={S.td}>₹{a.target_value}</td>
                  <td style={S.td}>₹{fmt(a.current_price)}</td>
                  <td style={S.td}><span style={{fontSize:10,padding:"2px 7px",borderRadius:99,background:a.live_status==="TRIGGERED"?"#065f46":"#78350f",color:a.live_status==="TRIGGERED"?"#34d399":"#fcd34d"}}>{a.live_status}</span></td>
                  <td style={S.td}><button style={{...S.btnR,padding:"2px 8px",flex:"none",fontSize:10}} onClick={()=>api.deleteAlert(a.alert_id).then(()=>api.getAlerts().then(setAlerts))}>✕</button></td>
                </tr>
              ))}</tbody>
            </table>
          </Card>
        </div>}

        {/* IPO */}
        {tab==="ipo" && <Card title="IPO Tracker — Upcoming & Recent">
          <table style={S.tbl}>
            <thead><tr>{["Company","Price Band","Lot","Issue (Cr)","Open","Close","Listing","Gain%","GMP","Subscribed","Status"].map(h=><th key={h} style={S.th}>{h}</th>)}</tr></thead>
            <tbody>{ipos.map(i=>{
              const gain = i.listing_price ? (i.listing_price-i.price_band_high)/i.price_band_high*100 : null;
              return <tr key={i.ipo_id}>
                <td style={{...S.td,fontWeight:500}}>{i.company_name}</td>
                <td style={S.td}>₹{i.price_band_low}–{i.price_band_high}</td>
                <td style={S.td}>{i.lot_size}</td>
                <td style={S.td}>{parseFloat(i.issue_size_cr||0).toLocaleString("en-IN")}</td>
                <td style={{...S.td,fontSize:11}}>{i.open_date}</td>
                <td style={{...S.td,fontSize:11}}>{i.close_date}</td>
                <td style={{...S.td,fontSize:11}}>{i.listing_date||"—"}</td>
                <td style={{...S.td,...(gain!=null?g(gain):{})}}>{ gain!=null ? `${gain.toFixed(1)}%` : "—"}</td>
                <td style={{...S.td,...g(i.gmp)}}>₹{i.gmp}</td>
                <td style={S.td}>{i.subscription_times>0?`${i.subscription_times}x`:"—"}</td>
                <td style={S.td}><span style={{fontSize:10,padding:"2px 7px",borderRadius:99,background:i.status==="UPCOMING"?"#1e3a5f":i.status==="OPEN"?"#065f46":"#1f2937",color:i.status==="UPCOMING"?"#60a5fa":i.status==="OPEN"?"#34d399":"#9ca3af"}}>{i.status}</span></td>
              </tr>;
            })}</tbody>
          </table>
        </Card>}

        {/* SCREENER */}
        {tab==="screener" && <>
          <Card title="Stock Screener">
            <div style={{display:"flex",gap:10,flexWrap:"wrap",alignItems:"flex-end"}}>
              <div><div style={{fontSize:11,color:"#9ca3af",marginBottom:4}}>P/E Max</div><input style={{...S.inp,width:130,marginBottom:0}} value={scFilter.pe_max} onChange={e=>setScFilter(f=>({...f,pe_max:e.target.value}))} placeholder="30"/></div>
              <div><div style={{fontSize:11,color:"#9ca3af",marginBottom:4}}>Div Yield Min%</div><input style={{...S.inp,width:130,marginBottom:0}} value={scFilter.div_min} onChange={e=>setScFilter(f=>({...f,div_min:e.target.value}))} placeholder="0.5"/></div>
              <div><div style={{fontSize:11,color:"#9ca3af",marginBottom:4}}>Market Cap</div>
                <select style={{...S.sel,width:150,marginBottom:0}} value={scFilter.market_cap} onChange={e=>setScFilter(f=>({...f,market_cap:e.target.value}))}>
                  <option value="">All</option>{["LARGE_CAP","MID_CAP","SMALL_CAP"].map(o=><option key={o}>{o}</option>)}
                </select>
              </div>
              <button style={{...S.btnP,width:"auto",padding:"8px 20px",marginTop:18}} onClick={doScreener}>Screen</button>
            </div>
          </Card>
          {screener.length > 0 && <div style={{marginTop:12}}>
            <Card title={`${screener.length} stocks found`}>
              <table style={S.tbl}>
                <thead><tr>{["Stock","Sector","Price","P/E","P/B","Div Yield","52W H","52W L","Cap"].map(h=><th key={h} style={S.th}>{h}</th>)}</tr></thead>
                <tbody>{screener.map(s=>(
                  <tr key={s.ticker} onClick={()=>setSelectedTicker(s.ticker)} style={{cursor:"pointer"}}>
                    <td style={S.td}><span style={S.pill}>{s.ticker}</span></td>
                    <td style={{...S.td,fontSize:11,color:"#6b7280"}}>{s.sector}</td>
                    <td style={S.td}>₹{fmt(s.current_price)}</td>
                    <td style={S.td}>{s.pe_ratio||"—"}</td>
                    <td style={S.td}>{s.pb_ratio||"—"}</td>
                    <td style={{...S.td,color:"#10b981"}}>{s.dividend_yield}%</td>
                    <td style={S.td}>₹{parseFloat(s.week_52_high||0).toFixed(0)}</td>
                    <td style={S.td}>₹{parseFloat(s.week_52_low||0).toFixed(0)}</td>
                    <td style={{...S.td,fontSize:10,color:"#6b7280"}}>{s.market_cap_cat}</td>
                  </tr>
                ))}</tbody>
              </table>
            </Card>
          </div>}
        </>}

        {/* AI RESEARCH ASSISTANT (spec section 34) -- rule-based, routes to real
            app data. Not an LLM. See app/routers/research.py for the design note. */}
        {tab==="research" && <Card title="💬 AI Research Assistant">
          <div style={{fontSize:11,color:"#6b7280",marginBottom:14,lineHeight:1.5}}>
            Ask about a stock, compare two stocks, ask about a sector's momentum,
            find high-volume stocks, or check your portfolio's risk. Answers are
            assembled from live app data (predictions, prices, holdings) — this
            doesn't use a language model, so it only understands a specific set
            of question patterns.
          </div>
          <div style={{display:"flex",gap:8,marginBottom:16}}>
            <input
              style={{...S.inp,flex:1,marginBottom:0}}
              placeholder="e.g. Analyze RELIANCE, Compare TCS and INFY, Banking stocks with momentum…"
              value={researchQuery}
              onChange={e=>setResearchQuery(e.target.value)}
              onKeyDown={e=>e.key==="Enter" && askResearch()}
            />
            <button style={{...S.btnP,width:"auto",padding:"9px 20px"}} onClick={askResearch} disabled={researchLoading || !researchQuery.trim()}>
              {researchLoading ? "…" : "Ask"}
            </button>
          </div>
          {researchHistory.slice().reverse().map((h,i)=>(
            <div key={i} style={{marginBottom:16,paddingBottom:16,borderBottom:"1px solid #1f2937"}}>
              <div style={{fontSize:12,color:"#a5b4fc",fontWeight:600,marginBottom:6}}>You asked: "{h.q}"</div>
              {h.result.error && <div style={{fontSize:12,color:"#f87171"}}>{h.result.error}</div>}
              {h.result.answer && <div style={{fontSize:13,color:"#e5e7eb",lineHeight:1.6}}>{h.result.answer}</div>}
              {h.result.intent==="compare" && h.result.data && (
                <div style={{display:"grid",gridTemplateColumns:`repeat(${Object.keys(h.result.data).length},1fr)`,gap:10,marginTop:10}}>
                  {Object.entries(h.result.data).map(([tk,d])=>(
                    <div key={tk} style={{background:"#1f2937",borderRadius:8,padding:"10px 12px",cursor:"pointer"}} onClick={()=>setSelectedTicker(tk)}>
                      <div style={{fontSize:10,color:"#6b7280",marginBottom:3}}>{tk}</div>
                      {d.error ? <div style={{fontSize:11,color:"#f87171"}}>{d.error}</div> : (
                        <>
                          <div style={{fontSize:13,fontWeight:600}}>{d.prediction} · {d.confidence}%</div>
                          <div style={{fontSize:11,color:"#6b7280"}}>₹{d.current_price}</div>
                        </>
                      )}
                    </div>
                  ))}
                </div>
              )}
              {h.result.intent==="sector_momentum" && h.result.data && (
                <table style={{...S.tbl,marginTop:8}}>
                  <tbody>{h.result.data.map(r=>(
                    <tr key={r.ticker} onClick={()=>setSelectedTicker(r.ticker)} style={{cursor:"pointer"}}>
                      <td style={S.td}><span style={S.pill}>{r.ticker}</span></td>
                      <td style={S.td}>{r.company?.slice(0,24)}</td>
                      <td style={{...S.td,...g(r.change_pct)}}>{r.change_pct>=0?"+":""}{r.change_pct}%</td>
                    </tr>
                  ))}</tbody>
                </table>
              )}
              {h.result.intent==="unusual_volume" && h.result.data?.data && (
                <table style={{...S.tbl,marginTop:8}}>
                  <tbody>{h.result.data.data.map(r=>(
                    <tr key={r.ticker} onClick={()=>setSelectedTicker(r.ticker)} style={{cursor:"pointer"}}>
                      <td style={S.td}><span style={S.pill}>{r.ticker}</span></td>
                      <td style={S.td}>{r.company?.slice(0,24)}</td>
                      <td style={S.td}>{r.volume_ratio}x avg volume</td>
                    </tr>
                  ))}</tbody>
                </table>
              )}
              {h.result.intent==="analyze" && h.result.ticker && !h.result.error && (
                <button style={{...S.btnP,width:"auto",padding:"5px 14px",fontSize:11,marginTop:8}} onClick={()=>setSelectedTicker(h.result.ticker)}>
                  Open {h.result.ticker} detail →
                </button>
              )}
            </div>
          ))}
          {!researchHistory.length && <div style={{color:"#6b7280",fontSize:12}}>No questions asked yet.</div>}
        </Card>}


        {tab==="analytics" && <>
          {benchmark && <div style={S.g3}>
            <Met label="Portfolio Return" value={`${(benchmark.portfolio_return_pct||0)>=0?"+":""}${benchmark.portfolio_return_pct}%`} color={(benchmark.portfolio_return_pct||0)>=0?"#10b981":"#ef4444"}/>
            <Met label="Alpha vs NIFTY 50" value={`${(benchmark.alpha_vs_nifty||0)>=0?"+":""}${benchmark.alpha_vs_nifty}%`} color={(benchmark.alpha_vs_nifty||0)>=0?"#10b981":"#ef4444"}/>
            <Met label="Holdings" value={portfolio?.summary?.holdings_count||0}/>
          </div>}
          {dividends && <Card title="Dividend Calendar" right={<span style={{fontSize:11,color:"#10b981"}}>Projected ₹{parseFloat(dividends.total_projected_income||0).toLocaleString("en-IN")}</span>}>
            <table style={S.tbl}>
              <thead><tr>{["Stock","Shares","Div/Share","Income","Ex-Date","Pay Date","Type"].map(h=><th key={h} style={S.th}>{h}</th>)}</tr></thead>
              <tbody>{(dividends.dividends||[]).map((d,i)=>(
                <tr key={i}>
                  <td style={S.td}><span style={S.pill}>{d.ticker}</span></td>
                  <td style={S.td}>{d.shares_held}</td>
                  <td style={S.td}>₹{d.amount_per_share}</td>
                  <td style={{...S.td,color:"#10b981"}}>₹{fmt(d.income_earned)}</td>
                  <td style={{...S.td,fontSize:11}}>{d.ex_date}</td>
                  <td style={{...S.td,fontSize:11}}>{d.pay_date||"—"}</td>
                  <td style={S.td}><span style={{fontSize:10,padding:"2px 7px",borderRadius:99,background:"#1e3a5f",color:"#60a5fa"}}>{d.dividend_type}</span></td>
                </tr>
              ))}</tbody>
            </table>
          </Card>}
        </>}

        {/* P&L TAX */}
        {tab==="pnl" && pnl && <>
          <div style={S.g4}>
            <Met label="STCG Gains" value={`₹${fmt(pnl.tax_summary?.stcg)}`} color="#f59e0b"/>
            <Met label="LTCG Gains" value={`₹${fmt(pnl.tax_summary?.ltcg)}`} color="#10b981"/>
            <Met label="STCG Tax @15%" value={`₹${fmt(pnl.tax_summary?.stcg_tax)}`} color="#ef4444"/>
            <Met label="LTCG Tax @10%" value={`₹${fmt(pnl.tax_summary?.ltcg_tax)}`} color="#ef4444"/>
          </div>
          <Card title="Realized Trades — Tax Report">
            <table style={S.tbl}>
              <thead><tr>{["Stock","Qty","Sell Price","Value","Tax Type","STT","Date"].map(h=><th key={h} style={S.th}>{h}</th>)}</tr></thead>
              <tbody>{(pnl.realized||[]).map((r,i)=>(
                <tr key={i}>
                  <td style={S.td}><span style={S.pill}>{r.ticker}</span></td>
                  <td style={S.td}>{r.quantity}</td>
                  <td style={S.td}>₹{fmt(r.price)}</td>
                  <td style={S.td}>₹{fmt(r.total_value)}</td>
                  <td style={S.td}><span style={{fontSize:10,padding:"2px 7px",borderRadius:99,background:r.tax_type==="STCG"?"#78350f":"#065f46",color:r.tax_type==="STCG"?"#fcd34d":"#34d399"}}>{r.tax_type}</span></td>
                  <td style={S.td}>₹{fmt(r.stt)}</td>
                  <td style={{...S.td,fontSize:11,color:"#6b7280"}}>{new Date(r.traded_at).toLocaleDateString("en-IN")}</td>
                </tr>
              ))}</tbody>
            </table>
          </Card>
        </>}

        {/* LIVE */}
        {tab==="live" && <div style={{maxWidth:480}}>
          <Card title="Live Price — Yahoo Finance">
            <div style={{display:"flex",gap:8,marginBottom:16}}>
              <input style={{...S.inp,flex:1,marginBottom:0}} value={liveTicker} onChange={e=>setLiveTicker(e.target.value.toUpperCase())} placeholder="Enter ticker e.g. INFY" onKeyDown={e=>e.key==="Enter"&&doLive()}/>
              <button style={{...S.btnP,width:"auto",padding:"8px 16px"}} onClick={doLive}>Fetch</button>
            </div>
            {liveData ? <>
              <div style={{fontSize:22,fontWeight:600,marginBottom:4}}>{liveData.ticker}</div>
              <div style={{fontSize:36,fontWeight:700,color:"#6366f1",marginBottom:12}}>₹{parseFloat(liveData.price).toFixed(2)}</div>
              <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:10}}>
                {[["Open",`₹${parseFloat(liveData.open).toFixed(2)}`],["High",`₹${parseFloat(liveData.high).toFixed(2)}`],
                  ["Low",`₹${parseFloat(liveData.low).toFixed(2)}`],["Volume",parseInt(liveData.volume).toLocaleString("en-IN")],
                  ["Change",`${parseFloat(liveData.change)>=0?"+":""}₹${parseFloat(liveData.change).toFixed(2)}`],
                  ["Change%",`${liveData.change_pct}%`]].map(([l,v])=>(
                  <div key={l} style={{background:"#1f2937",borderRadius:8,padding:"10px 12px"}}>
                    <div style={{fontSize:10,color:"#6b7280",marginBottom:3}}>{l}</div>
                    <div style={{fontSize:14,fontWeight:500,...(l.includes("Change")?g(parseFloat(liveData.change)):{})}}>{ v}</div>
                  </div>
                ))}
              </div>
            </> : <div style={{color:"#6b7280",fontSize:13,lineHeight:1.6}}>Enter any NSE/BSE ticker and press Fetch to get real-time OHLCV data from Yahoo Finance.</div>}
          </Card>
        </div>}

        {/* DATA HEALTH (spec section 39) -- real numbers from data_sync_log, nothing fabricated */}
        {tab==="data-health" && <Card title="🩺 Data Health" right={
          <button style={{...S.btnP,width:"auto",padding:"5px 12px",fontSize:11}} onClick={loadDataHealth} disabled={dataHealthLoading}>
            {dataHealthLoading ? "Refreshing…" : "↻ Refresh"}
          </button>
        }>
          {!dataHealth && !dataHealthLoading && <div style={{color:"#6b7280",fontSize:12}}>Loading…</div>}
          {dataHealth && <>
            <div style={S.g4}>
              <Met label="Stocks Tracked" value={dataHealth.stocks_tracked} />
              <Met label="Updated Today" value={dataHealth.stocks_updated_today} color="#10b981" />
              <Met label="Stale" value={dataHealth.stocks_stale} color={dataHealth.stocks_stale>0?"#f59e0b":"#10b981"} />
              <Met label="With Price History" value={dataHealth.stocks_with_price_history} />
            </div>
            <div style={{fontSize:11,color:"#6b7280",marginBottom:16}}>
              Latest successful sync: <b style={{color:"#f9fafb"}}>{dataHealth.latest_successful_sync || "never"}</b>
              {" · "}Stocks with today's AI prediction: <b style={{color:"#f9fafb"}}>{dataHealth.stocks_with_todays_prediction}</b>
            </div>

            <div style={{fontSize:12,fontWeight:600,marginBottom:8}}>Most Recent Run — Per Job</div>
            <table style={S.tbl}>
              <thead><tr>{["Job","Status","Started","Processed","Failed"].map(h=><th key={h} style={S.th}>{h}</th>)}</tr></thead>
              <tbody>{(dataHealth.recent_jobs||[]).map(j=>(
                <tr key={j.job_name}>
                  <td style={S.td}>{j.job_name}</td>
                  <td style={{...S.td, color: j.status==="SUCCESS"?"#10b981":j.status==="FAILED"?"#ef4444":j.status==="RUNNING"?"#f59e0b":"#9ca3af"}}>{j.status}</td>
                  <td style={{...S.td,color:"#6b7280"}}>{j.started_at}</td>
                  <td style={S.td}>{j.records_processed}</td>
                  <td style={{...S.td,color:j.records_failed>0?"#f87171":"#6b7280"}}>{j.records_failed}</td>
                </tr>
              ))}</tbody>
            </table>
            {!dataHealth.recent_jobs?.length && (
              <div style={{color:"#6b7280",fontSize:12,marginTop:10}}>
                No sync jobs have run yet. Set ENABLE_SCHEDULER=true in .env, or trigger one manually
                (see README.md) to start populating this page.
              </div>
            )}

            {!!dataHealth.failures_last_24h?.length && (
              <div style={{marginTop:16}}>
                <div style={{fontSize:12,fontWeight:600,marginBottom:8,color:"#f87171"}}>Failures — Last 24h</div>
                {dataHealth.failures_last_24h.map(f=>(
                  <div key={f.job_name} style={{fontSize:12,color:"#fca5a5",padding:"4px 0"}}>
                    {f.job_name}: {f.failures} run(s), {f.total_records_failed} record(s) failed
                  </div>
                ))}
              </div>
            )}
          </>}
        </Card>}
      </div>

      {selectedTicker && (
        <StockDetail ticker={selectedTicker} onClose={() => setSelectedTicker(null)} />
      )}
    </div>
  );
}
