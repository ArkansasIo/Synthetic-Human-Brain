# CI Troubleshooting

## Ruff lint failures

The CI workflow runs `ruff check .` before tests. A lint failure prevents pytest and the distribution build from running, so a red job does not yet indicate a test failure.

Run locally:

```bash
python -m pip install -e ".[dev]"
ruff check .
ruff check . --fix
ruff format .
ruff check .
pytest
python -m build
```

Review the diff after automatic fixes. Do not apply unsafe fixes without reviewing their behavioral effect.

## CL1 test boundary

The local CL1 simulator and synthetic data sources are software-only development targets. Tests must not require an installed proprietary CL SDK, connected CL1 hardware, or real biological tissue. Hardware integration tests should be opt-in and clearly separated from the default CI suite.

## Scientific reporting

Keep generated simulator output distinct from biological observations. Report model parameters, random seeds, data provenance, uncertainty, and validation criteria with experimental results.
