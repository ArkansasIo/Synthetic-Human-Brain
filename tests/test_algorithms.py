import math

from synthetic_brain.algorithms import (
    AdExNeuron,
    HodgkinHuxleyNeuron,
    IzhikevichNeuron,
    LIFNeuron,
    TsodyksMarkramSynapse,
    WorkingMemoryTrace,
    bcm_update,
    cable_diffusion_step,
    divisive_normalization,
    hebbian_update,
    hopfield_hebbian,
    kuramoto_step,
    oja_update,
    poisson_spike_train,
    predictive_coding_update,
    softmax,
    stdp_update,
    td_error,
    td_update,
    wilson_cowan_step,
)


def test_lif_spikes_with_sufficient_current() -> None:
    neuron = LIFNeuron()
    assert neuron.step(3.0, 20.0)


def test_izhikevich_is_finite() -> None:
    neuron = IzhikevichNeuron()
    for _ in range(100):
        neuron.step(10.0)
    assert math.isfinite(neuron.v)
    assert math.isfinite(neuron.u)


def test_adex_is_finite() -> None:
    neuron = AdExNeuron()
    for _ in range(100):
        neuron.step(1.0, 0.1)
    assert math.isfinite(neuron.v)
    assert math.isfinite(neuron.w)


def test_hodgkin_huxley_is_finite() -> None:
    neuron = HodgkinHuxleyNeuron()
    for _ in range(100):
        neuron.step(5.0, 0.01)
    assert all(math.isfinite(v) for v in (neuron.v, neuron.m, neuron.h, neuron.n))


def test_plasticity_rules() -> None:
    assert hebbian_update(1.0, 2.0, 3.0, 0.1) == 1.6
    assert oja_update(1.0, 2.0, 0.5, 0.1) == 1.075
    assert bcm_update(1.0, 2.0, 3.0, 1.0, 0.1) == 2.2
    assert stdp_update(1.0, 10.0) > 1.0
    assert stdp_update(1.0, -10.0) < 1.0


def test_short_term_plasticity() -> None:
    synapse = TsodyksMarkramSynapse()
    released = synapse.presynaptic_spike()
    assert 0.0 <= released <= 1.0
    synapse.step(10.0)
    assert 0.0 <= synapse.x <= 1.0


def test_population_and_oscillator_models() -> None:
    e, i = wilson_cowan_step(0.2, 0.1, 10, 10, 10, 10, 1, 0)
    assert 0.0 <= e <= 1.0 and 0.0 <= i <= 1.0
    phases = kuramoto_step([0.0, 1.0], [1.0, 1.1], 0.5, 0.01)
    assert len(phases) == 2


def test_normalization_and_softmax() -> None:
    normalized = divisive_normalization([1.0, 2.0, 3.0])
    assert all(v >= 0 for v in normalized)
    probabilities = softmax([1.0, 2.0, 3.0])
    assert math.isclose(sum(probabilities), 1.0)


def test_learning_and_prediction() -> None:
    error = td_error(1.0, 0.5, 0.2)
    assert math.isclose(error, 1.295)
    assert td_update(0.2, 1.0, 0.5, 0.1) > 0.2
    assert predictive_coding_update(2.0, 1.0, 1.0, 0.1) < 2.0


def test_hopfield_and_memory() -> None:
    weights = hopfield_hebbian([[1, -1, 1], [1, -1, 1]])
    assert len(weights) == 3
    assert weights[0][0] == 0.0
    assert math.isclose(WorkingMemoryTrace(decay_tau=10).step(1.0, 1.0), 1.0)


def test_cable_and_poisson_are_reproducible() -> None:
    cable = cable_diffusion_step([1.0, 0.0, 0.0], 1.0, 0.0, 0.1)
    assert cable[1] > 0.0
    assert poisson_spike_train(10, 0.1, 0.001, seed=7) == poisson_spike_train(10, 0.1, 0.001, seed=7)
