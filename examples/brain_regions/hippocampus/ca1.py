"""Computational CA1 example: integrate input traces and emit sparse events."""
from dataclasses import dataclass, field

@dataclass
class CA1Example:
    membrane: float = 0.0
    threshold: float = 1.0
    trace: list[float] = field(default_factory=list)

    def step(self, input_current: float, dt: float = 0.01) -> bool:
        self.membrane += dt * (-self.membrane + input_current)
        fired = self.membrane >= self.threshold
        if fired:
            self.trace.append(self.membrane)
            self.membrane = 0.0
        return fired

if __name__ == "__main__":
    model = CA1Example()
    for _ in range(200):
        if model.step(2.0):
            print("CA1 spike")
