"""Repeatable software benchmarks for CL1-style simulator behavior."""
from __future__ import annotations

from dataclasses import dataclass, asdict
from time import perf_counter

from synthetic_brain.cl1_analysis import firing_stats
from synthetic_brain.cl1_clone import Neurons


@dataclass(frozen=True, slots=True)
class BenchmarkResult:
    channel_count: int
    ticks: int
    ticks_per_second: float
    wall_time_seconds: float
    simulated_frames: int
    spike_count: int
    mean_rate_hz: float

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def run_benchmark(*, channel_count: int = 64, ticks: int = 100, ticks_per_second: float = 1000.0, seed: int = 0) -> BenchmarkResult:
    start = perf_counter()
    spikes = []
    with Neurons(channel_count=channel_count, seed=seed) as neurons:
        for tick in neurons.loop(ticks_per_second, stop_after_ticks=ticks):
            spikes.extend(tick.analysis.spikes)
    elapsed = perf_counter() - start
    frames = round(ticks * 25_000 / ticks_per_second)
    stats = firing_stats(spikes, duration_frames=frames)
    return BenchmarkResult(channel_count, ticks, ticks_per_second, elapsed, frames, len(spikes), stats.mean_rate_hz)


__all__ = ["BenchmarkResult", "run_benchmark"]
