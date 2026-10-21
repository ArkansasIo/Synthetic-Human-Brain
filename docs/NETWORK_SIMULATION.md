# Network-driven simulation

The project includes a graph-driven simulator that composes `NeuralNetwork` connectivity with `NeuronModel` and `SynapseModel` interfaces.

## Example

```python
from synthetic_brain import (
    NeuralNetwork,
    NetworkSimulation,
    SimulationConfig,
)

network = NeuralNetwork(neuron_count=3)
network.connect(0, 1, weight=0.8)
network.connect(1, 2, weight=0.5)
network.connect(2, 0, weight=-0.2)

simulation = NetworkSimulation(
    network,
    SimulationConfig(neuron_count=3, seed=42),
)

print(simulation.snapshot())
for _ in range(10):
    print(simulation.step(external_input=0.05))
```

## Update semantics

Each step first computes every weighted connection's signal using the prior
activity snapshot. Signals are summed per target. Each neuron model is then
called once with its prior activity, aggregated incoming signal plus external
input, and configured time step. The resulting values form the next snapshot.
This synchronous update avoids iteration-order-dependent propagation.

## Model contracts and validation

- `NeuronModel.update(activity, input_signal, time_step)` returns the next unit activity.
- `SynapseModel.transmit(signal, weight)` returns a connection signal.
- Custom model outputs must be finite numeric values.
- Network size must match `SimulationConfig.neuron_count`.
- A seeded local random generator creates the initial state.

The default leaky-rate unit clamps activity to [0, 1]. A custom neuron model may
use a different range; its outputs are validated for finiteness but are not
automatically clamped by the engine.

This remains an abstract computational system. It is not a validated model of
human neurophysiology and does not support clinical or consciousness claims.
