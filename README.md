# Synthetic Human Brain

A research-oriented software and hardware architecture for exploring **synthetic neural systems**, computational neuroscience, neural interfaces, and brain-inspired simulation. This repository does not implement, reproduce, or claim to be a human brain.

## Project goals

- Provide modular neural-network simulation primitives and a network-driven simulation engine.
- Model neural systems from cellular and synaptic dynamics through populations, regions, networks, and whole-brain abstractions.
- Provide research-backed computational neuroscience algorithms at cellular, synaptic, population, learning, and memory levels.
- Define software interfaces for external neural recording and stimulation systems.
- Provide a non-invasive-first neural scanning/interface architecture inspired by EEG/ECoG/other research modalities without assuming invasive implantation.
- Separate simulation state, model configuration, experiments, visualization, hardware interfaces, and provenance.
- Make experiments reproducible through explicit configuration and seeded randomness.
- Document assumptions, limitations, safety, and validation criteria.
- Keep the implementation testable and suitable for extension.

## Current status

**Research prototype — algorithm suite v0.2.0 plus whole-brain interface architecture.** The repository includes an abstract network simulator, computational-neuroscience algorithm library, CL1-oriented research adapters, and a growing anatomical/software/hardware interface architecture.

The implementation is **not** a complete human-brain simulation or a clinical brain-scanning system. It is a composable research toolbox from which progressively larger, data-constrained models can be built.

## License

The project software is licensed under Apache License 2.0 unless a more specific component notice applies. Original project hardware designs use the project hardware licensing policy, and original project data uses the project data licensing policy.

- [Software license](LICENSE)
- [Hardware license](LICENSES/HARDWARE_LICENSE.md)
- [Data license](LICENSES/DATA_LICENSE.md)
- [Third-party materials](LICENSES/THIRD_PARTY.md)
- [CL1 / Cortical Labs notice](LICENSES/CL1_NOTICE.md)

See [LICENSES/README.md](LICENSES/README.md) for the licensing map.

## Research boundary

This project separates **measured data**, **inferred state**, **simulated state**, and **hypotheses**. A neural-interface or scanning architecture described here is a research/software design, not a medical-device specification. Human-subject research, neural stimulation, and any implantable hardware require appropriate scientific, clinical, ethics, safety, and regulatory processes.

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Multiscale architecture](docs/MULTISCALE_ARCHITECTURE.md)
- [Computational neuroscience algorithms](docs/COMPUTATIONAL_NEUROSCIENCE_ALGORITHMS.md)
- [Whole-brain neural interface plan](docs/WHOLE_BRAIN_NEURAL_INTERFACE.md)
- [Hardware architecture](docs/HARDWARE_ARCHITECTURE.md)
- [Software/hardware mapping](docs/SOFTWARE_HARDWARE_MAPPING.md)
- [API reference and implementation plan](docs/API_REFERENCE.md)
- [API implementation plan](docs/API_IMPLEMENTATION_PLAN.md)
- [Experiments](docs/EXPERIMENTS.md)
- [Safety and limitations](docs/SAFETY_AND_LIMITATIONS.md)
- [UML index](docs/uml/README.md)

## Repository layout

```text
.
├── LICENSE
├── LICENSES/
│   ├── README.md
│   ├── HARDWARE_LICENSE.md
│   ├── DATA_LICENSE.md
│   ├── THIRD_PARTY.md
│   └── CL1_NOTICE.md
├── docs/
│   ├── API_REFERENCE.md
│   ├── API_IMPLEMENTATION_PLAN.md
│   ├── HARDWARE_ARCHITECTURE.md
│   ├── SOFTWARE_HARDWARE_MAPPING.md
│   ├── WHOLE_BRAIN_NEURAL_INTERFACE.md
│   └── uml/
├── examples/
│   └── neural_interface_architecture.py
└── src/synthetic_brain/
    ├── algorithms.py
    ├── brainlang.py
    ├── cl1.py
    └── ...
```

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

## Development

- Lint: `ruff check .`
- Tests: `pytest`
- Build: `python -m build`

Contributions should include tests for behavioral changes and documentation for scientific assumptions. Do not commit personal data, clinical records, credentials, or sensitive neural/biometric data.
