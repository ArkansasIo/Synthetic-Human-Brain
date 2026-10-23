# Synthetic Human Brain

A research-oriented software scaffold for exploring **synthetic neural systems**, computational neuroscience concepts, and brain-inspired simulation. This repository is software for experimentation and education; it does not implement, reproduce, or claim to be a human brain.

## Project goals

- Provide modular neural-network simulation primitives and a network-driven simulation engine.
- Provide research-backed computational neuroscience algorithms at cellular, synaptic, population, learning, and memory levels.
- Separate simulation state, model configuration, experiments, and visualization.
- Make experiments reproducible through explicit configuration and seeded randomness.
- Document assumptions, limitations, safety, and validation criteria.
- Keep the implementation testable and suitable for extension.

## Current status

**Research prototype — algorithm suite v0.2.0.** The repository now includes an abstract network simulator plus a standalone computational-neuroscience algorithm library. The library includes LIF, AdEx, Izhikevich, and Hodgkin-Huxley neuron dynamics; conductance and short-term synapse models; Hebbian/Oja/BCM/STDP/homeostatic plasticity; Wilson-Cowan and Kuramoto population dynamics; normalization and softmax; temporal-difference learning; predictive-error updates; Hopfield memory; working-memory traces; cable diffusion; and reproducible Poisson spike trains.

The implementation is **not** a complete human-brain simulation. It is a composable toolbox from which progressively larger, data-constrained models can be built.

## Research basis

The design follows the multiscale approach used in computational neuroscience. The Human Brain Project describes modeling from molecular and subcellular levels through cells, networks, and whole-brain models, while noting the computational challenge of full human-scale cellular simulation. Blue Brain similarly documents workflows for morphology, electrical models, cell types, synapses, connectivity, and large-scale simulation.

See [Computational Neuroscience Algorithms](docs/COMPUTATIONAL_NEUROSCIENCE_ALGORITHMS.md) for equations, model families, scientific boundaries, and research references.

## Quick start

Requires Python 3.11 or newer.

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux:
# source .venv/bin/activate
python -m pip install -e ".[dev]"
python -m pytest
python -m synthetic_brain
```

## Algorithm examples

```python
from synthetic_brain import HodgkinHuxleyNeuron, LIFNeuron, stdp_update

lif = LIFNeuron()
spiked = lif.step(current=3.0, dt=1.0)

hh = HodgkinHuxleyNeuron()
hh.step(current=5.0, dt=0.01)

stronger = stdp_update(weight=0.5, delta_t=10.0)
```

## Network-driven simulation

The reusable network engine composes `NeuralNetwork`, `NeuronModel`, and `SynapseModel`. Its default models provide bounded leaky-rate updates and linear weighted transmission.

```python
from synthetic_brain import NeuralNetwork, NetworkSimulation, SimulationConfig

network = NeuralNetwork(neuron_count=3)
network.connect(0, 1, weight=0.8)
network.connect(1, 2, weight=0.5)
network.connect(2, 0, weight=-0.2)

simulation = NetworkSimulation(
    network,
    SimulationConfig(neuron_count=3, seed=42),
)
for _ in range(10):
    snapshot = simulation.step(external_input=0.05)
    print(snapshot.step, snapshot.activity)
```

Every step calculates connection signals from the prior activity snapshot and then updates each unit once. This makes the update synchronous rather than dependent on node iteration order. See [the network simulation guide](docs/NETWORK_SIMULATION.md) and [architecture notes](docs/ARCHITECTURE.md).

## Repository layout

```text
.
├── .github/workflows/ci.yml
├── docs/
│   ├── ARCHITECTURE.md
│   ├── COMPUTATIONAL_NEUROSCIENCE_ALGORITHMS.md
│   ├── EXPERIMENTS.md
│   ├── NETWORK_SIMULATION.md
│   ├── PHASE_2.md
│   ├── ROADMAP.md
│   ├── SAFETY_AND_LIMITATIONS.md
│   └── uml/
├── src/synthetic_brain/
│   ├── algorithms.py
│   ├── config.py
│   ├── network.py
│   ├── network_simulation.py
│   ├── neuron.py
│   ├── simulation.py
│   └── synapse.py
├── tests/
│   ├── test_algorithms.py
│   └── existing simulator tests
└── pyproject.toml
```

## Development

- Lint: `ruff check .`
- Tests: `pytest`
- Build: `python -m build`

Contributions should include tests for behavioral changes and documentation for scientific assumptions. Do not commit personal data, clinical records, credentials, or sensitive neural/biometric data.

## Research integrity

Clearly distinguish measured data, model assumptions, simulated output, and hypotheses. Report parameter choices, seeds, limitations, and failures. Avoid claiming that output demonstrates cognition, consciousness, clinical validity, or biological equivalence without suitable evidence and independent validation.

## Roadmap

The next research layers are data-driven brain-region parcellation, morphology and compartmental cells, connectome ingestion, glia/metabolism, neuromodulatory systems, sensory/motor pathways, parameter fitting, benchmark experiments, uncertainty quantification, and optional HPC backends.

See [docs/ROADMAP.md](docs/ROADMAP.md) for staged work.

## License

No license has been selected yet. Until a license is added, standard copyright restrictions apply; do not assume this repository grants permission to reuse the code.
