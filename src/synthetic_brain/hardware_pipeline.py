"""Hardware data pipeline per docs/HARDWARE_ARCHITECTURE.md.

Implements the documented blocks as software stages so H1 (recorded-data
replay) and H2 (external acquisition prototype) have a stable API:

    Sensor interface -> Analog front end (config model) -> Digitizer
    -> Synchronization -> Edge-compute stub -> Data transport -> Storage

The pipeline deals exclusively with *research* data: timestamps, channel
identity, units, quality flags, and provenance. It deliberately contains no
stimulation parameters or clinical logic (see the safety boundary in the
architecture document).
"""

from __future__ import annotations

import json
import time
from collections.abc import Iterator, Sequence
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Protocol

PIPELINE_FORMAT = "synthetic-brain-hardware-pipeline-v1"
"""Versioned packet schema identifier (see Data transport)."""


class QualityFlag(Enum):
    """Per-sample quality flags from the Digitizer stage."""

    OK = 0
    SATURATED = 1 << 0
    DROPPED = 1 << 1
    OUT_OF_RANGE = 1 << 2
    UNSYNCED = 1 << 3


class SensorInterface(Protocol):
    """Generic inputs for validated research sensors.

    Exposes channel count, sampling metadata, units, timing, calibration, and
    provenance, exactly as required by the Sensor interface block.
    """

    def channel_count(self) -> int: ...

    def sample_rate_hz(self) -> float: ...

    def units(self) -> str: ...

    def calibration(self) -> dict[str, float]: ...

    def provenance(self) -> dict[str, Any]: ...


@dataclass(frozen=True, slots=True)
class AnalogFrontEndConfig:
    """Configuration model for the analog front end stage.

    The hardware design itself is out of scope; this carries the parameters
    the digitizer needs to interpret incoming conditioned signals.
    """

    gain: float = 100.0
    high_pass_hz: float = 0.5
    low_pass_hz: float = 500.0
    notch_hz: float | None = 50.0

    def __post_init__(self) -> None:
        if self.gain <= 0:
            raise ValueError("gain must be positive")
        if self.high_pass_hz >= self.low_pass_hz:
            raise ValueError("high_pass_hz must be below low_pass_hz")


@dataclass(frozen=True, slots=True)
class DigitizerSample:
    """One timestamped digital sample block for one channel."""

    channel: int
    timestamp_ns: int
    value: float
    quality: QualityFlag = QualityFlag.OK


class Digitizer:
    """Converts conditioned signals into timestamped digital samples.

    Supports synchronization metadata and dropped-sample detection: if a
    sample's timestamp gap exceeds one expected period by more than the
    tolerance, the frame is flagged DROPPED.
    """

    def __init__(self, sample_rate_hz: float, channels: int, *, dropped_tolerance_periods: float = 0.5) -> None:
        if sample_rate_hz <= 0:
            raise ValueError("sample_rate_hz must be positive")
        if channels < 1:
            raise ValueError("channels must be positive")
        self.sample_rate_hz = sample_rate_hz
        self.channels = channels
        self._expected_period_ns = int(1e9 / sample_rate_hz)
        self._tolerance_ns = int(self._expected_period_ns * dropped_tolerance_periods)
        self._last_timestamp: dict[int, int] = {}

    def digitize(self, raw: Sequence[float], channel: int, start_ns: int | None = None) -> list[DigitizerSample]:
        if not 0 <= channel < self.channels:
            raise ValueError(f"channel {channel} outside 0..{self.channels - 1}")
        start = start_ns if start_ns is not None else time.time_ns()
        samples: list[DigitizerSample] = []
        for index, value in enumerate(raw):
            timestamp = start + index * self._expected_period_ns
            quality = QualityFlag.OK
            previous = self._last_timestamp.get(channel)
            if previous is not None and timestamp - previous > self._expected_period_ns + self._tolerance_ns:
                quality = QualityFlag.DROPPED
            self._last_timestamp[channel] = timestamp
            samples.append(DigitizerSample(channel=channel, timestamp_ns=timestamp, value=float(value), quality=quality))
        return samples


@dataclass(slots=True)
class SyncClock:
    """Common timebase aligning multiple sensor systems and simulation state."""

    epoch_ns: int = field(default_factory=time.time_ns)
    drift_ppm: float = 0.0

    def now_ns(self) -> int:
        return time.time_ns() - self.epoch_ns

    def align(self, timestamp_ns: int) -> int:
        """Map a sensor timestamp onto the common timebase."""
        correction = 1.0 + self.drift_ppm * 1e-6
        return int((timestamp_ns - self.epoch_ns) / correction)


@dataclass(frozen=True, slots=True)
class TransportPacket:
    """Versioned packet: channel identity, timestamp, data, units, quality, source."""

    schema: str
    channel: int
    timestamp_ns: int
    samples: tuple[float, ...]
    units: str
    quality: int
    source_id: str

    def __post_init__(self) -> None:
        if self.schema != PIPELINE_FORMAT:
            raise ValueError(f"unsupported packet schema: {self.schema}")

    @classmethod
    def create(
        cls,
        channel: int,
        timestamp_ns: int,
        samples: Sequence[float],
        units: str,
        quality: int,
        source_id: str,
    ) -> "TransportPacket":
        """Convenience constructor filling the schema version automatically."""
        return cls(
            schema=PIPELINE_FORMAT,
            channel=channel,
            timestamp_ns=timestamp_ns,
            samples=tuple(samples),
            units=units,
            quality=quality,
            source_id=source_id,
        )

    def to_json(self) -> str:
        payload = asdict(self)
        payload["samples"] = list(self.samples)
        return json.dumps(payload, separators=(",", ":"))

    @classmethod
    def from_json(cls, raw: str) -> "TransportPacket":
        data = json.loads(raw)
        if data["schema"] != PIPELINE_FORMAT:
            raise ValueError(f"unsupported packet schema: {data['schema']}")
        return cls(
            schema=data["schema"],
            channel=data["channel"],
            timestamp_ns=data["timestamp_ns"],
            samples=tuple(data["samples"]),
            units=data["units"],
            quality=data["quality"],
            source_id=data["source_id"],
        )


class PacketStorage:
    """Immutable raw storage, separate from derived data (see Storage block)."""

    def __init__(self) -> None:
        self._raw: list[TransportPacket] = []

    def append(self, packet: TransportPacket) -> None:
        if packet.schema != PIPELINE_FORMAT:
            raise ValueError("packet schema mismatch")
        self._raw.append(packet)

    def raw(self) -> tuple[TransportPacket, ...]:
        return tuple(self._raw)

    def derived(self, transform, name: str) -> list[float]:
        """Derive a dataset; provenance is (source packets, transform name)."""
        return [transform(packet) for packet in self._raw]


def replay(source: Sequence[TransportPacket], speed: float = 1.0) -> Iterator[TransportPacket]:
    """H1 replay: stream prerecorded packets back at a given speed."""
    if speed <= 0:
        raise ValueError("speed must be positive")
    start = time.perf_counter()
    first_timestamp = source[0].timestamp_ns
    for packet in source:
        target = start + (packet.timestamp_ns - first_timestamp) / speed
        delay = target - time.perf_counter()
        if delay > 0:
            time.sleep(delay / 1e9)
        yield packet


__all__ = [
    "AnalogFrontEndConfig",
    "Digitizer",
    "DigitizerSample",
    "PIPELINE_FORMAT",
    "PacketStorage",
    "QualityFlag",
    "SensorInterface",
    "SyncClock",
    "TransportPacket",
    "replay",
]
