from synthetic_brain.cl1_clone import ChannelSet, StimDesign
from synthetic_brain.cl1_experiment import CL1Experiment, ExperimentConfig


def test_experiment_baseline() -> None:
    result = CL1Experiment(ExperimentConfig(channel_count=4, ticks=3, seed=10)).baseline()
    assert len(result.ticks) == 3
    assert result.config.name == "cl1-experiment"


def test_experiment_stimulation() -> None:
    result = CL1Experiment(ExperimentConfig(channel_count=4, ticks=4, seed=10)).stimulated(
        ChannelSet(0), StimDesign(160, -1.0, 160, 1.0)
    )
    assert result.stims
