"""Bridge BrainLang program definitions into the local CL1 experiment layer."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from synthetic_brain.brainlang import BrainRuntime, BrainObject
from synthetic_brain.cl1_clone import Neurons


@dataclass(slots=True)
class BrainLangCL1Program:
    source: str
    environment: Any
    brains: dict[str, BrainObject]


class BrainLangCL1Runner:
    """Compile the currently supported BrainLang structural subset for CL1 tests."""

    def compile(self, source: str) -> BrainLangCL1Program:
        runtime = BrainRuntime()
        environment = runtime.execute(source)
        brains = {
            name: value
            for name, value in environment.values.items()
            if isinstance(value, BrainObject) and "populations" in value.fields
        }
        return BrainLangCL1Program(source, environment, brains)

    def build_neurons(self, program: BrainLangCL1Program, *, seed: int = 0) -> Neurons:
        channel_count = 64
        for brain in program.brains.values():
            populations = brain.fields.get("populations", {})
            requested = sum(int(attrs.get("size", 0)) for attrs in populations.values())
            if requested > 0:
                channel_count = requested
                break
        return Neurons(channel_count=channel_count, seed=seed)


def compile_brainlang_cl1(source: str) -> BrainLangCL1Program:
    return BrainLangCL1Runner().compile(source)


__all__ = ["BrainLangCL1Program", "BrainLangCL1Runner", "compile_brainlang_cl1"]
