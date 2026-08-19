import os
import secrets
import logging
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv

from app.database import query

load_dotenv()
logger = logging.getLogger("dalal_street.security")

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    # Fail-safe for local dev only: generate a random key so the app still
    # runs, but warn loudly since this invalidates tokens on every restart
    # and must NEVER happen in production. Set SECRET_KEY in .env.
    SECRET_KEY = secrets.token_hex(32)
    logger.warning(
        "SECRET_KEY not found in environment/.env — generated a temporary "
        "random key for this process. All existing tokens are now invalid "
        "and new tokens won't survive a restart. Add SECRET_KEY=<random hex> "
        "to your .env file to fix this permanently."
    )

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str):
    return pwd_context.verify(password, hashed)


def create_token(data: dict):
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        uid = payload.get("sub")
        if uid is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    rows = query(
        "SELECT * FROM users WHERE user_id=%s",
        (uid,),
        fetch=True,
    )

    if not rows:
        raise HTTPException(status_code=401, detail="User not found")

    return rows[0]