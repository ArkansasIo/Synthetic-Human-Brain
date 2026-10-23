# Synthetic Human Brain API Reference

This document defines the stable conceptual API surface for the whole-brain software architecture. Implementations may evolve, but the contracts below separate anatomy, neural dynamics, connectivity, experiments, and external neural substrates.

## 1. Anatomy API

**Purpose:** represent anatomical hierarchy and metadata.

Core types:
- `BrainRegion`
- `BrainArea`
- `Nucleus`
- `CorticalLayer`
- `AnatomicalCoordinate`
- `AnatomicalPathway`

Functions:
- register structure
- resolve parent/child relationships
- attach atlas labels
- map coordinates to regions
- expose region metadata

## 2. Neuron API

**Purpose:** model individual neuron dynamics without tying the API to one mathematical model.

Core types:
- `Neuron`
- `NeuronType`
- `MembraneState`
- `Dendrite`
- `Soma`
- `Axon`
- `SpikeEvent`

Functions:
- integrate membrane state
- inject current
- apply synaptic conductance
- detect threshold crossings
- reset/refractory handling
- emit spike events

## 3. Synapse API

**Purpose:** represent directed synaptic transmission and plasticity.

Core types:
- `Synapse`
- `ExcitatorySynapse`
- `InhibitorySynapse`
- `Neurotransmitter`
- `SynapticState`

Functions:
- transmit
- delay events
- update weight
- apply plasticity rule
- enforce weight bounds

## 4. Connectivity API

**Purpose:** represent the structural and functional connectome.

Core types:
- `Connectome`
- `Connection`
- `Projection`
- `NeuralPathway`
- `RoutingTable`

Functions:
- connect/disconnect
- query incoming/outgoing projections
- propagate spikes/events
- import/export connectivity
- attach confidence/provenance

## 5. Neural Dynamics API

**Purpose:** provide interchangeable mathematical models.

Supported families include LIF, AdEx, Izhikevich, Hodgkin-Huxley, conductance-based synapses, Wilson-Cowan population dynamics, Kuramoto oscillators, neural fields, and rate models.

Functions:
- `step(dt)`
- `reset()`
- `state()`
- `derivative()`
- `validate_parameters()`

## 6. Plasticity API

**Purpose:** represent activity-dependent adaptation.

Core rules:
- Hebbian learning
- Oja learning
- BCM
- STDP
- LTP/LTD abstractions
- homeostatic plasticity

Functions:
- `update(pre, post, dt)`
- `apply(weight)`
- `clamp(weight)`
- `adapt_homeostasis()`

## 7. Simulation API

**Purpose:** provide deterministic, inspectable execution.

Core types:
- `Simulation`
- `SimulationClock`
- `EventQueue`
- `Scheduler`
- `SimulationState`
- `SimulationConfig`

Pipeline:
1. ingest inputs
2. update neural state
3. detect events
4. propagate events
5. update synapses
6. apply plasticity
7. record state
8. advance clock

## 8. Sensory API

Subsystems:
- vision
- audition
- somatosensation
- olfaction
- gustation
- vestibular/proprioceptive inputs

Each subsystem exposes normalized sensory events and provenance metadata rather than pretending to reconstruct unavailable biological information.

## 9. Motor API

Core types:
- `MotorCommand`
- `MotorState`
- `Movement`
- `Reflex`
- `MotorFeedback`

The API separates neural motor intent from physical actuator control.

## 10. Cognition API

Research abstractions:
- attention
- working memory
- episodic memory
- semantic memory
- decision processes
- planning
- predictive processing
- executive control

These are computational models, not claims of reproducing human cognition or consciousness.

## 11. Experiment API

Core types:
- `Experiment`
- `Stimulus`
- `Recording`
- `Measurement`
- `Analysis`
- `Dataset`
- `Provenance`

Experiments must record configuration, random seed, model version, input provenance, output provenance, and analysis parameters.

## 12. Neural Substrate API

This is the boundary for simulated or biological neural systems.

```python
class NeuralSubstrate:
    def initialize(self): ...
    def stimulate(self, stimulus): ...
    def record(self): ...
    def synchronize(self, time): ...
    def step(self, dt): ...
    def reset(self): ...
    def shutdown(self): ...
```

Implementations can include:
- `SyntheticWholeBrain`
- `ReplayBackend`
- `CL1SimulatorBackend`
- `CL1BiologicalBackend` (integration boundary only)
- `ExternalResearchInterface`

## 13. Neural Interface API

For external, non-invasive-first interfaces:

- `SensorArray`
- `SignalChannel`
- `AcquisitionDevice`
- `AmplifierInterface`
- `DigitizerInterface`
- `SignalStream`
- `ArtifactFilter`
- `RegionMapper`
- `StimulationInterface`
- `SynchronizationInterface`

The software must preserve the distinction between raw measurements, processed signals, inferred neural events, and simulated states.

## 14. Brain-region API convention

Each region module should expose:

```text
Region
├── identity
├── anatomy metadata
├── inputs
├── outputs
├── state variables
├── local dynamics
├── plasticity hooks
├── pathways
├── recording mappings
├── experiment hooks
└── validation metadata
```

Initial region families:
- cortex
- hippocampus
- limbic system
- basal ganglia
- thalamus/hypothalamus
- cerebellum
- brainstem
- spinal system
- sensory systems
- motor systems

## 15. Safety and scientific boundary

The API is intentionally designed so that a real-world neural interface is a replaceable backend. It does not define clinical procedures, implant recipes, stimulation doses, surgical techniques, or medical-device approval. Such systems require appropriate expert, ethics, safety, and regulatory processes.
