from __future__ import annotations

import asyncio
import time
from datetime import datetime, timedelta, timezone

import httpx
import jwt
from fastapi import Depends, FastAPI, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from . import models
from .auth import authenticate_user, issue_token, new_session_id, register_user
from .config import settings
from .db import db_session
from .hardware import HardwareError, hardware_registry
from .job_events import publish_job_event
from .job_router import select_worker
from .models import AuditLog, Experiment, Job, Project, ProjectMember, Role, Server, Session, TelemetryEvent, User, UserRole, Worker
from .protocol import envelope
from .rust_client import dispatch_job
from .telemetry import telemetry_hub

app = FastAPI(title=settings.app_name, version=settings.version)


@app.on_event("startup")
async def create_tables() -> None:
    from .db import engine

    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
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

class ServerCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    endpoint_url: str = Field(min_length=1, max_length=2048)
    platform: str = Field(default="linux", max_length=32)
    capabilities: dict = Field(default_factory=dict)

class WorkerCreate(BaseModel):
    server_id: str
    name: str = Field(min_length=1, max_length=255)
    backend: str = Field(default="rust", max_length=32)
    endpoint_url: str = Field(min_length=1, max_length=2048)
    capabilities: dict = Field(default_factory=dict)

class WorkerHeartbeat(BaseModel):
    status: str = Field(default="online", max_length=32)
    capabilities: dict | None = None


def utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)

def safe_user(user: User, roles: list[str]) -> dict:
    return {"id": user.id, "username": user.username, "display_name": user.display_name, "status": user.status, "roles": roles}

async def role_names(session: AsyncSession, user_id: str) -> list[str]:
    result = await session.execute(select(Role.name).join(UserRole, UserRole.role_id == Role.id).where(UserRole.user_id == user_id))
    return list(result.scalars().all())

async def current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer), session: AsyncSession = Depends(db_session)) -> User:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Bearer token required")
    try:
        claims = jwt.decode(credentials.credentials, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        user_id, session_id = claims.get("sub"), claims.get("sid")
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

async def write_audit(session: AsyncSession, user_id: str | None, action: str, resource_type: str | None = None, resource_id: str | None = None, details: dict | None = None) -> None:
    session.add(AuditLog(user_id=user_id, action=action, resource_type=resource_type, resource_id=resource_id, details_json=details or {}))

async def project_access(session: AsyncSession, project_id: str, user: User) -> Project:
    project = await session.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.owner_user_id == user.id:
        return project
    member = await session.scalar(select(ProjectMember).where(ProjectMember.project_id == project_id, ProjectMember.user_id == user.id))
    if member is None and "administrator" not in await role_names(session, user.id):
        raise HTTPException(status_code=403, detail="Project access denied")
    return project

@app.get("/api/v1/health")
async def health() -> dict:
    return {"status": "ok", "service": settings.app_name, "version": settings.version}

@app.get("/api/v1/about")
async def about() -> dict:
    return {"name": settings.app_name, "version": settings.version, "developer": settings.developer, "role": "Public research API and orchestration layer", "platforms": ["windows", "macos", "linux"], "clients": ["desktop", "browser"], "protocols": ["HTTPS", "WSS"], "workers": ["python", "rust"]}

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
    return {"access_token": issue_token(user.id, session_id), "token_type": "bearer", "session_id": session_id, "user": safe_user(user, await role_names(session, user.id))}

@app.post("/api/v1/auth/logout")
async def logout(credentials: HTTPAuthorizationCredentials | None = Depends(bearer), session: AsyncSession = Depends(db_session)) -> dict:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Bearer token required")
    try:
        claims = jwt.decode(credentials.credentials, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except jwt.InvalidTokenError as exc:
        raise HTTPException(status_code=401, detail="Invalid access token") from exc
    session_id, user_id = claims.get("sid"), claims.get("sub")
    auth_session = await session.get(Session, session_id) if session_id else None
    user = await session.get(User, user_id) if user_id else None
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
    query = select(Project).order_by(Project.created_at.desc()) if "administrator" in roles else select(Project).outerjoin(ProjectMember, ProjectMember.project_id == Project.id).where((Project.owner_user_id == user.id) | (ProjectMember.user_id == user.id)).distinct().order_by(Project.created_at.desc())
    result = await session.execute(query)
    return {"items": [{"id": p.id, "name": p.name, "description": p.description or "", "owner_user_id": p.owner_user_id, "visibility": p.visibility, "created_at": p.created_at.isoformat() if p.created_at else None} for p in result.scalars().all()]}

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
    job = Job(experiment_id=experiment_id, operation=request.operation, payload_json=request.payload, status="queued")
    session.add(job)
    await session.flush()
    selection = await select_worker(session, operation=request.operation, payload=request.payload, backend=experiment.backend)
    if selection is None:
        await session.rollback()
        raise HTTPException(status_code=503, detail="No healthy worker currently matches this job")
    await write_audit(session, user.id, "job.submit", "job", job.id, {"operation": request.operation, "worker_id": selection.worker_id})
    job.status = "running"
    job.started_at = utcnow()
    job.worker_id = selection.worker_id
    await session.commit()
    await publish_job_event(job_id=job.id, status="running", worker_id=selection.worker_id)
    try:
        result = await dispatch_job(job.id, job.operation, {**(job.payload_json or {}), "worker_id": selection.worker_id})
        job.result_json = result
        job.status = "completed" if result.get("status") == "completed" else "failed"
        job.completed_at = utcnow()
        await write_audit(session, user.id, "job.complete" if job.status == "completed" else "job.failed", "job", job.id, {"status": job.status, "worker_id": selection.worker_id})
        await session.commit()
        await publish_job_event(job_id=job.id, status=job.status, worker_id=selection.worker_id, result=result)
    except (httpx.HTTPError, ValueError) as exc:
        job.status = "failed"
        job.completed_at = utcnow()
        job.result_json = {"error": str(exc), "type": type(exc).__name__}
        await write_audit(session, user.id, "job.failed", "job", job.id, {"error": str(exc), "worker_id": selection.worker_id})
        await session.commit()
        await publish_job_event(job_id=job.id, status="failed", worker_id=selection.worker_id, result=job.result_json)
        raise HTTPException(status_code=502, detail="Selected worker unavailable or rejected the job") from exc
    return {"id": job.id, "experiment_id": job.experiment_id, "operation": job.operation, "status": job.status, "worker_id": selection.worker_id, "payload": job.payload_json or {}, "result": job.result_json or {}}

@app.get("/api/v1/jobs")
async def jobs(user: User = Depends(current_user), session: AsyncSession = Depends(db_session)) -> dict:
    roles = await role_names(session, user.id)
    if "administrator" in roles:
        result = await session.execute(select(Job).order_by(Job.created_at.desc()).limit(200))
    else:
        result = await session.execute(select(Job).join(Experiment, Job.experiment_id == Experiment.id).join(Project, Experiment.project_id == Project.id).outerjoin(ProjectMember, ProjectMember.project_id == Project.id).where((Project.owner_user_id == user.id) | (ProjectMember.user_id == user.id)).distinct().order_by(Job.created_at.desc()).limit(200))
    return {"items": [{"id": j.id, "experiment_id": j.experiment_id, "operation": j.operation, "status": j.status, "worker_id": getattr(j, "worker_id", None), "payload": j.payload_json or {}, "result": j.result_json or {}} for j in result.scalars().all()]}

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
    payload = {"id": event.id, "experiment_id": event.experiment_id, "metric": event.metric, "value": event.value, "timestamp": event.timestamp.isoformat() if event.timestamp else None, "metadata": event.metadata_json or {}}
    await telemetry_hub.publish(envelope("experiment.telemetry", payload))
    return payload

@app.get("/api/v1/experiments/{experiment_id}/telemetry")
async def get_telemetry(experiment_id: str, limit: int = Query(default=500, ge=1, le=5000), user: User = Depends(current_user), session: AsyncSession = Depends(db_session)) -> dict:
    experiment = await session.get(Experiment, experiment_id)
    if experiment is None:
        raise HTTPException(status_code=404, detail="Experiment not found")
    await project_access(session, experiment.project_id, user)
    result = await session.execute(select(TelemetryEvent).where(TelemetryEvent.experiment_id == experiment_id).order_by(TelemetryEvent.timestamp.desc()).limit(limit))
    return {"items": [{"id": e.id, "experiment_id": e.experiment_id, "metric": e.metric, "value": e.value, "timestamp": e.timestamp.isoformat() if e.timestamp else None, "metadata": e.metadata_json or {}} for e in result.scalars().all()]}

class NetworkSpec(BaseModel):
    """Weighted directed graph for the network-driven simulator."""

    neuron_count: int = Field(ge=1, le=4096)
    edges: list[tuple[int, int, float]] = Field(default_factory=list)
    steps: int = Field(default=10, ge=1, le=10_000)
    external_input: float = 0.0
    seed: int = 42


class NeuronModelSpec(BaseModel):
    """Configuration for the leaky-rate neuron model."""

    decay: float = Field(default=0.9, ge=0.0, le=1.0)
    minimum: float = 0.0
    maximum: float = 1.0


class SynapseModelSpec(BaseModel):
    """Configuration for the linear synapse model."""

    scale: float = 1.0


@app.get("/api/v1/network/models")
async def network_models(user: User = Depends(current_user)) -> dict:
    """Model contracts exposed by the network-driven simulator."""
    return {
        "neuron_model": {
            "protocol": "NeuronModel.update(activity, input_signal, time_step) -> float",
            "default": "LeakyRateNeuron",
            "parameters": {"decay": [0.0, 1.0], "minimum": "< maximum", "maximum": "> minimum"},
            "range": "clamped to [minimum, maximum]",
        },
        "synapse_model": {
            "protocol": "SynapseModel.transmit(signal, weight) -> float",
            "default": "LinearSynapse",
            "parameters": {"scale": "any finite float"},
        },
        "constraints": [
            "outputs must be finite numeric values",
            "network size must match SimulationConfig.neuron_count",
            "initial state drawn from a seeded local random generator",
            "synchronous update: all signals computed from the prior snapshot",
        ],
    }


@app.post("/api/v1/network/simulate")
async def network_simulate(spec: NetworkSpec, user: User = Depends(current_user)) -> dict:
    """Run the graph-driven simulator server-side and return the trajectory."""
    try:
        from synthetic_brain import NeuralNetwork, NetworkSimulation, SimulationConfig
    except ImportError as exc:  # pragma: no cover - depends on deployment
        raise HTTPException(status_code=503, detail=f"simulation engine unavailable: {exc}")
    network = NeuralNetwork(neuron_count=spec.neuron_count)
    try:
        for source, target, weight in spec.edges:
            network.connect(source, target, weight=weight)
        simulation = NetworkSimulation(network, SimulationConfig(neuron_count=spec.neuron_count, seed=spec.seed))
    except (ValueError, TypeError) as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    trajectory = [simulation.snapshot().activity]
    for _ in range(spec.steps):
        trajectory.append(simulation.step(external_input=spec.external_input).activity)
    return {
        "steps": spec.steps,
        "neuron_count": spec.neuron_count,
        "seed": spec.seed,
        "trajectory": [list(activity) for activity in trajectory],
    }


@app.post("/api/v1/network/models/neuron")
async def validate_neuron_model(spec: NeuronModelSpec, user: User = Depends(current_user)) -> dict:
    try:
        from synthetic_brain.neuron import LeakyRateNeuron

        model = LeakyRateNeuron(decay=spec.decay, minimum=spec.minimum, maximum=spec.maximum)
        value = model.update(0.5, 1.0, 0.1)
    except (ImportError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    return {"valid": True, "sample_update": value}


@app.post("/api/v1/network/models/synapse")
async def validate_synapse_model(spec: SynapseModelSpec, user: User = Depends(current_user)) -> dict:
    try:
        from synthetic_brain.synapse import LinearSynapse

        model = LinearSynapse(scale=spec.scale)
        value = model.transmit(0.5, 2.0)
    except (ImportError, ValueError, TypeError) as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    return {"valid": True, "sample_transmit": value}


@app.get("/api/v1/hardware")
async def list_hardware(user: User = Depends(current_user)) -> dict:
    """List every registered hardware device and its connection state."""
    return {"items": [info.__dict__ for info in hardware_registry.list()]}


@app.post("/api/v1/hardware/{device_id}/connect")
async def connect_hardware(device_id: str, user: User = Depends(current_user)) -> dict:
    try:
        hardware_registry.connect(device_id)
    except HardwareError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    return {"id": device_id, "connected": True}


@app.post("/api/v1/hardware/{device_id}/disconnect")
async def disconnect_hardware(device_id: str, user: User = Depends(current_user)) -> dict:
    hardware_registry.disconnect(device_id)
    return {"id": device_id, "connected": False}


@app.get("/api/v1/hardware/{device_id}/read")
async def read_hardware(device_id: str, user: User = Depends(current_user)) -> dict:
    try:
        frames = hardware_registry.get(device_id).read()
    except HardwareError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    return {"id": device_id, "frames": frames}


class HardwareStimRequest(BaseModel):
    channels: list[int] = Field(min_length=1)


@app.post("/api/v1/hardware/{device_id}/stim")
async def stim_hardware(device_id: str, request: HardwareStimRequest, user: User = Depends(current_user)) -> dict:
    try:
        hardware_registry.stim(device_id, request.channels)
    except HardwareError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"id": device_id, "stimulated": request.channels}


@app.get("/api/v1/servers")
async def list_servers(user: User = Depends(current_user), session: AsyncSession = Depends(db_session)) -> dict:
    await require_role(user, session, "administrator")
    result = await session.execute(select(Server).order_by(Server.created_at.desc()))
    return {"items": [{"id": s.id, "name": s.name, "endpoint_url": s.endpoint_url, "platform": s.platform, "status": s.status, "capabilities": s.capabilities_json or {}, "last_heartbeat": s.last_heartbeat.isoformat() if s.last_heartbeat else None} for s in result.scalars().all()]}

@app.post("/api/v1/servers")
async def register_server(request: ServerCreate, user: User = Depends(current_user), session: AsyncSession = Depends(db_session)) -> dict:
    await require_role(user, session, "administrator")
    server = Server(name=request.name, endpoint_url=request.endpoint_url, platform=request.platform, capabilities_json=request.capabilities, status="online", last_heartbeat=utcnow())
    session.add(server)
    await session.flush()
    await write_audit(session, user.id, "server.register", "server", server.id, {"platform": request.platform})
    await session.commit()
    return {"id": server.id, "name": server.name, "status": server.status}

@app.get("/api/v1/workers")
async def list_workers(user: User = Depends(current_user), session: AsyncSession = Depends(db_session)) -> dict:
    await require_role(user, session, "administrator", "researcher")
    result = await session.execute(select(Worker).order_by(Worker.created_at.desc()))
    return {"items": [{"id": w.id, "server_id": w.server_id, "name": w.name, "backend": w.backend, "endpoint_url": getattr(w, "endpoint_url", None), "status": w.status, "capabilities": w.capabilities_json or {}, "last_heartbeat": w.last_heartbeat.isoformat() if w.last_heartbeat else None} for w in result.scalars().all()]}

@app.post("/api/v1/workers")
async def register_worker(request: WorkerCreate, user: User = Depends(current_user), session: AsyncSession = Depends(db_session)) -> dict:
    await require_role(user, session, "administrator")
    server = await session.get(Server, request.server_id)
    if server is None:
        raise HTTPException(status_code=404, detail="Server not found")
    worker = Worker(server_id=request.server_id, name=request.name, backend=request.backend, endpoint_url=request.endpoint_url, capabilities_json=request.capabilities, status="online", last_heartbeat=utcnow())
    session.add(worker)
    await session.flush()
    await write_audit(session, user.id, "worker.register", "worker", worker.id, {"server_id": request.server_id, "backend": request.backend})
    await session.commit()
    return {"id": worker.id, "server_id": worker.server_id, "name": worker.name, "status": worker.status}

@app.post("/api/v1/workers/{worker_id}/heartbeat")
async def worker_heartbeat(worker_id: str, request: WorkerHeartbeat, user: User = Depends(current_user), session: AsyncSession = Depends(db_session)) -> dict:
    await require_role(user, session, "administrator", "researcher")
    worker = await session.get(Worker, worker_id)
    if worker is None:
        raise HTTPException(status_code=404, detail="Worker not found")
    worker.status = request.status
    worker.last_heartbeat = utcnow()
    if request.capabilities is not None:
        worker.capabilities_json = request.capabilities
    await session.commit()
    return {"id": worker.id, "status": worker.status, "last_heartbeat": worker.last_heartbeat.isoformat()}

async def _reject_websocket(websocket: WebSocket, reason: str) -> None:
    """Accept then reject with a readable reason instead of a bare 1008 close.

    Closing before ``accept()`` surfaces to clients as an opaque code-1008
    policy violation. Accepting and sending an explicit error frame lets the
    desktop/web clients show the real cause (bad token, unknown device…).
    """
    await websocket.accept()
    await websocket.send_json({"type": "error", "code": 4401, "detail": reason})
    await websocket.close(code=1008, reason=reason)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str | None = Query(default=None)) -> None:
    if not token:
        await _reject_websocket(websocket, "missing token — connect with ?token=<JWT> from /api/v1/auth/login")
        return
    try:
        claims = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        user_id, session_id = claims.get("sub"), claims.get("sid")
        if not user_id or not session_id:
            raise ValueError("missing token claims")
    except jwt.ExpiredSignatureError:
        await _reject_websocket(websocket, "token expired — sign in again")
        return
    except (jwt.InvalidTokenError, ValueError) as exc:
        await _reject_websocket(websocket, f"invalid token: {exc}")
        return
    await websocket.accept()
    queue = telemetry_hub.subscribe()
    await websocket.send_json(envelope("server.connected", {"user_id": user_id}, session_id=session_id))
    try:
        while True:
            try:
                message = await asyncio.wait_for(websocket.receive_json(), timeout=0.25)
                if message.get("type") == "ping":
                    await websocket.send_json(envelope("server.pong", {}, session_id=session_id))
            except asyncio.TimeoutError:
                pass
            while not queue.empty():
                await websocket.send_json(queue.get_nowait())
    except WebSocketDisconnect:
        pass
    finally:
        telemetry_hub.unsubscribe(queue)


@app.websocket("/ws/hardware/{device_id}")
async def hardware_stream_endpoint(
    websocket: WebSocket,
    device_id: str,
    token: str | None = Query(default=None),
    rate_hz: float = Query(default=25.0, gt=0.0, le=100.0),
) -> None:
    """Live hardware frame stream: polls the device and broadcasts frames."""
    if not token:
        await _reject_websocket(websocket, "missing token — connect with ?token=<JWT>")
        return
    try:
        jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except jwt.ExpiredSignatureError:
        await _reject_websocket(websocket, "token expired — sign in again")
        return
    except jwt.InvalidTokenError as exc:
        await _reject_websocket(websocket, f"invalid token: {exc}")
        return
    try:
        plugin = hardware_registry.get(device_id)
    except HardwareError:
        await _reject_websocket(websocket, f"unknown device '{device_id}' — see GET /api/v1/hardware")
        return
    await websocket.accept()
    interval = 1.0 / rate_hz
    try:
        while True:
            start = time.perf_counter()
            try:
                frames = plugin.read()
            except HardwareError as exc:
                await websocket.send_json({"type": "hardware.error", "detail": str(exc)})
                frames = []
            active = [f for f in frames if f.get("has_spike") or f.get("has_stim") or "label" in f]
            await websocket.send_json(
                {
                    "type": "hardware.frames",
                    "device": device_id,
                    "timestamp": int(time.time() * 1000),
                    "frame_count": len(frames),
                    "active": active[:16],
                }
            )
            elapsed = time.perf_counter() - start
            await asyncio.sleep(max(0.0, interval - elapsed))
    except WebSocketDisconnect:
        pass
