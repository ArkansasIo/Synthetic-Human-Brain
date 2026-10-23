# CL1 Software Clone

The repository now contains an independent **application-level CL1 clone** for local development. It is intentionally a software compatibility layer, not a clone of CL1 hardware, firmware, electrode electronics, cell culture, or biological behavior.

## Why a clone layer exists

Cortical Labs documents a Python API centered on `cl.open()`, `Neurons`, recordings, stimulation, and low-latency closed-loop loops. The official SDK Simulator is designed for application development and maintains API parity with the on-device API. citeturn1view0

This project adds a dependency-free research implementation so the Synthetic Human Brain codebase can exercise the same application concepts without requiring the official SDK.

## Modules

```text
src/synthetic_brain/
├── cl1.py              # optional official CL API bridge
├── cl1_simulator.py    # local simulator implementation
└── cl1_clone.py        # compact deterministic application API clone
```

## API surface

The clone currently provides:

- `open()` context manager
- `Neurons`
- `Spike`
- `Stim`
- `StimDesign`
- `BurstDesign`
- `ChannelSet`
- `DetectionResult`
- `Loop`
- `LoopTick`
- `Recording`
- deterministic seeded spike generation
- timestamped stimulation events
- closed-loop iteration
- recording of normalized events
- jitter-recovery API placeholder for application compatibility

The real CL API exposes recording, stimulation and closed-loop processing; its documented maximum loop frequency is 25 kHz. citeturn1view0

## Example

```python
from synthetic_brain.cl1_clone import ChannelSet, StimDesign, open

with open(channel_count=64, seed=42) as neurons:
    recording = neurons.record(experiment="baseline")

    neurons.stim(
        ChannelSet(0, 1),
        StimDesign(160, -1.0, 160, 1.0),
    )

    for tick in neurons.loop(1000, stop_after_ticks=10):
        for spike in tick.analysis.spikes:
            print(spike.timestamp, spike.channel)

    recording.stop()
```

## Simulation boundary

The clone generates synthetic spike events and schedules synthetic stimulation events. It does **not** model the living neural culture, electrode physics, CL1 signal-processing pipeline, or learning response of a biological network.

Cortical Labs explicitly describes its SDK Simulator as producing non-learning control data and recommends that simulator output be used for baseline controls rather than experimental biological conclusions. citeturn1view0

## Planned compatibility layers

```text
Layer 0  API objects
Layer 1  deterministic spike/stim engine
Layer 2  recording + replay
Layer 3  raw sample frames
Layer 4  custom simulator data sources
Layer 5  closed-loop controller runtime
Layer 6  CL1 analysis metrics
Layer 7  BrainLang experiment bindings
Layer 8  synthetic-vs-CL1 benchmark suite
```

The official simulator also supports random data, HDF5 recording replay, accelerated timing, and custom data sources. citeturn0search1

## Safety and scientific boundary

No physical-device stimulation is performed by this clone. It is a software development and research tool. Results from this simulator must remain clearly labeled as simulated data and must not be presented as evidence of biological equivalence, cognition, consciousness, or CL1 performance.
