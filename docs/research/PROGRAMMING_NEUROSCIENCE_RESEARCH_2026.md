# Programming Research: Synthetic Brain and CL1

**Research snapshot:** 2026-10-23

## Purpose

This document records external research that should guide the Synthetic Human Brain software architecture. The project is a computational research platform; it is not a claim that software can reproduce a complete biological human brain or consciousness.

## 1. Multiscale brain simulation

The Human Brain Project / EBRAINS describes brain simulation as a multiscale problem spanning molecular and subcellular mechanisms, cellular models, network models, and whole-brain models. Whole-brain models commonly use population or mean-field representations connected by structural connectomes because simulating every biological neuron and synapse at full detail is substantially more demanding.

**Engineering implication:** Synthetic Human Brain should support multiple abstraction levels instead of forcing every subsystem into a single neuron-level simulator.

Recommended layers:

```text
molecular / receptor
        -> membrane / ion channel
        -> neuron / compartment
        -> synapse / plasticity
        -> population / microcircuit
        -> brain region
        -> structural connectome
        -> whole-brain network
        -> sensorimotor / cognitive experiment
```

## 2. Simulation engines and programming interfaces

### NEST

NEST focuses on the dynamics, size, and structure of spiking neural systems rather than detailed individual-cell morphology. Its current 2026 release is NEST 3.10.

**Use for this project:** large spiking-network reference behavior, regression benchmarks, network dynamics, synaptic plasticity, and simulator interoperability.

### NEURON / CoreNEURON

The EBRAINS simulation stack uses NEURON for detailed cellular and circuit modeling. CoreNEURON provides an execution path optimized for larger simulations and modern compute architectures.

**Use for this project:** biophysical neuron and multicompartment validation targets, not as the only simulation backend.

### Brian / Brian2

Brian is a Python-oriented simulator useful for defining spiking models directly from equations.

**Use for this project:** compact equation-level reference implementations and algorithm validation.

### Arbor

EBRAINS describes Arbor as a high-performance library for morphologically detailed multicompartment simulations, with C++ and Python interfaces and CPU/GPU-oriented execution.

**Use for this project:** future morphology and high-performance backend adapter.

### PyNN

PyNN provides a simulator-independent Python API for spiking networks and can target multiple simulators and neuromorphic systems.

**Use for this project:** define a stable simulator-neutral network API so Synthetic Human Brain can compare backends without rewriting experiment definitions.

### The Virtual Brain (TVB)

TVB is an open-source platform for personalized brain network models, including whole-brain population dynamics driven by structural connectivity.

**Use for this project:** whole-brain population-level modeling and connectome-driven dynamics.

## 3. CL1 programming research

Cortical Labs publicly documents a Python CL API for CL1. The public API documentation includes connection management, spike detection/reactive loops, recording, data streams, raw-data access, and stimulation examples. The public GitHub organization also exposes `cl-sdk`, described as a CL API simulator.

**Architecture rule:** use the public API surface as the compatibility boundary. Do not copy proprietary firmware, private implementation, or unpublished biological-control details.

Recommended project boundary:

```text
Synthetic Brain model
        |
        v
CL1 adapter / compatibility API
        |
        +---- local deterministic simulator
        |
        +---- recording/replay backend
        |
        +---- public CL SDK/API integration
        |
        +---- controlled experimental backend
```

The local CL1 simulator must remain explicitly labeled as a software-development and testing simulator, not as a biological replacement for CL1.

## 4. Closed-loop programming model

The public CL API research emphasizes low-latency closed-loop experiment design. Synthetic Human Brain should therefore treat closed-loop experiments as first-class objects:

1. configure experiment;
2. connect to backend;
3. stimulate or provide input;
4. receive spikes/events;
5. perform deterministic analysis;
6. update control policy;
7. record all inputs, outputs, timestamps, parameters, and software versions;
8. replay the experiment offline.

Every closed-loop backend should implement the same project-owned protocol so tests can run against the simulator before any hardware experiment.

## 5. Data and reproducibility requirements

The research architecture should standardize:

- experiment identifiers;
- model/version identifiers;
- parameter manifests;
- random seeds;
- simulator/backend version;
- sampling rate and clock information;
- spike/event records;
- stimulation records;
- derived metrics;
- provenance and source citations;
- deterministic replay where possible;
- uncertainty and validation metadata.

Neural recordings and model data should be kept separate from executable code. The repository's `data/`, `experiments/`, and database layers should expose versioned schemas rather than embedding large datasets in Python modules.

## 6. Research algorithms to prioritize

### Cellular

- LIF
- AdEx
- Izhikevich
- Hodgkin-Huxley
- multicompartment cable equations
- ion-channel kinetics

### Synaptic

- conductance-based synapses
- short-term facilitation/depression
- STDP
- Hebbian/Oja/BCM plasticity
- homeostatic plasticity

### Network

- Wilson-Cowan
- balanced spiking networks
- oscillatory/phase models
- attractor networks
- recurrent predictive dynamics
- structural-connectome propagation

### Learning and cognition

- reinforcement-learning prediction errors
- temporal-difference learning
- associative memory
- working-memory traces
- attention/gating abstractions
- decision dynamics

### Analysis

- firing rate
- ISI and CV
- burst detection
- synchrony/coherence
- population activity
- dimensionality reduction
- stimulus-response latency
- decoding/classification

## 7. Large-scale simulation direction

A September 2026 arXiv preprint, CerebroSim, reports a whole-brain-scale spiking simulation approach using delay-aware spike communication, race-free synaptic dynamics, and compressed sparse synapse storage on a large supercomputer. This is relevant as an architectural research direction, not as a drop-in implementation requirement.

**Engineering implication:** future Synthetic Human Brain simulation should separate model semantics from execution. Sparse connectivity, event queues, delay handling, partitioning, deterministic replay, and memory-efficient synapse representations should be independent modules.

## 8. Recommended repository architecture

```text
src/synthetic_brain/
  core/                  # shared protocols and identifiers
  models/                # neuron, synapse, morphology, receptor models
  algorithms/            # reusable mathematical/neural algorithms
  connectivity/          # graphs, connectomes, projections
  simulation/            # clocks, events, schedulers, engines
  regions/               # anatomical/system-level modules
  cognition/             # memory, attention, decision, learning
  neuromodulation/       # reward/modulator abstractions
  cl1/                   # CL1 adapters, simulator, recording, analysis
  brainscript/           # language frontend/runtime/compiler
  experiments/           # experiment definitions and protocols
  data/                  # schemas and data access
  config/                # configuration models
```

Compatibility shims may remain temporarily at the old import paths during migration. The implementation of each subsystem should live in its new package, and the shims should contain no independent business logic.

## 9. Validation hierarchy

```text
unit equations
    -> algorithm regression tests
    -> deterministic simulator tests
    -> cross-backend comparison
    -> replay of recorded data
    -> controlled biological experiment
    -> independent validation
```

A successful software test does not establish biological validity. Claims about biological fidelity must identify the scale, source data, parameters, and validation evidence.

## Sources

- Human Brain Project / EBRAINS simulation overview: https://www.humanbrainproject.eu/en/science-development/focus-areas/simulations/
- Human Brain Project brain simulation overview: https://www.humanbrainproject.eu/en/brain-simulation/
- NEST Simulator: https://nest-simulator.org/
- Cortical Labs public CL API reference: https://docs.corticallabs.com/cl
- Cortical Labs public CL API documentation repository: https://github.com/Cortical-Labs/cl-api-doc
- Cortical Labs public GitHub organization and SDK repository: https://github.com/Cortical-Labs
- CerebroSim preprint: https://arxiv.org/abs/2609.27482

## Scientific boundary

This research supports a programmable synthetic-neuroscience platform. It does not establish that the resulting software is a human brain, has consciousness, or is biologically equivalent to CL1 neural cultures. Those are separate scientific claims requiring evidence beyond software architecture or simulation performance.
