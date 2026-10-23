from __future__ import annotations

import httpx
from .config import settings


async def dispatch_job(job_id: str, operation: str, payload: dict) -> dict:
    url = f"{settings.rust_backend_url.rstrip('/')}/api/v1/jobs"
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(url, json={"job_id": job_id, "operation": operation, "payload": payload})
        response.raise_for_status()
        return response.json()


async def rust_health() -> dict:
    url = f"{settings.rust_backend_url.rstrip('/')}/api/v1/health"
    async with httpx.AsyncClient(timeout=3.0) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()
