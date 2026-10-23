from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .config import settings
from .models import User
from .security import hash_password, verify_password


async def register_user(session: AsyncSession, username: str, display_name: str, password: str) -> User:
    existing = await session.scalar(select(User).where(User.username == username))
    if existing:
        raise ValueError("username already exists")
    user = User(username=username, display_name=display_name or username, password_hash=hash_password(password))
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def authenticate_user(session: AsyncSession, username: str, password: str) -> User | None:
    user = await session.scalar(select(User).where(User.username == username, User.status == "active"))
    if user is None or not verify_password(password, user.password_hash):
        return None
    return user


def issue_token(user_id: str, session_id: str) -> str:
    now = datetime.now(timezone.utc)
    return jwt.encode(
        {"sub": user_id, "sid": session_id, "iat": now, "exp": now + timedelta(minutes=settings.session_minutes)},
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )


def new_session_id() -> str:
    return str(uuid4())
