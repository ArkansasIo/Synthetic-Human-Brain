"""Brain-region and mesoscale connectivity primitives."""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from enum import Enum


class BrainRegion(str, Enum):
    CEREBRAL_CORTEX = "cerebral_cortex"
    HIPPOCAMPUS = "hippocampus"
    THALAMUS = "thalamus"
    CEREBELLUM = "cerebellum"
    BASAL_GANGLIA = "basal_ganglia"
    BRAINSTEM = "brainstem"
    HYPOTHALAMUS = "hypothalamus"
    AMYGDALA = "amygdala"
    OLFACTORY_BULB = "olfactory_bulb"
    SPINAL_CORD = "spinal_cord"


@dataclass
class NeuralPopulation:
    name: str
    size: int
    model: str = "LIF"
    region: BrainRegion = BrainRegion.CEREBRAL_CORTEX
    metadata: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.size < 1:
            raise ValueError("population size must be positive")


@dataclass(frozen=True)
class RegionConnection:
    source: str
    target: str
    probability: float
    weight: float = 1.0
    delay_ms: float = 1.0
    excitatory: bool = True

    def __post_init__(self) -> None:
        if not 0.0 <= self.probability <= 1.0:
            raise ValueError("probability must be in [0, 1]")
        if self.delay_ms < 0:
            raise ValueError("delay_ms must be non-negative")


class BrainNetwork:
    def __init__(self) -> None:
        self.populations: dict[str, NeuralPopulation] = {}
        self.connections: list[RegionConnection] = []

    def add_population(self, population: NeuralPopulation) -> None:
        if population.name in self.populations:
            raise ValueError(f"population already exists: {population.name}")
        self.populations[population.name] = population

    def connect(self, connection: RegionConnection) -> None:
        if connection.source not in self.populations:
            raise KeyError(connection.source)
        if connection.target not in self.populations:
            raise KeyError(connection.target)
        self.connections.append(connection)

    def region_populations(self, region: BrainRegion) -> Sequence[NeuralPopulation]:
        return tuple(p for p in self.populations.values() if p.region == region)

    def adjacency(self) -> Mapping[str, Sequence[str]]:
        result: dict[str, list[str]] = {name: [] for name in self.populations}
        for edge in self.connections:
            result[edge.source].append(edge.target)
        return result

    def validate(self) -> None:
        for edge in self.connections:
            if edge.source not in self.populations or edge.target not in self.populations:
                raise ValueError("connection references an unknown population")


DEFAULT_REGIONS: tuple[BrainRegion, ...] = tuple(BrainRegion)

__all__ = ["DEFAULT_REGIONS", "BrainNetwork", "BrainRegion", "NeuralPopulation", "RegionConnection"]
