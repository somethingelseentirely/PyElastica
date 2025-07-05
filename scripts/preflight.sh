#!/usr/bin/env bash
set -euo pipefail

# Move to repository root
cd "$(dirname "$0")/.."

# Ensure uv is installed
if ! command -v uv >/dev/null 2>&1; then
  echo "uv not found, installing with pip..." >&2
  pip install uv
fi

# Ensure a virtual environment exists for maturin
if [ ! -d ".venv" ]; then
  python -m venv .venv
fi
source .venv/bin/activate

# Install tools and project dependencies
uv pip install ruff pytest maturin -e .

# Run Rust tests and build Python extension
cargo test --manifest-path elastica_rust/Cargo.toml
maturin develop -m elastica_rust/Cargo.toml --release

# Run formatting on modified Python files and tests
files=$(git status --porcelain | awk '/\.py$/ {print $2}')
if [ -n "$files" ]; then
  ruff format $files
fi
pytest
