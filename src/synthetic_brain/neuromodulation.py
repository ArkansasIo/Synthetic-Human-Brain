"""Neuromodulatory and reward-signal primitives."""
from __future__ import annotations

from dataclasses import dataclass

from synthetic_brain.algorithms import td_error


@dataclass
class Neuromodulator:
    name: str
    level: float = 0.0
    baseline: float = 0.0
    decay_rate: float = 0.1
    minimum: float = 0.0
    maximum: float = 1.0

    def step(self, dt: float, drive: float = 0.0) -> float:
        if dt < 0:
            raise ValueError("dt must be non-negative")
        self.level += dt * (drive - self.decay_rate * (self.level - self.baseline))
        self.level = min(self.maximum, max(self.minimum, self.level))
        return self.level


@dataclass
class DopamineSignal:
    gain: float = 1.0
    baseline: float = 0.0

    def prediction_error(self, reward: float, value: float, next_value: float, gamma: float = 0.99) -> float:
        return self.gain * td_error(reward, value, next_value, gamma)

    def release(self, reward: float, value: float, next_value: float, gamma: float = 0.99) -> float:
        return self.baseline + self.prediction_error(reward, value, next_value, gamma)


@dataclass
class HomeostaticController:
    target_rate: float
    learning_rate: float = 0.01

    def update(self, current_rate: float, gain: float) -> float:
        return gain + self.learning_rate * (self.target_rate - current_rate)


DEFAULT_NEUROMODULATORS = {
    "dopamine": Neuromodulator("dopamine"),
    "serotonin": Neuromodulator("serotonin"),
    "acetylcholine": Neuromodulator("acetylcholine"),
    "norepinephrine": Neuromodulator("norepinephrine"),
}

__all__ = ["DEFAULT_NEUROMODULATORS", "DopamineSignal", "HomeostaticController", "Neuromodulator"]
