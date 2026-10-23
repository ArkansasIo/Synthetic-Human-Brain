"""Portable JSON recording and replay layer for CL1-style experiments."""
from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
from collections.abc import Iterable

from synthetic_brain.cl1_clone import Spike, Stim
from synthetic_brain.cl1_data_source import DataSourceBatch, DataSourceMetadata, DataSourceSpike, SimulatorDataSource


FORMAT = "synthetic-brain-cl1-recording-v1"


@dataclass(frozen=True, slots=True)
class RecordingMetadata:
    channel_count: int
    sample_rate_hz: int = 25_000
    duration_frames: int | None = None
    label: str = "synthetic"


@dataclass(slots=True)
class RecordingDataset:
    metadata: RecordingMetadata
    spikes: list[Spike]
    stims: list[Stim]
    frames: list[tuple[int, ...]]

    def save(self, path: str | Path) -> Path:
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "format": FORMAT,
            "metadata": asdict(self.metadata),
            "spikes": [asdict(spike) for spike in self.spikes],
            "stims": [asdict(stim) for stim in self.stims],
            "frames": [list(row) for row in self.frames],
        }
        destination.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return destination

    @classmethod
    def load(cls, path: str | Path) -> "RecordingDataset":
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        if payload.get("format") != FORMAT:
            raise ValueError("unsupported synthetic CL1 recording format")
        metadata = RecordingMetadata(**payload["metadata"])
        spikes = [Spike(**item) for item in payload.get("spikes", [])]
        stims = [Stim(**item) for item in payload.get("stims", [])]
        frames = [tuple(int(value) for value in row) for row in payload.get("frames", [])]
        return cls(metadata, spikes, stims, frames)


class RecordingWriter:
    """Incrementally collects normalized events and sample frames."""

    def __init__(self, metadata: RecordingMetadata) -> None:
        self.dataset = RecordingDataset(metadata, [], [], [])
        self._stopped = False

    def append(self, *, spikes: Iterable[Spike] = (), stims: Iterable[Stim] = (), frames: Iterable[Iterable[int]] = ()) -> None:
        if self._stopped:
            raise RuntimeError("recording is stopped")
        self.dataset.spikes.extend(spikes)
        self.dataset.stims.extend(stims)
        self.dataset.frames.extend(tuple(int(value) for value in row) for row in frames)

    def stop(self, path: str | Path) -> Path:
        self._stopped = True
        self.dataset.metadata = RecordingMetadata(
            channel_count=self.dataset.metadata.channel_count,
            sample_rate_hz=self.dataset.metadata.sample_rate_hz,
            duration_frames=len(self.dataset.frames),
            label=self.dataset.metadata.label,
        )
        return self.dataset.save(path)


class ReplayDataSource(SimulatorDataSource):
    """Seekable data source backed by a portable recording dataset."""

    def __init__(self, dataset: RecordingDataset | str | Path) -> None:
        self.dataset = RecordingDataset.load(dataset) if isinstance(dataset, (str, Path)) else dataset
        self.metadata = DataSourceMetadata(
            channel_count=self.dataset.metadata.channel_count,
            sample_rate_hz=self.dataset.metadata.sample_rate_hz,
            duration_frames=self.dataset.metadata.duration_frames,
            seekable=True,
            realtime_only=False,
            supports_accelerated=True,
        )

    def read(self, from_timestamp: int, frame_count: int) -> DataSourceBatch:
        if frame_count <= 0:
            raise ValueError("frame_count must be positive")
        start = max(0, from_timestamp - self.metadata.start_timestamp)
        end = start + frame_count
        frames = tuple(self.dataset.frames[start:end])
        if len(frames) < frame_count:
            frames += tuple(tuple(0 for _ in range(self.metadata.channel_count)) for _ in range(frame_count - len(frames)))
        spikes = tuple(
            DataSourceSpike(spike.timestamp, spike.channel)
            for spike in self.dataset.spikes
            if from_timestamp <= spike.timestamp < from_timestamp + frame_count
        )
        return DataSourceBatch(frames, spikes)


def replay(path: str | Path) -> ReplayDataSource:
    return ReplayDataSource(path)


__all__ = ["FORMAT", "RecordingDataset", "RecordingMetadata", "RecordingWriter", "ReplayDataSource", "replay"]
