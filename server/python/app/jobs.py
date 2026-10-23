from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4


@dataclass(slots=True)
class ResearchJob:
    operation: str
    payload: dict
    id: str = field(default_factory=lambda: str(uuid4()))
    status: str = "queued"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class JobQueue:
    def __init__(self) -> None:
        self._queue: asyncio.Queue[ResearchJob] = asyncio.Queue()
        self._jobs: dict[str, ResearchJob] = {}

    async def submit(self, operation: str, payload: dict) -> ResearchJob:
        job = ResearchJob(operation=operation, payload=payload)
        self._jobs[job.id] = job
        await self._queue.put(job)
        return job

    async def next(self) -> ResearchJob:
        job = await self._queue.get()
        job.status = "running"
        return job

    def complete(self, job: ResearchJob) -> None:
        job.status = "completed"

    def get(self, job_id: str) -> ResearchJob | None:
        return self._jobs.get(job_id)


job_queue = JobQueue()
