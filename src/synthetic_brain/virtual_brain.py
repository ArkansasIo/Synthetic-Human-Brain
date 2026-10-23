"""Virtual Synthetic Human Brain runtime facade.

Provides a deterministic software representation of the project's brain architecture.
It composes regions, populations, simulation state, cognition, sensory/motor IO,
and pluggable neural substrates behind one host API.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class BrainState:
    time: float = 0.0
    mode: str = "idle"
    sensory_events: list[dict[str, Any]] = field(default_factory=list)
    motor_commands: list[dict[str, Any]] = field(default_factory=list)
    metrics: dict[str, float] = field(default_factory=dict)


class VirtualBrain:
    """High-level virtual brain orchestration API."""

    def __init__(self, name: str = "SyntheticHumanBrain") -> None:
        self.name = name
        self.state = BrainState()
        self.regions: dict[str, Any] = {}
        self.connections: list[dict[str, Any]] = []
        self.running = False

    def register_region(self, name: str, region: Any) -> None:
        self.regions[name] = region

    def connect(self, source: str, target: str, weight: float = 1.0) -> None:
        self.connections.append({"source": source, "target": target, "weight": weight})

    def ingest(self, modality: str, payload: Any) -> None:
        self.state.sensory_events.append({"modality": modality, "payload": payload, "time": self.state.time})

    def step(self, dt: float = 1.0) -> BrainState:
        if dt <= 0:
            raise ValueError("dt must be positive")
        self.state.time += dt
        self.state.mode = "running"
        for region in self.regions.values():
            update = getattr(region, "step", None) or getattr(region, "update", None)
            if callable(update):
                update(dt)
        return self.state

    def run(self, duration: float, dt: float = 1.0) -> BrainState:
        if duration < 0:
            raise ValueError("duration must be non-negative")
        self.running = True
        steps = int(duration / dt)
        for _ in range(steps):
            self.step(dt)
        self.running = False
        self.state.mode = "paused"
        return self.state

    def reset(self) -> None:
        self.state = BrainState()
        self.running = False

    def snapshot(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "time": self.state.time,
            "mode": self.state.mode,
            "regions": list(self.regions),
            "connections": list(self.connections),
            "metrics": dict(self.state.metrics),
        }
