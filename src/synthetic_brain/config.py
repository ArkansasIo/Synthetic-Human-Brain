"""Validated configuration for the abstract neural simulation."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SimulationConfig:
    """Configuration for a small discrete-time rate-network simulation."""

    neuron_count: int = 8
    time_step: float = 1.0
    decay: float = 0.9
    seed: int = 7

    def __post_init__(self) -> None:
        if self.neuron_count < 1:
            raise ValueError("neuron_count must be at least 1")
        if self.time_step <= 0:
            raise ValueError("time_step must be greater than 0")
        if not 0.0 <= self.decay <= 1.0:
            raise ValueError("decay must be between 0 and 1 inclusive")
