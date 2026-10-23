# API Implementation Plan

## Phase 1 — Core contracts

Implement dependency-light Python contracts for anatomy, neurons, synapses, connectivity, dynamics, plasticity, simulation, experiments, and neural substrates.

## Phase 2 — Regional decomposition

Create region packages for:

- cerebral cortex
- hippocampus
- amygdala and limbic structures
- basal ganglia
- thalamus
- hypothalamus
- cerebellum
- brainstem
- spinal system
- sensory systems
- motor systems

Each package receives its own `__init__.py`, model modules, region documentation, tests, and UML diagram.

## Phase 3 — Signal pipeline

```text
External sensor
  -> acquisition
  -> calibration metadata
  -> artifact handling
  -> feature extraction
  -> neural event representation
  -> region mapper
  -> brain model
```

The reverse path is reserved for explicitly supported research stimulation interfaces and must remain separated from ordinary simulation.

## Phase 4 — Data and provenance

Every recording, model state, experiment, and generated dataset receives:

- unique identifier
- timestamp/time base
- source type
- anatomical mapping
- preprocessing version
- model version
- configuration hash
- provenance record
- quality flags

## Phase 5 — CL1 compatibility

Keep the existing CL1 modules as an adapter layer. The core brain model must not import a vendor-specific SDK directly. A CL1 adapter implements the generic `NeuralSubstrate` and recording/stimulation interfaces.

## Phase 6 — Whole-brain composition

Compose regional modules through the connectome and pathway APIs. Use multiscale approximations rather than pretending every neuron and synapse is available in real time.

## Phase 7 — Validation

For every algorithm and region:

1. unit tests
2. numerical sanity checks
3. parameter validation
4. reproducibility tests
5. benchmark against published reference behavior where appropriate
6. uncertainty and sensitivity analysis
7. provenance review

## Phase 8 — Hardware abstraction

Hardware drivers should be optional. The default test environment must run entirely in simulation or replay mode so the software remains testable without a physical neural-interface system.
