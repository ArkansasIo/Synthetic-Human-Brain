from pathlib import Path

from synthetic_brain.cl1_clone import Spike, Stim
from synthetic_brain.cl1_recording import RecordingDataset, RecordingMetadata, RecordingWriter, ReplayDataSource


def test_recording_round_trip(tmp_path: Path) -> None:
    writer = RecordingWriter(RecordingMetadata(2))
    writer.append(spikes=[Spike(2, 0)], stims=[Stim(3, 1)], frames=[(1, 2), (3, 4)])
    path = writer.stop(tmp_path / "recording.json")
    loaded = RecordingDataset.load(path)
    assert loaded.metadata.duration_frames == 2
    assert loaded.spikes == [Spike(2, 0)]
    assert loaded.stims == [Stim(3, 1)]


def test_replay_source(tmp_path: Path) -> None:
    dataset = RecordingDataset(RecordingMetadata(2, duration_frames=2), [Spike(1, 0)], [], [(1, 2), (3, 4)])
    path = dataset.save(tmp_path / "replay.json")
    batch = ReplayDataSource(path).read(0, 3)
    assert batch.frames[0] == (1, 2)
    assert batch.spikes[0].channel == 0
    assert len(batch.frames) == 3
