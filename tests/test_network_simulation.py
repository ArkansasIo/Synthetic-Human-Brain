"""Tests for the network-driven abstract simulation engine."""

import math

import pytest

from synthetic_brain import (
    LeakyRateNeuron,
    LinearSynapse,
    NeuralNetwork,
    NetworkSimulation,
    SimulationConfig,
)


def make_network() -> NeuralNetwork:
    network = NeuralNetwork(2)
    network.connect(0, 1, weight=0.5)
    network.connect(1, 0, weight=0.25)
    return network


def test_seed_reproduces_initial_and_step_states() -> None:
    first = NetworkSimulation(make_network(), SimulationConfig(neuron_count=2, seed=31))
    second = NetworkSimulation(make_network(), SimulationConfig(neuron_count=2, seed=31))
    assert first.snapshot() == second.snapshot()
    assert first.step() == second.step()


def test_connection_signal_changes_target_activity() -> None:
    network = NeuralNetwork(2)
    network.connect(0, 1, weight=1.0)
    config = SimulationConfig(neuron_count=2, decay=1.0, seed=2)
    model = NetworkSimulation(
        network,
        config,
        neuron_model=LeakyRateNeuron(decay=0.0),
        synapse_model=LinearSynapse(),
    )
    before = model.snapshot()
    after = model.step()
    assert after.activity[1] == pytest.approx(before.activity[0])
    assert after.activity[0] == 0.0


def test_updates_are_synchronous_and_repeatable() -> None:
    network = NeuralNetwork(3)
    network.connect(0, 1, 1.0)
    network.connect(1, 2, 1.0)
    config = SimulationConfig(neuron_count=3, seed=4, decay=0.0)
    first = NetworkSimulation(network, config, neuron_model=LeakyRateNeuron(decay=0.0))
    second = NetworkSimulation(network, config, neuron_model=LeakyRateNeuron(decay=0.0))
    expected = first.step()
    assert second.step() == expected


def test_custom_model_composition_is_supported() -> None:
    network = NeuralNetwork(1)
    simulation = NetworkSimulation(
        network,
        SimulationConfig(neuron_count=1, seed=1),
        neuron_model=LeakyRateNeuron(decay=0.0),
        synapse_model=LinearSynapse(gain=2.0),
    )
    assert len(simulation.step(external_input=0.25).activity) == 1


def test_network_size_must_match_config() -> None:
    with pytest.raises(ValueError, match="must match"):
        NetworkSimulation(NeuralNetwork(2), SimulationConfig(neuron_count=3))


def test_external_input_is_validated() -> None:
    simulation = NetworkSimulation(make_network())
    for invalid in (True, "bad"):
        with pytest.raises(TypeError, match="external_input"):
            simulation.step(invalid)  # type: ignore[arg-type]
    for invalid in (math.nan, math.inf, -math.inf, 10**10000):
        with pytest.raises(ValueError, match="finite number"):
            simulation.step(invalid)


def test_synapse_output_must_be_finite() -> None:
    class BadSynapse:
        def transmit(self, signal: float, weight: float) -> float:
            return math.nan

    simulation = NetworkSimulation(make_network(), synapse_model=BadSynapse())
    with pytest.raises(ValueError, match="synapse output"):
        simulation.step()


def test_neuron_output_must_be_finite() -> None:
    class BadNeuron:
        def update(self, activity: float, input_signal: float, time_step: float) -> float:
            return math.inf

    simulation = NetworkSimulation(make_network(), neuron_model=BadNeuron())
    with pytest.raises(ValueError, match="neuron output"):
        simulation.step()
