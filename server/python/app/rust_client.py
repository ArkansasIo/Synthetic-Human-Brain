from __future__ import annotations

import httpx
from .config import settings


def worker_base_url(endpoint_url: str | None) -> str:
    return (endpoint_url or settings.rust_backend_url).rstrip("/")


async def dispatch_job(job_id: str, operation: str, payload: dict, endpoint_url: str | None = None) -> dict:
    url = f"{worker_base_url(endpoint_url)}/api/v1/jobs"
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url, json={"job_id": job_id, "operation": operation, "payload": payload})
        response.raise_for_status()
        return response.json()


async def rust_health(endpoint_url: str | None = None) -> dict:
    url = f"{worker_base_url(endpoint_url)}/api/v1/health"
    async with httpx.AsyncClient(timeout=3.0) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()
