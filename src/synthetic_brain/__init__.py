"""Abstract, reproducible neural simulation toolkit.

This package is a research scaffold, not a biologically complete brain model.
"""

from synthetic_brain.config import SimulationConfig
from synthetic_brain.simulation import Simulation, SimulationSnapshot

__all__ = ["Simulation", "SimulationConfig", "SimulationSnapshot"]
__version__ = "0.1.0"
