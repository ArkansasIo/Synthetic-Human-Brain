"""Tests for the hardware data pipeline (docs/HARDWARE_ARCHITECTURE.md)."""

import json

import pytest

from synthetic_brain.hardware_pipeline import (
    AnalogFrontEndConfig,
    Digitizer,
    PIPELINE_FORMAT,
    PacketStorage,
    QualityFlag,
    SyncClock,
    TransportPacket,
)


class TestAnalogFrontEndConfig:
    def test_valid_config(self) -> None:
        config = AnalogFrontEndConfig()
        assert config.gain == 100.0

    def test_rejects_bad_gain(self) -> None:
        with pytest.raises(ValueError):
            AnalogFrontEndConfig(gain=0.0)

    def test_rejects_inverted_band(self) -> None:
        with pytest.raises(ValueError):
            AnalogFrontEndConfig(high_pass_hz=600.0, low_pass_hz=500.0)


class TestDigitizer:
    def test_samples_are_timestamped(self) -> None:
        digitizer = Digitizer(1000.0, 1)
        samples = digitizer.digitize([1.0, 2.0, 3.0], 0, start_ns=0)
        assert [sample.timestamp_ns for sample in samples] == [0, 1_000_000, 2_000_000]
        assert all(sample.quality == QualityFlag.OK for sample in samples)

    def test_dropped_sample_detection(self) -> None:
        digitizer = Digitizer(1000.0, 1)
        digitizer.digitize([1.0], 0, start_ns=0)
        samples = digitizer.digitize([2.0], 0, start_ns=10_000_000)
        assert samples[0].quality == QualityFlag.DROPPED

    def test_channel_range(self) -> None:
        digitizer = Digitizer(1000.0, 2)
        with pytest.raises(ValueError):
            digitizer.digitize([1.0], 5, start_ns=0)


class TestSyncClock:
    def test_align_maps_to_common_timebase(self) -> None:
        clock = SyncClock(epoch_ns=1_000)
        assert clock.align(1_500) == 500

    def test_drift_correction(self) -> None:
        clock = SyncClock(epoch_ns=0, drift_ppm=100.0)
        assert clock.align(1_000_000) == 999_900


class TestTransportPacket:
    def test_create_fills_schema(self) -> None:
        packet = TransportPacket.create(3, 123, (1.5, -2.5), "µV", 0, "mea-1")
        assert packet.schema == PIPELINE_FORMAT

    def test_json_roundtrip(self) -> None:
        packet = TransportPacket.create(3, 123, (1.5, -2.5), "µV", 0, "mea-1")
        restored = TransportPacket.from_json(packet.to_json())
        assert restored == packet

    def test_rejects_wrong_schema(self) -> None:
        with pytest.raises(ValueError):
            TransportPacket.create(0, 0, (), "µV", 0, "s").from_json(
                json.dumps({"schema": "other", "channel": 0, "timestamp_ns": 0,
                            "samples": [], "units": "µV", "quality": 0, "source_id": "s"})
            )


class TestPacketStorage:
    def test_raw_and_derived(self) -> None:
        storage = PacketStorage()
        packet = TransportPacket.create(0, 1, (1.0,), "µV", 0, "s")
        storage.append(packet)
        assert storage.raw() == (packet,)
        assert storage.derived(lambda pk: pk.samples[0], "peak") == [1.0]

    def test_schema_mismatch(self) -> None:
        storage = PacketStorage()
        bad = TransportPacket.create(0, 0, (), "µV", 0, "s")
        object.__setattr__(bad, "schema", "bad")
        with pytest.raises(ValueError):
            storage.append(bad)
