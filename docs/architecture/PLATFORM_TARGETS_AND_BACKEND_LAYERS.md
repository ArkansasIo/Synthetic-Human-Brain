# Platform Targets and Backend Layers

## Supported desktop platforms

| Platform | Python application | Rust backend | Browser UI | Virtual hardware |
|---|---|---|---|---|
| Windows | Yes | Yes | Yes | Yes |
| macOS | Yes | Yes | Yes | Yes |
| Linux | Yes | Yes | Yes | Yes |

## Layering

```text
Desktop launcher / browser shell
            |
            v
Python application layer
  - authentication/session boundary
  - BrainScript
  - research orchestration
  - experiments
  - API/UI routing
            |
            +----------------------+
            |                      |
            v                      v
Rust backend service          Python scientific stack
  - simulation kernels          - research models
  - event scheduling            - NumPy/scientific tooling
  - hardware plugins            - analysis
  - virtual hardware            - data preparation
  - telemetry
            |
            v
MySQL
  users / experiments / jobs / events / metrics / hardware / audit
            |
            v
Excel-compatible exports (.xlsx)
```

## Hardware

`rust/backend/hardware.rs` defines the ownership boundary for virtual devices and future hardware plugins. A plugin must expose initialization and shutdown behavior and identify its device. The virtual hardware layer provides deterministic devices for development and tests.

CL1 integration remains an adapter boundary. The project must not represent the simulator or compatibility API as the proprietary CL1 firmware.

## Python ↔ Rust contract

The intended integration is:

1. Python owns application state and user-facing workflows.
2. Python selects `python`, `rust`, or `auto` simulation backend.
3. Rust receives typed simulation requests and returns deterministic results.
4. MySQL stores durable metadata and event/metric records.
5. Python exports selected experiment data to `.xlsx` for analysis and sharing.

The next implementation stage is a PyO3/maturin adapter plus equivalence tests proving that the Python and Rust implementations produce the same reference results for the same inputs.
