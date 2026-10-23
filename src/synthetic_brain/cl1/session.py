from __future__ import annotations
from dataclasses import dataclass
from .backend import BackendKind

@dataclass
class CL1Session:
    backend: BackendKind = BackendKind.CL1_SIMULATOR
    running: bool = False

    def start(self) -> None:
        self.running = True

    def stop(self) -> None:
        self.running = False
