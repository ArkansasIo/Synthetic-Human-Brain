"""Lexer for the Python BrainScript implementation."""
from __future__ import annotations
from dataclasses import dataclass
import re

KEYWORDS = {"and","or","not","true","false","nil","var","let","const","fn","function","class","extends","return","if","else","elseif","while","for","in","brain","population","connect","weight","delay","stimulus","emit","record","step","backend","region","experiment","observe","init","self","this"}
OPERATORS = ("==","~=","!=","<=",">=","..","->","+","-","*","/","%","=","<",">")

@dataclass(frozen=True, slots=True)
class Token:
    kind: str
    lexeme: str
    literal: object | None = None
    line: int = 1
    column: int = 1

class BrainSyntaxError(SyntaxError):
    pass

def tokenize(source: str) -> list[Token]:
    out: list[Token] = []
    i = 0; line = 1; column = 1
    def advance() -> str:
        nonlocal i, line, column
        ch = source[i] if i < len(source) else ""
        i += 1
        if ch == "\n": line += 1; column = 1
        else: column += 1
        return ch
    while i < len(source):
        ch = source[i]
        if ch.isspace(): advance(); continue
        sl, sc = line, column
        if source.startswith("--", i) or source.startswith("//", i):
            advance(); advance()
            while i < len(source) and source[i] != "\n": advance()
            continue
        if ch in "'\"":
            quote = advance(); value = ""
            while i < len(source) and source[i] != quote:
                c = advance()
                if c == "\\" and i < len(source):
                    e = advance(); value += {"n":"\n","r":"\r","t":"\t","\\":"\\","\"":"\"","'":"'"}.get(e,e)
                else: value += c
            if i >= len(source): raise BrainSyntaxError(f"Unterminated string at {sl}:{sc}")
            advance(); out.append(Token("string", source, value, sl, sc)); out[-1] = Token("string", value, value, sl, sc); continue
        if ch.isdigit():
            start=i
            while i < len(source) and source[i].isdigit(): advance()
            if i < len(source) and source[i]=="." and i+1 < len(source) and source[i+1].isdigit():
                advance()
                while i < len(source) and source[i].isdigit(): advance()
            lex=source[start:i]; out.append(Token("number",lex,float(lex) if "." in lex else int(lex),sl,sc)); continue
        if ch.isalpha() or ch == "_":
            start=i; advance()
            while i < len(source) and (source[i].isalnum() or source[i]=="_"): advance()
            word=source[start:i]
            if word in KEYWORDS:
                literal={"true":True,"false":False,"nil":None}.get(word)
                out.append(Token("keyword",word,literal,sl,sc))
            else: out.append(Token("identifier",word,None,sl,sc))
            continue
        op=next((x for x in OPERATORS if source.startswith(x,i)),None)
        if op:
            for _ in op: advance()
            out.append(Token("operator",op,None,sl,sc)); continue
        if ch in ";,.:(){}[]":
            advance(); out.append(Token("punctuation",ch,None,sl,sc)); continue
        raise BrainSyntaxError(f"Unexpected character {ch!r} at {sl}:{sc}")
    out.append(Token("eof","",None,line,column)); return out
