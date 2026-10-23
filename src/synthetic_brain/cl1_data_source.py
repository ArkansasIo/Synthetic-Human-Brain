"""CL1-compatible simulator data sources for Synthetic Human Brain.

These sources model the application-level data-source contract documented by
Cortical Labs: fixed-rate int16 sample frames, optional spike events, metadata,
and stimulation callbacks. They are software research components and are not
models of living tissue or CL1 electronics.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Sequence
import math
import random

SAMPLE_RATE_HZ = 25_000


@dataclass(frozen=True, slots=True)
class DataSourceMetadata:
    channel_count: int = 64
    sample_rate_hz: int = SAMPLE_RATE_HZ
    start_timestamp: int = 0
    duration_frames: int | None = None
    seekable: bool = True
    realtime_only: bool = False
    supports_accelerated: bool = True
    uV_per_sample_unit: float = 1.0


@dataclass(frozen=True, slots=True)
class DataSourceSpike:
    timestamp: int
    channel: int


@dataclass(frozen=True, slots=True)
class DataSourceStim:
    timestamp: int
    channel: int


@dataclass(frozen=True, slots=True)
class DataSourceBatch:
    frames: tuple[tuple[int, ...], ...]
    spikes: tuple[DataSourceSpike, ...] = ()


class SimulatorDataSource:
    """Pull-style source that can answer arbitrary timestamp reads."""

    metadata: DataSourceMetadata

    def open(self) -> None:
        return None

    def close(self) -> None:
        return None

    def on_stim(self, stim: DataSourceStim) -> None:
        return None

    def on_stims(self, stims: Sequence[DataSourceStim]) -> None:
        for stim in stims:
            self.on_stim(stim)

    def read(self, from_timestamp: int, frame_count: int) -> DataSourceBatch:
        raise NotImplementedError


@dataclass(slots=True)
class RandomDataSource(SimulatorDataSource):
    """Deterministic random source with Poisson-like threshold spikes."""

    metadata: DataSourceMetadata = field(default_factory=DataSourceMetadata)
    seed: int | None = None
    mean: float = 170.0
    spike_probability: float = 0.00002
    spike_amplitude: int = 900
    _rng: random.Random = field(init=False)

    def __post_init__(self) -> None:
        if self.metadata.sample_rate_hz != SAMPLE_RATE_HZ:
            raise ValueError("CL1 simulator sample rate must be 25 kHz")
        self._rng = random.Random(self.seed)

    def read(self, from_timestamp: int, frame_count: int) -> DataSourceBatch:
        if frame_count <= 0:
            raise ValueError("frame_count must be positive")
        frames: list[tuple[int, ...]] = []
        spikes: list[DataSourceSpike] = []
        for offset in range(frame_count):
            row: list[int] = []
            timestamp = from_timestamp + offset
            for channel in range(self.metadata.channel_count):
                value = int(round(self.mean + self._rng.gauss(0.0, 8.0)))
                if self._rng.random() < self.spike_probability:
                    value += self.spike_amplitude
                    spikes.append(DataSourceSpike(timestamp, channel))
                row.append(max(-32768, min(32767, value)))
            frames.append(tuple(row))
        return DataSourceBatch(tuple(frames), tuple(spikes))


@dataclass(slots=True)
class ReactiveDataSource(RandomDataSource):
    """Random source whose stimulation events temporarily increase spiking."""

    response_frames: int = 500
    response_probability: float = 0.003
    _stim_until: dict[int, int] = field(default_factory=dict)

    def on_stim(self, stim: DataSourceStim) -> None:
        self._stim_until[stim.channel] = max(
            self._stim_until.get(stim.channel, 0), stim.timestamp + self.response_frames
        )

    def read(self, from_timestamp: int, frame_count: int) -> DataSourceBatch:
        if frame_count <= 0:
            raise ValueError("frame_count must be positive")
        frames: list[tuple[int, ...]] = []
        spikes: list[DataSourceSpike] = []
        for offset in range(frame_count):
            timestamp = from_timestamp + offset
            row: list[int] = []
            for channel in range(self.metadata.channel_count):
                value = int(round(self.mean + self._rng.gauss(0.0, 8.0)))
                probability = self.response_probability if timestamp < self._stim_until.get(channel, -1) else self.spike_probability
                if self._rng.random() < probability:
                    value += self.spike_amplitude
                    spikes.append(DataSourceSpike(timestamp, channel))
                row.append(max(-32768, min(32767, value)))
            frames.append(tuple(row))
        return DataSourceBatch(tuple(frames), tuple(spikes))


@dataclass(slots=True)
class ModelDataSource(SimulatorDataSource):
    """Adapter for a caller-provided neural model.

    ``frame_factory`` receives ``(timestamp, frame_count, channel_count)`` and
    returns integer sample rows. ``spike_factory`` is optional and may return
    timestamped spikes for the requested interval.
    """

    frame_factory: Callable[[int, int, int], Sequence[Sequence[int]]]
    spike_factory: Callable[[int, int, int], Sequence[DataSourceSpike]] | None = None
    metadata: DataSourceMetadata = field(default_factory=DataSourceMetadata)

    def read(self, from_timestamp: int, frame_count: int) -> DataSourceBatch:
        raw = self.frame_factory(from_timestamp, frame_count, self.metadata.channel_count)
        frames = tuple(tuple(int(value) for value in row) for row in raw)
        if len(frames) != frame_count or any(len(row) != self.metadata.channel_count for row in frames):
            raise ValueError("model frame factory returned invalid shape")
        spikes = () if self.spike_factory is None else tuple(self.spike_factory(from_timestamp, frame_count, self.metadata.channel_count))
        return DataSourceBatch(frames, spikes)


class DataSourceRegistry:
    """Small local registry mirroring the SDK's custom-source registration concept."""

    def __init__(self) -> None:
        self._factory: Callable[..., SimulatorDataSource] | None = None
        self._config: dict[str, object] = {}

    def set(self, factory: Callable[..., SimulatorDataSource], config: dict[str, object] | None = None) -> None:
        self._factory = factory
        self._config = dict(config or {})

    def clear(self) -> None:
        self._factory = None
        self._config.clear()

    def build(self) -> SimulatorDataSource | None:
        if self._factory is None:
            return None
        source = self._factory(**self._config)
        source.open()
        return source


__all__ = [
    "DataSourceBatch",
    "DataSourceMetadata",
    "DataSourceRegistry",
    "DataSourceSpike",
    "DataSourceStim",
    "ModelDataSource",
    "RandomDataSource",
    "ReactiveDataSource",
    "SAMPLE_RATE_HZ",
    "SimulatorDataSource",
]
