nd rust# Project Source Map — Python, Rust, Front End, Documentation

One-page map of every source tree in the repository and the documentation
that describes it. Use this as the master index; the linked docs contain the
file-level detail.

## Source trees

| Tree | Language | Role | Detailed reference |
| --- | --- | --- | --- |
| `src/synthetic_brain/` | Python | Core library: network simulation, algorithms, CL1 clone, BrainLang, regions. | [NETWORK_SIMULATION.md](NETWORK_SIMULATION.md), [CL1_CLONE_INFORMATION.md](CL1_CLONE_INFORMATION.md) |
| `desktop/python/` | Python/PySide6 | Desktop researcher GUI (also packaged as an exe). | [FRONTEND_REFERENCE.md](FRONTEND_REFERENCE.md), [GUI_PAGES_REFERENCE.md](GUI_PAGES_REFERENCE.md) |
| `web-client/` | TypeScript/Vite | Browser client. | [FRONTEND_REFERENCE.md](FRONTEND_REFERENCE.md) |
| `server/python/` | Python/FastAPI | Backend API, auth, jobs, telemetry, MySQL access. | [PYTHON_SERVER_REFERENCE.md](PYTHON_SERVER_REFERENCE.md), [API_SERVER_REFERENCE.md](API_SERVER_REFERENCE.md) |
| `server/config/mysql/` | SQL | Schema, seed, views, provisioning, maintenance. | `server/config/mysql/README.md` |
| `rust/` | Rust | Simulation core, backend library, HTTP server binary. | [RUST_BACKEND_REFERENCE.md](RUST_BACKEND_REFERENCE.md) |
| `dist/exe/` | — | Built executables (not committed): desktop exe, Rust server exe. | — |
| `tests/` | Python | 17 test files; `pytest` — 87 tests. | — |
| `docs/uml/` | PlantUML | 17 architecture diagrams. | [uml/README.md](uml/README.md) |

## Documentation by concern

### Architecture & plans
[ARCHITECTURE.md](ARCHITECTURE.md) · [MULTISCALE_ARCHITERENCE.md](MULTISCALE_ARCHITECTURE.md) ·
[HARDWARE_ARCHITECTURE.md](HARDWARE_ARCHITECTURE.md) · [SOFTWARE_HARDWARE_MAPPING.md](SOFTWARE_HARDWARE_MAPPING.md) ·
[WHOLE_BRAIN_NEURAL_INTERFACE.md](WHOLE_BRAIN_NEURAL_INTERFACE.md) · [API_REFERENCE.md](API_REFERENCE.md) ·
[API_IMPLEMENTATION_PLAN.md](API_IMPLEMENTATION_PLAN.md)

### Science
[NETWORK_SIMULATION.md](NETWORK_SIMULATION.md) · [COMPUTATIONAL_NEUROSCIENCE_ALGORITHMS.md](COMPUTATIONAL_NEUROSCIENCE_ALGORITHMS.md) ·
[EXPERIMENTS.md](EXPERIMENTS.md)

### Interfaces & UI
[CL1_CLONE_INFORMATION.md](CL1_CLONE_INFORMATION.md) · [GUI_MENUS_REFERENCE.md](GUI_MENUS_REFERENCE.md) ·
[GUI_PAGES_REFERENCE.md](GUI_PAGES_REFERENCE.md) · [DESKTOP_PAGES_REFERENCE.md](DESKTOP_PAGES_REFERENCE.md)

### Implementation detail
[PYTHON_SERVER_REFERENCE.md](PYTHON_SERVER_REFERENCE.md) · [RUST_BACKEND_REFERENCE.md](RUST_BACKEND_REFERENCE.md) ·
[FRONTEND_REFERENCE.md](FRONTEND_REFERENCE.md) · [API_SERVER_REFERENCE.md](API_SERVER_REFERENCE.md)

### Safety & licensing
[SAFETY_AND_LIMITATIONS.md](SAFETY_AND_LIMITATIONS.md) · [../LICENSES/README.md](../LICENSES/README.md) ·
[../LICENSES/CL1_NOTICE.md](../LICENSES/CL1_NOTICE.md)

## Build matrix

| Component | Command | Output |
| --- | --- | --- |
| Python package | `pip install -e ".[dev]"` | editable install |
| Tests | `pytest` | 87 tests |
| Lint | `ruff check .` | clean |
| Core demo | `python -m synthetic_brain` | console simulation |
| Desktop exe | PyInstaller → `dist/exe/SyntheticBrainResearcher.exe` | Windows app |
| Rust server | `cargo build --release` (rust/server) | `dist/exe/synthetic-brain-server.exe` |
| Rust tests | `cargo test` | 4 tests |
| Web client | `npm run build` (web-client) | `web-client/dist/` |
| API server | `uvicorn app.main:app --port 8787` | REST + WebSocket |
| MySQL | `server/config/mysql/*.sql` | schema + seed + views |

## Research boundary

This repository separates measured data, inferred state, simulated state, and
hypotheses. Nothing here is a medical device or a validated model of human
neurophysiology.
