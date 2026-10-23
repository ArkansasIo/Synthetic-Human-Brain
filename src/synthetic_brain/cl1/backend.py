"""Backend-neutral CL1 compatibility interfaces."""
from __future__ import annotations

from enum import Enum
from typing import Protocol


class BackendKind(str, Enum):
    SYNTHETIC = "synthetic"
    CL1_SIMULATOR = "cl1_simulator"
    CL1_REPLAY = "cl1_replay"
    CL1 = "cl1"


class CL1Backend(Protocol):
    kind: BackendKind

    def start(self) -> None: ...
    def stop(self) -> None: ...
    def step(self, duration_ms: float) -> None: ...
    def spikes(self): ...
    def stimulate(self, command) -> None: ...
