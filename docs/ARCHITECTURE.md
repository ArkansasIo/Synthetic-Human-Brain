# Architecture

## Scope

The project currently contains a discrete-time abstract rate-network model plus reusable weighted graph connectivity primitives. The starter model demonstrates reproducibility, validation, state updates, and testing. It is deliberately not intended to simulate biological detail.

## Components

- **SimulationConfig**: immutable configuration and range checks.
- **Simulation**: owns activity state and advances exactly one step per call.
- **SimulationSnapshot**: immutable representation of model output.
- **NeuralNetwork**: directed weighted connectivity graph with non-mutating signal calculation.
- **CLI**: configures a small run and prints states.
- **Tests**: verify determinism, shape, bounds, graph behavior, and invalid input handling.

## Network model

`NeuralNetwork` stores connections as `(source, target, weight)` records. Incoming signal is calculated as:

`signal[target] += activity[source] * weight`

The graph is intentionally independent from `Simulation` at this stage. This keeps the current ring-network example stable while providing a clean seam for future configurable-connectivity models.

## Current simulation update rule

For unit i with left and right neighbors:

`neighbor_i(t) = (activity_(i-1)(t) + activity_(i+1)(t)) / 2`

`activity_i(t+1) = clamp(decay * activity_i(t) + (1-decay) * neighbor_i(t) + time_step * external_input, 0, 1)`

All neighbor values come from the previous state, so updating one unit does not influence another unit within the same step. Boundary neighbors wrap around in a ring topology.

## Extension points

1. Connect `NeuralNetwork` to a configurable simulation backend.
2. Define explicit population and synapse interfaces.
3. Add experiment configuration files and persisted run metadata.
4. Add numerical baselines and regression tests.
5. Add visualization as an optional dependency.
6. Introduce biologically grounded dynamics only alongside citations, parameter provenance, units, and validation data.

## Determinism

Initial states use a local random generator seeded from configuration. The simulation does not rely on global random state. Reproducibility across future versions should be checked by explicit regression tests rather than assumed.
