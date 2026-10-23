from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
from .spikes import SpikeEvent

@dataclass
class RecordingFrame:
    timestamp: float
    spikes: list[SpikeEvent] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
