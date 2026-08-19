from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from app.database import query
from app.security import (
    hash_password,
    verify_password,
    create_token,
    get_current_user,
)
router = APIRouter(prefix="/auth", tags=["Auth"])

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    phone: str = ""
    pan_number: str = ""
    risk_profile: str = "MODERATE"
    starting_balance: float = 1000000.0

@router.post("/register", status_code=201)
def register(body: RegisterRequest):
    if query("SELECT user_id FROM users WHERE username=%s OR email=%s", (body.username, body.email), fetch=True):
        raise HTTPException(400, "Username or email already exists")
    uid = query("INSERT INTO users (username,email,phone,pan_number,password_hash,balance,risk_profile) VALUES (%s,%s,%s,%s,%s,%s,%s)",
          (body.username, body.email, body.phone, body.pan_number or None,
           hash_password(body.password), body.starting_balance, body.risk_profile), return_lastrowid=True)
    query("INSERT INTO portfolios (user_id,name,is_default,color) VALUES (%s,'My Portfolio',1,'#6366f1')", (uid,))
    return {"access_token": create_token({"sub": str(uid)}), "token_type": "bearer",
            "user_id": uid, "username": body.username}

@router.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends()):
    rows = query("SELECT * FROM users WHERE username=%s AND is_active=1", (form.username,), fetch=True)
    if not rows or not verify_password(form.password, rows[0]["password_hash"]):
        raise HTTPException(401, "Invalid credentials")
    user = rows[0]
    portfolios = query("SELECT portfolio_id,name,color FROM portfolios WHERE user_id=%s", (user["user_id"],), fetch=True)
    return {"access_token": create_token({"sub": str(user["user_id"])}), "token_type": "bearer",
            "user_id": user["user_id"], "username": user["username"], "portfolios": portfolios}

@router.get("/me")
def me(user: dict = Depends(get_current_user)):
    portfolios = query("SELECT portfolio_id,name,color,is_default FROM portfolios WHERE user_id=%s", (user["user_id"],), fetch=True)
    return {**user, "portfolios": portfolios}
