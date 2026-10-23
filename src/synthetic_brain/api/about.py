"""Framework-neutral About API payload."""

from synthetic_brain.about import about


def get_about() -> dict[str, object]:
    """Return build metadata for HTTP/API adapters."""
    return {"status": "ok", "about": about()}
