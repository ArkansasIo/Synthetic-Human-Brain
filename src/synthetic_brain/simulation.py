"""Small deterministic discrete-time rate-network example."""

from __future__ import annotations

from dataclasses import dataclass
import math
import random

from synthetic_brain.config import SimulationConfig


@dataclass(frozen=True, slots=True)
class SimulationSnapshot:
    """Immutable view of one simulation step."""

    step: int
    activity: tuple[float, ...]


class Simulation:
    """An abstract network whose units decay and receive neighbor input.

    Units are not biological neurons, and this update rule is not calibrated to physiology.
    """

    def __init__(self, config: SimulationConfig) -> None:
        self.config = config
        rng = random.Random(config.seed)
        self._activity = [rng.random() for _ in range(config.neuron_count)]
        self._step = 0

    @property
    def step_count(self) -> int:
        """Number of completed update steps."""
        return self._step

    def snapshot(self) -> SimulationSnapshot:
        """Return a read-only snapshot of the current model state."""
        return SimulationSnapshot(step=self._step, activity=tuple(self._activity))

    def step(self, external_input: float = 0.0) -> SimulationSnapshot:
        """Advance the model by one step, rejecting non-finite input."""
        if isinstance(external_input, bool) or not isinstance(external_input, (int, float)):
            raise ValueError("external_input must be a finite number")
        try:
            input_value = float(external_input)
        except OverflowError as exc:
            raise ValueError("external_input must be a finite number") from exc
        if not math.isfinite(input_value):
            raise ValueError("external_input must be a finite number")

        previous = self._activity
        count = len(previous)
        next_activity: list[float] = []
        for index, value in enumerate(previous):
            left = previous[(index - 1) % count]
            right = previous[(index + 1) % count]
            neighbor_signal = (left + right) / 2.0
            updated = (
                self.config.decay * value
                + (1.0 - self.config.decay) * neighbor_signal
                + self.config.time_step * input_value
            )
            next_activity.append(min(1.0, max(0.0, updated)))

        self._activity = next_activity
        self._step += 1
        return self.snapshot()
