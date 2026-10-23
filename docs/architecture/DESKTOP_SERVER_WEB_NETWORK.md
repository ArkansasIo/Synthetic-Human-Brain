# Desktop, Server, and Researcher Browser Network Architecture

## Target

Provide a 2026-era cross-platform research system where multiple Windows, macOS, and Linux desktop/laptop research stations connect to one or more servers. A browser-based Researcher Client uses the same network API.

## Topology

```text
 Windows Desktop ─┐
 macOS Desktop ───┼──── HTTPS/TLS + WebSocket ────> Research Server A
 Linux Desktop ───┤                                      |
 Linux Laptop ────┘                                      +--> Rust workers
                                                        +--> Python services
                                                        +--> MySQL
                                                        +--> Artifact storage

 Browser Researcher Client ────────────────────────────> Server API

 Optional Server B <──────── authenticated server-to-server replication/coordination ────────> Server A
```

## Client layers

Desktop and browser clients share the protocol but have different presentation layers:

- Desktop: native application shell + Python application + local Rust acceleration.
- Browser: TypeScript UI + HTTP/WebSocket API.
- Neither client accesses MySQL directly.
- Neither client calls Rust internals directly.

## Server layers

1. Edge/API service: authentication, authorization, request validation, rate limits.
2. Session service: desktop/browser sessions and WebSocket connections.
3. Research service: projects, experiments, datasets, provenance.
4. Job service: queue, scheduling, cancellation, retries.
5. Rust worker pool: simulation and numerical kernels.
6. Python worker pool: research algorithms and analysis.
7. Hardware service: virtual devices and optional plugin adapters.
8. Persistence: MySQL plus experiment/artifact storage.
9. Telemetry: metrics, logs, health and worker state.

## Protocols

| Link | Protocol |
|---|---|
| Browser -> server | HTTPS REST + WSS |
| Desktop -> server | HTTPS REST + WSS |
| Python -> local Rust | FFI/embedded library |
| Server scheduler -> Rust worker | Internal typed job contract |
| Server -> MySQL | MySQL/TLS |
| Server -> server | Future authenticated service protocol |

## Multi-server strategy

Start with one authoritative server. Add a server registry and explicit replication later. Each experiment has an owning server/cluster ID. Do not silently split mutable state between servers.

## Build targets

The same source tree produces:

- Windows desktop client
- macOS desktop client
- Linux desktop client
- Windows server
- Linux server
- macOS server for development/small deployments
- Browser bundle

Rust is compiled natively for each deployment target. Python packages are built for the corresponding OS/architecture. The protocol remains platform-independent.

## Security baseline

TLS, hashed passwords, session/token rotation, RBAC, project-level authorization, audit logs, request IDs, schema validation, size limits, and explicit experiment permissions are mandatory before multi-user deployment.
