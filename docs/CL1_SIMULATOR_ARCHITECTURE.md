# CL1 Simulator Architecture

This layer implements an application-level software compatibility target for CL1-style experiments. It does not reproduce CL1 electronics, firmware, electrode physics, living neural cultures, or biological learning.

## Components

```text
cl1_clone.py
    API objects, deterministic events, closed loop
          |
cl1_data_source.py
    random / reactive / model sources
          |
cl1_recording.py
    portable recording + replay
          |
cl1_analysis.py
    firing statistics / bursts / entropy / connectivity
          |
cl1_experiment.py
    repeatable experiment orchestration
          |
cl1_benchmark.py
    performance and reproducibility measurements
```

## Data flow

1. An experiment creates a `Neurons` instance.
2. A simulator data source produces timestamped frames and/or spikes.
3. Stimulation events are delivered to the source.
4. The closed-loop controller consumes normalized spike/stim events.
5. Recordings can be persisted to the repository's portable JSON format.
6. Replay feeds the same analysis pipeline without a live source.

Cortical Labs documents the SDK Simulator as a pluggable data-source architecture with pull and live/push sources. Its documented sample rate is currently 25 kHz. citeturn0view0

## Analysis

The local toolkit intentionally mirrors analysis categories exposed by the official analysis package: firing statistics, network bursts, information entropy, functional connectivity, and related event-level measurements. citeturn0view1

## Reproducibility

Every synthetic source can use a deterministic seed. Recordings include metadata and explicit format identifiers. Benchmarks report the simulated frame count, spike count, mean firing rate, and wall-clock execution time.

## Hardware boundary

The local clone never opens a physical CL1 by itself. `synthetic_brain.cl1.CL1Bridge` is a separate optional adapter for environments where the official `cl` package is intentionally installed. Any physical-device experiment must use its own hardware controls, safety procedures, approvals, and validated stimulation protocol.
