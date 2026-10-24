 # Python Server — Source Reference

Complete map of the Python backend (`server/python/`): the FastAPI
application, its modules, the database layer, and how it fronts the Rust
backend for the desktop GUI and web client.

## Application modules (`server/python/app/`)

| Module | Lines/size | Contents |
| --- | --- | --- |
| `main.py` | 27.7 KB | FastAPI app: auth, projects, experiments, jobs, telemetry, servers, workers, WebSocket, network-simulation endpoints, startup table creation. |
| `config.py` | 1.0 KB | `Settings` (pydantic-settings): database URL with SQLite fallback, JWT settings, CORS origins; `SYNTHETIC_BRAIN_*` env prefix. |
| `db.py` | — | Async SQLAlchemy engine + `db_session` dependency. |
| `models.py` | 9.2 KB | ORM models: `User`, `Role`, `UserRole`, `Project`, `ProjectMember`, `Session`, `Server`, `Worker`, `Experiment`, `Job`, `TelemetryEvent`, `AuditLog` (mirrors `server/config/mysql/schema.sql`). |
| `auth.py` | 1.5 KB | `register_user`, `authenticate_user`, `issue_token` (JWT), session ids. |
| `security.py` | — | argon2 password hashing/verification. |
| `rbac.py` | — | Role checks (`administrator`, `researcher`). |
| `jobs.py` | 1.2 KB | Job schemas and helpers. |
| `job_router.py` | 1.7 KB | `select_worker` — routes jobs to registered workers by capability. |
| `job_executor.py` | 2.0 KB | Executes queued jobs; updates status/transitions. |
| `job_events.py` | — | `publish_job_event` into the telemetry hub. |
| `telemetry.py` | — | `telemetry_hub` — in-process pub/sub for live metrics over WebSocket. |
| `worker_registry.py` | 2.6 KB | Worker registration and heartbeat bookkeeping. |
| `rust_client.py` | 0.9 KB | `dispatch_job` — HTTP call to the Rust backend (`SYNTHETIC_BRAIN_RUST_BACKEND_URL`). |
| `protocol.py` | — | `envelope()` — consistent WebSocket message envelope. |
| `cl1_labs_bridge.py` | CL1-Neural-labs protocol bridge — ported from `integration/cl1_labs_ts/server.ts`: stim channel validation, 384-byte little-endian binary frame codec, `/_/config` payload, `CultureParameters` defaults. |
| `experiments.py` | 1.0 KB | Experiment schema helpers. |

## Entry points

| File | Purpose |
| --- | --- |
| `server/python/app/main.py` | `uvicorn app.main:app` — the API server (default port 8787). |
| `server/python/worker_app.py` | Standalone worker process: registers with the server, polls jobs, reports heartbeats/results. |

## Database

- Development default: `sqlite+aiosqlite:///./synthetic_brain.db` (auto-created on startup).
- Production: MySQL — provision with `server/config/mysql/provision.sql`, then `schema.sql`, `views.sql`, `seed.sql` (see `server/config/mysql/README.md`).
- Table creation runs in the FastAPI startup hook (`Base.metadata.create_all`).

## API surface

Documented in [API_SERVER_REFERENCE.md](API_SERVER_REFERENCE.md); interactive
docs at `/docs` and `/openapi.json` on a running server.

## Running

```bash
cd server/python
../../.venv/Scripts/python.exe -m uvicorn app.main:app --port 8787
```

Environment template: `server/config/env.example`.

## Research boundary

The server coordinates research experiments only. It is not a medical device,
does not store clinical records, and enforces the data-handling rules in
[SAFETY_AND_LIMITATIONS.md](SAFETY_AND_LIMITATIONS.md).
