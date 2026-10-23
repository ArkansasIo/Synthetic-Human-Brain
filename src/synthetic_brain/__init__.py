"""Abstract, reproducible neural simulation toolkit.

This package is a research scaffold, not a biologically complete brain model.
"""

from synthetic_brain.algorithms import (
    AdExNeuron, ConductanceSynapse, HodgkinHuxleyNeuron, IzhikevichNeuron,
    LIFNeuron, TsodyksMarkramSynapse, WorkingMemoryTrace, bcm_update,
    cable_diffusion_step, divisive_normalization, hebbian_update,
    homeostatic_update, hopfield_hebbian, hopfield_update, kuramoto_step,
    oja_update, poisson_spike_train, predictive_coding_update, rk4_step,
    softmax, stdp_update, td_error, td_update, wilson_cowan_step,
)
from synthetic_brain.config import SimulationConfig
from synthetic_brain.network import Connection, NeuralNetwork
from synthetic_brain.network_simulation import NetworkSimulation, NetworkSimulationSnapshot
from synthetic_brain.neuromodulation import (
    DEFAULT_NEUROMODULATORS, DopamineSignal, HomeostaticController, Neuromodulator,
)
from synthetic_brain.neuron import LeakyRateNeuron, NeuronModel
from synthetic_brain.receptors import (
    AMPA_CURRENT, GABAA_CURRENT, GABAB_CURRENT, NMDA_CURRENT,
    AMPAReceptor, GABAbReceptor, GABAaReceptor, NMDAReceptor, ReceptorCurrent,
)
from synthetic_brain.regions import BrainNetwork, BrainRegion, NeuralPopulation, RegionConnection
from synthetic_brain.simulation import Simulation, SimulationSnapshot
from synthetic_brain.synapse import LinearSynapse, SynapseModel

__all__ = [
    "AdExNeuron", "AMPA_CURRENT", "AMPAReceptor", "BrainNetwork", "BrainRegion",
    "Connection", "ConductanceSynapse", "DEFAULT_NEUROMODULATORS", "DopamineSignal",
    "GABAA_CURRENT", "GABAB_CURRENT", "GABAbReceptor", "GABAaReceptor",
    "HodgkinHuxleyNeuron", "HomeostaticController", "IzhikevichNeuron", "LIFNeuron",
    "LeakyRateNeuron", "LinearSynapse", "NMDA_CURRENT", "NMDAReceptor",
    "NetworkSimulation", "NetworkSimulationSnapshot", "NeuralNetwork", "NeuralPopulation",
    "NeuronModel", "Neuromodulator", "ReceptorCurrent", "RegionConnection", "Simulation",
    "SimulationConfig", "SimulationSnapshot", "SynapseModel", "TsodyksMarkramSynapse",
    "WorkingMemoryTrace", "bcm_update", "cable_diffusion_step", "divisive_normalization",
    "hebbian_update", "homeostatic_update", "hopfield_hebbian", "hopfield_update",
    "kuramoto_step", "oja_update", "poisson_spike_train", "predictive_coding_update",
    "rk4_step", "softmax", "stdp_update", "td_error", "td_update", "wilson_cowan_step",
]
__version__ = "0.3.0"
