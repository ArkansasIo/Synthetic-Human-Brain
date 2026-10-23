#!/usr/bin/env bash
set -euo pipefail

# Apply safe, deterministic Ruff fixes, then report anything that needs review.
python -m ruff check . --fix
python -m ruff format .
python -m ruff check .
