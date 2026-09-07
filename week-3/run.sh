#!/usr/bin/env bash
# Helper: activate venv and set PYTHONPATH (needed when system python is a Cursor wrapper)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
export PYTHONPATH="${ROOT}/venv/lib/python3.14/site-packages:${PYTHONPATH:-}"
if [[ -f "${ROOT}/venv/bin/activate" ]]; then
  # shellcheck disable=SC1091
  source "${ROOT}/venv/bin/activate"
fi
exec "$@"
