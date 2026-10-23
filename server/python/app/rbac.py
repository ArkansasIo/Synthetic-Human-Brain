from __future__ import annotations

from collections.abc import Iterable

ROLE_PERMISSIONS: dict[str, set[str]] = {
    "administrator": {"*"},
    "researcher": {"project:read", "project:write", "experiment:read", "experiment:write", "job:submit", "telemetry:read"},
    "viewer": {"project:read", "experiment:read", "telemetry:read"},
}


def has_permission(roles: Iterable[str], permission: str) -> bool:
    return any("*" in ROLE_PERMISSIONS.get(role, set()) or permission in ROLE_PERMISSIONS.get(role, set()) for role in roles)
