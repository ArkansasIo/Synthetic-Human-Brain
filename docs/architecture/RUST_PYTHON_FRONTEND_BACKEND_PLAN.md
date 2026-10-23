# Rust + Python + Frontend/Backend Architecture Plan

## Goal

Keep Python as the primary research/application layer while introducing Rust as an optional high-performance execution layer. The browser GUI, terminal, BrainScript, experiment orchestration, and scientific workflow remain Python-facing APIs.

## Runtime layers

```text
Browser GUI / IDE
        |
        v
Python Application API
  |     |       |
  |     |       +--> Auth / users / administrators
  |     +----------> BrainScript / experiments / data
  +----------------> Simulation orchestration
        |
        v
Rust Core (optional accelerator)
  |-- neuron kernels
  |-- synapse/network kernels
  |-- event queue / scheduler
  |-- vectorized state updates
  +-- telemetry
        |
        v
Python research models / NumPy / scientific backends
```

## Ownership boundaries

| Layer | Responsibility |
|---|---|
| Frontend | GUI, file tree, source editor, simulation controls, telemetry, auth screens |
| Python API | application services, authorization, experiments, BrainScript, persistence, orchestration |
| Rust core | deterministic numerical kernels and high-throughput simulation primitives |
| Database | users, roles, projects, experiments, runs, metadata, audit records |
| CL1 adapter | public compatibility boundary for connection, recording, stimulation, replay |

## Rust source layout

```text
rust/
├── Cargo.toml
└── src/
    ├── lib.rs
    ├── neuron.rs
    ├── network.rs
    └── telemetry.rs
```

The first Rust kernel is a deterministic LIF step. It is deliberately small so Python behavior can be validated against it before adding more kernels.

## Python integration phases

### Phase 1 — Stable contract

Define Python-side interfaces for Rust-backed kernels. A Python implementation remains available as the reference implementation.

### Phase 2 — FFI boundary

Use a mature Python/Rust interoperability layer such as PyO3/maturin when the repository is ready for compiled extensions. Keep the Python API stable so callers do not care whether a kernel is Python or Rust.

### Phase 3 — Kernel migration

Migrate in this order:

1. LIF and simple neuron stepping
2. conductance/synapse updates
3. STDP/STP kernels
4. event queues and network propagation
5. population/vectorized updates
6. telemetry counters
7. optional parallel execution

### Phase 4 — Application integration

The Python application chooses the backend:

```text
backend = "python"  # reference/debug
backend = "rust"    # accelerated
backend = "auto"    # Rust when installed, Python fallback
```

### Phase 5 — GUI integration

The GUI exposes backend state but does not contain numerical implementation details:

```text
Simulation → Backend: Python | Rust | Auto
Telemetry  → Engine: simulation time, events/s, spikes, queue depth
Inspector  → Kernel: parameters, version, provenance
```

## Safety and reproducibility rules

- Rust must not silently change scientific semantics.
- Python remains the reference behavior until cross-backend tests pass.
- Every migrated kernel gets deterministic regression vectors.
- Record backend name and Rust crate version in experiment metadata.
- Do not claim that a faster numerical kernel is more biologically accurate.
- Hardware/CL1 interfaces remain separate from the Rust simulation core.

## Proposed future folders

```text
src/synthetic_brain/
├── api/
│   ├── auth/
│   ├── users/
│   ├── admin/
│   └── ...
├── core/
├── models/
├── algorithms/
├── simulation/
├── experiments/
├── cl1/
└── brainscript/

rust/
├── src/
│   ├── neuron.rs
│   ├── synapse.rs
│   ├── plasticity.rs
│   ├── network.rs
│   ├── scheduler.rs
│   ├── telemetry.rs
│   └── ffi.rs
└── tests/

web/
├── index.html
├── app.js
├── styles.css
├── components/
├── pages/
└── editor/
```

## Recommended execution model

The application should start in Python. Python owns the lifecycle and experiment state. Rust is loaded only for computational kernels. The frontend communicates with the Python application API rather than directly calling Rust. This keeps authentication, authorization, auditing, source editing, database access, and research provenance in one application boundary.

## Initial milestone

The repository now contains the Rust crate scaffold and a tested LIF kernel. The next milestone is the Python adapter plus a Rust/Python equivalence test suite; only after that should the event scheduler and larger network kernels move into Rust.
