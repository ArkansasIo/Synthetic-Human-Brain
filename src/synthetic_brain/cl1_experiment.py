"""Closed-loop experiment orchestration for the synthetic CL1 layer."""
from __future__ import annotations

from dataclasses import dataclass, field
from collections.abc import Callable
from time import perf_counter

from synthetic_brain.cl1_analysis import FiringStats, firing_stats
from synthetic_brain.cl1_clone import BurstDesign, ChannelSet, LoopTick, Neurons, StimDesign
from synthetic_brain.cl1_recording import RecordingMetadata, RecordingWriter


@dataclass(frozen=True, slots=True)
class ExperimentConfig:
    name: str = "cl1-experiment"
    channel_count: int = 64
    seed: int = 0
    ticks_per_second: float = 1000.0
    ticks: int = 10
    record_frames: bool = False


@dataclass(slots=True)
class ExperimentResult:
    config: ExperimentConfig
    ticks: list[LoopTick] = field(default_factory=list)
    wall_time_seconds: float = 0.0

    @property
    def spikes(self):
        return tuple(spike for tick in self.ticks for spike in tick.analysis.spikes)

    @property
    def stims(self):
        return tuple(stim for tick in self.ticks for stim in tick.analysis.stims)

    def firing_stats(self) -> FiringStats:
        duration_frames = round(self.config.ticks * 25_000 / self.config.ticks_per_second)
        return firing_stats(self.spikes, duration_frames=duration_frames)


class CL1Experiment:
    """Reusable experiment runner with a controller callback."""

    def __init__(self, config: ExperimentConfig | None = None) -> None:
        self.config = config or ExperimentConfig()
        if self.config.channel_count < 1:
            raise ValueError("channel_count must be positive")
        if self.config.ticks < 1:
            raise ValueError("ticks must be positive")

    def run(self, controller: Callable[[LoopTick, Neurons], None] | None = None) -> ExperimentResult:
        start = perf_counter()
        result = ExperimentResult(self.config)
        with Neurons(channel_count=self.config.channel_count, seed=self.config.seed) as neurons:
            for tick in neurons.loop(self.config.ticks_per_second, stop_after_ticks=self.config.ticks):
                result.ticks.append(tick)
                if controller is not None:
                    controller(tick, neurons)
        result.wall_time_seconds = perf_counter() - start
        return result

    def baseline(self) -> ExperimentResult:
        return self.run()

    def stimulated(self, channels: ChannelSet | int, design: StimDesign, burst: BurstDesign | None = None) -> ExperimentResult:
        def controller(tick: LoopTick, neurons: Neurons) -> None:
            if tick.iteration == 0:
                neurons.stim(channels, design, burst)
        return self.run(controller)

    def save(self, result: ExperimentResult, path: str) -> str:
        writer = RecordingWriter(RecordingMetadata(self.config.channel_count, label=self.config.name))
        writer.append(spikes=result.spikes, stims=result.stims)
        return str(writer.stop(path))


__all__ = ["CL1Experiment", "ExperimentConfig", "ExperimentResult"]
