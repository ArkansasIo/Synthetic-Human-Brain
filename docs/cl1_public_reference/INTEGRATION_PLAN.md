# CL1 Integration Plan

## Phase 1 — Public API compatibility

Implement project-owned abstractions for sessions, neural channels, spikes, recordings, data streams, stimulation commands, and closed-loop scheduling.

## Phase 2 — Backend selection

Expose one BrainScript experiment interface with interchangeable backends:

```text
synthetic
cl1_simulator
cl1_replay
cl1
```

## Phase 3 — Data normalization

Normalize all backends into common events:

```text
SpikeEvent
StimulusEvent
RecordingFrame
LoopTick
BackendMetadata
```

## Phase 4 — Brain model integration

Connect normalized events to:

```text
sensory input
    -> thalamic gateway
    -> cortical regions
    -> hippocampal/memory systems
    -> basal-ganglia action selection
    -> motor output
```

## Phase 5 — GUI/API

Expose backend state through the Synthetic Human Brain GUI/API:

- backend selector
- connection state
- spike-rate graphs
- raster view
- channel activity
- recording controls
- experiment controls
- provenance panel
- model-vs-biological comparison panel

## Phase 6 — Validation

Run the same experiment against synthetic, replay, simulator, and—where authorized and supported—real CL1 environments. Report differences rather than treating any backend as ground truth.

## Boundary

Real CL1 use requires the official SDK, compatible hardware, applicable documentation, and appropriate experimental authorization. The repository's clone and simulator remain software-only research targets.
