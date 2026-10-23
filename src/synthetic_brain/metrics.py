"""Simulation observables for validating neural activity."""
from __future__ import annotations

from math import log2
from statistics import mean
from collections.abc import Sequence


def firing_rate(spikes: Sequence[int | bool], duration_s: float) -> float:
    if duration_s <= 0:
        raise ValueError("duration_s must be positive")
    return sum(bool(spike) for spike in spikes) / duration_s


def coefficient_of_variation(intervals_s: Sequence[float]) -> float:
    if not intervals_s:
        return 0.0
    average = mean(intervals_s)
    if average <= 0:
        raise ValueError("mean interval must be positive")
    variance = mean((value - average) ** 2 for value in intervals_s)
    return variance**0.5 / average


def synchrony_index(rates: Sequence[float]) -> float:
    """Normalized population synchrony proxy in [0, 1]."""
    if not rates:
        return 0.0
    average = mean(rates)
    if average <= 0:
        return 0.0
    variance = mean((rate - average) ** 2 for rate in rates)
    return min(1.0, variance**0.5 / (average + 1e-12))


def population_entropy(values: Sequence[float]) -> float:
    """Shannon entropy of non-negative activity weights."""
    positive = [value for value in values if value > 0]
    total = sum(positive)
    if total <= 0:
        return 0.0
    return -sum((value / total) * log2(value / total) for value in positive)


def mean_abs_error(observed: Sequence[float], predicted: Sequence[float]) -> float:
    if len(observed) != len(predicted):
        raise ValueError("observed and predicted must have equal length")
    if not observed:
        return 0.0
    return mean(abs(a - b) for a, b in zip(observed, predicted))


__all__ = ["coefficient_of_variation", "firing_rate", "mean_abs_error", "population_entropy", "synchrony_index"]
