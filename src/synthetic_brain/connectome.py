"""Sparse connectome data structures and graph algorithms."""
from __future__ import annotations

from dataclasses import dataclass, field
from math import inf


@dataclass(frozen=True)
class ConnectomeEdge:
    source: str
    target: str
    weight: float = 1.0
    delay_ms: float = 1.0
    excitatory: bool = True

    def __post_init__(self) -> None:
        if self.delay_ms < 0:
            raise ValueError("delay_ms must be non-negative")


@dataclass
class Connectome:
    """Directed weighted graph suitable for region/population connectomes."""

    nodes: set[str] = field(default_factory=set)
    edges: list[ConnectomeEdge] = field(default_factory=list)

    def add_node(self, node: str) -> None:
        self.nodes.add(node)

    def add_edge(self, edge: ConnectomeEdge) -> None:
        self.nodes.update((edge.source, edge.target))
        self.edges.append(edge)

    def out_edges(self, node: str) -> tuple[ConnectomeEdge, ...]:
        return tuple(edge for edge in self.edges if edge.source == node)

    def in_edges(self, node: str) -> tuple[ConnectomeEdge, ...]:
        return tuple(edge for edge in self.edges if edge.target == node)

    def degree(self, node: str) -> tuple[int, int]:
        return len(self.in_edges(node)), len(self.out_edges(node))

    def weighted_out_strength(self, node: str) -> float:
        return sum(abs(edge.weight) for edge in self.out_edges(node))

    def shortest_path_delays(self, source: str) -> dict[str, float]:
        """Dijkstra shortest paths using conduction delay as edge cost."""
        if source not in self.nodes:
            raise KeyError(source)
        distances = {node: inf for node in self.nodes}
        distances[source] = 0.0
        visited: set[str] = set()
        while len(visited) < len(self.nodes):
            current = min((n for n in self.nodes if n not in visited), key=distances.get)
            if distances[current] == inf:
                break
            visited.add(current)
            for edge in self.out_edges(current):
                candidate = distances[current] + edge.delay_ms
                if candidate < distances[edge.target]:
                    distances[edge.target] = candidate
        return distances

    def validate(self) -> None:
        for edge in self.edges:
            if edge.source not in self.nodes or edge.target not in self.nodes:
                raise ValueError("edge references unknown node")


__all__ = ["Connectome", "ConnectomeEdge"]
