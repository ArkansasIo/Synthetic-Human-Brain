"""Multicompartment neuron and passive cable primitives.

This layer represents morphology explicitly enough to connect compartmental
models to the existing point-neuron and receptor APIs. It is not a substitute
for experimentally fitted ion-channel distributions.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from synthetic_brain.algorithms import cable_diffusion_step


@dataclass
class Compartment:
    """Single electrically coupled compartment."""

    name: str
    length_um: float = 10.0
    diameter_um: float = 2.0
    voltage_mV: float = -65.0
    leak: float = 0.0
    axial_coupling: float = 0.1
    metadata: dict[str, str] = field(default_factory=dict)

    @property
    def surface_area_um2(self) -> float:
        return 3.141592653589793 * self.diameter_um * self.length_um

    def __post_init__(self) -> None:
        if self.length_um <= 0 or self.diameter_um <= 0:
            raise ValueError("compartment dimensions must be positive")


@dataclass
class CompartmentTree:
    """One-dimensional approximation of a neuron morphology."""

    compartments: list[Compartment] = field(default_factory=list)

    def add(self, compartment: Compartment) -> None:
        if any(existing.name == compartment.name for existing in self.compartments):
            raise ValueError(f"compartment already exists: {compartment.name}")
        self.compartments.append(compartment)

    def voltages(self) -> list[float]:
        return [compartment.voltage_mV for compartment in self.compartments]

    def step(self, dt: float, coupling: float | None = None, leak: float | None = None) -> list[float]:
        if dt <= 0:
            raise ValueError("dt must be positive")
        if not self.compartments:
            return []
        coupling_value = coupling if coupling is not None else self.compartments[0].axial_coupling
        leak_value = leak if leak is not None else self.compartments[0].leak
        values = cable_diffusion_step(self.voltages(), coupling_value, leak_value, dt)
        for compartment, voltage in zip(self.compartments, values):
            compartment.voltage_mV = voltage
        return values


@dataclass(frozen=True)
class MorphologyEdge:
    parent: str
    child: str
    branch_order: int = 0


@dataclass
class NeuronMorphology:
    """Named compartments plus explicit parent-child topology."""

    name: str
    tree: CompartmentTree = field(default_factory=CompartmentTree)
    edges: list[MorphologyEdge] = field(default_factory=list)

    def connect(self, parent: str, child: str, branch_order: int = 0) -> None:
        names = {compartment.name for compartment in self.tree.compartments}
        if parent not in names or child not in names:
            raise KeyError("parent and child compartments must exist")
        self.edges.append(MorphologyEdge(parent, child, branch_order))


__all__ = ["Compartment", "CompartmentTree", "MorphologyEdge", "NeuronMorphology"]
