# Phase 2 Model Architecture

Phase 2 separates the simulation engine into reusable computational abstractions.

## Components

- `NeuralNetwork`: directed weighted connectivity graph.
- `NeuronModel`: protocol for updating one abstract unit.
- `LeakyRateNeuron`: bounded leaky rate implementation.
- `SynapseModel`: protocol for transforming transmitted signals.
- `LinearSynapse`: weighted linear transmission implementation.
- `Simulation`: existing deterministic ring-network reference implementation.

## Design rule

Neuron and synapse models are intentionally independent of the existing simulation
loop. This permits future simulation backends to compose them without changing the
public model interfaces.

## Planned integration

1. Build a network-driven simulation backend.
2. Apply `SynapseModel` to each connection.
3. Aggregate incoming signals by target node.
4. Apply `NeuronModel` to each node.
5. Emit immutable snapshots.
6. Serialize experiment configuration and results.

## Scientific boundary

These abstractions are computational modeling primitives. They do not constitute a
human-brain simulation, a biological neuron model by default, or evidence of
cognition or consciousness. Biologically grounded models must document equations,
units, parameter provenance, validation datasets, and limitations.
