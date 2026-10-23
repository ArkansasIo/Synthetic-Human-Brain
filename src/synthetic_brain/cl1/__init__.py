"""Project-owned CL1 compatibility package.

This package provides a software abstraction around the public CL1 concepts used by
Synthetic Human Brain. It does not contain Cortical Labs proprietary implementation.
"""

from .backend import BackendKind, CL1Backend
from .session import CL1Session
from .spikes import SpikeEvent
from .stimulation import StimulusCommand
from .recording import RecordingFrame
from .closed_loop import ClosedLoopController

__all__ = [
    "BackendKind",
    "CL1Backend",
    "CL1Session",
    "SpikeEvent",
    "StimulusCommand",
    "RecordingFrame",
    "ClosedLoopController",
]
