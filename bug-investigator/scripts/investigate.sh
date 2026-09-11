#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

export PYTHONPATH="$ROOT/src"

if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi

# shellcheck disable=SC1091
source .venv/bin/activate

pip install -q -r requirements.txt

if [[ ! -f data/manifest.json ]]; then
  echo "RAG index not found — running index first..."
  ./scripts/index.sh
fi

python -m bug_investigator investigate "$@"
