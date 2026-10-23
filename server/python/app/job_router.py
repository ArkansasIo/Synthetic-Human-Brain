from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from .models import Worker
from .worker_registry import list_available_workers, worker_is_stale


@dataclass(frozen=True)
class WorkerSelection:
    worker_id: str
    backend: str
    score: int
    reason: str


def _capability_score(worker: Worker, operation: str, payload: dict[str, Any]) -> int:
    capabilities = worker.capabilities_json or {}
    score = 0
    operations = capabilities.get("operations", [])
    if operation in operations or "*" in operations:
        score += 100
    if payload.get("requires_gpu") and capabilities.get("gpu"):
        score += 50
    if payload.get("requires_neural_device") and capabilities.get("neural_device"):
        score += 50
    if worker.backend == "rust":
        score += 20
    elif worker.backend == "hybrid":
        score += 10
    if worker.status == "online":
        score += 5
    return score


async def select_worker(
    session: AsyncSession,
    *,
    operation: str,
    payload: dict[str, Any],
    backend: str = "auto",
) -> WorkerSelection | None:
    candidates = await list_available_workers(session, backend)
    candidates = [worker for worker in candidates if not worker_is_stale(worker)]
    if not candidates:
        return None

    ranked = sorted(candidates, key=lambda worker: _capability_score(worker, operation, payload), reverse=True)
    selected = ranked[0]
    score = _capability_score(selected, operation, payload)
    return WorkerSelection(
        worker_id=selected.id,
        backend=selected.backend,
        score=score,
        reason="capability-and-health ranking",
    )
