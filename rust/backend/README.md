# Rust Backend

The Rust backend is the performance-oriented service layer for the Synthetic Human Brain application.

## Platform targets

- Windows
- macOS
- Linux

## Responsibilities

- deterministic simulation kernels
- hardware plugin interfaces
- virtual hardware devices
- experiment/job scheduling
- telemetry and API contracts
- database-facing data models
- Python FFI boundary

Rust does not replace the Python research/application layer. Python remains the orchestration, research, BrainScript, and GUI-facing layer.

## Planned storage

MySQL is the authoritative relational store for users, experiments, runs, neural events, metrics, jobs, hardware devices, and audit records. Excel-compatible exports are generated as `.xlsx` research artifacts rather than treated as the primary database.
