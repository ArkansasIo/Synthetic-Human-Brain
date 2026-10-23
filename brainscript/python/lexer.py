from __future__ import annotations

from dataclasses import dataclass
import re


@dataclass(frozen=True)
class Token:
    kind: str
    value: str
    line: int
    column: int


_TOKEN = re.compile(
    r'(?P<SPACE>[ \t]+)|(?P<COMMENT>#[^\n]*)|(?P<NUMBER>\d+(?:\.\d+)?)|'
    r'(?P<STRING>"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\')|'
    r'(?P<OP>==|!=|<=|>=|=>|[+\-*/%<>=:(),.])|(?P<IDENT>[A-Za-z_][A-Za-z0-9_]*)|(?P<NEWLINE>\n)'
)

KEYWORDS = {"object", "property", "function", "lambda", "if", "else", "end", "return", "true", "false", "and", "or", "not"}


def tokenize(source: str) -> list[Token]:
    tokens: list[Token] = []
    line = 1
    column = 1
    pos = 0
    while pos < len(source):
        match = _TOKEN.match(source, pos)
        if not match:
            raise SyntaxError(f"Unexpected character at {line}:{column}: {source[pos]!r}")
        kind = match.lastgroup or ""
        value = match.group()
        if kind not in {"SPACE", "COMMENT"}:
            if kind == "IDENT" and value in KEYWORDS:
                kind = value.upper()
            tokens.append(Token(kind, value, line, column))
        newlines = value.count("\n")
        if newlines:
            line += newlines
            column = len(value.rsplit("\n", 1)[-1]) + 1
        else:
            column += len(value)
        pos = match.end()
    tokens.append(Token("EOF", "", line, column))
    return tokens
