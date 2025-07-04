#!/usr/bin/env bash
set -euo pipefail

# Move to repository root
cd "$(dirname "$0")/.."

# Ensure uv is installed to manage dependencies
if ! command -v uv >/dev/null 2>&1; then
  echo "uv not found, installing with pip..." >&2
  pip install uv
fi

# Install project dependencies to avoid ModuleNotFound errors during tests
uv pip install -e . --system

# Run only the tests for quick iteration
pytest "$@"
