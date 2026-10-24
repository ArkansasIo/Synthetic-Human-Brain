# Server API Reference (Implemented)

Endpoints implemented in `server/python/app/main.py`. All responses are JSON.
Authentication uses `Authorization: Bearer <JWT>`; obtain a token from
`/api/v1/auth/register` or `/api/v1/auth/login`.

## Health & metadata

| Method | Path | Auth | Purpose |
| --- | --- | --- | --- |
| GET | `/api/v1/health` | none | Liveness probe. |
| GET | `/api/v1/about` | none | App name, version, developer. |

## Auth & sessions

| Method | Path | Purpose |
| --- | --- | --- |
| POST | `/api/v1/auth/register` | Create user, return JWT + session. |
| POST | `/api/v1/auth/login` | Authenticate, return JWT + session. |
| POST | `/api/v1/auth/logout` | Revoke the current session. |
| GET | `/api/v1/me` | Current user profile and roles. |

## Projects & experiments

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/api/v1/projects` | List projects (role-filtered). |
| POST | `/api/v1/projects` | Create project. |
| GET | `/api/v1/projects/{id}/experiments` | List experiments in a project. |
| POST | `/api/v1/projects/{id}/experiments` | Create experiment. |
| POST | `/api/v1/experiments/{id}/jobs` | Submit simulation job. |
| GET | `/api/v1/jobs` | List jobs. |

## Telemetry

| Method | Path | Purpose |
| --- | --- | --- |
| POST | `/api/v1/experiments/{id}/telemetry` | Append a metric sample. |
| GET | `/api/v1/experiments/{id}/telemetry` | Read metric samples (`limit` ≤ 5000). |

## Servers & workers (admin/researcher)

| Method | Path | Purpose |
| --- | --- | --- |
| GET/POST | `/api/v1/servers` | List / register compute servers. |
| GET/POST | `/api/v1/workers` | List / register workers. |
| POST | `/api/v1/workers/{id}/heartbeat` | Worker status heartbeat. |

## Network-driven simulation (docs/NETWORK_SIMULATION.md)

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/api/v1/network/models` | `NeuronModel`/`SynapseModel` contracts and constraints. |
| POST | `/api/v1/network/simulate` | Run graph-driven simulation; body: `NetworkSpec` (`neuron_count`, `edges` as `[source, target, weight]`, `steps`, `external_input`, `seed`); returns activity trajectory. |
| POST | `/api/v1/network/models/neuron` | Validate `LeakyRateNeuron` parameters (`decay`, `minimum`, `maximum`); returns a sample update. |
| POST | `/api/v1/network/models/synapse` | Validate `LinearSynapse` (`scale`); returns a sample transmit. |

## WebSocket

| Path | Purpose |
| --- | --- |
| `/ws?token=<JWT>` | Server events; `ping`/`pong` keepalive; telemetry push via `telemetry_hub`. |

## Interactive docs

- Swagger UI: `/docs`
- OpenAPI schema: `/openapi.json`
