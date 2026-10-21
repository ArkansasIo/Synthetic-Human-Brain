"""Validated configuration for the abstract neural simulation."""

from dataclasses import dataclass
import math


@dataclass(frozen=True, slots=True)
class SimulationConfig:
    """Configuration for a small discrete-time rate-network simulation."""

    neuron_count: int = 8
    time_step: float = 1.0
    decay: float = 0.9
    seed: int = 7

    def __post_init__(self) -> None:
        if isinstance(self.neuron_count, bool) or not isinstance(self.neuron_count, int):
            raise ValueError("neuron_count must be an integer")
        if self.neuron_count < 1:
            raise ValueError("neuron_count must be at least 1")
        if isinstance(self.time_step, bool) or not isinstance(self.time_step, (int, float)):
            raise ValueError("time_step must be a finite number greater than 0")
        if not math.isfinite(float(self.time_step)) or self.time_step <= 0:
            raise ValueError("time_step must be a finite number greater than 0")
        if isinstance(self.decay, bool) or not isinstance(self.decay, (int, float)):
            raise ValueError("decay must be a finite number between 0 and 1")
        if not math.isfinite(float(self.decay)) or not 0.0 <= self.decay <= 1.0:
            raise ValueError("decay must be a finite number between 0 and 1 inclusive")
        if isinstance(self.seed, bool) or not isinstance(self.seed, int):
            raise ValueError("seed must be an integer")
