from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from database import get_security_db
from auth import (
    verify_password, create_access_token, create_refresh_token,
    get_current_user, logout_token, is_token_blacklisted,
    require_role, oauth2_scheme
)
from config import ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM, LOGIN_RATE_LIMIT

router = APIRouter(prefix="/api/auth", tags=["auth"])

# Rate limiting simple en memoria para login
_login_attempts = {}

def _check_login_rate_limit(ip: str):
    """Permite 5 intentos por minuto por IP."""
    now = datetime.now(timezone.utc)
    window = _login_attempts.get(ip, [])
    window = [t for t in window if now - t < timedelta(seconds=60)]
    if len(window) >= 5:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Demasiados intentos de login. Espere 1 minuto."
        )
    window.append(now)
    _login_attempts[ip] = window


@router.post("/login")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_security_db)):
    from database import User
    _check_login_rate_limit(form_data.username)
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or user.is_active != 1 or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(data={"sub": user.username})
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "username": user.username,
        "role": user.role,
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }


@router.get("/me")
def read_users_me(current_user=Depends(get_current_user)):
    return {"username": current_user.username, "role": current_user.role}


@router.post("/logout")
def logout(token: str = Depends(oauth2_scheme), db: Session = Depends(get_security_db)):
    logout_token(token, db)
    return {"message": "Logged out successfully"}


@router.post("/refresh")
def refresh_token(refresh_token: str = Body(..., embed=True), db: Session = Depends(get_security_db)):
    if is_token_blacklisted(refresh_token, db):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has been revoked")
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    from database import User
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    new_access = create_access_token(data={"sub": user.username})
    new_refresh = create_refresh_token(data={"sub": user.username})
    return {
        "access_token": new_access,
        "refresh_token": new_refresh,
        "token_type": "bearer",
    }


@router.get("/users")
def list_users(current_user=Depends(require_role("admin")), db: Session = Depends(get_security_db)):
    from database import User
    users = db.query(User).all()
    return [
        {"id": u.id, "username": u.username, "role": u.role, "is_active": u.is_active}
        for u in users
    ]
