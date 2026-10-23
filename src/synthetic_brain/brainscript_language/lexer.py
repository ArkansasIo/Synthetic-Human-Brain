"""Readable, deterministic BrainScript lexer.

This module only tokenizes source; it does not execute scripts or access devices.
"""
from __future__ import annotations

from dataclasses import dataclass


KEYWORDS = {
    "and", "or", "not", "true", "false", "nil", "var", "let", "const",
    "fn", "function", "class", "extends", "return", "if", "else", "elseif",
    "while", "for", "in", "brain", "population", "connect", "weight", "delay",
    "stimulus", "emit", "record", "step", "backend", "region", "experiment",
    "observe", "init", "self", "this",
}
OPERATORS = (
    "==", "~=", "!=", "<=", ">=", "..", "->",
    "+", "-", "*", "/", "%", "=", "<", ">",
)


@dataclass(frozen=True, slots=True)
class Token:
    kind: str
    lexeme: str
    literal: object | None = None
    line: int = 1
    column: int = 1


class BrainSyntaxError(SyntaxError):
    """Source syntax error with a line and column location."""


def tokenize(source: str) -> list[Token]:
    """Convert BrainScript source text into tokens, retaining source locations."""
    if not isinstance(source, str):
        raise TypeError("source must be a string")

    tokens: list[Token] = []
    i = 0
    line = 1
    column = 1

    def advance() -> str:
        nonlocal i, line, column
        char = source[i] if i < len(source) else ""
        i += 1
        if char == "\n":
            line += 1
            column = 1
        else:
            column += 1
        return char

    while i < len(source):
        char = source[i]
        if char.isspace():
            advance()
            continue

        start_line, start_column = line, column

        if source.startswith("--", i) or source.startswith("//", i):
            advance()
            advance()
            while i < len(source) and source[i] != "\n":
                advance()
            continue

        if char in "'\"":
            quote = advance()
            value: list[str] = []
            while i < len(source) and source[i] != quote:
                current = advance()
                if current == "\\" and i < len(source):
                    escaped = advance()
                    value.append({
                        "n": "\n", "r": "\r", "t": "\t",
                        "\\": "\\", "\"": "\"",
                        "'": "'",
                    }.get(escaped, escaped))
                else:
                    value.append(current)
            if i >= len(source):
                raise BrainSyntaxError(
                    f"Unterminated string at {start_line}:{start_column}"
                )
            advance()
            lexeme = "".join(value)
            tokens.append(Token("string", lexeme, lexeme, start_line, start_column))
            continue

        if char.isdigit():
            start = i
            while i < len(source) and source[i].isdigit():
                advance()
            if (
                i + 1 < len(source)
                and source[i] == "."
                and source[i + 1].isdigit()
            ):
                advance()
                while i < len(source) and source[i].isdigit():
                    advance()
            lexeme = source[start:i]
            literal = float(lexeme) if "." in lexeme else int(lexeme)
            tokens.append(Token("number", lexeme, literal, start_line, start_column))
            continue

        if char.isalpha() or char == "_":
            start = i
            advance()
            while i < len(source) and (source[i].isalnum() or source[i] == "_"):
                advance()
            word = source[start:i]
            if word in KEYWORDS:
                literal = {"true": True, "false": False, "nil": None}.get(word)
                tokens.append(Token("keyword", word, literal, start_line, start_column))
            else:
                tokens.append(Token("identifier", word, None, start_line, start_column))
            continue

        operator = next(
            (candidate for candidate in OPERATORS if source.startswith(candidate, i)),
            None,
        )
        if operator is not None:
            for _ in operator:
                advance()
            tokens.append(
                Token("operator", operator, None, start_line, start_column)
            )
            continue

        if char in ";,.:(){}[]":
            advance()
            tokens.append(
                Token("punctuation", char, None, start_line, start_column)
            )
            continue

        raise BrainSyntaxError(
            f"Unexpected character {char!r} at {start_line}:{start_column}"
        )

    tokens.append(Token("eof", "", None, line, column))
    return tokens


__all__ = ["BrainSyntaxError", "KEYWORDS", "OPERATORS", "Token", "tokenize"]
