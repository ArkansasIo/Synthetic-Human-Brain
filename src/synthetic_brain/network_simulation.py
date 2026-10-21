"""Network-driven deterministic simulation engine.

This engine composes a weighted connectivity graph with pluggable neuron and
synapse models. It is an abstract software model, not a biological brain model.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass

from synthetic_brain.config import SimulationConfig
from synthetic_brain.network import NeuralNetwork
from synthetic_brain.neuron import LeakyRateNeuron, NeuronModel
from synthetic_brain.synapse import LinearSynapse, SynapseModel


@dataclass(frozen=True, slots=True)
class NetworkSimulationSnapshot:
    """Immutable state captured after a network-simulation step."""

    step: int
    activity: tuple[float, ...]


class NetworkSimulation:
    """Update a directed network synchronously from its previous state.

    For every simulation step, incoming activity is computed from the previous
    snapshot. Each unit then updates exactly once, preventing iteration order
    from affecting the result. Model instances may be supplied to customize
    abstract dynamics; defaults provide a bounded leaky-rate unit and linear
    weighted synapses.
    """

    def __init__(
        self,
        network: NeuralNetwork,
        config: SimulationConfig | None = None,
        *,
        neuron_model: NeuronModel | None = None,
        synapse_model: SynapseModel | None = None,
    ) -> None:
        if not isinstance(network, NeuralNetwork):
            raise TypeError("network must be a NeuralNetwork")
        self.config = config or SimulationConfig(neuron_count=network.neuron_count)
        if self.config.neuron_count != network.neuron_count:
            raise ValueError("config.neuron_count must match network.neuron_count")

        self.network = network
        self.neuron_model = neuron_model or LeakyRateNeuron(decay=self.config.decay)
        self.synapse_model = synapse_model or LinearSynapse()
        rng = random.Random(self.config.seed)
        self._activity = [rng.random() for _ in range(network.neuron_count)]
        self._step = 0

    @property
    def step_count(self) -> int:
        """Number of completed simulation steps."""
        return self._step

    def snapshot(self) -> NetworkSimulationSnapshot:
        """Return immutable current model state."""
        return NetworkSimulationSnapshot(self._step, tuple(self._activity))

    def step(self, external_input: float = 0.0) -> NetworkSimulationSnapshot:
        """Advance one synchronous step, applying the same input to each unit."""
        if isinstance(external_input, bool) or not isinstance(external_input, (int, float)):
            raise TypeError("external_input must be a finite number")
        try:
            input_value = float(external_input)
        except OverflowError as exc:
            raise ValueError("external_input must be a finite number") from exc
        if not math.isfinite(input_value):
            raise ValueError("external_input must be a finite number")

        previous = tuple(self._activity)
        next_activity: list[float] = []
        incoming = [0.0] * self.network.neuron_count
        for connection in self.network.connections:
            signal = self.synapse_model.transmit(
                previous[connection.source], connection.weight
            )
            if isinstance(signal, bool) or not isinstance(signal, (int, float)):
                raise TypeError("synapse output must be a finite number")
            signal = float(signal)
            if not math.isfinite(signal):
                raise ValueError("synapse output must be a finite number")
            incoming[connection.target] += signal

        for index, activity in enumerate(previous):
            total_input = incoming[index] + input_value
            updated = self.neuron_model.update(
                activity, total_input, self.config.time_step
            )
            if isinstance(updated, bool) or not isinstance(updated, (int, float)):
                raise TypeError("neuron output must be a finite number")
            updated = float(updated)
            if not math.isfinite(updated):
                raise ValueError("neuron output must be a finite number")
            next_activity.append(updated)

        self._activity = next_activity
        self._step += 1
        return self.snapshot()
