"""Behavioral tests for the abstract simulation starter."""

import math

import pytest

from synthetic_brain import Simulation, SimulationConfig


def test_seed_makes_initial_state_reproducible() -> None:
    first = Simulation(SimulationConfig(seed=123))
    second = Simulation(SimulationConfig(seed=123))
    assert first.snapshot() == second.snapshot()


def test_step_advances_counter_and_preserves_shape() -> None:
    simulation = Simulation(SimulationConfig(neuron_count=4))
    result = simulation.step()
    assert result.step == 1
    assert len(result.activity) == 4


def test_activity_remains_bounded() -> None:
    simulation = Simulation(SimulationConfig(neuron_count=5))
    for _ in range(20):
        result = simulation.step(external_input=0.2)
        assert all(0.0 <= activity <= 1.0 for activity in result.activity)


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"neuron_count": 0}, "neuron_count"),
        ({"time_step": 0}, "time_step"),
        ({"decay": -0.1}, "decay"),
        ({"decay": 1.1}, "decay"),
        ({"neuron_count": True}, "neuron_count"),
        ({"time_step": float("nan")}, "time_step"),
        ({"decay": float("inf")}, "decay"),
        ({"seed": 2.5}, "seed"),
    ],
)
def test_invalid_configuration_is_rejected(kwargs: dict, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        SimulationConfig(**kwargs)


@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf, "bad", True, 10**10000])
def test_invalid_external_input_is_rejected(value: object) -> None:
    simulation = Simulation(SimulationConfig())
    with pytest.raises((TypeError, ValueError), match="finite number"):
        simulation.step(value)  # type: ignore[arg-type]


def test_snapshot_is_immutable_tuple() -> None:
    simulation = Simulation(SimulationConfig())
    assert isinstance(simulation.snapshot().activity, tuple)
    with pytest.raises(AttributeError):
        simulation.snapshot().activity.append(0.5)  # type: ignore[attr-defined]
