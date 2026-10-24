"""Local CL1-compatible software simulator.

This module is an independent research simulator. It does not emulate CL1
hardware electrically or biologically and must not be used as a substitute
for biological validation. Its purpose is to provide a stable application
interface for development, replay, testing, and synthetic-neural experiments.

The public shape follows the concepts documented by Cortical Labs: a context
manager, neurons, spikes, stimulation designs, closed-loop ticks, recording,
and deterministic simulator data generation.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import dataclasses
import json
import math
import random
import time
from pathlib import Path
from typing import Any, Callable, Iterator, Sequence


SAMPLE_RATE_HZ = 25_000
DEFAULT_CHANNEL_COUNT = 64


@dataclass(frozen=True, slots=True)
class Spike:
    timestamp: int
    channel: int
    samples: tuple[float, ...] = ()


@dataclass(frozen=True, slots=True)
class Stim:
    timestamp: int
    channel: int
    design: "StimDesign | None" = None


@dataclass(frozen=True, slots=True)
class StimDesign:
    """A mono-, bi-, or tri-phasic current pulse definition."""

    segments: tuple[tuple[int, float], ...]

    def __init__(self, *segments: float | int) -> None:
        if len(segments) == 0 or len(segments) % 2:
            raise ValueError("StimDesign requires width/current pairs")
        pairs = tuple((int(segments[i]), float(segments[i + 1])) for i in range(0, len(segments), 2))
        if len(pairs) > 3:
            raise ValueError("StimDesign supports at most three pulse segments")
        if any(width <= 0 for width, _ in pairs):
            raise ValueError("pulse widths must be positive")
        object.__setattr__(self, "segments", pairs)


@dataclass(frozen=True, slots=True)
class BurstDesign:
    count: int
    frequency_hz: float

    def __post_init__(self) -> None:
        if self.count <= 0 or self.frequency_hz <= 0:
            raise ValueError("burst count and frequency must be positive")


class ChannelSet(tuple[int, ...]):
    """Immutable channel collection with CL-style construction."""

    def __new__(cls, *channels: int | Sequence[int]) -> "ChannelSet":
        if len(channels) == 1 and not isinstance(channels[0], int):
            values = tuple(int(channel) for channel in channels[0])
        else:
            values = tuple(int(channel) for channel in channels)
        if not values:
            raise ValueError("at least one channel is required")
        if any(channel < 0 for channel in values):
            raise ValueError("channels must be non-negative")
        return super().__new__(cls, dict.fromkeys(values))


@dataclass(frozen=True, slots=True)
class LoopAnalysis:
    spikes: tuple[Spike, ...]
    stims: tuple[Stim, ...]


@dataclass(slots=True)
class LoopTick:
    iteration: int
    iteration_timestamp: int
    analysis: LoopAnalysis
    loop: "Loop"


@dataclass(slots=True)
class Recording:
    path: Path | None = None
    spikes: list[Spike] = field(default_factory=list)
    stims: list[Stim] = field(default_factory=list)
    attributes: dict[str, Any] = field(default_factory=dict)
    _closed: bool = False

    def stop(self) -> None:
        self._closed = True
        self._write()

    def wait_until_stopped(self) -> None:
        return None

    def _write(self) -> None:
        if self.path is None:
            return
        payload = {
            "format": "synthetic-brain-cl1-simulator-v1",
            "attributes": self.attributes,
            "spikes": [dataclasses.asdict(spike) for spike in self.spikes],
            "stims": [
                {"timestamp": stim.timestamp, "channel": stim.channel}
                for stim in self.stims
            ],
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


class DataStream:
    def __init__(self, name: str, attributes: dict[str, Any] | None = None) -> None:
        self.name = name
        self.attributes = dict(attributes or {})
        self.entries: list[tuple[int, Any]] = []

    def append(self, timestamp: int, data: Any) -> None:
        if self.entries and timestamp <= self.entries[-1][0]:
            raise ValueError("data stream timestamps must be strictly ascending")
        self.entries.append((int(timestamp), data))

    def set_attribute(self, name: str, value: Any) -> None:
        self.attributes[name] = value

    def update_attributes(self, values: dict[str, Any]) -> None:
        self.attributes.update(values)


class Loop:
    def __init__(self, neurons: "Neurons", ticks_per_second: float, *, stop_after_ticks: int | None, stop_after_seconds: float | None) -> None:
        if ticks_per_second <= 0 or ticks_per_second > SAMPLE_RATE_HZ:
            raise ValueError(f"ticks_per_second must be in (0, {SAMPLE_RATE_HZ}]")
        self.neurons = neurons
        self.ticks_per_second = ticks_per_second
        self.stop_after_ticks = stop_after_ticks
        self.stop_after_seconds = stop_after_seconds
        self._stopped = False

    def __iter__(self) -> Iterator[LoopTick]:
        start = time.monotonic()
        iteration = 0
        while not self._stopped:
            if self.stop_after_ticks is not None and iteration >= self.stop_after_ticks:
                break
            if self.stop_after_seconds is not None and time.monotonic() - start >= self.stop_after_seconds:
                break
            timestamp = self.neurons._timestamp
            spikes, stims = self.neurons._tick(self.ticks_per_second)
            tick = LoopTick(
                iteration=iteration,
                iteration_timestamp=timestamp,
                analysis=LoopAnalysis(tuple(spikes), tuple(stims)),
                loop=self,
            )
            yield tick
            iteration += 1
            if self.neurons.realtime:
                time.sleep(1.0 / self.ticks_per_second)

    def run(self, loop_body_callback: Callable[[LoopTick], None]) -> None:
        for tick in self:
            loop_body_callback(tick)

    def stop(self) -> None:
        self._stopped = True

    def recover_from_jitter(self, handle_recovery_tick: Callable[[LoopTick], None] | None = None, timeout_seconds: float = 5.0) -> None:
        return None


class Neurons:
    """Stateful local CL1-style simulator connection."""

    def __init__(self, *, channel_count: int = DEFAULT_CHANNEL_COUNT, seed: int | None = None, realtime: bool = False) -> None:
        if channel_count <= 0:
            raise ValueError("channel_count must be positive")
        self.channel_count = channel_count
        self.rng = random.Random(seed)
        self.seed = seed
        self.realtime = realtime
        self._timestamp = 0
        self._recordings: list[Recording] = []
        self._streams: dict[str, DataStream] = {}
        self._queued_stims: list[Stim] = []
        self._open = False

    def __enter__(self) -> "Neurons":
        self._open = True
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        self.close()

    def close(self) -> None:
        for recording in self._recordings:
            if not recording._closed:
                recording.stop()
        self._open = False

    def timestamp(self) -> int:
        return self._timestamp

    def record(self, *, file_location: str | None = None, file_suffix: str | None = None, attributes: dict[str, Any] | None = None, **_: Any) -> Recording:
        path = None
        if file_location:
            suffix = file_suffix or "recording"
            path = Path(file_location) / f"{suffix}.json"
        recording = Recording(path=path, attributes={"sample_rate_hz": SAMPLE_RATE_HZ, "channel_count": self.channel_count, **(attributes or {})})
        self._recordings.append(recording)
        return recording

    def create_data_stream(self, name: str, attributes: dict[str, Any] | None = None) -> DataStream:
        if name in self._streams:
            raise ValueError(f"data stream already exists: {name}")
        stream = DataStream(name, attributes)
        self._streams[name] = stream
        return stream

    def stim(self, channel_set: ChannelSet | int, stim_design: StimDesign | float, burst_design: BurstDesign | None = None, lead_time_us: int = 80) -> None:
        channels = ChannelSet(channel_set) if isinstance(channel_set, int) else ChannelSet(channel_set)
        design = stim_design if isinstance(stim_design, StimDesign) else StimDesign(160, -float(stim_design), 160, float(stim_design))
        if burst_design is None:
            burst_design = BurstDesign(1, 1.0)
        spacing = int(SAMPLE_RATE_HZ / burst_design.frequency_hz)
        first = self._timestamp + max(0, int(lead_time_us * SAMPLE_RATE_HZ / 1_000_000))
        for index in range(burst_design.count):
            timestamp = first + index * spacing
            for channel in channels:
                if channel >= self.channel_count:
                    raise ValueError(f"channel {channel} is outside simulator range")
                self._queued_stims.append(Stim(timestamp, channel, design))

    def loop(self, ticks_per_second: float, *, stop_after_ticks: int | None = None, stop_after_seconds: float | None = None, **_: Any) -> Loop:
        return Loop(self, ticks_per_second, stop_after_ticks=stop_after_ticks, stop_after_seconds=stop_after_seconds)

    def _tick(self, ticks_per_second: float) -> tuple[list[Spike], list[Stim]]:
        frames = max(1, int(SAMPLE_RATE_HZ / ticks_per_second))
        end = self._timestamp + frames
        stims = [stim for stim in self._queued_stims if self._timestamp <= stim.timestamp < end]
        self._queued_stims = [stim for stim in self._queued_stims if stim.timestamp >= end]
        spikes: list[Spike] = []
        p_per_frame = 0.002
        for channel in range(self.channel_count):
            for frame in range(frames):
                if self.rng.random() < p_per_frame:
                    spikes.append(Spike(self._timestamp + frame, channel))
        self._timestamp = end
        for recording in self._recordings:
            if not recording._closed:
                recording.spikes.extend(spikes)
                recording.stims.extend(stims)
        return spikes, stims


class CL1Simulator:
    """Convenience facade matching the conceptual ``cl.open()`` workflow."""

    def __init__(self, **kwargs: Any) -> None:
        self.neurons = Neurons(**kwargs)

    def __enter__(self) -> Neurons:
        return self.neurons.__enter__()

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        self.neurons.__exit__(exc_type, exc, tb)


def open(*, channel_count: int = DEFAULT_CHANNEL_COUNT, seed: int | None = None, realtime: bool = False, **_: Any) -> CL1Simulator:
    """Return a local simulator context.

    This is intentionally named ``open`` to make porting application-level
    experiments from the CL API straightforward without shadowing the real
    ``cl`` package.
    """
    return CL1Simulator(channel_count=channel_count, seed=seed, realtime=realtime)


__all__ = [
    "BurstDesign",
    "ChannelSet",
    "CL1Simulator",
    "DataStream",
    "Loop",
    "LoopAnalysis",
    "LoopTick",
    "Neurons",
    "Recording",
    "SAMPLE_RATE_HZ",
    "Spike",
    "Stim",
    "StimDesign",
    "open",
]
