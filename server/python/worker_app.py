from __future__ import annotations

from datetime import datetime, timezone

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import db_session
from app.models import Server, Worker
from app.worker_registry import heartbeat_worker, register_worker

app = FastAPI(title="Synthetic Human Brain Worker Registry", version="0.1.0-alpha")
bearer = HTTPBearer(auto_error=False)


class ServerRegistration(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    host: str = Field(min_length=1, max_length=255)
    port: int = Field(ge=1, le=65535)


class WorkerRegistration(BaseModel):
    server_id: str
    worker_id: str | None = None
    backend: str = Field(default="hybrid", max_length=32)
    capabilities: dict = Field(default_factory=dict)


class WorkerHeartbeat(BaseModel):
    status: str = "online"


async def require_registry_token(credentials: HTTPAuthorizationCredentials | None = Depends(bearer)) -> None:
    """Protect registry endpoints with a deployment-level environment token."""
    import os

    expected = os.getenv("SYNTHETIC_BRAIN_WORKER_REGISTRY_TOKEN")
    if not expected or credentials is None or credentials.credentials != expected:
        raise HTTPException(status_code=401, detail="Worker registry authentication required")


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "service": "worker-registry", "version": "0.1.0-alpha"}


@app.post("/api/v1/servers/register", dependencies=[Depends(require_registry_token)])
async def register_server(request: ServerRegistration, session: AsyncSession = Depends(db_session)) -> dict:
    server = await session.scalar(select(Server).where(Server.name == request.name))
    if server is None:
        server = Server(name=request.name, host=request.host, port=request.port, status="online")
        session.add(server)
    else:
        server.host = request.host
        server.port = request.port
        server.status = "online"
    server.last_heartbeat = datetime.now(timezone.utc).replace(tzinfo=None)
    await session.commit()
    await session.refresh(server)
    return {"server_id": server.id, "name": server.name, "status": server.status}


@app.post("/api/v1/workers/register", dependencies=[Depends(require_registry_token)])
async def register(request: WorkerRegistration, session: AsyncSession = Depends(db_session)) -> dict:
    try:
        worker = await register_worker(
            session,
            server_id=request.server_id,
            worker_id=request.worker_id,
            backend=request.backend,
            capabilities=request.capabilities,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    await session.commit()
    return {
        "worker_id": worker.id,
        "server_id": worker.server_id,
        "backend": worker.backend,
        "status": worker.status,
        "capabilities": worker.capabilities_json or {},
    }


@app.post("/api/v1/workers/{worker_id}/heartbeat", dependencies=[Depends(require_registry_token)])
async def heartbeat(worker_id: str, request: WorkerHeartbeat, session: AsyncSession = Depends(db_session)) -> dict:
    try:
        worker = await heartbeat_worker(session, worker_id, request.status)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    await session.commit()
    return {
        "worker_id": worker.id,
        "server_id": worker.server_id,
        "status": worker.status,
        "last_heartbeat": worker.last_heartbeat.isoformat() if worker.last_heartbeat else None,
    }


@app.get("/api/v1/workers", dependencies=[Depends(require_registry_token)])
async def workers(session: AsyncSession = Depends(db_session)) -> dict:
    result = await session.execute(select(Worker).order_by(Worker.created_at.desc()))
    return {
        "items": [
            {
                "worker_id": worker.id,
                "server_id": worker.server_id,
                "backend": worker.backend,
                "status": worker.status,
                "capabilities": worker.capabilities_json or {},
                "last_heartbeat": worker.last_heartbeat.isoformat() if worker.last_heartbeat else None,
            }
            for worker in result.scalars().all()
        ]
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("worker_app:app", host="0.0.0.0", port=8790, reload=False)
