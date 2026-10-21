"""Pluggable abstract neuron/rate models.

These models are computational abstractions and are not claims about biological
neurons or complete brain physiology.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class NeuronModel(Protocol):
    """Protocol for deterministic single-unit update models."""

    def update(self, activity: float, input_signal: float, time_step: float) -> float:
        """Return the next activity value for one abstract unit."""


@dataclass(frozen=True, slots=True)
class LeakyRateNeuron:
    """Simple bounded leaky rate model."""

    decay: float = 0.9
    minimum: float = 0.0
    maximum: float = 1.0

    def __post_init__(self) -> None:
        if not 0.0 <= self.decay <= 1.0:
            raise ValueError("decay must be between 0 and 1")
        if self.minimum >= self.maximum:
            raise ValueError("minimum must be less than maximum")

    def update(self, activity: float, input_signal: float, time_step: float) -> float:
        """Apply decay plus input and clamp to the configured range."""
        value = self.decay * activity + time_step * input_signal
        return min(self.maximum, max(self.minimum, value))
