"""
tests/test_api.py — pytest test suite
Run: pytest tests/ -v
"""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root():
    r = client.get("/")
    assert r.status_code == 200
    assert r.json()["app"] == "Dalal Street Pro API"

def test_register_and_login():
    r = client.post("/auth/register", json={
        "username": "test_user_pytest", "email": "pytest@test.com",
        "password": "Test@1234", "risk_profile": "MODERATE"
    })
    assert r.status_code in (201, 400)

def test_list_stocks():
    r = client.get("/stocks/")
    assert r.status_code == 200
    assert isinstance(r.json(), list)

def test_stock_by_ticker():
    r = client.get("/stocks/RELIANCE")
    assert r.status_code == 200
    assert r.json()["ticker"] == "RELIANCE"

def test_stock_not_found():
    r = client.get("/stocks/INVALIDXYZ")
    assert r.status_code == 404

def test_screener():
    r = client.get("/stocks/screener?pe_max=30&div_min=0.5")
    assert r.status_code == 200

def test_top_gainers():
    r = client.get("/stocks/top-gainers")
    assert r.status_code == 200

def test_ipo_list():
    r = client.get("/ipo/")
    assert r.status_code == 200

def test_ipo_upcoming():
    r = client.get("/ipo/upcoming")
    assert r.status_code == 200

def test_mf_list():
    r = client.get("/mf/")
    assert r.status_code == 200

def test_mf_top_performers():
    r = client.get("/mf/top-performers")
    assert r.status_code == 200
    assert len(r.json()) <= 10

def test_market_overview():
    r = client.get("/analytics/market-overview")
    assert r.status_code == 200
    data = r.json()
    assert "indices" in data and "gainers" in data and "news" in data

def test_leaderboard():
    r = client.get("/analytics/leaderboard")
    assert r.status_code == 200

def test_protected_route_without_token():
    r = client.get("/watchlist/")
    assert r.status_code == 401

def test_protected_route_bad_token():
    r = client.get("/watchlist/", headers={"Authorization": "Bearer bad_token"})
    assert r.status_code == 401
