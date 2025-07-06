#!/usr/bin/env bash
set -euo pipefail

# Move to repository root
cd "$(dirname "$0")/.."

# Ensure uv is installed to manage dependencies
if ! command -v uv >/dev/null 2>&1; then
  echo "uv not found, installing with pip..." >&2
  pip install uv
fi

# Ensure a virtual environment exists for maturin
if [ ! -d ".venv" ]; then
  python -m venv .venv
fi
source .venv/bin/activate

# Install project dependencies and build tools
uv pip install -e . maturin

# Ensure the venv site-packages is first in PYTHONPATH
export PYTHONPATH="$(python -c 'import site; print(site.getsitepackages()[0])')${PYTHONPATH:+:$PYTHONPATH}"

# Build the Rust extension so tests can import it
cargo test --manifest-path elastica_rust/Cargo.toml
# Build the release library for integration with Python
cargo build --release --manifest-path elastica_rust/Cargo.toml
python -m maturin develop -m elastica_rust/Cargo.toml --release

# Run only the tests for quick iteration
pytest "$@"
