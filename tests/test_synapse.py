"""Tests for abstract synapse models."""

from synthetic_brain.synapse import LinearSynapse


def test_linear_synapse_transmits_weighted_signal() -> None:
    synapse = LinearSynapse(gain=2.0)
    assert synapse.transmit(0.25, 0.4) == 0.2
