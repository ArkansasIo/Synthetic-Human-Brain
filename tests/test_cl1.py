from types import SimpleNamespace

from synthetic_brain.cl1 import CL1Bridge, CL1Spike, CL1Stimulus, CL1Tick, cl1_available


class FakeNeurons:
    def __init__(self) -> None:
        self.stim_calls = []

    def record(self, **kwargs):
        return kwargs

    def stim(self, channels, stim_design, burst_design=None):
        self.stim_calls.append((channels, stim_design, burst_design))

    def loop(self, ticks_per_second, **kwargs):
        assert ticks_per_second == 100
        assert kwargs["stop_after_ticks"] == 2
        return iter(
            [
                SimpleNamespace(
                    iteration=0,
                    iteration_timestamp=100,
                    analysis=SimpleNamespace(
                        spikes=[SimpleNamespace(timestamp=90, channel=3)],
                        stims=[SimpleNamespace(timestamp=80, channel=7)],
                    ),
                ),
                SimpleNamespace(
                    iteration=1,
                    iteration_timestamp=200,
                    analysis=SimpleNamespace(spikes=[], stims=[]),
                ),
            ]
        )


def test_cl1_event_types():
    spike = CL1Spike(timestamp=1, channel=2)
    stim = CL1Stimulus(timestamp=3, channel=4)
    tick = CL1Tick(iteration=0, timestamp=5, spikes=(spike,), stims=(stim,))
    assert tick.spikes[0].channel == 2
    assert tick.stims[0].channel == 4


def test_closed_loop_normalizes_events():
    bridge = CL1Bridge(FakeNeurons(), simulator=True)
    seen = []
    ticks = bridge.closed_loop(100, stop_after_ticks=2, on_tick=seen.append)
    assert len(ticks) == 2
    assert ticks[0].spikes == (CL1Spike(timestamp=90, channel=3),)
    assert ticks[0].stims == (CL1Stimulus(timestamp=80, channel=7),)
    assert seen == ticks


def test_stimulation_is_forwarded_without_hidden_parameters():
    neurons = FakeNeurons()
    bridge = CL1Bridge(neurons)
    bridge.stimulate((1, 2), "explicit-design", "explicit-burst")
    assert neurons.stim_calls == [((1, 2), "explicit-design", "explicit-burst")]


def test_cl1_availability_is_boolean():
    assert isinstance(cl1_available(), bool)
