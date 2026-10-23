from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Program:
    statements: list[object] = field(default_factory=list)

@dataclass
class Return:
    expression: object

@dataclass
class Literal:
    value: object

@dataclass
class Name:
    value: str

@dataclass
class Binary:
    left: object
    operator: str
    right: object

@dataclass
class Call:
    target: object
    arguments: list[object]

@dataclass
class Function:
    name: str
    parameters: list[str]
    body: list[object]

@dataclass
class Object:
    name: str
    properties: list[str]
    functions: list[Function]
