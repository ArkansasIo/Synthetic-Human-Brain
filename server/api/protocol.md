# Research Station Network Protocol

## Scope

The system supports multiple Windows, macOS, and Linux research desktops connecting to one or more Synthetic Brain servers. Phones are not part of this desktop research-station target.

## Transport

- HTTPS/TLS: authentication, project management, experiment control, metadata, files and job management.
- WebSocket over TLS: live telemetry, job status, collaboration events, simulation streams and server notifications.
- REST/JSON: stable browser and desktop API contract.
- Optional binary frames: high-rate telemetry where JSON is insufficient; payloads must be versioned.

## Client identity

Every desktop installation has a `client_id`. Every login creates a server-side session. Every request carries a request ID for tracing and idempotency.

## Message envelope

```json
{
  "protocol_version": "1.0",
  "request_id": "uuid",
  "session_id": "uuid",
  "message_type": "experiment.telemetry",
  "timestamp": "2026-10-23T19:00:00Z",
  "payload": {}
}
```

## Multi-server model

```text
Research Station A ─┐
Research Station B ─┼──> Server Cluster / Server 1 ──> MySQL
Research Station C ─┤             |
Research Station D ─┘             +──> Rust simulation workers
                                  |
                                  +──> Server 2 / worker pool
```

A desktop can be configured with a primary server and optional secondary server endpoints. Project data remains authoritative on the selected server/cluster; replication is an explicit server feature rather than an implicit client behavior.

## Security

- TLS required outside localhost/development.
- Passwords are hashed server-side; plaintext passwords are never stored.
- Short-lived access tokens plus refresh/session rotation.
- Role-based authorization at project and administrative boundaries.
- Audit every administrative and experiment-control operation.
- Validate message size, protocol version and payload schema.

## Compatibility

The Python application is the high-level client/API layer. Rust implements performance-sensitive server workers. The TypeScript browser client speaks the same HTTP/WebSocket protocol and never depends directly on Rust internals.
