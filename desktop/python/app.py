from __future__ import annotations

import sys

import httpx
from PySide6.QtWidgets import QApplication, QLabel, QMainWindow, QTabWidget, QVBoxLayout, QWidget


class ResearcherClient(QMainWindow):
    def __init__(self, server_url: str = "http://127.0.0.1:8787") -> None:
        super().__init__()
        self.server_url = server_url.rstrip("/")
        self.setWindowTitle("Synthetic Human Brain Researcher")
        self.resize(1280, 800)

        tabs = QTabWidget()
        for title in ("Dashboard", "Projects", "Experiments", "Brain Regions", "Telemetry", "Jobs", "BrainScript", "Servers", "Admin"):
            panel = QWidget()
            layout = QVBoxLayout(panel)
            layout.addWidget(QLabel(f"{title} workspace"))
            tabs.addTab(panel, title)
        self.setCentralWidget(tabs)

        self.statusBar().showMessage(self._health_text())

    def _health_text(self) -> str:
        try:
            response = httpx.get(f"{self.server_url}/api/v1/health", timeout=3.0)
            response.raise_for_status()
            data = response.json()
            return f"Server: {data.get('status', 'unknown')} | {data.get('version', '')}"
        except Exception as exc:
            return f"Server unavailable: {exc}"


def main() -> int:
    app = QApplication(sys.argv)
    window = ResearcherClient()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
