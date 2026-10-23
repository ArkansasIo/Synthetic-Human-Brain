from synthetic_brain.cl1_data_source import (
    DataSourceMetadata,
    DataSourceRegistry,
    DataSourceSpike,
    ModelDataSource,
    ReactiveDataSource,
    RandomDataSource,
    SAMPLE_RATE_HZ,
)


def test_random_source_is_reproducible() -> None:
    metadata = DataSourceMetadata(channel_count=2)
    first = RandomDataSource(metadata=metadata, seed=123)
    second = RandomDataSource(metadata=metadata, seed=123)
    assert first.read(0, 10) == second.read(0, 10)


def test_reactive_source_receives_stim() -> None:
    source = ReactiveDataSource(metadata=DataSourceMetadata(channel_count=2), seed=4)
    source.on_stim(type("Stim", (), {"channel": 0, "timestamp": 0})())
    batch = source.read(0, 10)
    assert batch.frames


def test_model_source_shape_validation() -> None:
    source = ModelDataSource(
        frame_factory=lambda timestamp, count, channels: [[0] * channels for _ in range(count)],
        spike_factory=lambda timestamp, count, channels: [DataSourceSpike(timestamp, 0)],
        metadata=DataSourceMetadata(channel_count=2),
    )
    batch = source.read(0, 4)
    assert len(batch.frames) == 4
    assert batch.frames[0] == (0, 0)
    assert batch.spikes[0].timestamp == 0


def test_registry() -> None:
    registry = DataSourceRegistry()
    registry.set(lambda: RandomDataSource(seed=1))
    source = registry.build()
    assert source is not None
    assert source.metadata.sample_rate_hz == SAMPLE_RATE_HZ
    registry.clear()
    assert registry.build() is None
