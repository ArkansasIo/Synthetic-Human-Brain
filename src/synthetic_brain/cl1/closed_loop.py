from __future__ import annotations
from collections.abc import Callable

class ClosedLoopController:
    """Backend-neutral observe -> decide -> act loop."""
    def __init__(self, observe: Callable, decide: Callable, act: Callable):
        self.observe = observe
        self.decide = decide
        self.act = act

    def tick(self):
        observation = self.observe()
        decision = self.decide(observation)
        self.act(decision)
        return observation, decision
