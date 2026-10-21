"""Pluggable synapse transformations for abstract network simulations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class SynapseModel(Protocol):
    """Protocol for transforming a connection signal."""

    def transmit(self, signal: float, weight: float) -> float:
        """Return the transmitted signal."""


@dataclass(frozen=True, slots=True)
class LinearSynapse:
    """Pass a signal through a scalar connection weight."""

    gain: float = 1.0

    def transmit(self, signal: float, weight: float) -> float:
        """Return signal multiplied by weight and gain."""
        return signal * weight * self.gain
