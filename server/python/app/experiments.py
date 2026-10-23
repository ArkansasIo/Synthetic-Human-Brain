from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4


class ExperimentService:
    """Application-level experiment contract.

    Persistence is deliberately separated from execution so the same contract can
    dispatch work to a Python or Rust worker.
    """

    def create(self, project_id: str, name: str, backend: str = "auto") -> dict:
        return {
            "id": str(uuid4()),
            "project_id": project_id,
            "name": name,
            "backend": backend,
            "status": "created",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

    def telemetry_event(self, experiment_id: str, metric: str, value: float, timestamp: str | None = None) -> dict:
        return {
            "experiment_id": experiment_id,
            "metric": metric,
            "value": value,
            "timestamp": timestamp or datetime.now(timezone.utc).isoformat(),
        }
