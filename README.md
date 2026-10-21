# Synthetic Human Brain

A research-oriented software scaffold for exploring **synthetic neural systems**, computational neuroscience concepts, and brain-inspired simulation. This repository is software for experimentation and education; it does not implement, reproduce, or claim to be a human brain.

## Project goals

- Provide a modular neural-network simulation core.
- Separate simulation state, model configuration, experiments, and visualization.
- Make experiments reproducible through explicit configuration and seeded randomness.
- Document assumptions, limitations, safety, and validation criteria.
- Keep the initial implementation small, testable, and suitable for extension.

## Current status

**Scaffold / early research prototype.** This project is not a medically validated model, a consciousness implementation, a brain-computer interface, or a substitute for biological data or expert review. Numerical behavior and scientific claims must be validated before research conclusions are drawn.

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

The starter simulation is intentionally simple: it demonstrates reproducible state updates in a small abstract network. It is not a biophysically detailed neuronal simulator.

## Repository layout

```text
.
├── .github/workflows/ci.yml
├── docs/
│   ├── ARCHITECTURE.md
│   ├── EXPERIMENTS.md
│   ├── SAFETY_AND_LIMITATIONS.md
│   └── uml/
│       └── system-context.mmd
├── src/synthetic_brain/
│   ├── __init__.py
│   ├── __main__.py
│   ├── config.py
│   └── simulation.py
├── tests/
│   └── test_simulation.py
├── pyproject.toml
└── README.md
```

## Development

- Format/lint: `ruff check .`
- Tests: `pytest`
- Build: `python -m build`

Contributions should include tests for behavioral changes and documentation for scientific assumptions. Do not commit personal data, clinical records, credentials, or sensitive neural/biometric data.

## Research integrity

Clearly distinguish measured data, model assumptions, simulated output, and hypotheses. Report parameter choices, seeds, limitations, and failures. Avoid claiming that output demonstrates cognition, consciousness, clinical validity, or biological equivalence without suitable evidence and independent validation.

## License

No license has been selected yet. Until a license is added, standard copyright restrictions apply; do not assume this repository grants permission to reuse the code.
