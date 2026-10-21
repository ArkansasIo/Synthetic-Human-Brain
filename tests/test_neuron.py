"""Tests for pluggable abstract neuron models."""

import pytest

from synthetic_brain.neuron import LeakyRateNeuron


def test_leaky_rate_neuron_updates_and_clamps() -> None:
    neuron = LeakyRateNeuron(decay=0.5)
    assert neuron.update(0.4, 0.2, 1.0) == 0.4
    assert neuron.update(0.9, 1.0, 1.0) == 1.0
    assert neuron.update(0.1, -2.0, 1.0) == 0.0


@pytest.mark.parametrize("decay", [-0.1, 1.1])
def test_invalid_decay_is_rejected(decay: float) -> None:
    with pytest.raises(ValueError, match="decay"):
        LeakyRateNeuron(decay=decay)


def test_invalid_range_is_rejected() -> None:
    with pytest.raises(ValueError, match="minimum"):
        LeakyRateNeuron(minimum=1.0, maximum=1.0)
