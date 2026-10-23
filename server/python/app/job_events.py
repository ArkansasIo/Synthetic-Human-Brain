from __future__ import annotations

from typing import Any

from .protocol import envelope
from .telemetry import telemetry_hub


async def publish_job_event(
    *,
    job_id: str,
    status: str,
    worker_id: str | None = None,
    result: dict[str, Any] | None = None,
) -> None:
    payload = {
        "job_id": job_id,
        "status": status,
        "worker_id": worker_id,
        "result": result or {},
    }
    await telemetry_hub.publish(envelope("job.status", payload))
