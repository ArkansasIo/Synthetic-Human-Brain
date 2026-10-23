from .runtime import BrainScriptRuntime
from .lexer import tokenize


def test_number_classification() -> None:
    runtime = BrainScriptRuntime()
    rows = runtime.execute_example([0, 1, 2, 9, 11, 12])
    assert rows[0]["classification"] == "neither"
    assert rows[2]["classification"] == "prime"
    assert rows[3]["classification"] == "odd"
    assert rows[5]["classification"] == "even"


def test_lexer() -> None:
    tokens = tokenize("return 2 + 2\n")
    assert [token.kind for token in tokens[:4]] == ["RETURN", "NUMBER", "OP", "NUMBER"]
