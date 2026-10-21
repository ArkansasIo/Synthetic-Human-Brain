"""Graph-based connectivity primitives for the research simulator."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Connection:
    """Directed weighted connection between two abstract units."""

    source: int
    target: int
    weight: float


class NeuralNetwork:
    """Small directed weighted graph used by future simulation models."""

    def __init__(self, neuron_count: int) -> None:
        if isinstance(neuron_count, bool) or not isinstance(neuron_count, int):
            raise TypeError("neuron_count must be an integer")
        if neuron_count < 1:
            raise ValueError("neuron_count must be at least 1")
        self.neuron_count = neuron_count
        self._connections: list[Connection] = []

    @property
    def connections(self) -> tuple[Connection, ...]:
        """Return immutable connection state."""
        return tuple(self._connections)

    def connect(self, source: int, target: int, weight: float = 1.0) -> Connection:
        """Add a directed connection after validating node indices."""
        self._validate_node(source)
        self._validate_node(target)
        if not isinstance(weight, (int, float)) or isinstance(weight, bool):
            raise TypeError("weight must be a number")
        connection = Connection(source, target, float(weight))
        self._connections.append(connection)
        return connection

    def incoming_signal(self, activity: tuple[float, ...]) -> tuple[float, ...]:
        """Calculate weighted incoming signal without mutating the network."""
        if len(activity) != self.neuron_count:
            raise ValueError("activity length must equal neuron_count")
        result = [0.0] * self.neuron_count
        for connection in self._connections:
            result[connection.target] += activity[connection.source] * connection.weight
        return tuple(result)

    def _validate_node(self, node: int) -> None:
        if isinstance(node, bool) or not isinstance(node, int) or not 0 <= node < self.neuron_count:
            raise ValueError("node index is outside the network")
