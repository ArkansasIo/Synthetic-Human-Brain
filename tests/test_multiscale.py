from synthetic_brain.neuromodulation import DopamineSignal, HomeostaticController, Neuromodulator
from synthetic_brain.receptors import AMPAReceptor, GABAaReceptor, NMDAReceptor
from synthetic_brain.regions import BrainNetwork, BrainRegion, NeuralPopulation, RegionConnection


def test_brain_network_regions_and_adjacency():
    net = BrainNetwork()
    net.add_population(NeuralPopulation("visual", 100, region=BrainRegion.CEREBRAL_CORTEX))
    net.add_population(NeuralPopulation("hippocampal", 50, region=BrainRegion.HIPPOCAMPUS))
    net.connect(RegionConnection("visual", "hippocampal", probability=0.2, weight=0.5))
    assert net.region_populations(BrainRegion.HIPPOCAMPUS)[0].size == 50
    assert net.adjacency()["visual"] == ["hippocampal"]


def test_receptor_kinetics():
    ampa = AMPAReceptor()
    gaba = GABAaReceptor()
    nmda = NMDAReceptor()
    assert ampa.step(1.0, 1.0) > 0.0
    assert gaba.step(1.0, 1.0) > 0.0
    assert nmda.step(1.0, -65.0, 1.0) > 0.0
    assert nmda.magnesium_block(-20.0) > nmda.magnesium_block(-80.0)


def test_neuromodulator_and_dopamine():
    signal = Neuromodulator("dopamine", level=0.0, decay_rate=0.0)
    assert signal.step(1.0, 0.5) == 0.5
    dopamine = DopamineSignal()
    assert dopamine.prediction_error(1.0, 0.0, 0.0) == 1.0


def test_homeostatic_controller():
    controller = HomeostaticController(target_rate=10.0, learning_rate=0.1)
    assert controller.update(5.0, 1.0) == 1.5
