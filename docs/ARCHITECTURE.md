# Architecture

## Scope

The starter uses a discrete-time, abstract rate-network model to demonstrate reproducibility, validation, state updates, and testing. It is deliberately not intended to simulate biological detail.

## Components

- **SimulationConfig**: immutable configuration and range checks.
- **Simulation**: owns activity state and advances exactly one step per call.
- **SimulationSnapshot**: immutable representation of model output.
- **CLI**: configures a small run and prints states.
- **Tests**: verify determinism, shape, bounds, and invalid-input handling.

## Update rule

For unit i with left and right neighbors:

`neighbor_i(t) = (activity_(i-1)(t) + activity_(i+1)(t)) / 2`

`activity_i(t+1) = clamp(decay * activity_i(t) + (1-decay) * neighbor_i(t) + time_step * external_input, 0, 1)`

All neighbor values come from the previous state, so updating one unit does not influence another unit within the same step. Boundary neighbors wrap around in a ring topology.

## Extension points

1. Add a graph-backed connectivity matrix.
2. Define explicit population and synapse interfaces.
3. Add experiment configuration files and persisted run metadata.
4. Add numerical baselines and regression tests.
5. Add visualization as an optional dependency.
6. Introduce biologically grounded dynamics only alongside citations, parameter provenance, and validation data.

## Determinism

Initial states use a local random generator seeded from configuration. The simulation does not rely on global random state. Reproducibility across future versions should be checked by explicit regression tests rather than assumed.
