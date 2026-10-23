from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


def envelope(message_type: str, payload: Any, request_id: str | None = None, session_id: str | None = None) -> dict:
    return {
        "protocol_version": "1.0",
        "request_id": request_id or str(uuid4()),
        "session_id": session_id,
        "message_type": message_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "payload": payload,
    }
