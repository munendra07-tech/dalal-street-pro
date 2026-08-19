from fastapi import APIRouter, Depends
from typing import Optional
from app.database import query
from app.auth import get_current_user

router = APIRouter(prefix="/mf", tags=["Mutual Funds"])

@router.get("/")
def list_funds(category: Optional[str] = None):
    if category:
        return query("SELECT * FROM mutual_funds WHERE category=%s ORDER BY rating DESC,returns_1y DESC", (category.upper(),), fetch=True)
    return query("SELECT * FROM mutual_funds ORDER BY rating DESC,returns_1y DESC", fetch=True)

@router.get("/top-performers")
def top_performers():
    return query("SELECT * FROM mutual_funds WHERE returns_1y IS NOT NULL ORDER BY returns_1y DESC LIMIT 10", fetch=True)

@router.get("/holdings/{portfolio_id}")
def mf_holdings(portfolio_id: int, user: dict = Depends(get_current_user)):
    return query("""
        SELECT mf.fund_name, mf.fund_house, mf.category, mf.current_nav, mf.returns_1y, mf.returns_3y,
               mf.expense_ratio, mf.rating, mh.units, mh.avg_nav, mh.invested_amount,
               ROUND(mh.units*mf.current_nav,2) AS current_value,
               ROUND(mh.units*mf.current_nav-mh.invested_amount,2) AS pnl,
               ROUND((mh.units*mf.current_nav-mh.invested_amount)/mh.invested_amount*100,2) AS pnl_pct
        FROM mf_holdings mh JOIN mutual_funds mf ON mh.fund_id=mf.fund_id
        WHERE mh.portfolio_id=%s ORDER BY current_value DESC
    """, (portfolio_id,), fetch=True)
