import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app import auth
from app.routers import (
    portfolio,
    stocks,
    analytics,
    watchlist,
    alerts,
    ipo,
    mutualfunds,
    live,
    ai_prediction,
    screener,
    intelligence,
    research,
    data_health,
)
from app.scheduler import start_scheduler, shutdown_scheduler

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Dalal Street Pro API", version="2.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# NOTE: routers/prediction.py (legacy, prefix "/prediction") has been
# retired. It duplicated ai_prediction.py's ensemble logic with its own
# standalone RandomForest and wasn't used anywhere in the frontend
# (api.js only ever called /prediction/ai/{ticker}). The file is still
# on disk in case you want to diff it, but it's no longer imported or
# registered. Delete it once you've confirmed nothing external calls it.
for r in [
    auth.router,
    portfolio.router,
    stocks.router,
    analytics.router,
    watchlist.router,
    alerts.router,
    ipo.router,
    mutualfunds.router,
    live.router,
    ai_prediction.router,
    screener.router,
    intelligence.router,
    research.router,
    data_health.router,
]:
    app.include_router(r)


@app.on_event("startup")
def _on_startup():
    start_scheduler()


@app.on_event("shutdown")
def _on_shutdown():
    shutdown_scheduler()


@app.get("/")
def root():
    return {
        "app": "Dalal Street Pro API",
        "version": "2.2",
        "docs": "/docs",
    }
