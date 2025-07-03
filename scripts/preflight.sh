#!/usr/bin/env bash
set -euo pipefail

# Move to repository root
cd "$(dirname "$0")/.."

# Ensure uv is installed
if ! command -v uv >/dev/null 2>&1; then
  echo "uv not found, installing with pip..." >&2
  pip install uv
fi

# Install required tools and project dependencies if missing
missing_pkgs=()
for pkg in ruff pytest; do
  if ! command -v "$pkg" >/dev/null 2>&1; then
    missing_pkgs+=("$pkg")
  fi
done
if [ ${#missing_pkgs[@]} -gt 0 ]; then
  uv pip install --system "${missing_pkgs[@]}"
fi

# Ensure project dependencies are installed from pyproject
uv pip install -e . --system

# Run formatting on modified Python files and tests
files=$(git status --porcelain | awk '/\.py$/ {print $2}')
if [ -n "$files" ]; then
  ruff format $files
fi
pytest
