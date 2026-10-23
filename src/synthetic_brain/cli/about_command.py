"""Terminal About command backed by the canonical build metadata."""

from synthetic_brain.about import about_text


def run_about() -> int:
    print(about_text())
    return 0
