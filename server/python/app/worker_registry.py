from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Server, Worker


STALE_AFTER_SECONDS = 30


def utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


async def register_worker(
    session: AsyncSession,
    *,
    server_id: str,
    worker_id: str | None,
    backend: str,
    capabilities: dict[str, Any],
) -> Worker:
    server = await session.get(Server, server_id)
    if server is None:
        raise ValueError("server not found")

    worker: Worker | None = None
    if worker_id:
        worker = await session.get(Worker, worker_id)
        if worker is not None and worker.server_id != server_id:
            raise ValueError("worker belongs to another server")

    if worker is None:
        worker = Worker(server_id=server_id, backend=backend, status="online", capabilities_json=capabilities)
        session.add(worker)
    else:
        worker.backend = backend
        worker.status = "online"
        worker.capabilities_json = capabilities

    server.status = "online"
    server.last_heartbeat = utcnow()
    await session.flush()
    return worker


async def heartbeat_worker(session: AsyncSession, worker_id: str, status: str = "online") -> Worker:
    worker = await session.get(Worker, worker_id)
    if worker is None:
        raise ValueError("worker not found")
    if status not in {"online", "busy", "draining", "offline"}:
        raise ValueError("invalid worker status")
    worker.status = status
    worker.last_heartbeat = utcnow()
    server = await session.get(Server, worker.server_id)
    if server is not None:
        server.last_heartbeat = worker.last_heartbeat
        server.status = "offline" if status == "offline" else "online"
    await session.flush()
    return worker


async def list_available_workers(session: AsyncSession, backend: str = "auto") -> list[Worker]:
    query = select(Worker).where(Worker.status.in_(["online", "busy"]))
    if backend != "auto":
        query = query.where(Worker.backend.in_([backend, "hybrid"]))
    result = await session.execute(query.order_by(Worker.last_heartbeat.desc()))
    return list(result.scalars().all())


def worker_is_stale(worker: Worker, now: datetime | None = None) -> bool:
    if worker.last_heartbeat is None:
        return True
    current = now or utcnow()
    return (current - worker.last_heartbeat).total_seconds() > STALE_AFTER_SECONDS
