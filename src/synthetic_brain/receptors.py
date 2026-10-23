"""Receptor-level synaptic response primitives."""
from __future__ import annotations

from dataclasses import dataclass
from math import exp


def _exp_decay(value: float, dt_ms: float, tau_ms: float) -> float:
    if tau_ms <= 0:
        raise ValueError("tau_ms must be positive")
    return value * exp(-dt_ms / tau_ms)


@dataclass
class AMPAReceptor:
    tau_ms: float = 2.0
    conductance: float = 0.0

    def step(self, dt_ms: float, events: float = 0.0) -> float:
        self.conductance = _exp_decay(self.conductance, dt_ms, self.tau_ms) + events
        return self.conductance


@dataclass
class NMDAReceptor:
    tau_ms: float = 100.0
    magnesium_mM: float = 1.0
    conductance: float = 0.0

    def magnesium_block(self, voltage_mV: float) -> float:
        return 1.0 / (1.0 + self.magnesium_mM * exp(-0.062 * voltage_mV) / 3.57)

    def step(self, dt_ms: float, voltage_mV: float, events: float = 0.0) -> float:
        self.conductance = _exp_decay(self.conductance, dt_ms, self.tau_ms) + events
        return self.conductance * self.magnesium_block(voltage_mV)


@dataclass
class GABAaReceptor:
    tau_ms: float = 8.0
    conductance: float = 0.0

    def step(self, dt_ms: float, events: float = 0.0) -> float:
        self.conductance = _exp_decay(self.conductance, dt_ms, self.tau_ms) + events
        return self.conductance


@dataclass
class GABAbReceptor:
    tau_ms: float = 150.0
    conductance: float = 0.0

    def step(self, dt_ms: float, events: float = 0.0) -> float:
        self.conductance = _exp_decay(self.conductance, dt_ms, self.tau_ms) + events
        return self.conductance


@dataclass
class ReceptorCurrent:
    reversal_mV: float

    def __call__(self, conductance: float, voltage_mV: float) -> float:
        return conductance * (self.reversal_mV - voltage_mV)


AMPA_CURRENT = ReceptorCurrent(0.0)
NMDA_CURRENT = ReceptorCurrent(0.0)
GABAA_CURRENT = ReceptorCurrent(-70.0)
GABAB_CURRENT = ReceptorCurrent(-90.0)

__all__ = [
    "AMPA_CURRENT", "GABAA_CURRENT", "GABAB_CURRENT", "NMDA_CURRENT",
    "AMPAReceptor", "GABAaReceptor", "GABAbReceptor", "NMDAReceptor", "ReceptorCurrent",
]
