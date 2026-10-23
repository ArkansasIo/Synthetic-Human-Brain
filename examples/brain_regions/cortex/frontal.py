"""Computational example for frontal cortical functions."""
from dataclasses import dataclass

@dataclass
class FrontalCortexExample:
    planning_signal: float = 0.0
    inhibition: float = 0.5

    def step(self, goal: float, dt: float = 0.01) -> float:
        self.planning_signal += (goal - self.planning_signal) * min(1.0, dt * 10.0)
        return max(0.0, self.planning_signal - self.inhibition)

if __name__ == "__main__":
    model = FrontalCortexExample()
    for _ in range(10):
        print(model.step(1.0))
