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


class AuthRequest(BaseModel):
    username: str = Field(min_length=1, max_length=128)
    password: str = Field(min_length=1, max_length=512)
    display_name: str = Field(default="", max_length=255)
    client_id: str = Field(default="browser", max_length=128)
    platform: str = Field(default="browser", max_length=32)


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str = ""
    visibility: str = "private"


class ExperimentCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    backend: str = Field(default="auto", max_length=32)
    configuration: dict = Field(default_factory=dict)


class JobCreate(BaseModel):
    operation: str = Field(min_length=1, max_length=128)
    payload: dict = Field(default_factory=dict)


class TelemetryCreate(BaseModel):
    metric: str = Field(min_length=1, max_length=128)
    value: float
    metadata: dict = Field(default_factory=dict)


def utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def safe_user(user: User, roles: list[str]) -> dict:
    return {"id": user.id, "username": user.username, "display_name": user.display_name, "status": user.status, "roles": roles}


async def role_names(session: AsyncSession, user_id: str) -> list[str]:
    result = await session.execute(
        select(Role.name).join(UserRole, UserRole.role_id == Role.id).where(UserRole.user_id == user_id)
    )
    return list(result.scalars().all())


async def current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    session: AsyncSession = Depends(db_session),
) -> User:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Bearer token required")
    try:
        claims = jwt.decode(credentials.credentials, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        user_id = claims.get("sub")
        session_id = claims.get("sid")
        if not user_id or not session_id:
            raise ValueError("missing token claims")
    except (jwt.InvalidTokenError, ValueError) as exc:
        raise HTTPException(status_code=401, detail="Invalid access token") from exc

    auth_session = await session.get(Session, session_id)
    user = await session.get(User, user_id)
    if auth_session is None or user is None or auth_session.revoked_at is not None or auth_session.expires_at < utcnow():
        raise HTTPException(status_code=401, detail="Session expired or revoked")
    auth_session.last_seen_at = utcnow()
    await session.commit()
    return user


async def require_role(user: User, session: AsyncSession, *allowed: str) -> list[str]:
    roles = await role_names(session, user.id)
    if not set(roles).intersection(allowed):
        raise HTTPException(status_code=403, detail="Insufficient role")
    return roles


async def write_audit(
    session: AsyncSession,
    user_id: str | None,
    action: str,
    resource_type: str | None = None,
    resource_id: str | None = None,
    details: dict | None = None,
) -> None:
    session.add(
        AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details_json=details or {},
        )
    )


async def project_access(session: AsyncSession, project_id: str, user: User) -> Project:
    project = await session.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.owner_user_id == user.id:
        return project
    member = await session.scalar(
        select(ProjectMember).where(ProjectMember.project_id == project_id, ProjectMember.user_id == user.id)
    )
    if member is None:
        roles = await role_names(session, user.id)
        if "administrator" not in roles:
            raise HTTPException(status_code=403, detail="Project access denied")
    return project


@app.get("/api/v1/health")
async def health() -> dict:
    return {"status": "ok", "service": settings.app_name, "version": settings.version}


@app.get("/api/v1/about")
async def about() -> dict:
    return {
        "name": settings.app_name,
        "version": settings.version,
        "developer": settings.developer,
        "role": "Public research API and orchestration layer",
        "platforms": ["windows", "macos", "linux"],
        "clients": ["desktop", "browser"],
        "protocols": ["HTTPS", "WSS"],
    }


@app.post("/api/v1/auth/register")
async def register(request: AuthRequest, session: AsyncSession = Depends(db_session)) -> dict:
    try:
        user = await register_user(session, request.username, request.display_name, request.password)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    role = await session.scalar(select(Role).where(Role.name == "researcher"))
    if role is not None:
        session.add(UserRole(user_id=user.id, role_id=role.id))
    session_id = new_session_id()
    expires = utcnow() + timedelta(minutes=settings.session_minutes)
    session.add(Session(id=session_id, user_id=user.id, client_id=request.client_id, platform=request.platform, expires_at=expires))
    await write_audit(session, user.id, "auth.register", "user", user.id)
    await session.commit()
    return {"access_token": issue_token(user.id, session_id), "token_type": "bearer", "session_id": session_id, "user": safe_user(user, ["researcher"])}


@app.post("/api/v1/auth/login")
async def login(request: AuthRequest, session: AsyncSession = Depends(db_session)) -> dict:
    user = await authenticate_user(session, request.username, request.password)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    session_id = new_session_id()
    expires = utcnow() + timedelta(minutes=settings.session_minutes)
    user.last_login_at = utcnow()
    session.add(Session(id=session_id, user_id=user.id, client_id=request.client_id, platform=request.platform, expires_at=expires))
    await write_audit(session, user.id, "auth.login", "user", user.id, {"client_id": request.client_id, "platform": request.platform})
    await session.commit()
    roles = await role_names(session, user.id)
    return {"access_token": issue_token(user.id, session_id), "token_type": "bearer", "session_id": session_id, "user": safe_user(user, roles)}


@app.post("/api/v1/auth/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Depends(bearer), session: AsyncSession = Depends(db_session)) -> dict:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Bearer token required")
    try:
        claims = jwt.decode(credentials.credentials, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except jwt.InvalidTokenError as exc:
        raise HTTPException(status_code=401, detail="Invalid access token") from exc
    session_id = claims.get("sid")
    user_id = claims.get("sub")
    if not session_id or not user_id:
        raise HTTPException(status_code=401, detail="Invalid session claims")
    auth_session = await session.get(Session, session_id)
    user = await session.get(User, user_id)
    if auth_session is None or user is None or auth_session.revoked_at is not None:
        raise HTTPException(status_code=401, detail="Session unavailable")
    auth_session.revoked_at = utcnow()
    await write_audit(session, user.id, "auth.logout", "session", session_id)
    await session.commit()
    return {"ok": True, "session_id": session_id}


@app.get("/api/v1/me")
async def me(user: User = Depends(current_user), session: AsyncSession = Depends(db_session)) -> dict:
    return safe_user(user, await role_names(session, user.id))


@app.get("/api/v1/projects")
async def projects(user: User = Depends(current_user), session: AsyncSession = Depends(db_session)) -> dict:
    roles = await role_names(session, user.id)
    if "administrator" in roles:
        result = await session.execute(select(Project).order_by(Project.created_at.desc()))
    else:
        result = await session.execute(
            select(Project).outerjoin(ProjectMember, ProjectMember.project_id == Project.id).where(
                (Project.owner_user_id == user.id) | (ProjectMember.user_id == user.id)
            ).distinct().order_by(Project.created_at.desc())
        )
    items = [
        {"id": p.id, "name": p.name, "description": p.description or "", "owner_user_id": p.owner_user_id, "visibility": p.visibility, "created_at": p.created_at.isoformat() if p.created_at else None}
        for p in result.scalars().all()
    ]
    return {"items": items}


@app.post("/api/v1/projects")
async def create_project(project: ProjectCreate, user: User = Depends(current_user), session: AsyncSession = Depends(db_session)) -> dict:
    await require_role(user, session, "administrator", "researcher")
    if project.visibility not in {"private", "project", "server"}:
        raise HTTPException(status_code=422, detail="Invalid project visibility")
    record = Project(name=project.name, description=project.description, owner_user_id=user.id, visibility=project.visibility)
    session.add(record)
    await session.flush()
    session.add(ProjectMember(project_id=record.id, user_id=user.id, project_role="owner"))
    await write_audit(session, user.id, "project.create", "project", record.id)
    await session.commit()
    await session.refresh(record)
    return {"id": record.id, "name": record.name, "description": record.description or "", "owner_user_id": record.owner_user_id, "visibility": record.visibility}


@app.get("/api/v1/projects/{project_id}/experiments")
async def list_experiments(project_id: str, user: User = Depends(current_user), session: AsyncSession = Depends(db_session)) -> dict:
    await project_access(session, project_id, user)
    result = await session.execute(select(Experiment).where(Experiment.project_id == project_id).order_by(Experiment.created_at.desc()))
    return {"items": [{"id": e.id, "name": e.name, "status": e.status, "backend": e.backend, "configuration": e.configuration_json or {}} for e in result.scalars().all()]}


@app.post("/api/v1/projects/{project_id}/experiments")
async def create_experiment(project_id: str, request: ExperimentCreate, user: User = Depends(current_user), session: AsyncSession = Depends(db_session)) -> dict:
    project = await project_access(session, project_id, user)
    roles = await role_names(session, user.id)
    if project.owner_user_id != user.id and "administrator" not in roles:
        member = await session.scalar(select(ProjectMember).where(ProjectMember.project_id == project_id, ProjectMember.user_id == user.id))
        if member is None or member.project_role == "viewer":
            raise HTTPException(status_code=403, detail="Experiment write access denied")
    experiment = Experiment(project_id=project_id, name=request.name, backend=request.backend, configuration_json=request.configuration)
    session.add(experiment)
    await session.flush()
    await write_audit(session, user.id, "experiment.create", "experiment", experiment.id, {"project_id": project_id})
    await session.commit()
    await session.refresh(experiment)
    return {"id": experiment.id, "project_id": experiment.project_id, "name": experiment.name, "status": experiment.status, "backend": experiment.backend}


@app.post("/api/v1/experiments/{experiment_id}/jobs")
async def submit_job(experiment_id: str, request: JobCreate, user: User = Depends(current_user), session: AsyncSession = Depends(db_session)) -> dict:
    experiment = await session.get(Experiment, experiment_id)
    if experiment is None:
        raise HTTPException(status_code=404, detail="Experiment not found")
    await project_access(session, experiment.project_id, user)
    job = Job(experiment_id=experiment_id, operation=request.operation, payload_json=request.payload)
    session.add(job)
    await write_audit(session, user.id, "job.submit", "job", job.id, {"operation": request.operation})
    await session.commit()
    await session.refresh(job)
    return {"id": job.id, "experiment_id": job.experiment_id, "operation": job.operation, "status": job.status, "payload": job.payload_json or {}}


@app.get("/api/v1/jobs")
async def jobs(user: User = Depends(current_user), session: AsyncSession = Depends(db_session)) -> dict:
    roles = await role_names(session, user.id)
    if "administrator" in roles:
        result = await session.execute(select(Job).order_by(Job.created_at.desc()).limit(200))
    else:
        result = await session.execute(
            select(Job).join(Experiment, Job.experiment_id == Experiment.id).join(Project, Experiment.project_id == Project.id).outerjoin(ProjectMember, ProjectMember.project_id == Project.id).where(
                (Project.owner_user_id == user.id) | (ProjectMember.user_id == user.id)
            ).distinct().order_by(Job.created_at.desc()).limit(200)
        )
    return {"items": [{"id": j.id, "experiment_id": j.experiment_id, "operation": j.operation, "status": j.status, "payload": j.payload_json or {}, "result": j.result_json or {}} for j in result.scalars().all()]}


@app.post("/api/v1/experiments/{experiment_id}/telemetry")
async def add_telemetry(experiment_id: str, request: TelemetryCreate, user: User = Depends(current_user), session: AsyncSession = Depends(db_session)) -> dict:
    experiment = await session.get(Experiment, experiment_id)
    if experiment is None:
        raise HTTPException(status_code=404, detail="Experiment not found")
    await project_access(session, experiment.project_id, user)
    event = TelemetryEvent(experiment_id=experiment_id, metric=request.metric, value=request.value, metadata_json=request.metadata)
    session.add(event)
    await session.commit()
    await session.refresh(event)
    return {"id": event.id, "experiment_id": event.experiment_id, "metric": event.metric, "value": event.value, "timestamp": event.timestamp.isoformat() if event.timestamp else None}


@app.get("/api/v1/experiments/{experiment_id}/telemetry")
async def get_telemetry(experiment_id: str, limit: int = Query(default=500, ge=1, le=5000), user: User = Depends(current_user), session: AsyncSession = Depends(db_session)) -> dict:
    experiment = await session.get(Experiment, experiment_id)
    if experiment is None:
        raise HTTPException(status_code=404, detail="Experiment not found")
    await project_access(session, experiment.project_id, user)
    result = await session.execute(select(TelemetryEvent).where(TelemetryEvent.experiment_id == experiment_id).order_by(TelemetryEvent.timestamp.desc()).limit(limit))
    items = [{"id": e.id, "metric": e.metric, "value": e.value, "timestamp": e.timestamp.isoformat() if e.timestamp else None, "metadata": e.metadata_json or {}} for e in reversed(result.scalars().all())]
    return {"items": items}


@app.get("/api/v1/admin/servers")
async def admin_servers(user: User = Depends(current_user), session: AsyncSession = Depends(db_session)) -> dict:
    await require_role(user, session, "administrator")
    servers = (await session.execute(select(Server).order_by(Server.name))).scalars().all()
    return {"items": [{"id": s.id, "name": s.name, "host": s.host, "port": s.port, "status": s.status, "last_heartbeat": s.last_heartbeat.isoformat() if s.last_heartbeat else None} for s in servers]}


@app.get("/api/v1/admin/workers")
async def admin_workers(user: User = Depends(current_user), session: AsyncSession = Depends(db_session)) -> dict:
    await require_role(user, session, "administrator")
    workers = (await session.execute(select(Worker).order_by(Worker.created_at.desc()))).scalars().all()
    return {"items": [{"id": w.id, "server_id": w.server_id, "backend": w.backend, "status": w.status, "capabilities": w.capabilities_json or {}, "last_heartbeat": w.last_heartbeat.isoformat() if w.last_heartbeat else None} for w in workers]}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str | None = Query(default=None)) -> None:
    if not token:
        await websocket.close(code=1008)
        return
    try:
        claims = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        if not claims.get("sub") or not claims.get("sid"):
            raise ValueError("invalid claims")
    except (jwt.InvalidTokenError, ValueError):
        await websocket.close(code=1008)
        return

    await websocket.accept()
    session_id = claims["sid"]
    await websocket.send_json(envelope("server.connected", {"authenticated": True}, session_id=session_id))
    try:
        while True:
            message = await websocket.receive_json()
            message_type = message.get("message_type", "client.message")
            await websocket.send_json(envelope("server.ack", {"received": True, "message_type": message_type}, request_id=message.get("request_id"), session_id=session_id))
    except WebSocketDisconnect:
        return
