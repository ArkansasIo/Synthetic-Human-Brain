from synthetic_brain.brainlang_cl1 import BrainLangCL1Runner


def test_brainlang_program_builds_neuron_count() -> None:
    source = """
    brain Cortex {
        population Excitatory size 8;
        population Inhibitory size 2;
        connect Excitatory -> Inhibitory weight 0.2 delay 1.0;
    }
    """
    runner = BrainLangCL1Runner()
    program = runner.compile(source)
    neurons = runner.build_neurons(program, seed=1)
    assert neurons.channel_count == 10
    neurons.close()
