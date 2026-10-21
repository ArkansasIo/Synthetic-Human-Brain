# Architecture

## Scope

The project contains a discrete-time abstract rate-network example and a reusable network-driven simulation engine. These components demonstrate reproducibility, validation, weighted graph connectivity, model composition, and immutable snapshots. They are computational abstractions, not biological brain models.

## Components

- **SimulationConfig**: immutable configuration and validation.
- **Simulation**: reference ring-topology simulator.
- **SimulationSnapshot**: immutable state from the reference simulator.
- **NeuralNetwork**: directed weighted graph.
- **NeuronModel / LeakyRateNeuron**: protocol and default abstract unit dynamics.
- **SynapseModel / LinearSynapse**: protocol and default weighted signal transform.
- **NetworkSimulation**: composes graph, synapse transform, and neuron update model.
- **NetworkSimulationSnapshot**: immutable state from network-driven runs.
- **CLI**: runs the reference simulation.
- **Tests and CI**: check determinism, validation, graph behavior, model composition, and package quality.

## Network model

`NeuralNetwork` stores directed connections as `(source, target, weight)` records. The signal from a connection is transformed by the configured synapse model and added to its target's incoming signal:

```text
incoming[target] += synapse.transmit(activity[source], weight)
```

## Network simulation update rule

Every update is synchronous:

1. Capture the prior activity snapshot.
2. Compute all connection signals from that prior snapshot.
3. Sum signals by target unit.
4. Call each neuron model once with its prior activity, total incoming signal plus external input, and configured time step.
5. Publish the resulting state as an immutable snapshot.

This avoids an early unit update changing the input seen by a later unit during the same step. The engine verifies custom synapse and neuron outputs are finite numbers. The default `LeakyRateNeuron` clamps to its configured bounds; custom implementations own their own output-range semantics.

See [NETWORK_SIMULATION.md](NETWORK_SIMULATION.md) for a usage example.

## Reference ring simulation

The original `Simulation` remains a small ring-topology example. For each unit i:

```text
neighbor_i(t) = (activity_(i-1)(t) + activity_(i+1)(t)) / 2
activity_i(t+1) = clamp(decay * activity_i(t)
                       + (1-decay) * neighbor_i(t)
                       + time_step * external_input, 0, 1)
```

All neighbor values use the previous state and boundaries wrap in a ring.

## Determinism

Both engines initialize activity from a local pseudo-random generator controlled by the configured seed. Reproducibility should be checked by regression tests across supported Python/runtime versions.

## Future extension points

1. Experiment configuration files and persisted run metadata.
2. JSON/CSV output and a reproducible experiment runner.
3. Sparse connectivity and network serialization.
4. Numerical baselines and optional visualization.
5. Biologically grounded dynamics only with cited equations, units, parameter provenance, reference datasets, and quantitative validation.
