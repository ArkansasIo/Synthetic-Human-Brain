from __future__ import annotations

import sys
from typing import Any

import httpx
from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QAction, QColor, QKeySequence, QPainter, QPen
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QDoubleSpinBox,
    QFormLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSpinBox,
    QStatusBar,
    QTabWidget,
    QTextEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtWidgets import QComboBox, QGridLayout, QHBoxLayout, QScrollArea, QSplitter

SAMPLE_RATE_HZ = 25_000


# ---------------------------------------------------------------------------
# Graphics / data-chart canvases (painted with QPainter, no external deps)
# ---------------------------------------------------------------------------

class NetworkGraphCanvas(QWidget):
    """Directed-graph canvas of network connectivity with signed weights."""

    def __init__(self) -> None:
        super().__init__()
        self.setMinimumHeight(260)
        self.edges: list[tuple[int, int, float]] | None = None

    def render(self, edges: list[tuple[int, int, float]] | None) -> None:
        self.edges = edges
        self.update()

    def paintEvent(self, event: Any) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(18, 18, 24))
        if not self.edges:
            painter.setPen(QColor(160, 160, 160))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "No network — run the example first.")
            painter.end()
            return
        nodes = sorted({n for edge in self.edges for n in edge[:2]})
        count = len(nodes)
        w, h = self.width(), self.height()
        radius = min(w, h) / 3
        center_x, center_y = w / 2, h / 2
        import math

        positions = {
            node: (
                center_x + radius * math.cos(2 * math.pi * index / count - math.pi / 2),
                center_y + radius * math.sin(2 * math.pi * index / count - math.pi / 2),
            )
            for index, node in enumerate(nodes)
        }
        for source, target, weight in self.edges:
            x0, y0 = positions[source]
            x1, y1 = positions[target]
            color = QColor(80, 220, 120) if weight >= 0 else QColor(230, 90, 90)
            pen = QPen(color, max(1, abs(weight) * 4))
            painter.setPen(pen)
            painter.drawLine(QPointF(x0, y0), QPointF(x1, y1))
            painter.drawText(QPointF((x0 + x1) / 2, (y0 + y1) / 2 - 4), f"{weight:+.1f}")
        painter.setPen(QPen(QColor(240, 240, 240), 1))
        painter.setBrush(QColor(70, 70, 110))
        for node, (x, y) in positions.items():
            painter.drawEllipse(QPointF(x, y), 14, 14)
            painter.drawText(QPointF(x - 4, y + 4), str(node))
        painter.end()


class SpikeRasterCanvas(QWidget):
    """Spike raster: one row per channel, dots at spike timestamps."""

    def __init__(self) -> None:
        super().__init__()
        self.setMinimumHeight(220)
        self.spikes: list[Any] = []
        self.channel_count = 1

    def render(self, recording: Any) -> None:
        if recording is None:
            self.spikes = []
            self.channel_count = 1
        else:
            self.spikes = list(recording.spikes)
            self.channel_count = max([s.channel for s in self.spikes], default=0) + 1
        self.update()

    def paintEvent(self, event: Any) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(18, 18, 24))
        if not self.spikes:
            painter.setPen(QColor(160, 160, 160))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "No recording — start a recording, run a loop, then render.")
            painter.end()
            return
        t0 = min(s.timestamp for s in self.spikes)
        t1 = max(s.timestamp for s in self.spikes) or t0 + 1
        w, h = self.width(), self.height()
        margin = 24
        rows = max(1, self.channel_count)
        row_h = (h - 2 * margin) / rows
        painter.setPen(QPen(QColor(60, 220, 160), 3))
        for spike in self.spikes:
            x = margin + (spike.timestamp - t0) / max(1, t1 - t0) * (w - 2 * margin)
            y = margin + spike.channel * row_h + row_h / 2
            painter.drawPoint(int(x), int(y))
        painter.setPen(QColor(120, 120, 120))
        painter.drawText(QRectF(4, 2, w - 8, 16), Qt.AlignmentFlag.AlignLeft, f"{len(self.spikes)} spikes | channels 0..{rows - 1} | t {t0}..{t1}")
        painter.end()


class ChannelHistogramCanvas(QWidget):
    """Bar chart of spike counts per channel."""

    def __init__(self) -> None:
        super().__init__()
        self.setMinimumHeight(220)
        self.counts: dict[int, int] = {}

    def render(self, recording: Any) -> None:
        self.counts = {}
        if recording is not None:
            for spike in recording.spikes:
                self.counts[spike.channel] = self.counts.get(spike.channel, 0) + 1
        self.update()

    def paintEvent(self, event: Any) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(18, 18, 24))
        if not self.counts:
            painter.setPen(QColor(160, 160, 160))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "No data — record spikes first.")
            painter.end()
            return
        channels = sorted(self.counts)
        peak = max(self.counts.values()) or 1
        w, h = self.width(), self.height()
        margin = 30
        bar_w = max(3, (w - 2 * margin) / max(1, len(channels)) - 2)
        painter.setPen(QPen(QColor(80, 140, 255), 1))
        for index, channel in enumerate(channels):
            bar_h = self.counts[channel] / peak * (h - 2 * margin)
            x = margin + index * (bar_w + 2)
            painter.fillRect(QRectF(x, h - margin - bar_h, bar_w, bar_h), QColor(80, 140, 255))
        painter.setPen(QColor(120, 120, 120))
        painter.drawText(QRectF(4, 2, w - 8, 16), Qt.AlignmentFlag.AlignLeft, f"spikes/channel | peak {peak} | {len(channels)} active channels")
        painter.end()


class ActivityLineCanvas(QWidget):
    """Line chart of spikes-per-tick population activity."""

    def __init__(self) -> None:
        super().__init__()
        self.setMinimumHeight(220)
        self.series: list[int] = []

    def render(self, series: list[int]) -> None:
        self.series = list(series)
        self.update()

    def paintEvent(self, event: Any) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(18, 18, 24))
        if not self.series:
            painter.setPen(QColor(160, 160, 160))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "No loop data — run a loop first.")
            painter.end()
            return
        peak = max(self.series) or 1
        w, h = self.width(), self.height()
        margin = 26
        step_x = (w - 2 * margin) / max(1, len(self.series) - 1)
        painter.setPen(QPen(QColor(255, 170, 60), 2))
        previous: QPointF | None = None
        for index, value in enumerate(self.series):
            point = QPointF(margin + index * step_x, h - margin - value / peak * (h - 2 * margin))
            if previous is not None:
                painter.drawLine(previous, point)
            previous = point
        painter.setPen(QColor(120, 120, 120))
        painter.drawText(QRectF(4, 2, w - 8, 16), Qt.AlignmentFlag.AlignLeft, f"spikes per tick | peak {peak} | {len(self.series)} ticks")
        painter.end()


# ---------------------------------------------------------------------------
# CL1 clone integration (mirrors synthetic_brain.cl1_clone API)
# ---------------------------------------------------------------------------

def cl1_open(channel_count: int = 64, seed: int = 0) -> Any:
    """Import the local CL1 clone simulator lazily."""
    from synthetic_brain.cl1_clone import open as cl1_open_

    return cl1_open_(channel_count=channel_count, seed=seed)


# ---------------------------------------------------------------------------
# Login dialog
# ---------------------------------------------------------------------------

class LoginDialog(QDialog):
    def __init__(self, server_url: str) -> None:
        super().__init__()
        self.server_url = server_url.rstrip("/")
        self.token: str | None = None
        self.user: dict = {}
        self.setWindowTitle("Synthetic Human Brain — Researcher Login")
        self.resize(420, 220)

        layout = QFormLayout(self)
        self.server = QLineEdit(self.server_url)
        self.username = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.client_id = QLineEdit("desktop-researcher")
        login = QPushButton("Sign in")
        register = QPushButton("Register new researcher")
        login.clicked.connect(self._login)
        register.clicked.connect(self._register)
        layout.addRow("Server", self.server)
        layout.addRow("Username", self.username)
        layout.addRow("Password", self.password)
        layout.addRow("Client ID", self.client_id)
        layout.addRow(login, register)

    def _payload(self) -> dict:
        return {
            "username": self.username.text(),
            "password": self.password.text(),
            "client_id": self.client_id.text() or "desktop-researcher",
            "platform": "windows" if sys.platform.startswith("win") else "macos" if sys.platform == "darwin" else "linux",
        }

    def _login(self) -> None:
        try:
            response = httpx.post(f"{self.server_url}/api/v1/auth/login", json=self._payload(), timeout=8.0)
            response.raise_for_status()
            data = response.json()
            self.token = data["access_token"]
            self.user = data["user"]
            self.accept()
        except Exception as exc:
            QMessageBox.critical(self, "Login failed", str(exc))

    def _register(self) -> None:
        try:
            response = httpx.post(f"{self.server_url}/api/v1/auth/register", json=self._payload(), timeout=8.0)
            response.raise_for_status()
            data = response.json()
            self.token = data["access_token"]
            self.user = data["user"]
            self.accept()
        except Exception as exc:
            QMessageBox.critical(self, "Registration failed", str(exc))


# ---------------------------------------------------------------------------
# Main window with menus and submenus
# ---------------------------------------------------------------------------

class ResearcherClient(QMainWindow):
    def __init__(self, server_url: str = "http://127.0.0.1:8787") -> None:
        super().__init__()
        self.server_url = server_url.rstrip("/")
        self.token: str | None = None
        self.user: dict = {}
        self.setWindowTitle("Synthetic Human Brain Researcher")
        self.resize(1280, 800)

        self.neurons: Any = None
        self.recording: Any = None
        self.loop_ticks = 0

        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)
        self.output.setPlaceholderText("Output from server requests and CL1 clone operations appears here.")

        self.brainscript = QTextEdit()
        self.brainscript.setPlainText(
            "brain Cortex {\n"
            "    population Excitatory size 100\n"
            "    population Inhibitory size 25\n"
            "    connect Excitatory -> Inhibitory weight 0.2 delay 1.5\n"
            "}"
        )

        self.tabs = QTabWidget()
        dashboard = self._dashboard_tab()
        projects = self._simple_tab("Projects", self.load_projects)
        experiments = self._simple_tab("Experiments", self.load_experiments)
        regions = self._simple_tab("Brain Regions", self.load_regions)
        telemetry = self._simple_tab("Telemetry", self.load_telemetry)
        jobs = self._simple_tab("Jobs", self.load_jobs)
        servers = self._simple_tab("Servers", self.load_servers)
        cl1_tab = self._cl1_tab()
        script_tab = self._script_tab()
        network_tab = self._network_sim_tab()

        self.tabs.addTab(dashboard, "Dashboard")
        self.tabs.addTab(cl1_tab, "CL1 Clone")
        self.tabs.addTab(network_tab, "Network Simulation")
        self.tabs.addTab(script_tab, "BrainScript")
        self.tabs.addTab(projects, "Projects")
        self.tabs.addTab(experiments, "Experiments")
        self.tabs.addTab(regions, "Brain Regions")
        self.tabs.addTab(telemetry, "Telemetry")
        self.tabs.addTab(jobs, "Jobs")
        self.tabs.addTab(servers, "Servers")

        self._build_menus()

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.addWidget(self.tabs)
        layout.addWidget(QLabel("Output:"))
        layout.addWidget(self.output)
        self.setCentralWidget(central)
        self.statusBar().showMessage("Not authenticated")

    # -- tab builders ------------------------------------------------------

    def _dashboard_tab(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        refresh = QPushButton("Refresh Server")
        refresh.clicked.connect(self.refresh_dashboard)
        layout.addWidget(refresh)
        return panel

    def _simple_tab(self, title: str, handler) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        button = QPushButton(f"Load {title}")
        button.clicked.connect(handler)
        layout.addWidget(button)
        return panel

    def _cl1_tab(self) -> QWidget:
        """CL1 Clone page with nested sub-pages (tabs within the tab)."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        sub = QTabWidget()
        sub.addTab(self._cl1_session_page(), "Session")
        sub.addTab(self._cl1_stimulation_page(), "Stimulation")
        sub.addTab(self._cl1_recording_page(), "Recording")
        sub.addTab(self._cl1_run_page(), "Run")
        sub.addTab(self._cl1_analytics_page(), "Graphics & Charts")
        sub.addTab(self._cl1_sources_page(), "Information Source Files")
        sub.addTab(self._cl1_modules_page(), "Modules")
        layout.addWidget(sub)
        return panel

    def _cl1_session_page(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.addWidget(QLabel("Session: open or close a simulated neural dish (Neurons context)."))
        open_btn = QPushButton("Open Simulator (64 channels, seed 0)")
        open_btn.clicked.connect(self.cl1_open)
        close_btn = QPushButton("Close Session")
        close_btn.clicked.connect(self.cl1_close)
        layout.addWidget(open_btn)
        layout.addWidget(close_btn)
        return panel

    def _cl1_stimulation_page(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.addWidget(QLabel("Stimulation: deliver single pulses or bursts (StimDesign / BurstDesign)."))
        stim_btn = QPushButton("Deliver Stim (channels 0-3, ±80 µA, 2 pulses)")
        stim_btn.clicked.connect(self.cl1_stim)
        single_btn = QPushButton("Single Pulse…")
        single_btn.clicked.connect(self.cl1_stim_single)
        burst_btn = QPushButton("Burst…")
        burst_btn.clicked.connect(self.cl1_stim_burst)
        layout.addWidget(stim_btn)
        layout.addWidget(single_btn)
        layout.addWidget(burst_btn)
        return panel

    def _cl1_recording_page(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.addWidget(QLabel("Recording: capture spikes/stims (Recording, DetectionResult)."))
        record_btn = QPushButton("Start Recording")
        record_btn.clicked.connect(self.cl1_record)
        stop_btn = QPushButton("Stop Recording")
        stop_btn.clicked.connect(self.cl1_stop_recording)
        report_btn = QPushButton("Show Report")
        report_btn.clicked.connect(self.cl1_report)
        layout.addWidget(record_btn)
        layout.addWidget(stop_btn)
        layout.addWidget(report_btn)
        return panel

    def _cl1_run_page(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.addWidget(QLabel("Run: iterate the simulator loop (Loop / LoopTick)."))
        run_btn = QPushButton("Run Loop (10 ticks @ 25 Hz)")
        run_btn.clicked.connect(self.cl1_run_loop)
        layout.addWidget(run_btn)
        return panel

    def _cl1_sources_page(self) -> QWidget:
        """Sub-page listing the CL1 clone information source files."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.addWidget(QLabel("CL1 clone information source files"))
        tree = QTreeWidget()
        tree.setHeaderLabels(["Source file", "Exposes"])
        sources = [
            ("src/synthetic_brain/cl1_clone.py", "open, CL1Clone, Neurons, Loop, LoopTick, Recording, DetectionResult, Spike, Stim, StimDesign, BurstDesign, ChannelSet, SAMPLE_RATE_HZ"),
            ("src/synthetic_brain/cl1_simulator.py", "Standalone simulator loop with recording serialization (synthetic-brain-cl1-simulator-v1)"),
            ("src/synthetic_brain/cl1.py", "CL1 research adapter surface"),
            ("src/synthetic_brain/cl1_recording.py", "Recording helpers"),
            ("src/synthetic_brain/cl1_analysis.py", "Spike/stim analysis routines"),
            ("src/synthetic_brain/cl1_benchmark.py", "Benchmark scenarios"),
            ("src/synthetic_brain/cl1_data_source.py", "Recording import/export data sources"),
            ("src/synthetic_brain/cl1_experiment.py", "Experiment definitions"),
            ("docs/CL1_CLONE_INFORMATION.md", "API summary and research boundary"),
            ("LICENSES/CL1_NOTICE.md", "Cortical Labs attribution notice"),
        ]
        for path, exposes in sources:
            QTreeWidgetItem(tree, [path, exposes])
        tree.resizeColumnToContents(0)
        layout.addWidget(tree)
        return panel

    # -- graphics / charts ---------------------------------------------------

    def _raster_chart(self) -> QWidget:
        """Spike raster canvas widget with refresh button."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        canvas = SpikeRasterCanvas()
        refresh = QPushButton("Render Spike Raster (from last recording)")
        refresh.clicked.connect(lambda: canvas.render(self.recording))
        layout.addWidget(refresh)
        layout.addWidget(canvas)
        return panel

    def _rate_chart(self) -> QWidget:
        """Per-channel firing-rate bar chart."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        canvas = ChannelHistogramCanvas()
        refresh = QPushButton("Render Channel Histogram (from last recording)")
        refresh.clicked.connect(lambda: canvas.render(self.recording))
        layout.addWidget(refresh)
        layout.addWidget(canvas)
        return panel

    def _activity_chart(self) -> QWidget:
        """Population activity line chart over loop ticks."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        canvas = ActivityLineCanvas()
        refresh = QPushButton("Render Activity Trace (from last loop run)")
        refresh.clicked.connect(lambda: canvas.render(getattr(self, "activity_trace", [])))
        layout.addWidget(refresh)
        layout.addWidget(canvas)
        return panel

    def _cl1_analytics_page(self) -> QWidget:
        """Sub-page with all graphic/data-chart canvases."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.addWidget(QLabel("CL1 clone data charts — spike raster, channel histogram, population activity."))
        charts = QTabWidget()
        charts.addTab(self._raster_chart(), "Spike Raster")
        charts.addTab(self._rate_chart(), "Channel Histogram")
        charts.addTab(self._activity_chart(), "Activity Trace")
        layout.addWidget(charts)
        return panel

    def _cl1_modules_page(self) -> QWidget:
        """Modular / sub-module map of the CL1 stack."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.addWidget(QLabel("CL1 module / sub-module map"))
        tree = QTreeWidget()
        tree.setHeaderLabels(["Module", "Sub-modules / responsibilities"])
        modules = [
            ("cl1_clone", "open, CL1Clone, Neurons, Loop, LoopTick, Recording, DetectionResult, Spike, Stim, StimDesign, BurstDesign, ChannelSet"),
            ("cl1_simulator", "standalone loop, JSON recording serialization"),
            ("cl1", "research adapter surface"),
            ("cl1_recording", "recording capture helpers"),
            ("cl1_analysis", "spike/stim analysis, per-channel rates"),
            ("cl1_benchmark", "benchmark scenarios and timing"),
            ("cl1_data_source", "import/export of recording data"),
            ("cl1_experiment", "experiment definitions wired to server"),
            ("brainlang_cl1", "BrainLang → CL1 neuron-count bridge"),
        ]
        for name, desc in modules:
            QTreeWidgetItem(tree, [name, desc])
        tree.resizeColumnToContents(0)
        layout.addWidget(tree)
        return panel

    # -- network-driven simulation (docs/NETWORK_SIMULATION.md) ---------------

    def _network_sim_tab(self) -> QWidget:
        """Network-driven simulation page with sub-pages."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        sub = QTabWidget()
        sub.addTab(self._network_example_page(), "Example")
        sub.addTab(self._network_graph_page(), "Connectivity Graph")
        sub.addTab(self._network_activity_page(), "Activity Chart")
        layout.addWidget(sub)
        return panel

    def _network_example_page(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.addWidget(QLabel("Network-driven simulation: NeuralNetwork + NetworkSimulation + SimulationConfig."))
        run = QPushButton("Run Network Example (3 neurons, 10 steps, external input 0.05)")
        run.clicked.connect(self.run_network_example)
        layout.addWidget(run)
        return panel

    def _network_graph_page(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        canvas = NetworkGraphCanvas()
        refresh = QPushButton("Render Connectivity Graph (from last run)")
        refresh.clicked.connect(lambda: canvas.render(getattr(self, "network_edges", None)))
        layout.addWidget(refresh)
        layout.addWidget(canvas)
        return panel

    def _network_activity_page(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        canvas = ActivityLineCanvas()
        refresh = QPushButton("Render Total Activity (from last run)")
        refresh.clicked.connect(lambda: canvas.render(getattr(self, "network_activity", [])))
        layout.addWidget(refresh)
        layout.addWidget(canvas)
        return panel

    def run_network_example(self) -> None:
        try:
            from synthetic_brain import NeuralNetwork, NetworkSimulation, SimulationConfig

            network = NeuralNetwork(neuron_count=3)
            network.connect(0, 1, weight=0.8)
            network.connect(1, 2, weight=0.5)
            network.connect(2, 0, weight=-0.2)
            simulation = NetworkSimulation(network, SimulationConfig(neuron_count=3, seed=42))
            self.log(f"Network snapshot: {simulation.snapshot()}")
            self.network_edges = [(0, 1, 0.8), (1, 2, 0.5), (2, 0, -0.2)]
            self.network_activity = []
            for _ in range(10):
                snapshot = simulation.step(external_input=0.05)
                self.network_activity.append(sum(snapshot.activity) / len(snapshot.activity))
                self.log(f"Step {snapshot.step}: {snapshot.activity}")
            self.log("Network example complete — open Network Simulation → Connectivity Graph / Activity Chart to render.")
        except Exception as exc:
            self.log(f"Network example failed: {exc}")

    def _script_tab(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        run = QPushButton("Compile & Run BrainScript")
        run.clicked.connect(self.run_brainscript)
        layout.addWidget(run)
        layout.addWidget(self.brainscript)
        return panel

    # -- menus -------------------------------------------------------------

    def _build_menus(self) -> None:
        menu_bar = self.menuBar()

        # File menu ---------------------------------------------------------
        file_menu = menu_bar.addMenu("&File")
        connect_action = QAction("Connect to &Server…", self)
        connect_action.setShortcut(QKeySequence("Ctrl+O"))
        connect_action.triggered.connect(self.change_server)
        file_menu.addAction(connect_action)

        file_menu.addSeparator()
        quit_action = QAction("E&xit", self)
        quit_action.setShortcut(QKeySequence("Ctrl+Q"))
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        # CL1 menu ----------------------------------------------------------
        cl1_menu = menu_bar.addMenu("&CL1")

        session_menu = cl1_menu.addMenu("&Session")
        open_action = QAction("&Open Simulator…", self)
        open_action.triggered.connect(self.cl1_open)
        session_menu.addAction(open_action)
        close_action = QAction("C&lose Session", self)
        close_action.triggered.connect(self.cl1_close)
        session_menu.addAction(close_action)

        stim_menu = cl1_menu.addMenu("&Stimulation")
        single_action = QAction("&Single Pulse…", self)
        single_action.triggered.connect(self.cl1_stim_single)
        stim_menu.addAction(single_action)
        burst_action = QAction("&Burst…", self)
        burst_action.triggered.connect(self.cl1_stim_burst)
        stim_menu.addAction(burst_action)

        record_menu = cl1_menu.addMenu("&Recording")
        start_action = QAction("&Start Recording", self)
        start_action.triggered.connect(self.cl1_record)
        record_menu.addAction(start_action)
        stop_action = QAction("Sto&p Recording", self)
        stop_action.triggered.connect(self.cl1_stop_recording)
        record_menu.addAction(stop_action)
        report_action = QAction("Show &Report", self)
        report_action.triggered.connect(self.cl1_report)
        record_menu.addAction(report_action)

        run_menu = cl1_menu.addMenu("&Run")
        loop_action = QAction("Run &Loop…", self)
        loop_action.triggered.connect(self.cl1_run_loop)
        run_menu.addAction(loop_action)

        # Simulation menu ----------------------------------------------------
        sim_menu = menu_bar.addMenu("&Simulation")
        core_menu = sim_menu.addMenu("&Core Engine")
        core_menu.addAction("Run Synthetic Brain Demo", self.run_core_demo)
        network_menu = sim_menu.addMenu("&Network")
        network_menu.addAction("Build Default Network", self.run_core_demo)
        regions_menu = sim_menu.addMenu("&Regions")
        regions_menu.addAction("List Brain Regions", self.load_regions)
        graphics_menu = sim_menu.addMenu("&Graphics && Charts")
        graphics_menu.addAction("Show Spike Raster", lambda: self._focus_cl1_subpage("Graphics & Charts"))
        graphics_menu.addAction("Show Channel Histogram", lambda: self._focus_cl1_subpage("Graphics & Charts"))
        graphics_menu.addAction("Show Activity Trace", lambda: self._focus_cl1_subpage("Graphics & Charts"))
        net_graph_menu = sim_menu.addMenu("&Network Simulation")
        net_graph_menu.addAction("Run Network Example", self.run_network_example)
        net_graph_menu.addAction("Show Connectivity Graph", lambda: self._focus_tab("Network Simulation"))
        net_graph_menu.addAction("Show Activity Chart", lambda: self._focus_tab("Network Simulation"))
        modules_menu = sim_menu.addMenu("&Modules")
        modules_menu.addAction("CL1 Module Map", lambda: self._focus_cl1_subpage("Modules"))

        # BrainLang menu -----------------------------------------------------
        lang_menu = menu_bar.addMenu("&BrainLang")
        lang_menu.addAction("&Compile && Run Script", self.run_brainscript)
        lang_menu.addAction("Load &Example", self.load_example_script)

        # View menu ----------------------------------------------------------
        view_menu = menu_bar.addMenu("&View")
        cl1_view = view_menu.addMenu("&CL1 Clone Pages")
        for title in ("Session", "Stimulation", "Recording", "Run", "Graphics & Charts", "Information Source Files", "Modules"):
            action = QAction(title, self)
            action.triggered.connect(lambda _checked, t=title: self._focus_cl1_subpage(t))
            cl1_view.addAction(action)
        pages_menu = view_menu.addMenu("&Pages")
        for title in ("Dashboard", "CL1 Clone", "Network Simulation", "BrainScript", "Projects", "Experiments", "Brain Regions", "Telemetry", "Jobs", "Servers"):
            action = QAction(title, self)
            action.triggered.connect(lambda _checked, t=title: self._focus_tab(t))
            pages_menu.addAction(action)

        # Help menu ----------------------------------------------------------
        help_menu = menu_bar.addMenu("&Help")
        help_menu.addAction("&About", self.show_about)
        help_menu.addAction("CL1 &API Reference", self.show_cl1_reference)

    def _focus_tab(self, title: str) -> None:
        for index in range(self.tabs.count()):
            if self.tabs.tabText(index) == title:
                self.tabs.setCurrentIndex(index)
                return

    def _focus_cl1_subpage(self, title: str) -> None:
        self._focus_tab("CL1 Clone")
        cl1_tab = self.tabs.currentWidget()
        sub = cl1_tab.findChild(QTabWidget)
        if sub is None:
            return
        for index in range(sub.count()):
            if sub.tabText(index) == title:
                sub.setCurrentIndex(index)
                return

    # -- helpers -----------------------------------------------------------

    def auth_headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.token}"} if self.token else {}

    def log(self, text: str) -> None:
        self.output.appendPlainText(text)

    def _require_server(self) -> bool:
        if not self.token:
            QMessageBox.information(self, "Not signed in", "Sign in first (File → Connect to Server).")
            return False
        return True

    def _require_simulator(self) -> bool:
        if self.neurons is None:
            QMessageBox.information(self, "No session", "Open a CL1 session first (CL1 → Session → Open Simulator).")
            return False
        return True

    # -- server actions ----------------------------------------------------

    def change_server(self) -> None:
        url, ok = QInputDialog.getText(self, "Server URL", "Server base URL:", text=self.server_url)
        if ok and url.strip():
            self.server_url = url.strip().rstrip("/")
            self.statusBar().showMessage(f"Server set to {self.server_url}")

    def refresh_dashboard(self) -> None:
        try:
            response = httpx.get(f"{self.server_url}/api/v1/about", headers=self.auth_headers(), timeout=5.0)
            response.raise_for_status()
            self.log(f"About: {response.json()}")
            self.statusBar().showMessage("Server connected")
        except Exception as exc:
            self.log(f"Server unavailable: {exc}")

    def _load_endpoint(self, path: str, label: str) -> None:
        if not self._require_server():
            return
        try:
            response = httpx.get(f"{self.server_url}{path}", headers=self.auth_headers(), timeout=5.0)
            response.raise_for_status()
            self.log(f"{label}: {response.json()}")
        except Exception as exc:
            self.log(f"{label} request failed: {exc}")

    def load_projects(self) -> None:
        self._load_endpoint("/api/v1/projects", "Projects")

    def load_experiments(self) -> None:
        self._load_endpoint("/api/v1/experiments", "Experiments")

    def load_regions(self) -> None:
        self.log("Brain regions module: cortical lobes (frontal, parietal, temporal, occipital) available in synthetic_brain.regions.cortex.")

    def load_telemetry(self) -> None:
        self._load_endpoint("/api/v1/telemetry", "Telemetry")

    def load_jobs(self) -> None:
        self._load_endpoint("/api/v1/jobs", "Jobs")

    def load_servers(self) -> None:
        self._load_endpoint("/api/v1/servers", "Servers")

    def run_core_demo(self) -> None:
        try:
            from synthetic_brain import Simulation, SimulationConfig

            simulation = Simulation(SimulationConfig())
            for _ in range(3):
                simulation.step()
            self.log(f"Core simulation steps complete: activity={simulation.activity!r}")
        except Exception as exc:
            self.log(f"Core simulation failed: {exc}")

    # -- BrainLang ----------------------------------------------------------

    def load_example_script(self) -> None:
        self.brainscript.setPlainText(
            "brain Cortex {\n"
            "    population Excitatory size 100\n"
            "    population Inhibitory size 25\n"
            "    connect Excitatory -> Inhibitory weight 0.2 delay 1.5\n"
            "}"
        )

    def run_brainscript(self) -> None:
        try:
            from synthetic_brain.brainlang import BrainRuntime

            env = BrainRuntime().execute(self.brainscript.toPlainText())
            brains = {name: v.fields for name, v in env.values.items() if hasattr(v, "fields")}
            self.log(f"BrainLang result: {brains}")
        except Exception as exc:
            self.log(f"BrainLang error: {exc}")

    # -- CL1 clone actions ---------------------------------------------------

    def cl1_open(self) -> None:
        channels, ok = QInputDialog.getInt(self, "Open Simulator", "Channel count:", 64, 1, 4096)
        if not ok:
            return
        seed, ok = QInputDialog.getInt(self, "Open Simulator", "Random seed:", 0, 0, 2**31 - 1)
        if not ok:
            return
        try:
            self.cl1_close()
        except Exception:
            pass
        try:
            self.neurons = cl1_open(channel_count=channels, seed=seed).__enter__()
            self.loop_ticks = 0
            self.log(f"CL1 session opened: {channels} channels, seed {seed}, sample rate {SAMPLE_RATE_HZ} Hz")
        except Exception as exc:
            self.log(f"Open failed: {exc}")

    def cl1_close(self) -> None:
        if self.neurons is not None:
            try:
                self.neurons.close()
                self.log("CL1 session closed.")
            except Exception as exc:
                self.log(f"Close failed: {exc}")
            self.neurons = None
            self.recording = None

    def cl1_stim(self) -> None:
        self._stim_dialog(channels="0-3", amplitude=80.0, burst_count=2, frequency=100.0)

    def cl1_stim_single(self) -> None:
        self._stim_dialog(channels="0", amplitude=80.0, burst_count=1, frequency=1.0)

    def cl1_stim_burst(self) -> None:
        self._stim_dialog(channels="0-3", amplitude=120.0, burst_count=5, frequency=50.0)

    def _stim_dialog(self, channels: str, amplitude: float, burst_count: int, frequency: float) -> None:
        if not self._require_simulator():
            return
        channels_text, ok = QInputDialog.getText(self, "Stimulate", "Channels (e.g. 0-3 or 1,4,7):", text=channels)
        if not ok:
            return
        amplitude, ok = QDoubleSpinBox(), None
        amplitude.setRange(1.0, 4000.0)
        amplitude.setValue(80.0)
        amp, ok_amp = QInputDialog.getDouble(self, "Stimulate", "Amplitude (µA):", amplitude.value(), 1.0, 4000.0, 1)
        if not (ok and ok_amp):
            return
        count, ok_count = QInputDialog.getInt(self, "Stimulate", "Pulse count:", burst_count, 1, 1000)
        if not ok_count:
            return
        freq, ok_freq = QInputDialog.getDouble(self, "Stimulate", "Burst frequency (Hz):", frequency, 0.1, 10000.0, 1)
        if not ok_freq:
            return
        try:
            from synthetic_brain.cl1_clone import BurstDesign, ChannelSet, StimDesign

            channel_set = ChannelSet()
            channels_parsed: list[int] = []
            for part in channels_text.split(","):
                part = part.strip()
                if "-" in part:
                    lo, hi = part.split("-", 1)
                    channels_parsed.extend(range(int(lo), int(hi) + 1))
                elif part:
                    channels_parsed.append(int(part))
            channel_set = ChannelSet(*channels_parsed)
            stim_design = StimDesign(160, -amp, 160, amp)
            burst = BurstDesign(count=count, frequency_hz=freq)
            self.neurons.stim(channel_set, stim_design, burst)
            self.log(f"Stim delivered: channels={list(channel_set)}, amplitude=±{amp} µA, pulses={count}, freq={freq} Hz")
        except Exception as exc:
            self.log(f"Stim failed: {exc}")

    def cl1_record(self) -> None:
        if not self._require_simulator():
            return
        self.recording = self.neurons.record(source="desktop-client")
        self.log("Recording started.")

    def cl1_stop_recording(self) -> None:
        if self.recording is None:
            self.log("No active recording.")
            return
        self.recording.stop()
        self.log(f"Recording stopped: {len(self.recording.spikes)} spikes, {len(self.recording.stims)} stims captured.")
        self.recording = None

    def cl1_report(self) -> None:
        if self.recording is None:
            self.log("No active recording to report on. Start one first.")
            return
        spikes = self.recording.spikes
        stims = self.recording.stims
        per_channel: dict[int, int] = {}
        for spike in spikes:
            per_channel[spike.channel] = per_channel.get(spike.channel, 0) + 1
        top = sorted(per_channel.items(), key=lambda kv: kv[1], reverse=True)[:10]
        self.log(f"Recording report: {len(spikes)} spikes, {len(stims)} stims. Top channels: {top}")

    def cl1_run_loop(self) -> None:
        if not self._require_simulator():
            return
        ticks, ok = QInputDialog.getInt(self, "Run Loop", "Ticks (loop iterations):", 10, 1, 10_000)
        if not ok:
            return
        rate, ok = QInputDialog.getDouble(self, "Run Loop", "Ticks per second:", 25.0, 0.1, SAMPLE_RATE_HZ, 1)
        if not ok:
            return
        try:
            total_spikes = 0
            self.activity_trace: list[int] = []
            for tick in self.neurons.loop(rate, stop_after_ticks=ticks):
                total_spikes += len(tick.analysis.spikes)
                self.activity_trace.append(len(tick.analysis.spikes))
                self.loop_ticks = tick.iteration
            self.log(f"Loop finished: {ticks} ticks at {rate} Hz, {total_spikes} spikes detected. Activity trace captured for the charts.")
        except Exception as exc:
            self.log(f"Loop failed: {exc}")

    # -- misc ----------------------------------------------------------------

    def show_about(self) -> None:
        QMessageBox.about(
            self,
            "About",
            "Synthetic Human Brain Researcher Client\n\n"
            "Research prototype for synthetic neural systems, CL1-style simulation, "
            "computational neuroscience, and neural interface research.\n\n"
            "Not a medical device. Not a human brain.",
        )

    def show_cl1_reference(self) -> None:
        self._focus_cl1_subpage("Information Source Files")
        self.log(
            "CL1 clone API: open(channel_count, seed) -> Neurons; "
            "neurons.stim(ChannelSet, StimDesign, BurstDesign); neurons.record(**attrs) -> Recording; "
            "neurons.loop(ticks_per_second, stop_after_ticks=…) -> Loop of LoopTick(analysis=DetectionResult(spikes, stims)); "
            "recording.stop() then inspect recording.spikes / recording.stims. See docs/CL1_CLONE_INFORMATION.md."
        )


def main() -> int:
    app = QApplication(sys.argv)
    server_url = "http://127.0.0.1:8787"
    window = ResearcherClient(server_url)
    login = LoginDialog(server_url)
    if login.exec() != QDialog.DialogCode.Accepted:
        return 0
    window.server_url = login.server_url
    window.token = login.token
    window.user = login.user
    window.statusBar().showMessage(f"Signed in as {login.user.get('display_name', login.user.get('username', 'researcher'))}")
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
