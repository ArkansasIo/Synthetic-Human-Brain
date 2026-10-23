from synthetic_brain.brainlang import BrainRuntime, Parser, lex


def test_lexer_and_parser():
    tokens = lex("var x = 10 + 2")
    assert tokens[0].value == "var"
    program = Parser("var x = 10 + 2").program()
    assert program[0]["type"] == "var"


def test_runtime_arithmetic_and_logic():
    runtime = BrainRuntime()
    env = runtime.execute("var x = 10 + 2 * 3\nvar ok = x >= 16 and x < 20")
    assert env.get("x") == 16
    assert env.get("ok") is True


def test_functions_and_return():
    source = """
    fn td(reward, value, next_value) {
        return reward + 0.99 * next_value - value
    }
    var error = td(1, 0.25, 0.8)
    """
    env = BrainRuntime().execute(source)
    assert abs(env.get("error") - 1.542) < 1e-9


def test_brain_population_and_connectivity():
    source = """
    brain Cortex {
        population Excitatory size 100
        population Inhibitory size 25
        connect Excitatory -> Inhibitory weight 0.2 delay 1.5
    }
    """
    env = BrainRuntime().execute(source)
    cortex = env.get("Cortex")
    assert cortex.fields["populations"]["Excitatory"]["size"] == 100
    assert cortex.fields["connections"][0]["source"] == "Excitatory"
    assert cortex.fields["connections"][0]["weight"] == 0.2
