from synthetic_brain.connectome import Connectome, ConnectomeEdge
from synthetic_brain.metrics import coefficient_of_variation, firing_rate, mean_abs_error, population_entropy
from synthetic_brain.morphology import Compartment, NeuronMorphology


def test_compartment_tree_and_morphology():
    morphology = NeuronMorphology("test-neuron")
    morphology.tree.add(Compartment("soma"))
    morphology.tree.add(Compartment("dendrite"))
    morphology.connect("soma", "dendrite", branch_order=1)
    assert morphology.tree.voltages() == [-65.0, -65.0]
    assert morphology.edges[0].child == "dendrite"


def test_connectome_shortest_delays_and_degree():
    graph = Connectome()
    graph.add_edge(ConnectomeEdge("cortex", "thalamus", delay_ms=2.0))
    graph.add_edge(ConnectomeEdge("thalamus", "motor", delay_ms=3.0))
    assert graph.degree("thalamus") == (1, 1)
    assert graph.shortest_path_delays("cortex")["motor"] == 5.0


def test_validation_metrics():
    assert firing_rate([1, 0, 1, 0], 2.0) == 1.0
    assert coefficient_of_variation([1.0, 1.0]) == 0.0
    assert population_entropy([1.0, 1.0]) == 1.0
    assert mean_abs_error([1.0, 3.0], [2.0, 2.0]) == 1.0
