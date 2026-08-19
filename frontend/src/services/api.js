const BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";
const h = () => {
  const t = localStorage.getItem("token");
  return { "Content-Type": "application/json", ...(t ? { Authorization: `Bearer ${t}` } : {}) };
};
const req = async (path, opts = {}) => {
  const r = await fetch(`${BASE}${path}`, { headers: h(), ...opts });
  return r.json();
};
export const api = {
  me: () => req("/auth/me"),
  register: d => req("/auth/register", { method: "POST", body: JSON.stringify(d) }),
  login: (u, p) => req("/auth/login", {
    method: "POST", headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({ username: u, password: p })
  }),
  getStocks: (p = {}) => req(`/stocks/?${new URLSearchParams(p)}`),
  getStock: t => req(`/stocks/${t}`),
  screener: p => req(`/stocks/screener?${new URLSearchParams(p)}`),
  getPortfolio: id => req(`/portfolio/${id}`),
  executeTrade: (id, d) => req(`/portfolio/${id}/trade`, { method: "POST", body: JSON.stringify(d) }),
  getTrades: id => req(`/portfolio/${id}/trades`),
  getPnl: id => req(`/portfolio/${id}/pnl`),
  createSip: (id, d) => req(`/portfolio/${id}/sip`, { method: "POST", body: JSON.stringify(d) }),
  getSips: id => req(`/portfolio/${id}/sip`),
  getWatchlist: () => req("/watchlist/"),
  addWatchlist: d => req("/watchlist/", { method: "POST", body: JSON.stringify(d) }),
  removeWatchlist: id => req(`/watchlist/${id}`, { method: "DELETE" }),
  getAlerts: () => req("/alerts/"),
  createAlert: d => req("/alerts/", { method: "POST", body: JSON.stringify(d) }),
  deleteAlert: id => req(`/alerts/${id}`, { method: "DELETE" }),
  leaderboard: () => req("/analytics/leaderboard"),
  sectorBreakdown: id => req(`/analytics/sector-breakdown/${id}`),
  benchmark: id => req(`/analytics/benchmark/${id}`),
  dividends: uid => req(`/analytics/dividends/${uid}`),
  marketOverview: () => req("/analytics/market-overview"),
  getIpos: s => req(`/ipo/${s ? "?status=" + s : ""}`),
  getUpcomingIpos: () => req("/ipo/upcoming"),
  getMFs: cat => req(`/mf/${cat ? "?category=" + cat : ""}`),
  getMFHoldings: id => req(`/mf/holdings/${id}`),
  livePrice: t => req(`/live/${t}`),
  aiPrediction: ticker =>
  req(`/prediction/ai/${encodeURIComponent(ticker)}`),
  stockHistory: (ticker, period = "6mo") =>
  req(`/live/${encodeURIComponent(ticker)}/history?period=${period}`),
  aiScreenerTop: (p = {}) => req(`/screener/top?${new URLSearchParams(p)}`),
  unusualVolume: () => req("/screener/unusual-volume"),
  marketBreadth: () => req("/analytics/breadth"),
  sectorPerformance: () => req("/analytics/sectors"),
  stockNews: (ticker, refresh = false) =>
  req(`/news/${encodeURIComponent(ticker)}${refresh ? "?refresh=true" : ""}`),
  stockSentiment: ticker => req(`/sentiment/${encodeURIComponent(ticker)}`),
  stockFundamentals: (ticker, refresh = false) =>
  req(`/fundamentals/${encodeURIComponent(ticker)}${refresh ? "?refresh=true" : ""}`),
  marketRegime: () => req("/analytics/regime"),
  dataHealth: () => req("/admin/data-health/"),
  researchAsk: (q, portfolioId) =>
  req(`/research/ask?q=${encodeURIComponent(q)}${portfolioId ? "&portfolio_id=" + portfolioId : ""}`),
};
