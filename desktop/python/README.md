# Desktop Researcher Client

The desktop client targets **Windows, macOS, and Linux** laptops/workstations.

## Responsibilities

- researcher login and logout
- server selection and connection status
- project and experiment navigation
- BrainScript source editing
- simulation controls
- telemetry and job monitoring
- hardware/worker status
- administrator console when RBAC permits it

The desktop client communicates with the public server API over HTTPS and WSS. It does **not** connect directly to MySQL.

## Planned implementation

The first implementation uses Python/PySide6 so the application remains aligned with the Python research layer. Rust compute components remain behind the server/worker boundary.
