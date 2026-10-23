# Synthetic Human Brain Browser/IDE UI

## Purpose

The Synthetic Human Brain UI is designed as a browser-style scientific IDE. It exposes each API and brain subsystem through tabs, nested navigation, panels, telemetry views, graph editors, experiment controls, and data inspectors.

This is a software research interface. Brain regions are engineering modules and are not claims of biological equivalence.

## Global shell

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ SHB │ File Edit View Brain Simulation Experiments Data Tools Help   ● RUN   │
├──────────────────────────────────────────────────────────────────────────────┤
│ ← → ⟳ │ Search / Command Palette... │ Cortex ▾ │ + │                      │
├──────────────┬───────────────────────────────────────────────────────────────┤
│ WORKSPACE    │ [Overview] [Cortex] [Hippocampus] [Basal Ganglia] [CL1] [+]│
│              ├───────────────────────────────────────────────────────────────┤
│ Brain        │                                                               │
│  ├ Cortex    │  ┌───────────────┐ ┌──────────────────┐ ┌────────────────┐ │
│  │ Frontal   │  │ REGION STATE  │ │ ACTIVITY GRAPH   │ │ TELEMETRY      │ │
│  │ Parietal  │  │ population    │ │ spikes / rate   │ │ CPU / memory   │ │
│  │ Temporal  │  │ membrane      │ │ synchrony       │ │ events/sec     │ │
│  │ Occipital │  │ plasticity    │ │ spectral power  │ │ latency        │ │
│  ├ Hippocampus│ └───────────────┘ └──────────────────┘ └────────────────┘ │
│  ├ Thalamus  │                                                               │
│  ├ Cerebellum│  ┌───────────────────────┐ ┌──────────────────────────────┐ │
│  ├ Brainstem │  │ CONNECTOME / GRAPH    │ │ INSPECTOR                    │ │
│  └ Spinal    │  │ nodes + projections   │ │ selected node / synapse      │ │
│              │  │ weights + delays      │ │ parameters / history         │ │
│ Algorithms   │  └───────────────────────┘ └──────────────────────────────┘ │
│ Simulation   │                                                               │
│ CL1          │  [Stimulate] [Record] [Pause] [Step] [Replay] [Export]      │
│ BrainScript  │                                                               │
│ Data         │                                                               │
└──────────────┴───────────────────────────────────────────────────────────────┘
```

## Top navigation

- **File:** new project, open model, import/export, recent experiments.
- **Edit:** undo, redo, duplicate, preferences.
- **View:** panels, layout presets, fullscreen, telemetry, logs.
- **Brain:** anatomy, regions, populations, connectome, cognition, neuromodulation.
- **Simulation:** start, pause, single-step, reset, scheduler, clock, events.
- **Experiments:** protocols, stimuli, recordings, replay, analysis.
- **Data:** datasets, schemas, provenance, database browser.
- **Tools:** algorithm catalog, parameter fitting, validation, benchmarks.
- **Help:** documentation, API reference, scientific boundaries.

## Browser tabs

Each major subsystem gets a persistent tab. Tabs can contain nested sub-tabs.

### Brain tab

Sub-tabs:

1. Overview
2. Anatomy
3. Connectome
4. Regions
5. Populations
6. Neurons
7. Synapses
8. Plasticity
9. Neuromodulation
10. Cognition
11. Sensory
12. Motor

### Region tab

Every region follows the same panel contract:

- Overview
- Model
- Neurons
- Populations
- Connectivity
- Dynamics
- Plasticity
- Inputs
- Outputs
- State
- Metrics
- Experiments
- CL1 Mapping
- Tests

### Algorithms tab

- Neuron models
- Synaptic models
- Plasticity
- Learning
- Network dynamics
- Signal processing
- Numerical methods
- Validation benchmarks

### Simulation tab

- Engine
- Clock
- Scheduler
- Event queue
- Network state
- Performance
- Replay
- Logs

### CL1 tab

- Connection
- Channels
- Spike stream
- Stimulation
- Recording
- Closed loop
- Analysis
- Replay
- Simulator
- Experiment history

The CL1 screen must distinguish simulator data from controlled experimental data.

### BrainScript tab

- Editor
- Syntax tree
- Compiler
- Runtime
- Variables
- Populations
- Connections
- Step/clock
- Console
- Diagnostics

## Reusable inner-panel contract

Each API section should expose the same UI primitives where applicable:

```text
Header
├── status badge
├── version/model identifier
├── start/stop/reset controls
└── context menu

Navigation
├── tabs
├── dropdown filters
└── command palette

Visualization
├── line chart
├── raster/spike plot
├── histogram
├── spectrogram
├── network graph
└── state timeline

Inspector
├── parameters
├── current state
├── provenance
└── history

Actions
├── stimulate
├── record
├── step
├── replay
├── export
└── validate

Diagnostics
├── event log
├── warnings
├── errors
└── performance telemetry
```

## Brain-region navigation map

```text
Brain
├── Cerebral Cortex
│   ├── Frontal
│   ├── Parietal
│   ├── Temporal
│   ├── Occipital
│   └── Insula
├── Hippocampus
│   ├── Entorhinal
│   ├── Dentate Gyrus
│   ├── CA3
│   ├── CA2
│   ├── CA1
│   └── Subiculum
├── Limbic
│   ├── Amygdala
│   ├── Mammillary Bodies
│   └── Fornix
├── Basal Ganglia
│   ├── Caudate
│   ├── Putamen
│   ├── Globus Pallidus
│   ├── Subthalamic Nucleus
│   └── Substantia Nigra
├── Diencephalon
│   ├── Thalamus
│   ├── Hypothalamus
│   └── Pituitary
├── Cerebellum
│   ├── Cortex
│   └── Deep Nuclei
├── Brainstem
│   ├── Midbrain
│   ├── Pons
│   └── Medulla
├── Spinal
│   ├── Spinal Cord
│   └── Reflex
├── Sensory
│   ├── Vision
│   ├── Auditory
│   ├── Somatosensory
│   ├── Olfactory
│   └── Gustatory
└── Motor
    ├── Motor System
    ├── Corticospinal
    └── Autonomic
```

## Telemetry

Telemetry panels should expose software-measured values such as simulation time, wall-clock time, event throughput, queue depth, spike count, firing rate, synchronization measures, memory use, CPU/GPU utilization where available, and backend latency.

Biological measurements must retain their acquisition metadata and must never be silently presented as simulator measurements.

## UI data/API boundary

The UI should consume typed API resources rather than importing simulator internals directly:

```text
Browser UI
   ↓
UI service/API client
   ↓
Synthetic Brain API
   ├── Anatomy API
   ├── Neuron API
   ├── Synapse API
   ├── Connectivity API
   ├── Dynamics API
   ├── Plasticity API
   ├── Simulation API
   ├── Cognition API
   ├── CL1 API
   ├── BrainScript API
   ├── Experiment API
   └── Data/Telemetry API
```

## Design requirements

- Responsive browser layout.
- Dark scientific/IDE presentation with accessible contrast.
- Keyboard shortcuts and command palette.
- Dockable/resizable panels.
- Persistent workspace layouts.
- Search across regions, APIs, experiments, parameters, and logs.
- Explicit simulator-versus-hardware data labels.
- Reproducibility metadata visible from every experiment.
- No UI language implying that the software is a conscious human mind.

## Initial implementation phases

1. Browser shell and global navigation.
2. Region tabs and reusable panel framework.
3. Telemetry and graph panels.
4. Connectome/graph inspector.
5. Simulation controls and event timeline.
6. CL1 simulator and public API views.
7. BrainScript IDE.
8. Experiment/replay workspace.
9. Data/provenance browser.
10. Validation and benchmark dashboards.
