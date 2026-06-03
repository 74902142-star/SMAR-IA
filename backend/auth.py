"""SMAR-IA — Autenticación JWT, autorización RBAC y blacklist de tokens persistente."""

import bcrypt
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional

from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from database import get_security_db, User, RevokedToken
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

logger = logging.getLogger("smar-ia-auth")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica contraseña contra hash bcrypt."""
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except (ValueError, TypeError, AttributeError):
        return False


def get_password_hash(password: str) -> str:
    """Genera hash bcrypt de una contraseña."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


JWT_AUDIENCE = "smar-ia-api"


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crea JWT de acceso con expiración."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "aud": JWT_AUDIENCE, "role": data.get("role", "viewer"), "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict) -> str:
    """Crea JWT de refresco con expiración de 7 días."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=7)
    to_encode.update({"exp": expire, "aud": JWT_AUDIENCE, "type": "refresh", "role": data.get("role", "viewer")})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def logout_token(token: str, db: Session):
    """Añade token a la blacklist persistente."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], audience=JWT_AUDIENCE)
        exp = payload.get("exp")
        expires_at = datetime.fromtimestamp(exp, tz=timezone.utc) if exp else datetime.now(timezone.utc) + timedelta(hours=1)
    except JWTError:
        expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
    existing = db.query(RevokedToken).filter(RevokedToken.token == token).first()
    if not existing:
        db.add(RevokedToken(token=token, expires_at=expires_at))
        db.commit()


def is_token_blacklisted(token: str, db: Session) -> bool:
    """Verifica si un token está en la blacklist persistente."""
    entry = db.query(RevokedToken).filter(RevokedToken.token == token).first()
    if entry:
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        expires = entry.expires_at
        if expires and expires.tzinfo is not None:
            expires = expires.replace(tzinfo=None)
        if expires and expires < now:
            db.delete(entry)
            db.commit()
            return False
        return True
    return False


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_security_db)) -> User:
    """Obtiene el usuario autenticado desde el JWT."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], audience=JWT_AUDIENCE)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    if is_token_blacklisted(token, db):
        raise credentials_exception

    token_type = payload.get("type")
    if token_type is not None and token_type != "access":
        raise credentials_exception

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user


async def get_current_user_ws(websocket=None, token: str = None):
    """Valida JWT para conexiones WebSocket (token vía primer mensaje)."""
    if not token:
        if websocket:
            await websocket.close(code=4001)
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], audience=JWT_AUDIENCE)
        username: str = payload.get("sub")
        if username is None:
            if websocket:
                await websocket.close(code=4001)
            return None
        db = next(get_security_db())
        try:
            if is_token_blacklisted(token, db):
                if websocket:
                    await websocket.close(code=4001)
                return None
            user = db.query(User).filter(User.username == username).first()
            return user
        finally:
            db.close()
    except JWTError:
        if websocket:
            await websocket.close(code=4001)
        return None


def require_role(required_role: str):
    """Dependency factory: requiere un rol específico (admin o viewer)."""
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role != required_role and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user
    return role_checker
