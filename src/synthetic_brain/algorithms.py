"""Foundational computational-neuroscience algorithms.

This module collects reusable mathematical primitives rather than claiming to
implement a complete human brain. Models are intentionally explicit so that
parameters, units, numerical methods, and validation data can be documented.

Implemented families include:
- numerical integration and membrane/cable equations;
- leaky integrate-and-fire, adaptive exponential IF, Izhikevich and
  Hodgkin-Huxley neuron dynamics;
- conductance synapses and short-term Tsodyks-Markram dynamics;
- Hebbian, Oja, BCM, STDP and homeostatic plasticity;
- Wilson-Cowan population dynamics and Kuramoto synchronization;
- divisive normalization, softmax and sparse competition;
- temporal-difference reinforcement learning and predictive-coding updates;
- Hopfield associative memory and simple working-memory decay.

These are established computational models used in neuroscience and related
fields, but no single set constitutes "the human brain algorithm". Parameters
must be fitted and validated against appropriate experimental data.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import exp, tanh, sqrt, sin, pi
from typing import Callable, Sequence


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def euler_step(state: float, derivative: float, dt: float) -> float:
    return state + dt * derivative


def rk4_step(state: float, derivative: Callable[[float], float], dt: float) -> float:
    k1 = derivative(state)
    k2 = derivative(state + 0.5 * dt * k1)
    k3 = derivative(state + 0.5 * dt * k2)
    k4 = derivative(state + dt * k3)
    return state + dt * (k1 + 2 * k2 + 2 * k3 + k4) / 6.0


@dataclass(slots=True)
class LIFNeuron:
    """Current-based leaky integrate-and-fire neuron."""

    membrane: float = -65.0
    rest: float = -65.0
    threshold: float = -50.0
    reset: float = -65.0
    resistance: float = 10.0
    tau: float = 20.0
    refractory: float = 2.0
    refractory_left: float = 0.0

    def step(self, current: float, dt: float) -> bool:
        if self.refractory_left > 0.0:
            self.refractory_left = max(0.0, self.refractory_left - dt)
            self.membrane = self.reset
            return False
        dv = (-(self.membrane - self.rest) + self.resistance * current) / self.tau
        self.membrane += dt * dv
        if self.membrane >= self.threshold:
            self.membrane = self.reset
            self.refractory_left = self.refractory
            return True
        return False


@dataclass(slots=True)
class AdExNeuron:
    """Adaptive exponential integrate-and-fire model."""

    v: float = -70.0
    w: float = 0.0
    c: float = -58.0
    vr: float = -70.0
    vt: float = -50.0
    delta_t: float = 2.0
    tau_m: float = 20.0
    tau_w: float = 100.0
    a: float = 0.0
    b: float = 0.0
    r: float = 10.0
    v_peak: float = 20.0

    def step(self, current: float, dt: float) -> bool:
        exp_term = self.delta_t * exp(clamp((self.v - self.vt) / self.delta_t, -50.0, 50.0))
        dv = (- (self.v - self.vr) + exp_term - self.r * self.w + self.r * current) / self.tau_m
        dw = (self.a * (self.v - self.vr) - self.w) / self.tau_w
        self.v += dt * dv
        self.w += dt * dw
        if self.v >= self.v_peak:
            self.v = self.c
            self.w += self.b
            return True
        return False


@dataclass(slots=True)
class IzhikevichNeuron:
    """Two-variable spiking model from Izhikevich's canonical formulation."""

    v: float = -65.0
    u: float = -13.0
    a: float = 0.02
    b: float = 0.2
    c: float = -65.0
    d: float = 8.0

    def step(self, current: float, dt: float = 1.0) -> bool:
        self.v += dt * (0.04 * self.v * self.v + 5 * self.v + 140 - self.u + current)
        self.u += dt * (self.a * (self.b * self.v - self.u))
        if self.v >= 30.0:
            self.v = self.c
            self.u += self.d
            return True
        return False


@dataclass(slots=True)
class HodgkinHuxleyNeuron:
    """Classical conductance-based Hodgkin-Huxley membrane model."""

    v: float = -65.0
    m: float = 0.0529
    h: float = 0.596
    n: float = 0.317
    cm: float = 1.0
    g_na: float = 120.0
    g_k: float = 36.0
    g_l: float = 0.3
    e_na: float = 50.0
    e_k: float = -77.0
    e_l: float = -54.387

    @staticmethod
    def _rates(v: float) -> tuple[float, float, float, float, float, float]:
        am = 0.1 * (v + 40.0) / (1.0 - exp(-(v + 40.0) / 10.0)) if abs(v + 40.0) > 1e-8 else 1.0
        bm = 4.0 * exp(-(v + 65.0) / 18.0)
        ah = 0.07 * exp(-(v + 65.0) / 20.0)
        bh = 1.0 / (1.0 + exp(-(v + 35.0) / 10.0))
        an = 0.01 * (v + 55.0) / (1.0 - exp(-(v + 55.0) / 10.0)) if abs(v + 55.0) > 1e-8 else 0.1
        bn = 0.125 * exp(-(v + 65.0) / 80.0)
        return am, bm, ah, bh, an, bn

    def step(self, current: float, dt: float = 0.01) -> bool:
        am, bm, ah, bh, an, bn = self._rates(self.v)
        ina = self.g_na * self.m**3 * self.h * (self.v - self.e_na)
        ik = self.g_k * self.n**4 * (self.v - self.e_k)
        il = self.g_l * (self.v - self.e_l)
        dv = (current - ina - ik - il) / self.cm
        self.m += dt * (am * (1.0 - self.m) - bm * self.m)
        self.h += dt * (ah * (1.0 - self.h) - bh * self.h)
        self.n += dt * (an * (1.0 - self.n) - bn * self.n)
        old_v = self.v
        self.v += dt * dv
        return old_v < 0.0 <= self.v


@dataclass(slots=True)
class ConductanceSynapse:
    """Exponential conductance synapse with a reversal potential."""

    conductance: float = 0.0
    tau: float = 5.0
    reversal: float = 0.0

    def decay(self, dt: float) -> None:
        self.conductance *= exp(-dt / self.tau)

    def activate(self, amount: float = 1.0) -> None:
        self.conductance += amount

    def current(self, membrane_voltage: float) -> float:
        return self.conductance * (self.reversal - membrane_voltage)


@dataclass(slots=True)
class TsodyksMarkramSynapse:
    """Short-term facilitation/depression model."""

    u: float = 0.2
    x: float = 1.0
    tau_f: float = 1500.0
    tau_d: float = 200.0
    use: float = 0.2

    def step(self, dt: float) -> None:
        self.u += dt * (self.use - self.u) / self.tau_f
        self.x += dt * (1.0 - self.x) / self.tau_d

    def presynaptic_spike(self) -> float:
        self.u += self.use * (1.0 - self.u)
        released = self.u * self.x
        self.x -= released
        return released


def hebbian_update(weight: float, pre: float, post: float, learning_rate: float) -> float:
    return weight + learning_rate * pre * post


def oja_update(weight: float, pre: float, post: float, learning_rate: float) -> float:
    return weight + learning_rate * post * (pre - post * weight)


def bcm_update(weight: float, pre: float, post: float, threshold: float, learning_rate: float) -> float:
    return weight + learning_rate * pre * post * (post - threshold)


def homeostatic_update(weight: float, rate: float, target_rate: float, learning_rate: float) -> float:
    return weight + learning_rate * (target_rate - rate)


def stdp_update(
    weight: float,
    delta_t: float,
    a_plus: float = 0.01,
    a_minus: float = 0.012,
    tau_plus: float = 20.0,
    tau_minus: float = 20.0,
) -> float:
    """Pair-based spike-timing-dependent plasticity."""
    if delta_t > 0.0:
        return weight + a_plus * exp(-delta_t / tau_plus)
    if delta_t < 0.0:
        return weight - a_minus * exp(delta_t / tau_minus)
    return weight


def wilson_cowan_step(
    excitatory: float,
    inhibitory: float,
    ee: float,
    ei: float,
    ie: float,
    ii: float,
    external_e: float,
    external_i: float,
    dt: float = 0.1,
    tau_e: float = 1.0,
    tau_i: float = 1.0,
) -> tuple[float, float]:
    """One Euler step of a Wilson-Cowan E/I population model."""
    sigmoid = lambda x: 1.0 / (1.0 + exp(-x))
    se = sigmoid(ee * excitatory - ei * inhibitory + external_e)
    si = sigmoid(ie * excitatory - ii * inhibitory + external_i)
    de = (-excitatory + (1.0 - excitatory) * se) / tau_e
    di = (-inhibitory + (1.0 - inhibitory) * si) / tau_i
    return clamp(excitatory + dt * de, 0.0, 1.0), clamp(inhibitory + dt * di, 0.0, 1.0)


def kuramoto_step(phases: Sequence[float], natural_frequencies: Sequence[float], coupling: float, dt: float) -> list[float]:
    """One mean-field Kuramoto oscillator step."""
    n = len(phases)
    if n == 0:
        return []
    out: list[float] = []
    for i, phase in enumerate(phases):
        interaction = sum(sin(other - phase) for other in phases) / n
        out.append(phase + dt * (natural_frequencies[i] + coupling * interaction))
    return out


def divisive_normalization(values: Sequence[float], sigma: float = 1.0, alpha: float = 1.0) -> list[float]:
    total = sigma + alpha * sum(max(0.0, v) for v in values)
    return [max(0.0, v) / total for v in values]


def softmax(values: Sequence[float], temperature: float = 1.0) -> list[float]:
    if temperature <= 0:
        raise ValueError("temperature must be positive")
    if not values:
        return []
    m = max(values)
    exps = [exp((v - m) / temperature) for v in values]
    total = sum(exps)
    return [v / total for v in exps]


def td_error(reward: float, value_next: float, value_current: float, gamma: float = 0.99) -> float:
    return reward + gamma * value_next - value_current


def td_update(value: float, reward: float, value_next: float, learning_rate: float, gamma: float = 0.99) -> float:
    return value + learning_rate * td_error(reward, value_next, value, gamma)


def predictive_coding_update(value: float, prediction: float, precision: float, learning_rate: float) -> float:
    """Gradient-style update toward a prediction-error minimum."""
    error = value - prediction
    return value - learning_rate * precision * error


def hopfield_update(state: Sequence[int], weights: Sequence[Sequence[float]], neuron: int) -> int:
    field = sum(weights[neuron][j] * state[j] for j in range(len(state)))
    return 1 if field >= 0.0 else -1


def hopfield_hebbian(patterns: Sequence[Sequence[int]]) -> list[list[float]]:
    """Hebbian Hopfield weight matrix with zero diagonal."""
    if not patterns:
        return []
    n = len(patterns[0])
    weights = [[0.0 for _ in range(n)] for _ in range(n)]
    for pattern in patterns:
        if len(pattern) != n:
            raise ValueError("all patterns must have equal length")
        for i in range(n):
            for j in range(n):
                if i != j:
                    weights[i][j] += pattern[i] * pattern[j] / n
    return weights


@dataclass(slots=True)
class WorkingMemoryTrace:
    """Simple activity trace for working-memory experiments."""

    value: float = 0.0
    decay_tau: float = 500.0

    def step(self, input_value: float, dt: float) -> float:
        self.value = self.value * exp(-dt / self.decay_tau) + input_value
        return self.value


def cable_diffusion_step(compartments: Sequence[float], coupling: float, leak: float, dt: float) -> list[float]:
    """Explicit finite-difference step for a 1-D passive cable."""
    if not compartments:
        return []
    out = list(compartments)
    for i, value in enumerate(compartments):
        left = compartments[i - 1] if i else value
        right = compartments[i + 1] if i + 1 < len(compartments) else value
        laplacian = left - 2.0 * value + right
        out[i] = value + dt * (coupling * laplacian - leak * value)
    return out


def poisson_spike_train(rate_hz: float, duration_s: float, dt_s: float, seed: int = 0) -> list[int]:
    """Deterministic Bernoulli approximation to a Poisson spike train."""
    import random

    rng = random.Random(seed)
    if rate_hz < 0 or duration_s < 0 or dt_s <= 0:
        raise ValueError("rate_hz and duration_s must be non-negative; dt_s must be positive")
    p = 1.0 - exp(-rate_hz * dt_s)
    return [1 if rng.random() < p else 0 for _ in range(int(duration_s / dt_s))]


__all__ = [
    "AdExNeuron", "ConductanceSynapse", "HodgkinHuxleyNeuron", "IzhikevichNeuron",
    "LIFNeuron", "TsodyksMarkramSynapse", "WorkingMemoryTrace", "bcm_update",
    "cable_diffusion_step", "clamp", "divisive_normalization", "euler_step",
    "hebbian_update", "homeostatic_update", "hopfield_hebbian", "hopfield_update",
    "kuramoto_step", "oja_update", "poisson_spike_train", "predictive_coding_update",
    "rk4_step", "softmax", "stdp_update", "td_error", "td_update", "wilson_cowan_step",
]
