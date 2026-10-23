# Synthetic Human Brain Multi-Researcher Server

The server layer provides a shared network service for multiple desktop research clients.

## Architecture

```text
Windows / macOS / Linux desktop clients
              |
              | HTTPS / WebSocket
              v
       Synthetic Brain Server
        |      |       |
        |      |       +-- job scheduler
        |      +---------- research/session API
        +----------------- Rust simulation backend
              |
              +---- MySQL
              +---- experiment artifacts
              +---- hardware/CL1 adapters
```

The server is authoritative for users, projects, experiments, jobs, permissions, and collaborative session state. Desktop clients remain presentation and local-workspace clients.

## Multi-researcher model

- `users`: researcher identities
- `projects`: shared research workspaces
- `project_members`: project-level roles
- `experiments`: reproducible simulation/experiment definitions
- `jobs`: queued/running/completed backend work
- `sessions`: connected desktop clients
- `events`: audit and collaboration events

Authentication must use password hashes, never plaintext passwords. Administrative operations require an administrator role and should be audited.
