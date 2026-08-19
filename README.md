# 📈 Dalal Street Pro

> A production-grade **Indian Stock Market Portfolio Tracker** — FastAPI + MySQL + React

[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1?style=flat&logo=mysql)](https://mysql.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=flat&logo=react)](https://reactjs.org)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python)](https://python.org)

---

## Features

| Module | What it does |
|---|---|
| 🔐 JWT Auth | Register with PAN, bcrypt passwords, risk profile |
| 💼 Portfolio | Live P&L via SQL VIEW, day gain tracking |
| 🔄 Trade Engine | BUY/SELL with CNC/MIS/NRML, auto STT + brokerage |
| 📅 SIP Planner | Daily/Weekly/Monthly/Quarterly SIPs with return tracking |
| 🏦 Mutual Funds | NAV, 1Y/3Y/5Y returns, expense ratio, star rating |
| 💰 Dividends | Ex-date calendar, income projection per holding |
| 🔍 Stock Screener | Filter by P/E, P/B, dividend yield, sector, market cap |
| 🆚 Benchmark | Portfolio vs NIFTY 50, alpha calculation |
| 🚀 IPO Tracker | GMP, subscription, listing gain, upcoming IPOs |
| 🧾 Tax Report | STCG (15%) / LTCG (10%) auto-classification |
| 📡 Live Prices | Alpha Vantage real-time quotes, background DB sync |
| 🔔 Smart Alerts | Price alerts via App, SMS, Email, WhatsApp |
| ⭐ Watchlist | 52-week range, P/E, dividend yield tracking |
| 🏛️ Market | NIFTY/SENSEX indices, top gainers/losers, news feed |

---

## SQL Concepts Used

| Concept | Where |
|---|---|
| `CREATE TABLE` + `FOREIGN KEY` | All 14 tables |
| `ON DELETE CASCADE` | portfolios → holdings, trades |
| `ENUM`, `CHECK`, `UNIQUE` | stocks, trades, alerts |
| `GENERATED ALWAYS AS` | trades.total_value |
| `ON UPDATE CURRENT_TIMESTAMP` | stocks.updated_at |
| `VIEW` | v_portfolio_pnl, v_dividend_income, v_tax_report, v_sip_performance |
| `INDEX` | 9 custom indexes |
| `GROUP BY` + `HAVING` | Sector breakdown |
| `WINDOW: RANK()` | Leaderboard |
| `WINDOW: LAG()` | Price daily change |
| `WINDOW: NTILE()` | Portfolio quartile |
| `CTE (WITH)` | User wealth, sector ranking |
| `CASE WHEN` | STCG vs LTCG classification |
| `ON DUPLICATE KEY UPDATE` | Price history upsert |

---

## Setup

### Backend

```bash
git clone https://github.com/YOUR_USERNAME/dalal-street-pro.git
cd dalal-street-pro

python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env           # Fill in DB password, SECRET_KEY, ALPHA_VANTAGE_KEY

mysql -u root -p < sql/01_schema.sql
mysql -u root -p < sql/02_seed.sql

uvicorn app.main:app --reload
# API  → http://localhost:8000
# Docs → http://localhost:8000/docs
```

### Frontend

```bash
cd frontend
npm install
npm run dev
# Dashboard → http://localhost:3000
```

### Tests

```bash
pytest tests/ -v
```

---

## Project Structure

```
dalal-street-pro/
├── sql/
│   ├── 01_schema.sql    # 14 tables, 4 views, 9 indexes
│   ├── 02_seed.sql      # 20 NSE stocks, 8 MFs, real IPOs
│   └── 03_queries.sql   # 12 practice queries
├── app/
│   ├── main.py          # FastAPI entry point
│   ├── auth.py          # JWT + bcrypt
│   ├── database.py      # MySQL connection pool
│   └── routers/
│       ├── auth.py      # /auth/*
│       ├── portfolio.py # /portfolio/* (holdings, trades, SIP, P&L)
│       ├── stocks.py    # /stocks/* (list, screener, history)
│       ├── analytics.py # /analytics/* (leaderboard, benchmark, dividends)
│       ├── watchlist.py # /watchlist/
│       ├── alerts.py    # /alerts/
│       ├── ipo.py       # /ipo/
│       ├── mutualfunds.py # /mf/
│       └── live.py      # /live/* (Alpha Vantage)
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── pages/
│   │   │   ├── Login.jsx       # Register + login
│   │   │   └── Dashboard.jsx   # 12 feature tabs
│   │   └── services/api.js     # All API calls
│   ├── package.json
│   └── vite.config.js
├── tests/
│   └── test_api.py      # 15 pytest tests
├── requirements.txt
├── .env.example
└── README.md
```

---

## What makes this stand out on GitHub

- Real Indian market data — 20 NSE/BSE stocks, actual IPOs (Swiggy, Hexaware, Ather)
- 14 SQL tables with proper relationships, constraints, indexes
- 4 SQL Views calculating P&L, dividends, tax, SIP performance live
- Window functions RANK(), LAG(), NTILE() used in real analytical queries
- Full-stack — working REST API + React dashboard + 15 automated tests
- India-specific — STCG/LTCG tax rules, STT, CNC/MIS/NRML order types, INR formatting, PAN

## Tech Stack

| Layer | Technology |
|---|---|
| API | FastAPI + Uvicorn |
| Database | MySQL 8.0 (raw SQL, connection pool) |
| Auth | JWT (python-jose) + bcrypt (passlib) |
| Live Prices | Alpha Vantage API (httpx async) |
| Frontend | React 18 + Vite + Recharts |
| Testing | pytest + FastAPI TestClient |
