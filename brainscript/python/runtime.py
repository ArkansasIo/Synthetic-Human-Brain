from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class BrainObject:
    name: str
    properties: dict[str, Any]


class BrainScriptRuntime:
    """Small deterministic expression runtime used by the first BrainScript prototype.

    The language intentionally starts with safe arithmetic, comparisons, variables,
    and Python-callable functions. File execution is not Python eval and has no
    access to imports, filesystem APIs, or arbitrary Python statements.
    """

    def __init__(self) -> None:
        self.globals: dict[str, Any] = {
            "true": True,
            "false": False,
            "odd": lambda n: int(n) % 2 != 0,
            "even": lambda n: int(n) % 2 == 0,
            "prime": self.is_prime,
        }

    @staticmethod
    def is_prime(number: int) -> bool:
        n = int(number)
        if n < 2:
            return False
        if n == 2:
            return True
        if n % 2 == 0:
            return False
        divisor = 3
        while divisor * divisor <= n:
            if n % divisor == 0:
                return False
            divisor += 2
        return True

    def classify_number(self, number: int) -> str:
        if number < 2:
            return "neither"
        if self.is_prime(number):
            return "prime"
        return "even" if number % 2 == 0 else "odd"

    def execute_example(self, numbers: list[int]) -> list[dict[str, Any]]:
        return [
            {
                "number": n,
                "classification": self.classify_number(n),
                "is_even": n % 2 == 0,
                "is_odd": n % 2 != 0,
                "is_prime": self.is_prime(n),
            }
            for n in numbers
        ]
