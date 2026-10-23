from synthetic_brain.cl1_simulator import (
    SAMPLE_RATE_HZ,
    BurstDesign,
    ChannelSet,
    StimDesign,
    open as cl1_open,
)


def test_channel_set_and_stim_design() -> None:
    assert ChannelSet(1, 2, 2) == (1, 2)
    assert StimDesign(160, -1.0, 160, 1.0).segments == ((160, -1.0), (160, 1.0))
    assert BurstDesign(3, 20).count == 3


def test_deterministic_closed_loop() -> None:
    with cl1_open(channel_count=4, seed=42) as neurons:
        ticks = list(neurons.loop(1000, stop_after_ticks=3))
    assert len(ticks) == 3
    assert ticks[0].iteration == 0
    assert ticks[1].iteration_timestamp == SAMPLE_RATE_HZ // 1000


def test_stimulation_and_recording(tmp_path) -> None:
    with cl1_open(channel_count=4, seed=7) as neurons:
        recording = neurons.record(file_location=str(tmp_path), file_suffix="cl1")
        neurons.stim(ChannelSet(0, 1), StimDesign(160, -1, 160, 1), BurstDesign(2, 20))
        ticks = list(neurons.loop(1000, stop_after_ticks=5))
        recording.stop()

    assert any(tick.analysis.stims for tick in ticks)
    assert recording.path is not None
    assert recording.path.exists()
