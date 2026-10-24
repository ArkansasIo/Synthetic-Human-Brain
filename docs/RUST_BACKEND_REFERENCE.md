# Rust Backend & Core — Source Reference

Complete map of the Rust layer (`rust/`): the simulation core, the backend
service library, the HTTP server binary, and configuration. These components
sit behind the Python API server (`server/python/app/rust_client.py`) and are
never accessed directly by the desktop GUI or web client.

## Crates and source files

### `rust/` — simulation core (`synthetic_brain_core`)

| File | Contents |
| --- | --- |
| `src/lib.rs` | Crate root; exports the simulation types. |
| `src/neuron.rs` | Leaky integrate-and-fire neuron model (`LIFNeuron`): threshold, reset, membrane dynamics in pure functions. |
| `src/network.rs` | Weighted network simulation primitives shared with the Python `NetworkSimulation`. |
| `src/telemetry.rs` | Lightweight telemetry counters surfaced to the server. |

### `rust/backend/` — backend service library (`synthetic-brain-backend`)

| File | Contents |
| --- | --- |
| `src/lib.rs` | Crate root; re-exports api, hardware, jobs, platform, service, settings, store. |
| `src/api.rs` | API request/response types (`ApiRequest`, `ApiResponse`) consumed by the server. |
| `src/service.rs` | `BackendService`: dispatches operations (step, jobs) to the core simulation. |
| `src/service_fixed.rs` | Variant used by tests/build matrix for the fixed-step path. |
| `src/jobs.rs` | `Job`, `JobKind`, `JobQueue` — job records and queueing. |
| `src/hardware.rs` | Hardware abstraction: `HardwareDevice`, `HardwareKind`, `HardwarePlugin`, `VirtualHardware`, capabilities and errors. |
| `src/platform.rs` | `Platform` detection used for Windows/macOS/Linux builds. |
| `src/platform_targets.rs` | Compile-time platform target helpers. |
| `src/settings.rs` | `Settings`, `MySqlSettings`, `WorkerSettings`, `OptionSettings` — environment-driven configuration (`SYNTHETIC_DRAIN_*`/`SYNTHETIC_BRAIN_*` variables), settings tests. |
| `src/store.rs` | `MySqlConfig`, `ExperimentRecord` — database-facing types matching the MySQL schema in `server/config/mysql/schema.sql`. |

### `rust/server/` — HTTP server binary (`synthetic-brain-server`)

| File | Contents |
| --- | --- |
| `Cargo.toml` | Binary crate wrapping `synthetic-brain-backend` with axum + tower-http. |
| `src/main.rs` | Full REST API: `/health`, `/about`, `/step` (single LIF neuron step), `/jobs` (enqueue), WebSocket upgrade endpoint; CORS + tracing middleware. Builds the release binary `synthetic-brain-server.exe` in `dist/exe`. |

### Build outputs

| Path | Artifact |
| --- | --- |
| `dist/exe/synthetic-brain-server.exe` | Release server binary (LTO), ~2.5 MB. |
| `dist/exe/synthetic_brain_core.dll` | Core simulation shared library. |
| `dist/exe/config.toml`, `run-server.bat` | Server configuration and launcher. |

## Configuration

- `server/config/server.example.toml` — TOML settings template (ports, database, worker pool).
- `server/config/env.example` — environment variables consumed by both the Python server and the Rust backend.
- `rust/backend/src/settings.rs` — defaults matching the TOML/env templates; refuses placeholder secrets when `refuse_placeholder_secrets` is enabled.

## Relationship to the Python layer

1. Desktop GUI / web client → Python FastAPI server (authentication, projects, jobs).
2. Python server → `rust_client.dispatch_job` → Rust backend over HTTP (`/jobs`, `/step`).
3. Rust backend → `synthetic_brain_core` for simulation math; `store.rs` types mirror the MySQL schema.

## Build commands

```bash
cd rust && cargo build            # core + backend libraries
cd rust/server && cargo build --release   # synthetic-brain-server.exe
cargo test --manifest-path rust/backend/Cargo.toml
```

## Research boundary

All Rust components are abstract computational systems for research
prototyping. They are not validated models of human neurophysiology and do
not support clinical or consciousness claims. See
[SAFETY_AND_LIMITATIONS.md](SAFETY_AND_LIMITATIONS.md).
