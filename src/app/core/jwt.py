from datetime import datetime, timedelta
# import jwt  # PyJWT
from typing import Tuple
# from src.app.core.config import settings_jwt

# def create_access_token(subject: str) -> Tuple[str, int]:
#     expire = datetime.utcnow() + timedelta(minutes=settings_jwt.ACCESS_TOKEN_EXPIRE_MINUTES)
#     payload = {"sub": subject, "exp": expire, "type": "access"}
#     token = jwt.encode(payload, settings_jwt.JWT_SECRET, algorithm=settings_jwt.JWT_ALGORITHM)
#     return token, int(timedelta(minutes=settings_jwt.ACCESS_TOKEN_EXPIRE_MINUTES).total_seconds())
#
# def create_refresh_token(subject: str) -> Tuple[str, int]:
#     expire = datetime.utcnow() + timedelta(days=settings_jwt.REFRESH_TOKEN_EXPIRE_DAYS)
#     payload = {"sub": subject, "exp": expire, "type": "refresh"}
#     token = jwt.encode(payload, settings_jwt.JWT_SECRET, algorithm=settings_jwt.JWT_ALGORITHM)
#     return token, int(timedelta(days=settings_jwt.REFRESH_TOKEN_EXPIRE_DAYS).total_seconds())
#
# def decode_token(token: str) -> dict:
#     return jwt.decode(token, settings_jwt.JWT_SECRET, algorithms=[settings_jwt.JWT_ALGORITHM])
from jose import jwt, JWTError
from fastapi import Request, HTTPException, status

SECRET_KEY = "super-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
ACCESS_TOKEN_COOKIE = "access_token"

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


async def get_current_user_id(request: Request) -> str:
    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    return user_id