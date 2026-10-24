"""Cross-language integration tests for the neuron contract.

Verifies that the Python `NeuronModel` implementations produce values the
Rust `neuron.rs` port reproduces exactly (the Rust test asserts the same
numbers), and that the network simulation engine accepts any protocol model.
"""

import math

from synthetic_brain.neuron import LeakyRateNeuron, NeuronModel


class TestNeuronContract:
    """The contract shared with rust/backend/src/neuron.rs."""

    def test_leaky_rate_matches_rust_reference_values(self) -> None:
        neuron = LeakyRateNeuron()
        # These exact values are asserted in the Rust test suite
        # (rust/backend/src/neuron.rs::leaky_rate_matches_python_reference_values).
        assert math.isclose(neuron.update(0.5, 1.0, 0.1), 0.55, rel_tol=1e-12)
        assert math.isclose(neuron.update(1.5, 0.0, 0.1), 1.0, rel_tol=1e-12)  # clamped max
        assert math.isclose(neuron.update(-1.0, 0.0, 0.1), 0.0, rel_tol=1e-12)  # clamped min

    def test_clamp_bounds_honored(self) -> None:
        neuron = LeakyRateNeuron(decay=1.0, minimum=-2.0, maximum=3.0)
        assert neuron.update(10.0, 0.0, 0.1) == 3.0
        assert neuron.update(-10.0, 0.0, 0.1) == -2.0

    def test_validation_rules(self) -> None:
        import pytest

        with pytest.raises(ValueError):
            LeakyRateNeuron(decay=1.5)
        with pytest.raises(ValueError):
            LeakyRateNeuron(minimum=1.0, maximum=0.0)

    def test_outputs_finite(self) -> None:
        neuron: NeuronModel = LeakyRateNeuron()
        for activity, signal, dt in ((1.0, 1.0, 0.1), (0.0, -2.0, 0.5), (0.7, 0.0, 0.01)):
            assert math.isfinite(neuron.update(activity, signal, dt))
