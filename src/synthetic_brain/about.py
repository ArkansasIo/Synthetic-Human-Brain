"""Build and product metadata for the Synthetic Human Brain platform."""

from __future__ import annotations

PROJECT_NAME = "Synthetic Human Brain"
BUILD_NAME = "Synthetic Human Brain Research Platform"
BUILD_VERSION = "0.7.0"
BUILD_ID = "SHB-20261023-UI01"
DEVELOPER_NAME = "ArkansasIo"
RELEASE_CHANNEL = "research"
PYTHON_MIN_VERSION = "3.11"


def about() -> dict[str, str]:
    """Return stable product metadata suitable for UIs, APIs, and CLI output."""
    return {
        "project_name": PROJECT_NAME,
        "build_name": BUILD_NAME,
        "build_version": BUILD_VERSION,
        "build_id": BUILD_ID,
        "developer_name": DEVELOPER_NAME,
        "release_channel": RELEASE_CHANNEL,
        "python_min_version": PYTHON_MIN_VERSION,
    }


def about_text() -> str:
    """Return a compact human-readable About panel."""
    return (
        f"{PROJECT_NAME}\n"
        f"Build: {BUILD_NAME}\n"
        f"Version: {BUILD_VERSION}\n"
        f"Build ID: {BUILD_ID}\n"
        f"Developer: {DEVELOPER_NAME}\n"
        f"Channel: {RELEASE_CHANNEL}\n"
        f"Python: >= {PYTHON_MIN_VERSION}"
    )
