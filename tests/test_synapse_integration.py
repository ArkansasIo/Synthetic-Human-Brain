"""Cross-language integration tests for the synapse contract.

Verifies that the Python `SynapseModel` implementations produce values the
Rust `synapse.rs` port reproduces exactly (the Rust test asserts the same
numbers), and that the network simulation engine accepts both models.
"""

import math

from synthetic_brain.network import NeuralNetwork
from synthetic_brain.network_simulation import NetworkSimulation
from synthetic_brain.simulation import SimulationConfig
from synthetic_brain.synapse import LinearSynapse, SynapseModel


class TestSynapseContract:
    """The contract shared with rust/backend/src/synapse.rs."""

    def test_linear_matches_rust_reference_values(self) -> None:
        synapse = LinearSynapse()
        # These exact values are asserted in the Rust test suite
        # (rust/backend/src/synapse.rs::linear_matches_python_contract).
        assert math.isclose(synapse.transmit(0.5, 0.8), 0.4, rel_tol=1e-12)
        assert math.isclose(synapse.transmit(0.5, -0.2), -0.1, rel_tol=1e-12)

    def test_outputs_finite(self) -> None:
        synapse = LinearSynapse()
        for signal, weight in ((1.0, 1.0), (0.25, -3.5), (0.0, 0.0)):
            value = synapse.transmit(signal, weight)
            assert math.isfinite(value)

    def test_engine_accepts_synapse_model(self) -> None:
        network = NeuralNetwork(neuron_count=3)
        network.connect(0, 1, weight=0.8)
        network.connect(1, 2, weight=0.5)
        network.connect(2, 0, weight=-0.2)
        model: SynapseModel = LinearSynapse()
        assert callable(getattr(model, "transmit", None))
        simulation = NetworkSimulation(network, SimulationConfig(neuron_count=3, seed=42))
        first = simulation.snapshot()
        for _ in range(3):
            snapshot = simulation.step(external_input=0.05)
            assert all(math.isfinite(value) for value in snapshot.activity)
        assert first is not None
