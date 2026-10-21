"""Tests for weighted network connectivity."""

import pytest

from synthetic_brain.network import NeuralNetwork


def test_connect_and_compute_incoming_signal() -> None:
    network = NeuralNetwork(3)
    network.connect(0, 1, 0.5)
    network.connect(2, 1, 2.0)
    assert network.incoming_signal((0.2, 0.0, 0.4)) == (0.0, 0.9, 0.0)


def test_connections_are_immutable_view() -> None:
    network = NeuralNetwork(2)
    network.connect(0, 1)
    assert isinstance(network.connections, tuple)


@pytest.mark.parametrize("source,target", [(2, 0), (0, 2), (-1, 0), (0, -1)])
def test_invalid_nodes_are_rejected(source: int, target: int) -> None:
    network = NeuralNetwork(2)
    with pytest.raises(ValueError, match="node index"):
        network.connect(source, target)


def test_activity_size_must_match_network() -> None:
    network = NeuralNetwork(2)
    with pytest.raises(ValueError, match="activity length"):
        network.incoming_signal((0.1,))
