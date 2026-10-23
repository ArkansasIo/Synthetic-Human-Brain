"""Project-owned CL1 compatibility package.

This package provides a software abstraction around public CL1 concepts used by
Synthetic Human Brain. It does not contain Cortical Labs proprietary implementation.
"""

from .backend import BackendKind, CL1Backend
from .session import CL1Session
from .spikes import SpikeEvent
from .stimulation import StimulusCommand
from .recording import RecordingFrame
from .closed_loop import ClosedLoopController
from .compat import CL1Bridge, CL1Connection, CL1Spike, CL1Stimulus, CL1Tick, cl1_available, monotonic_event_timestamp

__all__ = [
    "BackendKind",
    "CL1Backend",
    "CL1Session",
    "SpikeEvent",
    "StimulusCommand",
    "RecordingFrame",
    "ClosedLoopController",
    "CL1Bridge",
    "CL1Connection",
    "CL1Spike",
    "CL1Stimulus",
    "CL1Tick",
    "cl1_available",
    "monotonic_event_timestamp",
]
