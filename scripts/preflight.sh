#!/usr/bin/env bash
set -euo pipefail

# Move to repository root
cd "$(dirname "$0")/.."

# Ensure poetry is installed
if ! command -v poetry >/dev/null 2>&1; then
  echo "poetry not found. Please install it first." >&2
  exit 1
fi

# Run formatting check and tests
make formatting
make test
