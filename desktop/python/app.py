from __future__ import annotations

import sys

import httpx
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)


class LoginDialog(QDialog):
    def __init__(self, server_url: str) -> None:
        super().__init__()
        self.server_url = server_url.rstrip("/")
        self.token: str | None = None
        self.user: dict = {}
        self.setWindowTitle("Synthetic Human Brain — Researcher Login")
        self.resize(420, 220)

        layout = QFormLayout(self)
        self.username = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.client_id = QLineEdit("desktop-researcher")
        login = QPushButton("Sign in")
        login.clicked.connect(self._login)
        layout.addRow("Username", self.username)
        layout.addRow("Password", self.password)
        layout.addRow("Client ID", self.client_id)
        layout.addRow(login)

    def _login(self) -> None:
        try:
            response = httpx.post(
                f"{self.server_url}/api/v1/auth/login",
                json={
                    "username": self.username.text(),
                    "password": self.password.text(),
                    "client_id": self.client_id.text() or "desktop-researcher",
                    "platform": "windows" if sys.platform.startswith("win") else "macos" if sys.platform == "darwin" else "linux",
                },
                timeout=8.0,
            )
            response.raise_for_status()
            data = response.json()
            self.token = data["access_token"]
            self.user = data["user"]
            self.accept()
        except Exception as exc:
            QMessageBox.critical(self, "Login failed", str(exc))


class ResearcherClient(QMainWindow):
    def __init__(self, server_url: str = "http://127.0.0.1:8787") -> None:
        super().__init__()
        self.server_url = server_url.rstrip("/")
        self.token: str | None = None
        self.user: dict = {}
        self.setWindowTitle("Synthetic Human Brain Researcher")
        self.resize(1280, 800)

        tabs = QTabWidget()
        self.output = QLabel("Authenticate to load server-backed research data.")
        self.output.setWordWrap(True)
        for title in ("Dashboard", "Projects", "Experiments", "Brain Regions", "Telemetry", "Jobs", "BrainScript", "Servers", "Admin"):
            panel = QWidget()
            layout = QVBoxLayout(panel)
            label = QLabel(f"{title} workspace")
            layout.addWidget(label)
            if title == "Dashboard":
                layout.addWidget(self.output)
                refresh = QPushButton("Refresh Server")
                refresh.clicked.connect(self.refresh_dashboard)
                layout.addWidget(refresh)
            if title == "Projects":
                load = QPushButton("Load Projects")
                load.clicked.connect(self.load_projects)
                layout.addWidget(load)
                layout.addWidget(self.output)
            tabs.addTab(panel, title)
        self.setCentralWidget(tabs)
        self.statusBar().showMessage("Not authenticated")

    def auth_headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.token}"} if self.token else {}

    def refresh_dashboard(self) -> None:
        try:
            response = httpx.get(f"{self.server_url}/api/v1/about", headers=self.auth_headers(), timeout=5.0)
            response.raise_for_status()
            self.output.setText(str(response.json()))
            self.statusBar().showMessage("Server connected")
        except Exception as exc:
            self.output.setText(f"Server unavailable: {exc}")

    def load_projects(self) -> None:
        try:
            response = httpx.get(f"{self.server_url}/api/v1/projects", headers=self.auth_headers(), timeout=5.0)
            response.raise_for_status()
            self.output.setText(str(response.json()))
        except Exception as exc:
            self.output.setText(f"Project request failed: {exc}")


def main() -> int:
    app = QApplication(sys.argv)
    server_url = "http://127.0.0.1:8787"
    window = ResearcherClient(server_url)
    login = LoginDialog(server_url)
    if login.exec() != QDialog.DialogCode.Accepted:
        return 0
    window.token = login.token
    window.user = login.user
    window.statusBar().showMessage(f"Signed in as {login.user.get('display_name', login.user.get('username', 'researcher'))}")
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
