"""BrainLang: a small Lua-inspired, object-oriented DSL for brain simulation.

BrainLang is deliberately compact. It provides objects/classes, functions,
variables, conditionals, loops, return statements, arithmetic/boolean logic,
property access, method calls, and simulation-oriented statements.

Syntax example::

    brain Cortex {
        population Excitatory size 100
        population Inhibitory size 25
        connect Excitatory -> Inhibitory weight 0.20 delay 1.5
    }

    class Neuron {
        var threshold = -50
        fn fire(input) {
            if input >= threshold { return true }
            return false
        }
    }

    fn reward(value, target) {
        return target - value
    }

The parser is intentionally dependency-free so BrainLang can be embedded in
the Python research package or replaced later by a native parser.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import re
from typing import Any, Callable


KEYWORDS = {
    "and", "or", "not", "true", "false", "null", "var", "const", "fn",
    "class", "extends", "return", "if", "else", "while", "for", "in",
    "brain", "population", "connect", "weight", "delay", "stimulus",
    "emit", "record", "step", "let", "this",
}

TOKEN_RE = re.compile(
    r'(?P<comment>//[^\\n]*|#[^\\n]*)|(?P<string>"(?:\\\\.|[^"\\\\])*"|\'(?:\\\\.|[^\'\\\\])*\')|'
    r'(?P<number>\\d+(?:\\.\\d+)?)|(?P<op>==|!=|<=|>=|->|\\+|-|\\*|/|%|=|<|>|!|\\.)|'
    r'(?P<punct>[{}()\\[\\],;:])|(?P<name>[A-Za-z_][A-Za-z0-9_]*)|(?P<space>\\s+)|(?P<bad>.)'
)


@dataclass(frozen=True, slots=True)
class Token:
    kind: str
    value: str
    position: int


def lex(source: str) -> list[Token]:
    tokens: list[Token] = []
    for match in TOKEN_RE.finditer(source):
        kind = match.lastgroup
        value = match.group()
        if kind in {"space", "comment"}:
            continue
        if kind == "name" and value in KEYWORDS:
            kind = "keyword"
        if kind == "bad":
            raise SyntaxError(f"Unexpected character {value!r} at {match.start()}")
        tokens.append(Token(kind, value, match.start()))
    tokens.append(Token("eof", "", len(source)))
    return tokens


class Parser:
    """Recursive-descent parser for the BrainLang core syntax."""

    def __init__(self, source: str):
        self.tokens = lex(source)
        self.i = 0

    @property
    def current(self) -> Token:
        return self.tokens[self.i]

    def advance(self) -> Token:
        token = self.current
        self.i += 1
        return token

    def accept(self, value: str) -> bool:
        if self.current.value == value:
            self.advance()
            return True
        return False

    def expect(self, value: str) -> Token:
        if self.current.value != value:
            raise SyntaxError(f"Expected {value!r} at {self.current.position}, got {self.current.value!r}")
        return self.advance()

    def name(self) -> str:
        if self.current.kind not in {"name", "keyword"}:
            raise SyntaxError(f"Expected identifier at {self.current.position}")
        return self.advance().value

    def program(self) -> list[dict[str, Any]]:
        nodes = []
        while self.current.kind != "eof":
            nodes.append(self.statement())
        return nodes

    def block(self) -> list[dict[str, Any]]:
        self.expect("{")
        body = []
        while self.current.value != "}":
            if self.current.kind == "eof":
                raise SyntaxError("Unclosed block")
            body.append(self.statement())
        self.advance()
        return body

    def statement(self) -> dict[str, Any]:
        v = self.current.value
        if v in {"var", "let", "const"}:
            self.advance()
            name = self.name()
            self.expect("=")
            value = self.expression()
            self.accept(";")
            return {"type": "var", "name": name, "value": value}
        if v == "return":
            self.advance()
            value = {"type": "literal", "value": None} if self.current.value in {";", "}"} else self.expression()
            self.accept(";")
            return {"type": "return", "value": value}
        if v == "fn":
            self.advance()
            name = self.name()
            params = self.parameters()
            body = self.block()
            return {"type": "fn", "name": name, "params": params, "body": body}
        if v == "class":
            self.advance()
            name = self.name()
            parent = None
            if self.accept("extends"):
                parent = self.name()
            body = self.block()
            return {"type": "class", "name": name, "parent": parent, "body": body}
        if v == "brain":
            self.advance()
            name = self.name()
            body = self.block()
            return {"type": "brain", "name": name, "body": body}
        if v == "population":
            self.advance()
            name = self.name()
            attrs = self.attributes()
            return {"type": "population", "name": name, "attrs": attrs}
        if v == "connect":
            self.advance()
            source = self.name()
            self.expect("->")
            target = self.name()
            attrs = self.attributes()
            return {"type": "connect", "source": source, "target": target, "attrs": attrs}
        if v == "if":
            self.advance()
            condition = self.expression()
            yes = self.block()
            no = self.block() if self.accept("else") else []
            return {"type": "if", "condition": condition, "yes": yes, "no": no}
        if v == "while":
            self.advance()
            condition = self.expression()
            return {"type": "while", "condition": condition, "body": self.block()}
        if v == "step":
            self.advance()
            duration = self.expression()
            self.accept(";")
            return {"type": "step", "duration": duration}
        expr = self.expression(); self.accept(";")
        return {"type": "expr", "value": expr}

    def parameters(self) -> list[str]:
        self.expect("(")
        params = []
        if self.current.value != ")":
            while True:
                params.append(self.name())
                if not self.accept(","):
                    break
        self.expect(")")
        return params

    def attributes(self) -> dict[str, dict[str, Any]]:
        attrs: dict[str, dict[str, Any]] = {}
        while self.current.value not in {"}", ";", "eof"}:
            key = self.name()
            value = self.expression()
            attrs[key] = value
            if self.accept(","):
                continue
            if self.current.value in {"weight", "delay"} or self.current.kind in {"name", "keyword"}:
                continue
            break
        self.accept(";")
        return attrs

    def expression(self) -> dict[str, Any]:
        return self.binary(0)

    PRECEDENCE = {"or": 1, "and": 2, "==": 3, "!=": 3, "<": 4, "<=": 4, ">": 4, ">=": 4,
                  "+": 5, "-": 5, "*": 6, "/": 6, "%": 6}

    def binary(self, minimum: int) -> dict[str, Any]:
        left = self.unary()
        while self.current.value in self.PRECEDENCE and self.PRECEDENCE[self.current.value] >= minimum:
            op = self.advance().value
            right = self.binary(self.PRECEDENCE[op] + 1)
            left = {"type": "binary", "op": op, "left": left, "right": right}
        return left

    def unary(self) -> dict[str, Any]:
        if self.current.value in {"not", "!", "-"}:
            op = self.advance().value
            return {"type": "unary", "op": op, "value": self.unary()}
        return self.primary()

    def primary(self) -> dict[str, Any]:
        token = self.advance()
        if token.kind == "number":
            value: Any = float(token.value) if "." in token.value else int(token.value)
            return {"type": "literal", "value": value}
        if token.kind == "string":
            return {"type": "literal", "value": token.value[1:-1]}
        if token.value in {"true", "false", "null"}:
            return {"type": "literal", "value": {"true": True, "false": False, "null": None}[token.value]}
        if token.value == "(":
            value = self.expression()
            self.expect(")")
            return value
        if token.kind in {"name", "keyword"}:
            node: dict[str, Any] = {"type": "name", "name": token.value}
            while True:
                if self.accept("."):
                    node = {"type": "get", "object": node, "name": self.name()}
                elif self.accept("("):
                    args = []
                    if self.current.value != ")":
                        while True:
                            args.append(self.expression())
                            if not self.accept(","):
                                break
                    self.expect(")")
                    node = {"type": "call", "callee": node, "args": args}
                else:
                    break
            return node
        raise SyntaxError(f"Unexpected token {token.value!r} at {token.position}")


class ReturnSignal(Exception):
    def __init__(self, value: Any):
        self.value = value


@dataclass
class BrainObject:
    fields: dict[str, Any] = field(default_factory=dict)


@dataclass
class BrainClass:
    name: str
    methods: dict[str, Callable[..., Any]] = field(default_factory=dict)
    parent: "BrainClass | None" = None

    def instantiate(self, *args: Any) -> BrainObject:
        obj = BrainObject()
        if self.parent:
            obj.fields.update(self.parent.instantiate().fields)
        obj.fields["__class__"] = self
        constructor = self.methods.get("init")
        if constructor:
            constructor(obj, *args)
        return obj


class Environment:
    def __init__(self, parent: "Environment | None" = None):
        self.parent = parent
        self.values: dict[str, Any] = {}

    def define(self, name: str, value: Any) -> None:
        self.values[name] = value

    def get(self, name: str) -> Any:
        if name in self.values:
            return self.values[name]
        if self.parent:
            return self.parent.get(name)
        raise NameError(name)


class BrainRuntime:
    """Dependency-free interpreter for the executable BrainLang subset."""

    def __init__(self):
        self.global_env = Environment()
        self.global_env.define("print", print)
        self.global_env.define("min", min)
        self.global_env.define("max", max)

    def execute(self, source: str) -> Environment:
        nodes = Parser(source).program()
        for node in nodes:
            self.execute_node(node, self.global_env)
        return self.global_env

    def execute_node(self, node: dict[str, Any], env: Environment) -> Any:
        kind = node["type"]
        if kind == "var":
            value = self.evaluate(node["value"], env); env.define(node["name"], value); return value
        if kind == "expr":
            return self.evaluate(node["value"], env)
        if kind == "return":
            raise ReturnSignal(self.evaluate(node["value"], env))
        if kind == "if":
            body = node["yes"] if self.evaluate(node["condition"], env) else node["no"]
            return self.execute_block(body, env)
        if kind == "while":
            result = None; guard = 0
            while self.evaluate(node["condition"], env):
                result = self.execute_block(node["body"], env); guard += 1
                if guard > 1_000_000: raise RuntimeError("while loop exceeded safety limit")
            return result
        if kind == "fn":
            def function(*args: Any) -> Any:
                local = Environment(env)
                for index, name in enumerate(node["params"]):
                    local.define(name, args[index] if index < len(args) else None)
                try:
                    return self.execute_block(node["body"], local)
                except ReturnSignal as signal:
                    return signal.value
            env.define(node["name"], function); return function
        if kind == "class":
            cls = BrainClass(node["name"])
            for member in node["body"]:
                if member["type"] == "fn":
                    def make_method(method_node: dict[str, Any]):
                        def method(obj: BrainObject, *args: Any) -> Any:
                            local = Environment(env); local.define("this", obj)
                            for index, name in enumerate(method_node["params"]):
                                local.define(name, args[index] if index < len(args) else None)
                            try: return self.execute_block(method_node["body"], local)
                            except ReturnSignal as signal: return signal.value
                        return method
                    cls.methods[member["name"]] = make_method(member)
            env.define(node["name"], cls); return cls
        if kind == "brain":
            brain = BrainObject({"name": node["name"], "populations": {}, "connections": []})
            env.define(node["name"], brain)
            for child in node["body"]:
                self.execute_brain_node(child, brain, env)
            return brain
        if kind == "step":
            return self.evaluate(node["duration"], env)
        raise RuntimeError(f"Unsupported statement {kind}")

    def execute_brain_node(self, node: dict[str, Any], brain: BrainObject, env: Environment) -> None:
        if node["type"] == "population":
            attrs = {key: self.evaluate(value, env) for key, value in node["attrs"].items()}
            brain.fields["populations"][node["name"]] = attrs
        elif node["type"] == "connect":
            attrs = {key: self.evaluate(value, env) for key, value in node["attrs"].items()}
            brain.fields["connections"].append({"source": node["source"], "target": node["target"], **attrs})

    def execute_block(self, nodes: list[dict[str, Any]], env: Environment) -> Any:
        result = None
        for node in nodes: result = self.execute_node(node, env)
        return result

    def evaluate(self, node: dict[str, Any], env: Environment) -> Any:
        kind = node["type"]
        if kind == "literal": return node["value"]
        if kind == "name": return env.get(node["name"])
        if kind == "get":
            obj = self.evaluate(node["object"], env)
            if isinstance(obj, BrainObject): return obj.fields[node["name"]]
            return getattr(obj, node["name"])
        if kind == "call":
            callee = self.evaluate(node["callee"], env)
            args = [self.evaluate(arg, env) for arg in node["args"]]
            return callee(*args)
        if kind == "unary":
            value = self.evaluate(node["value"], env)
            return {"not": lambda: not value, "!": lambda: not value, "-": lambda: -value}[node["op"]]()
        if kind == "binary":
            left = self.evaluate(node["left"], env); right = self.evaluate(node["right"], env); op = node["op"]
            operations = {"+": lambda: left + right, "-": lambda: left - right, "*": lambda: left * right,
                          "/": lambda: left / right, "%": lambda: left % right, "==": lambda: left == right,
                          "!=": lambda: left != right, "<": lambda: left < right, "<=": lambda: left <= right,
                          ">": lambda: left > right, ">=": lambda: left >= right, "and": lambda: bool(left and right),
                          "or": lambda: bool(left or right)}
            return operations[op]()
        raise RuntimeError(f"Unsupported expression {kind}")


def run(source: str) -> Environment:
    """Parse and execute BrainLang source."""
    return BrainRuntime().execute(source)


__all__ = ["BrainClass", "BrainLang", "BrainObject", "BrainRuntime", "Environment", "Parser", "Token", "lex", "run"]

# Public language descriptor used by tooling and documentation.
BrainLang = BrainRuntime
