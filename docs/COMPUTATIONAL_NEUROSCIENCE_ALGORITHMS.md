# Computational Neuroscience Algorithm Suite

## Scope

There is no scientifically established list of "all algorithms of the human brain". Human cognition emerges from biological mechanisms operating across molecular, cellular, circuit, systems, and whole-organ scales. The repository therefore implements a **research-backed algorithmic toolbox** rather than claiming to reproduce the human brain.

This approach follows the multiscale strategy used by major brain-simulation programs: models can range from differential-equation cellular models to population and whole-brain models, with different levels of detail and different validation targets.

## Research basis

- The Human Brain Project describes simulation across molecular, subcellular, cellular, network, and whole-brain levels and notes that full human-scale cellular simulation remains computationally infeasible at the biological level of detail. See: https://www.humanbrainproject.eu/en/brain-simulation/
- EBRAINS describes NESTML/PyNN workflows containing neuron and synaptic plasticity models and tools for cellular and circuit simulation. See: https://www.humanbrainproject.eu/en/science-development/focus-areas/simulations/
- Blue Brain documents detailed neuron, ion-channel, synapse, morphology, microcircuit, and connectome modeling. See: https://portal.bluebrain.epfl.ch/resources/models/
- Blue Brain reports a reconstruction workflow involving brain-region geometry, cell densities, morphology/electrical/genetic types, dendrites, axons, connectomes, synapses, and large-scale simulation. See: https://bluebrainproject.epfl.ch/bbp/research/domains/bluebrain/
- Published large-scale simulation work describes Hodgkin-Huxley cellular dynamics, compartment/cable models, and probabilistic Tsodyks-Markram synapses. See: https://www.alcf.anl.gov/science/projects/large-scale-simulation-brain-tissue-blue-brain-project-epfl

## Implemented algorithms

### Numerical methods

- Euler integration
- fourth-order Runge-Kutta integration
- finite-difference 1-D passive cable diffusion

### Cellular electrophysiology

- Leaky integrate-and-fire (LIF)
- Adaptive exponential integrate-and-fire (AdEx)
- Izhikevich spiking neuron
- Hodgkin-Huxley conductance-based neuron

### Synaptic dynamics

- exponential conductance synapse
- reversal-potential current calculation
- Tsodyks-Markram short-term facilitation/depression

### Long-term plasticity

- Hebbian learning
- Oja's normalized Hebbian rule
- BCM-style sliding-threshold plasticity
- pair-based STDP
- simple homeostatic rate adaptation

### Population/network dynamics

- Wilson-Cowan excitatory/inhibitory populations
- Kuramoto phase synchronization
- divisive normalization
- softmax competition

### Learning, memory, and inference primitives

- temporal-difference error and value update
- prediction-error update
- Hopfield Hebbian associative memory
- working-memory activity traces
- deterministic Poisson spike-train generation for experiments

## Architecture rule

Each algorithm is a pure or stateful, testable primitive. A future simulation backend can compose these models into:

```text
molecule/channel
      ↓
membrane + ion channels
      ↓
neuron + dendritic compartments
      ↓
synapse + plasticity
      ↓
local microcircuit
      ↓
brain region / population
      ↓
large-scale network / connectome
      ↓
sensory ↔ cognitive ↔ motor loops
      ↓
behavioral experiment
```

## What remains scientifically necessary

A serious human-brain model still requires experimentally constrained data and validation for:

1. region geometry and parcellation;
2. cell-type distributions and morphology;
3. ion-channel and receptor kinetics;
4. synapse distributions and receptor composition;
5. long-range structural connectivity;
6. neuromodulatory systems;
7. glial and metabolic processes;
8. sensory and motor pathways;
9. developmental and homeostatic processes;
10. learning and memory mechanisms;
11. population-scale dynamics;
12. human neuroimaging/physiology validation;
13. uncertainty quantification and parameter fitting;
14. reproducible benchmark tasks.

## Scientific boundary

These algorithms are models, not direct implementations of consciousness or a biological human mind. A model should only be described as biologically faithful at a particular scale when its parameters, equations, data provenance, and validation results support that claim.
