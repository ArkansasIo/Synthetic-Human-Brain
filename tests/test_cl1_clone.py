from synthetic_brain.cl1_clone import SAMPLE_RATE_HZ, ChannelSet, StimDesign, open


def test_clone_closed_loop_is_deterministic() -> None:
    with open(channel_count=4, seed=42) as neurons:
        first = list(neurons.loop(1000, stop_after_ticks=3))
    with open(channel_count=4, seed=42) as neurons:
        second = list(neurons.loop(1000, stop_after_ticks=3))

    assert first[0].iteration_timestamp == 0
    assert first[1].iteration_timestamp == SAMPLE_RATE_HZ // 1000
    assert [tick.analysis.spikes for tick in first] == [tick.analysis.spikes for tick in second]


def test_clone_stimulation_and_recording() -> None:
    with open(channel_count=4, seed=7) as neurons:
        recording = neurons.record(experiment="unit")
        neurons.stim(ChannelSet(0, 1), StimDesign(160, -1.0, 160, 1.0))
        ticks = list(neurons.loop(1000, stop_after_ticks=2))
        recording.stop()

    assert any(tick.analysis.stims for tick in ticks)
    assert recording.stims
    assert recording.attributes["channel_count"] == 4
