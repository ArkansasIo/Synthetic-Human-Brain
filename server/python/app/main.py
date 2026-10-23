from __future__ import annotations

from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, FastAPI, HTTPException, Query, WebSocket, WebSocketDisconnect, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .auth import authenticate_user, issue_token, new_session_id, register_user
from .config import settings
from .db import db_session
from .models import (
    AuditLog,
    Experiment,
    Job,
    Project,
    ProjectMember,
    Role,
    Server,
    Session,
    TelemetryEvent,
    User,
    UserRole,
    Worker,
)
from .protocol import envelope

app = FastAPI(title=settings.app_name, version=settings.version)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

bearer = HTTPBearer(auto_error=False)


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    display_name: str | None = None


class ProjectRequest(BaseModel):
    name: str
    description: str = ""


class ExperimentRequest(BaseModel):
    name: str
    backend: str = "auto"


class JobRequest(BaseModel):
    operation: str
    payload: dict = Field(default_factory=dict)


class TelemetryRequest(BaseModel):
    metric: str
    value: float
    timestamp: datetime | None = None


async def current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: AsyncSession = Depends(db_session),
) -> User:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    try:
        claims = jwt.decode(credentials.credentials, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc

    user_id = claims.get("sub")
    session_id = claims.get("sid")
    if not user_id or not session_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session")

    session = await db.get(Session, session_id)
    if session is None or session.revoked_at is not None or session.expires_at <= datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired or revoked")

    user = await db.get(User, user_id)
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User unavailable")
    return user


async def role_names(db: AsyncSession, user_id: str) -> set[str]:
    result = await db.execute(
        select(Role.name).join(UserRole, UserRole.role_id == Role.id).where(UserRole.user_id == user_id)
    )
    return set(result.scalars().all())


async def require_role(db: AsyncSession, user: User, *allowed: str) -> None:
    roles = await role_names(db, user.id)
    if not roles.intersection(allowed) and "administrator" not in roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")


async def write_audit(db: AsyncSession, user_id: str | None, action: str, target_type: str, target_id: str | None) -> None:
    db.add(AuditLog(user_id=user_id, action=action, target_type=target_type, target_id=target_id))


@app.get("/api/v1/health")
async def health() -> dict:
    return {"status": "ok", "service": settings.app_name, "version": settings.version}


@app.get("/api/v1/about")
async def about() -> dict:
    return {"name": settings.app_name, "version": settings.version, "developer": settings.developer}


@app.post("/api/v1/auth/register")
async def register(request: RegisterRequest, db: AsyncSession = Depends(db_session)) -> dict:
    try:
        user = await register_user(db, request.username, request.email, request.password, request.display_name)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    await db.commit()
    return {"id": user.id, "username": user.username, "email": user.email}


@app.post("/api/v1/auth/login")
async def login(request: LoginRequest, db: AsyncSession = Depends(db_session)) -> dict:
    user = await authenticate_user(db, request.username, request.password)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    session_id = new_session_id()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.session_minutes)
    db.add(Session(id=session_id, user_id=user.id, expires_at=expires_at))
    token = issue_token(user.id, session_id)
    await write_audit(db, user.id, "auth.login", "user", user.id)
    await db.commit()
    return {"access_token": token, "token_type": "bearer", "expires_at": expires_at.isoformat()}


@app.post("/api/v1/auth/logout")
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: AsyncSession = Depends(db_session),
) -> dict:
    try:
        claims = jwt.decode(credentials.credentials, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc
    session_id = claims.get("sid")
    user_id = claims.get("sub")
    session = await db.get(Session, session_id) if session_id else None
    if session is not None:
        session.revoked_at = datetime.now(timezone.utc)
    await write_audit(db, user_id, "auth.logout", "session", session_id)
    await db.commit()
    return {"status": "logged_out"}
