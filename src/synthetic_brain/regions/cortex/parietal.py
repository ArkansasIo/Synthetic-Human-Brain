"""Parietal cortex model boundary for somatosensory/spatial integration."""
from dataclasses import dataclass

@dataclass
class ParietalCortex:
    sensory_state: float = 0.0
    spatial_state: float = 0.0

    def step(self, sensory: float, spatial: float) -> None:
        self.sensory_state = sensory
        self.spatial_state = spatial
