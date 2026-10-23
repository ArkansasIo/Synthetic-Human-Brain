# Cortical Labs CL1 Integration

The Synthetic Human Brain project now has an optional integration boundary for the Cortical Labs CL1 platform.

## Why CL1 belongs in this project

The CL1 is a biological-neural-computing platform rather than a conventional artificial-neural-network accelerator. Cortical Labs documents a Python CL API for recording neural activity, delivering stimulation, and running real-time closed-loop algorithms. The same API has a local SDK Simulator intended to preserve application-level interface compatibility. citeturn0search0turn0search1

This repository therefore treats CL1 as an **experimental biological-neural backend** alongside the synthetic simulator. It is not treated as evidence that the software reproduces a human brain.

## Architecture

```text
Synthetic Human Brain
        |
        +-- BrainLang / experiment definitions
        |
        +-- Cellular models
        |     +-- LIF / AdEx / Izhikevich / Hodgkin-Huxley
        |     +-- synapses / plasticity
        |
        +-- Network + region models
        |
        +-- Experiment controller
        |
        +-- CL1Bridge  <---- optional boundary ---->  Cortical Labs CL API
        |                                             |
        |                                             +-- spikes
        |                                             +-- stimulation events
        |                                             +-- recordings
        |                                             +-- closed-loop ticks
        |
        +-- Analysis / metrics / provenance
```

## Software boundary

`synthetic_brain.cl1` intentionally uses lazy import of the optional `cl` package. The main project can therefore run without CL1 hardware or the SDK.

The adapter normalizes the device event model into three small types:

- `CL1Spike(timestamp, channel)`
- `CL1Stimulus(timestamp, channel, metadata)`
- `CL1Tick(iteration, timestamp, spikes, stims)`

`CL1Bridge.closed_loop()` converts CL API loop ticks into these project-level events so a controller can consume them without depending on the concrete CL SDK object model.

## Example

```python
from synthetic_brain import CL1Bridge

with CL1Bridge.open() as cl1:
    def controller(tick):
        for spike in tick.spikes:
            print(spike.timestamp, spike.channel)

    cl1.closed_loop(
        1000,
        stop_after_seconds=5,
        on_tick=controller,
    )
```

The bridge does not choose stimulation amplitudes, pulse widths, channels, or experimental protocols. Those are supplied explicitly by the caller and must follow the hardware documentation, experimental protocol, and applicable institutional requirements. Cortical Labs documents current-based stimulation, channel selection, pulse design, burst design, and device-side limits in its API reference. citeturn0search0turn0search1

## Closed-loop design

A CL1 experiment should be modeled as:

1. **Observe** — acquire spikes, stimulation events, and optionally electrode frames.
2. **Decode** — compute rates, synchrony, entropy, population state, or task-specific features.
3. **Estimate** — update a latent state, prediction error, reward signal, or controller state.
4. **Decide** — select an experiment action using deterministic, rule-based, RL, or model-based logic.
5. **Act** — issue an explicitly configured stimulation operation when the experimental protocol permits it.
6. **Record** — persist raw/processed observations, parameters, software revision, and outcomes.
7. **Validate** — compare biological observations with synthetic models and predefined controls.

Cortical Labs documents a tightly timed `Neurons.loop()` interface, spike/stim analysis per tick, recording support, and jitter detection/recovery. The API documentation states a maximum loop frequency of 25 kHz and describes deadline enforcement for real-time loop bodies. citeturn0search0turn0search1

## Simulator strategy

The CL SDK Simulator can be used as a software-integration target. Cortical Labs documents simulator sources based on generated data, recording replay, and custom data sources. Custom sources can represent models, hardware streams, or test fixtures. The simulator itself should not be interpreted as a learning biological model. citeturn0search0turn0search2

For this project, the preferred testing hierarchy is:

```text
unit tests
   -> synthetic neural simulation
      -> CL SDK Simulator / replay
         -> controlled CL1 experiment
            -> independently validated biological result
```

## Research data model

Each CL1 experiment should record at least:

- project and experiment identifier
- software version / Git commit
- model configuration
- random seed where applicable
- CL1 system and cell-batch identifiers when available
- sampling and timing metadata
- stimulation configuration
- raw or derived neural data
- analysis version
- predefined outcome metrics
- control condition
- deviations and failures

Cortical Labs' recording API exposes system metadata and recording metadata including project, system, cell-batch, sampling, duration, timestamps, and software provenance fields. citeturn0search1

## Research questions enabled by the integration

The CL1 boundary supports experiments such as:

### 1. Synthetic-to-biological model comparison

Compare firing-rate distributions, inter-spike interval statistics, synchrony, entropy, response latency, and adaptation between a synthetic model and biological recordings.

### 2. Closed-loop prediction

Use the synthetic controller to predict an upcoming population state, then evaluate prediction error against recorded CL1 activity.

### 3. Plasticity-response characterization

Estimate how repeated input/output relationships change over an experiment without assuming that a particular textbook plasticity rule is the biological ground truth.

### 4. Controller robustness

Test whether a controller remains stable under missing spikes, jitter, dropped frames, replayed recordings, and distribution shifts.

### 5. Model fitting

Fit parameters of candidate synthetic neuron/network models to observed CL1 statistics and report uncertainty rather than a single overconfident parameter set.

## Scientific boundary

CL1 integration does **not** establish consciousness, human-like cognition, sentience, memory equivalence, or biological equivalence to a human brain. A biological neural culture and a computational model operate at different levels of description. The correct objective is controlled measurement, modeling, prediction, and falsifiable comparison.

## Next implementation layers

1. Add a `CL1DataSource` compatible with the repository's experiment interface.
2. Add HDF5 recording ingestion and event normalization.
3. Add CL1-specific feature extraction adapters.
4. Add experiment manifests and provenance schemas.
5. Add synthetic-vs-CL1 benchmark reports.
6. Add BrainLang commands for `record`, `stimulus`, `emit`, and `step` backed by an explicit experiment context.
7. Add replay-driven regression tests using non-sensitive fixture data.
