"""BrainScript: the canonical scripting language for Synthetic Human Brain.

BrainScript is the renamed successor to the repository's original BrainLang DSL.
It is Lua-inspired, object-oriented, dependency-free, and designed for declaring
brain regions, populations, connections, experiments, and simulation logic.

The initial implementation intentionally reuses the proven BrainLang parser/runtime
contract so existing research programs can migrate without changing their semantics.
"""
from __future__ import annotations

from .brainlang import (
    BrainClass,
    BrainLang,
    BrainObject,
    BrainRuntime,
    Environment,
    Parser,
    ReturnSignal,
    Token,
    lex,
)

LANGUAGE_NAME = "BrainScript"
LANGUAGE_EXTENSION = ".brain"
LANGUAGE_VERSION = "0.3.0"

__all__ = [
    "LANGUAGE_NAME",
    "LANGUAGE_EXTENSION",
    "LANGUAGE_VERSION",
    "BrainClass",
    "BrainLang",
    "BrainObject",
    "BrainRuntime",
    "Environment",
    "Parser",
    "ReturnSignal",
    "Token",
    "lex",
]
