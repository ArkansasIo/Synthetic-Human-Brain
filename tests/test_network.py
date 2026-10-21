"""Tests for weighted network connectivity."""

import math

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


@pytest.mark.parametrize("weight", ["bad", True, math.nan, math.inf])
def test_invalid_weights_are_rejected(weight: object) -> None:
    network = NeuralNetwork(2)
    with pytest.raises((TypeError, ValueError), match="weight"):
        network.connect(0, 1, weight)  # type: ignore[arg-type]


def test_invalid_network_size_is_rejected() -> None:
    with pytest.raises(TypeError, match="neuron_count"):
        NeuralNetwork(True)
    with pytest.raises(ValueError, match="neuron_count"):
        NeuralNetwork(0)
