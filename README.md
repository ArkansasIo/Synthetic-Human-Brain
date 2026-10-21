# Synthetic Human Brain

A research-oriented software scaffold for exploring **synthetic neural systems**, computational neuroscience concepts, and brain-inspired simulation. This repository is software for experimentation and education; it does not implement, reproduce, or claim to be a human brain.

## Project goals

- Provide modular neural-network simulation primitives and a network-driven simulation engine.
- Separate simulation state, model configuration, experiments, and visualization.
- Make experiments reproducible through explicit configuration and seeded randomness.
- Document assumptions, limitations, safety, and validation criteria.
- Keep the implementation testable and suitable for extension.

## Current status

**Early research prototype.** The repository includes an abstract ring-network reference simulator, a directed weighted connectivity graph, pluggable neuron and synapse interfaces, and a graph-driven engine that applies weighted connections and advances all units synchronously. The code is not a medically validated model, a consciousness implementation, a brain-computer interface, or a substitute for biological data or expert review.

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
│   ├── EXPERIMENTS.md
│   ├── NETWORK_SIMULATION.md
│   ├── PHASE_2.md
│   ├── ROADMAP.md
│   ├── SAFETY_AND_LIMITATIONS.md
│   └── uml/
├── src/synthetic_brain/
│   ├── config.py
│   ├── network.py
│   ├── network_simulation.py
│   ├── neuron.py
│   ├── simulation.py
│   └── synapse.py
├── tests/
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

See [docs/ROADMAP.md](docs/ROADMAP.md) for staged work on sparse networks, serialization, experiment tooling, validation, and optional high-performance backends.

## License

No license has been selected yet. Until a license is added, standard copyright restrictions apply; do not assume this repository grants permission to reuse the code.
