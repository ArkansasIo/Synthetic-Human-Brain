"""Deterministic application-level CL1 API clone for local research.

This is not a hardware, firmware, electrical, or biological clone. It provides
an isolated software target for developing CL-style applications, closed-loop
controllers, experiment scripts, and BrainLang bindings without CL1 hardware.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import random
from typing import Any, Callable, Iterator, Sequence

SAMPLE_RATE_HZ = 25_000


@dataclass(frozen=True, slots=True)
class Spike:
    timestamp: int
    channel: int


@dataclass(frozen=True, slots=True)
class Stim:
    timestamp: int
    channel: int


@dataclass(frozen=True, slots=True)
class StimDesign:
    segments: tuple[tuple[int, float], ...]

    def __init__(self, *values: float | int) -> None:
        if not values or len(values) % 2 or len(values) > 6:
            raise ValueError("StimDesign requires one to three width/current pairs")
        pairs = tuple((int(values[i]), float(values[i + 1])) for i in range(0, len(values), 2))
        if any(width <= 0 for width, _ in pairs):
            raise ValueError("pulse widths must be positive")
        object.__setattr__(self, "segments", pairs)


@dataclass(frozen=True, slots=True)
class BurstDesign:
    count: int
    frequency_hz: float

    def __post_init__(self) -> None:
        if self.count < 1 or self.frequency_hz <= 0:
            raise ValueError("invalid burst design")


class ChannelSet(tuple[int, ...]):
    def __new__(cls, *channels: int | Sequence[int]) -> "ChannelSet":
        values = tuple(channels[0]) if len(channels) == 1 and not isinstance(channels[0], int) else channels
        normalized = tuple(dict.fromkeys(int(channel) for channel in values))
        if not normalized or any(channel < 0 for channel in normalized):
            raise ValueError("channel set must contain non-negative channels")
        return super().__new__(cls, normalized)


@dataclass(frozen=True, slots=True)
class DetectionResult:
    spikes: tuple[Spike, ...] = ()
    stims: tuple[Stim, ...] = ()


@dataclass(slots=True)
class LoopTick:
    iteration: int
    iteration_timestamp: int
    analysis: DetectionResult
    loop: "Loop"


@dataclass(slots=True)
class Recording:
    spikes: list[Spike] = field(default_factory=list)
    stims: list[Stim] = field(default_factory=list)
    attributes: dict[str, Any] = field(default_factory=dict)
    stopped: bool = False

    def stop(self) -> None:
        self.stopped = True

    def wait_until_stopped(self) -> None:
        return None


class Loop:
    def __init__(self, neurons: "Neurons", ticks_per_second: int | float, stop_after_ticks: int | None, stop_after_seconds: float | None) -> None:
        if not 0 < ticks_per_second <= SAMPLE_RATE_HZ:
            raise ValueError(f"ticks_per_second must be in (0, {SAMPLE_RATE_HZ}]")
        self.neurons = neurons
        self.ticks_per_second = float(ticks_per_second)
        self.stop_after_ticks = stop_after_ticks
        self.stop_after_seconds = stop_after_seconds
        self._stopped = False

    def __iter__(self) -> Iterator[LoopTick]:
        count = 0
        while not self._stopped:
            if self.stop_after_ticks is not None and count >= self.stop_after_ticks:
                return
            if self.stop_after_seconds is not None and count / self.ticks_per_second >= self.stop_after_seconds:
                return
            timestamp = self.neurons.timestamp()
            spikes, stims = self.neurons._advance(self.ticks_per_second)
            yield LoopTick(count, timestamp, DetectionResult(tuple(spikes), tuple(stims)), self)
            count += 1

    def run(self, callback: Callable[[LoopTick], None]) -> None:
        for tick in self:
            callback(tick)

    def stop(self) -> None:
        self._stopped = True

    def recover_from_jitter(self, handle_recovery_tick: Callable[[LoopTick], None] | None = None, timeout_seconds: float = 5.0) -> None:
        return None


class Neurons:
    """In-process deterministic neural event simulator."""

    def __init__(self, *, channel_count: int = 64, seed: int | None = 0) -> None:
        if channel_count < 1:
            raise ValueError("channel_count must be positive")
        self.channel_count = channel_count
        self._rng = random.Random(seed)
        self._timestamp = 0
        self._queued: list[Stim] = []
        self._recordings: list[Recording] = []

    def __enter__(self) -> "Neurons":
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        for recording in self._recordings:
            if not recording.stopped:
                recording.stop()

    def timestamp(self) -> int:
        return self._timestamp

    def record(self, **attributes: Any) -> Recording:
        recording = Recording(attributes={"sample_rate_hz": SAMPLE_RATE_HZ, "channel_count": self.channel_count, **attributes})
        self._recordings.append(recording)
        return recording

    def stim(self, channels: ChannelSet | int, stim_design: StimDesign | float, burst_design: BurstDesign | None = None, lead_time_us: int = 80) -> None:
        channel_set = ChannelSet(channels) if isinstance(channels, int) else ChannelSet(channels)
        if not isinstance(stim_design, StimDesign):
            stim_design = StimDesign(160, -float(stim_design), 160, float(stim_design))
        burst = burst_design or BurstDesign(1, 1)
        spacing = max(1, int(SAMPLE_RATE_HZ / burst.frequency_hz))
        start = self._timestamp + max(0, int(lead_time_us * SAMPLE_RATE_HZ / 1_000_000))
        for burst_index in range(burst.count):
            for channel in channel_set:
                if channel >= self.channel_count:
                    raise ValueError(f"channel {channel} outside simulator")
                self._queued.append(Stim(start + burst_index * spacing, channel))

    def loop(self, ticks_per_second: int | float, *, stop_after_ticks: int | None = None, stop_after_seconds: float | None = None, **_: Any) -> Loop:
        return Loop(self, ticks_per_second, stop_after_ticks, stop_after_seconds)

    def _advance(self, ticks_per_second: float) -> tuple[list[Spike], list[Stim]]:
        frames = max(1, int(SAMPLE_RATE_HZ / ticks_per_second))
        end = self._timestamp + frames
        stims = [stim for stim in self._queued if self._timestamp <= stim.timestamp < end]
        self._queued = [stim for stim in self._queued if stim.timestamp >= end]
        spikes: list[Spike] = []
        for channel in range(self.channel_count):
            for frame in range(frames):
                if self._rng.random() < 0.002:
                    spikes.append(Spike(self._timestamp + frame, channel))
        self._timestamp = end
        for recording in self._recordings:
            if not recording.stopped:
                recording.spikes.extend(spikes)
                recording.stims.extend(stims)
        return spikes, stims


class CL1Clone:
    """Context manager analogous to the application-level ``cl.open()`` API."""

    def __init__(self, **kwargs: Any) -> None:
        self.neurons = Neurons(**kwargs)

    def __enter__(self) -> Neurons:
        return self.neurons.__enter__()

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        self.neurons.__exit__(exc_type, exc, tb)


def open(**kwargs: Any) -> CL1Clone:
    return CL1Clone(**kwargs)


__all__ = [
    "BurstDesign",
    "ChannelSet",
    "CL1Clone",
    "DetectionResult",
    "Loop",
    "LoopTick",
    "Neurons",
    "Recording",
    "SAMPLE_RATE_HZ",
    "Spike",
    "Stim",
    "StimDesign",
    "open",
]
