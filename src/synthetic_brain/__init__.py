"""Abstract, reproducible neural simulation toolkit.

This package is a research scaffold, not a biologically complete brain model.
"""

from synthetic_brain.config import SimulationConfig
from synthetic_brain.network import Connection, NeuralNetwork
from synthetic_brain.network_simulation import NetworkSimulation, NetworkSimulationSnapshot
from synthetic_brain.neuron import LeakyRateNeuron, NeuronModel
from synthetic_brain.simulation import Simulation, SimulationSnapshot
from synthetic_brain.synapse import LinearSynapse, SynapseModel

__all__ = [
    "Connection",
    "LeakyRateNeuron",
    "LinearSynapse",
    "NetworkSimulation",
    "NetworkSimulationSnapshot",
    "NeuralNetwork",
    "NeuronModel",
    "Simulation",
    "SimulationConfig",
    "SimulationSnapshot",
    "SynapseModel",
]
__version__ = "0.1.1"
