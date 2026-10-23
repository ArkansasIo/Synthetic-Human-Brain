"""Dependency-free analysis primitives for CL1-style spike recordings.

The functions intentionally operate on normalized spike events so the same
analysis can be applied to the local simulator, SDK simulator exports, or
research datasets. They do not infer biological equivalence.
"""
from __future__ import annotations

from dataclasses import dataclass
from collections import defaultdict
from collections.abc import Iterable, Sequence
from math import log2
from statistics import mean

from synthetic_brain.cl1_clone import Spike, Stim


@dataclass(frozen=True, slots=True)
class FiringStats:
    duration_seconds: float
    total_spikes: int
    active_channels: int
    mean_rate_hz: float
    channel_rates_hz: dict[int, float]
    channel_isi_seconds: dict[int, tuple[float, ...]]


@dataclass(frozen=True, slots=True)
class Burst:
    start_timestamp: int
    end_timestamp: int
    spike_count: int


@dataclass(frozen=True, slots=True)
class NetworkBurstStats:
    bursts: tuple[Burst, ...]
    bin_size_seconds: float
    population_rates_hz: tuple[float, ...]


@dataclass(frozen=True, slots=True)
class EntropyStats:
    bin_size_seconds: float
    values: tuple[float, ...]


@dataclass(frozen=True, slots=True)
class ConnectivityStats:
    channel_count: int
    adjacency: tuple[tuple[float, ...], ...]
    edge_count: int
    mean_abs_correlation: float


def _duration(spikes: Sequence[Spike], sample_rate_hz: int, duration_frames: int | None) -> float:
    if duration_frames is not None:
        return max(0.0, duration_frames / sample_rate_hz)
    if not spikes:
        return 0.0
    lo = min(spike.timestamp for spike in spikes)
    hi = max(spike.timestamp for spike in spikes)
    return max(1 / sample_rate_hz, (hi - lo + 1) / sample_rate_hz)


def firing_stats(spikes: Iterable[Spike], *, sample_rate_hz: int = 25_000, duration_frames: int | None = None) -> FiringStats:
    events = sorted(spikes, key=lambda spike: (spike.timestamp, spike.channel))
    duration = _duration(events, sample_rate_hz, duration_frames)
    timestamps: dict[int, list[int]] = defaultdict(list)
    for spike in events:
        timestamps[spike.channel].append(spike.timestamp)
    rates = {channel: len(values) / duration for channel, values in timestamps.items()} if duration else {}
    isi = {
        channel: tuple((b - a) / sample_rate_hz for a, b in zip(values, values[1:]))
        for channel, values in timestamps.items()
    }
    return FiringStats(duration, len(events), len(timestamps), len(events) / duration if duration else 0.0, rates, isi)


def network_bursts(spikes: Iterable[Spike], *, sample_rate_hz: int = 25_000, bin_size_seconds: float = 0.1, threshold_hz: float = 5.0) -> NetworkBurstStats:
    events = tuple(spikes)
    if bin_size_seconds <= 0:
        raise ValueError("bin_size_seconds must be positive")
    if not events:
        return NetworkBurstStats((), bin_size_seconds, ())
    width = max(1, round(bin_size_seconds * sample_rate_hz))
    first = min(spike.timestamp for spike in events)
    last = max(spike.timestamp for spike in events)
    bins = [0] * (((last - first) // width) + 1)
    for spike in events:
        bins[(spike.timestamp - first) // width] += 1
    rates = tuple(count / bin_size_seconds for count in bins)
    bursts: list[Burst] = []
    start = None
    count = 0
    for index, rate in enumerate(rates + (0.0,)):
        active = rate >= threshold_hz
        if active and start is None:
            start = index
            count = bins[index]
        elif active and start is not None:
            count += bins[index]
        elif start is not None:
            bursts.append(Burst(first + start * width, first + index * width, count))
            start = None
            count = 0
    return NetworkBurstStats(tuple(bursts), bin_size_seconds, rates)


def information_entropy(spikes: Iterable[Spike], *, sample_rate_hz: int = 25_000, bin_size_seconds: float = 0.1) -> EntropyStats:
    events = tuple(spikes)
    if bin_size_seconds <= 0:
        raise ValueError("bin_size_seconds must be positive")
    if not events:
        return EntropyStats(bin_size_seconds, ())
    width = max(1, round(bin_size_seconds * sample_rate_hz))
    first = min(spike.timestamp for spike in events)
    bins: dict[int, set[int]] = defaultdict(set)
    for spike in events:
        bins[(spike.timestamp - first) // width].add(spike.channel)
    channel_count = max((spike.channel for spike in events), default=-1) + 1
    values: list[float] = []
    for index in range(max(bins) + 1):
        active = len(bins.get(index, set()))
        p = active / channel_count if channel_count else 0.0
        values.append(0.0 if p in (0.0, 1.0) else -(p * log2(p) + (1 - p) * log2(1 - p)))
    return EntropyStats(bin_size_seconds, tuple(values))


def functional_connectivity(spikes: Iterable[Spike], *, sample_rate_hz: int = 25_000, bin_size_seconds: float = 0.1, channel_count: int | None = None, threshold: float = 0.3) -> ConnectivityStats:
    events = tuple(spikes)
    if bin_size_seconds <= 0:
        raise ValueError("bin_size_seconds must be positive")
    count = channel_count or (max((spike.channel for spike in events), default=-1) + 1)
    if count <= 0:
        return ConnectivityStats(0, (), 0, 0.0)
    width = max(1, round(bin_size_seconds * sample_rate_hz))
    first = min((spike.timestamp for spike in events), default=0)
    bin_count = max(((max((spike.timestamp for spike in events), default=first) - first) // width) + 1, 1)
    matrix = [[0.0] * bin_count for _ in range(count)]
    for spike in events:
        if spike.channel < count:
            matrix[spike.channel][(spike.timestamp - first) // width] += 1.0
    means = [mean(row) for row in matrix]
    adjacency = [[0.0] * count for _ in range(count)]
    values: list[float] = []
    for i in range(count):
        for j in range(i + 1, count):
            ai = matrix[i]
            aj = matrix[j]
            di = sum((x - means[i]) ** 2 for x in ai) ** 0.5
            dj = sum((x - means[j]) ** 2 for x in aj) ** 0.5
            corr = sum((x - means[i]) * (y - means[j]) for x, y in zip(ai, aj)) / (di * dj) if di and dj else 0.0
            if abs(corr) >= threshold:
                adjacency[i][j] = adjacency[j][i] = corr
                values.append(abs(corr))
    return ConnectivityStats(count, tuple(tuple(row) for row in adjacency), len(values), mean(values) if values else 0.0)


def stimulus_response(spikes: Iterable[Spike], stims: Iterable[Stim], *, window_frames: int = 250, sample_rate_hz: int = 25_000) -> dict[int, float]:
    """Return post-stim spike rate per stimulated channel in a fixed window."""
    if window_frames <= 0:
        raise ValueError("window_frames must be positive")
    events = tuple(spikes)
    result: dict[int, float] = {}
    for stim in stims:
        count = sum(1 for spike in events if spike.channel == stim.channel and stim.timestamp < spike.timestamp <= stim.timestamp + window_frames)
        result[stim.channel] = result.get(stim.channel, 0.0) + count / (window_frames / sample_rate_hz)
    return result


__all__ = [
    "Burst",
    "ConnectivityStats",
    "EntropyStats",
    "FiringStats",
    "NetworkBurstStats",
    "firing_stats",
    "functional_connectivity",
    "information_entropy",
    "network_bursts",
    "stimulus_response",
]
