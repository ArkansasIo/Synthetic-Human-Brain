## Current status

The repository is currently documentation-only. Source code, packaging metadata, tests, and CI workflows must be added before project quick-start commands can work.

## Proposed baseline

- Python 3.11 or newer.
- Package source in `src/synthetic_brain/`.
- Tests in `tests/`.
- GitHub Actions for CI; pytest for tests; Ruff for linting.

## Setup (after package metadata is added)

Windows PowerShell:

```powershell
python -m venv .venv
.venv\\Scripts\\Activate.ps1
python -m pip install -e ".[dev]"
python -m pytest
ruff check .
python -m build
```

macOS/Linux:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
python -m pytest
ruff check .
python -m build
```

## Contribution expectations

- Add tests for behavioral changes and edge cases.
- Document parameters, units, seed behavior, and numerical assumptions.
- Do not claim biological accuracy without validation evidence.
- Do not commit secrets, private datasets, or unreviewed generated results.
- Include the exact commands and environment used when reporting test outcomes.

## Release checks

Run tests, linting, packaging checks, documentation review, and a diff scan for secrets. Releases should identify a source commit, supported Python versions, installation instructions, breaking changes, and known limitations. Do not claim checks passed unless they were run.
