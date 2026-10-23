from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class StimulusCommand:
    channel: int
    timestamp: float
    waveform: tuple[tuple[float, float], ...] = ()
    label: str = ""
