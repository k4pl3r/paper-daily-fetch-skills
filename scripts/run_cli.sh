#!/bin/sh
set -eu

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
REPO_ROOT="$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)"
PYTHON_BIN="${PAPER_DAILY_FETCH_PYTHON:-}"

if [ -z "$PYTHON_BIN" ]; then
  PYTHON_BIN="$(sh "$SCRIPT_DIR/resolve_python.sh")"
fi

if ! "$PYTHON_BIN" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)' >/dev/null 2>&1; then
  PYTHON_BIN="$(PAPER_DAILY_FETCH_PYTHON="$PYTHON_BIN" sh "$SCRIPT_DIR/resolve_python.sh")"
fi

PYTHONPATH="$REPO_ROOT/src${PYTHONPATH:+:$PYTHONPATH}" exec "$PYTHON_BIN" -m paper_daily_fetch "$@"
