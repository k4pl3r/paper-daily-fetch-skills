#!/bin/sh
set -eu

MIN_VERSION="3.11"
seen=""
detected=""

add_detected() {
  entry="$1"
  if [ -z "$detected" ]; then
    detected="$entry"
  else
    detected="$detected, $entry"
  fi
}

check_candidate() {
  candidate="$1"
  [ -n "$candidate" ] || return 1
  case " $seen " in
    *" $candidate "*) return 1 ;;
  esac
  seen="$seen $candidate"
  if ! command -v "$candidate" >/dev/null 2>&1; then
    return 1
  fi
  version="$("$candidate" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")' 2>/dev/null || true)"
  if [ -n "$version" ]; then
    add_detected "$candidate=$version"
  fi
  if "$candidate" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)' >/dev/null 2>&1; then
    command -v "$candidate"
    exit 0
  fi
  return 1
}

if [ -n "${PAPER_DAILY_FETCH_PYTHON_CANDIDATES:-}" ]; then
  set -- $PAPER_DAILY_FETCH_PYTHON_CANDIDATES
else
  set -- python3.13 python3.12 python3.11 python3.10 python3.9 python3.8 python3 python
fi

if [ -n "${PAPER_DAILY_FETCH_PYTHON:-}" ]; then
  check_candidate "$PAPER_DAILY_FETCH_PYTHON" || true
fi

for candidate in "$@"; do
  check_candidate "$candidate" || true
done

echo "No supported Python interpreter found for paper-daily-fetch." >&2
if [ -n "$detected" ]; then
  echo "Detected interpreters: $detected" >&2
fi
echo "This repository currently requires Python $MIN_VERSION+." >&2
echo "If no compatible interpreter exists, ask the user whether they want help locating Python $MIN_VERSION+, creating a virtual environment, or updating the install flow." >&2
exit 1
