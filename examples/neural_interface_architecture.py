"""Minimal software-side example for the whole-brain interface architecture.

This example is deliberately backend-neutral: it demonstrates how measured data,
region mapping, and a synthetic brain substrate can be composed without requiring
physical hardware or a vendor SDK.
"""
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class SignalSample:
    channel: str
    timestamp: float
    value: float
    unit: str = "arbitrary"
    region: str | None = None


class NeuralSubstrate(Protocol):
    def record(self) -> list[SignalSample]: ...
    def step(self, dt: float) -> None: ...


class ReplaySubstrate:
    def __init__(self, samples: list[SignalSample]) -> None:
        self.samples = samples

    def record(self) -> list[SignalSample]:
        return list(self.samples)

    def step(self, dt: float) -> None:
        del dt


class RegionMapper:
    """Maps observation channels to model regions; it does not claim neuron identity."""

    def __init__(self, mapping: dict[str, str]) -> None:
        self.mapping = mapping

    def map(self, sample: SignalSample) -> SignalSample:
        return SignalSample(
            channel=sample.channel,
            timestamp=sample.timestamp,
            value=sample.value,
            unit=sample.unit,
            region=self.mapping.get(sample.channel),
        )


def main() -> None:
    substrate = ReplaySubstrate(
        [
            SignalSample("EEG-F3", 0.000, 0.12),
            SignalSample("EEG-P3", 0.001, 0.08),
        ]
    )
    mapper = RegionMapper({"EEG-F3": "frontal_cortex", "EEG-P3": "parietal_cortex"})

    for sample in substrate.record():
        print(mapper.map(sample))


if __name__ == "__main__":
    main()
