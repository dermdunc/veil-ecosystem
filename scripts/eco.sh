#!/usr/bin/env bash
# eco.sh -- Phase 0 of docs/interactive-plan.md. Entire Phase-0 UI: renders
# the local tier of veil.ecostatus.v1 to the terminal. `up|down|smoke`
# orchestration profiles are Phase 1, not built yet.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON="${PYTHON:-python3}"

usage() {
  cat <<'EOF'
Usage: scripts/eco.sh status [--json]

  status        Run the collector + contradiction checker, render to the
                terminal. Exits non-zero if any error-severity
                contradiction is found (so this is CI-safe once wired in).
  status --json Print the full veil.ecostatus.v1 document instead.
EOF
}

case "${1:-}" in
  status)
    shift
    exec "$PYTHON" "$ROOT_DIR/scripts/eco_checker.py" "$@"
    ;;
  -h|--help|"")
    usage
    exit 0
    ;;
  *)
    echo "Unknown subcommand: $1" >&2
    usage >&2
    exit 1
    ;;
esac
