from __future__ import annotations

from datetime import datetime, timezone

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from .db import SessionFactory
from .job_events import publish_job_event
from .models import AuditLog, Job
from .rust_client import dispatch_job


def utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


async def execute_job(job_id: str, *, worker_id: str, endpoint_url: str | None, user_id: str | None) -> None:
    async with SessionFactory() as session:  # type: AsyncSession
        job = await session.get(Job, job_id)
        if job is None:
            return
        job.worker_id = worker_id
        job.status = "running"
        job.started_at = job.started_at or utcnow()
        await session.commit()
        await publish_job_event(job_id=job.id, status="running", worker_id=worker_id)
        try:
            result = await dispatch_job(job.id, job.operation, {**(job.payload_json or {}), "worker_id": worker_id}, endpoint_url)
            job.result_json = result
            job.status = "completed" if result.get("status") == "completed" else "failed"
            job.completed_at = utcnow()
            session.add(AuditLog(user_id=user_id, action="job.complete" if job.status == "completed" else "job.failed", resource_type="job", resource_id=job.id, details_json={"worker_id": worker_id, "status": job.status}))
            await session.commit()
            await publish_job_event(job_id=job.id, status=job.status, worker_id=worker_id, result=result)
        except (httpx.HTTPError, ValueError) as exc:
            job.status = "failed"
            job.completed_at = utcnow()
            job.result_json = {"error": str(exc), "type": type(exc).__name__}
            session.add(AuditLog(user_id=user_id, action="job.failed", resource_type="job", resource_id=job.id, details_json=job.result_json))
            await session.commit()
            await publish_job_event(job_id=job.id, status="failed", worker_id=worker_id, result=job.result_json)
