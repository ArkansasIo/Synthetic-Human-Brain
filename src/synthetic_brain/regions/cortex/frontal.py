"""Frontal cortex model boundary: executive, motor, planning, inhibition."""
from dataclasses import dataclass

@dataclass
class FrontalCortex:
    executive_state: float = 0.0
    motor_drive: float = 0.0

    def step(self, executive_input: float, motor_input: float) -> None:
        self.executive_state = executive_input
        self.motor_drive = motor_input
