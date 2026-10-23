from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class SpikeEvent:
    timestamp: float
    channel: int
    source: str = "cl1"
