#!/usr/bin/env python3
"""Validate the intent registry (.hekton/intents/) against the operating
definition in docs/intent-driven-development.md.

Checks, per intent file:
  - parses as YAML, carries every required field, id matches its directory
  - disproof_criteria non-empty (falsifiability is the point -- an intent
    whose author cannot state what would disprove it is not accepted)
  - status vocabulary and risk tiers are the lab's, verbatim
  - the history block is an append-only log whose transitions are legal per
    the state machine, and whose final entry agrees with the status field
  - every terminal-status intent cites evidence in its final history entry
  - every bindings.mission_manifests path exists in the repository

Ported verbatim from tektograph's scripts/validate_intents.py (the only live,
ongoing intent-registry practice in the Hekton ecosystem at adoption time,
2026-09-03) -- see docs/decisions.md for why this schema was chosen over
intent-assurance-lab's nested 1.0 shape.

Advisory posture, same precedent: this script reports and exits non-zero on
registry-mechanics violations only -- it never gates on architecture verdicts,
and whether it ever blocks a merge is a later decision.

Governance tooling, not engine surface: imports nothing from engine/. Requires
PyYAML, a deliberate dependency for this script only -- see docs/decisions.md
"Intent registry needs real YAML, engine stays dependency-free" and
engine/schema.md "Why not YAML". Do not wire this into scripts/verify-lab.sh,
which must keep running on a blank machine with no pip dependency.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

STATUSES = [
    "declared", "critiqued", "accepted", "in_progress", "technically_confirmed",
    "provisionally_confirmed", "operationally_confirmed", "disproven",
    "superseded", "abandoned",
]
TERMINAL = {"operationally_confirmed", "disproven", "superseded", "abandoned"}
RISK_TIERS = {"T0", "T1", "T2", "T3"}
KINDS = {"feature", "fix", "refactor", "experiment", "ops", "security", "decision"}

# The lab's state machine (docs/intent-driven-development.md), adopted verbatim
# from tektograph's docs/intent-lifecycle.md: forward chain plus side-exits to
# disproven/superseded/abandoned at any point after accepted, plus the two
# recorded loop-backs (critique fails -> declared; material amendment
# approved -> accepted).
_FORWARD = ["declared", "critiqued", "accepted", "in_progress",
            "technically_confirmed", "provisionally_confirmed", "operationally_confirmed"]
LEGAL_TRANSITIONS: dict[str, set[str]] = {
    s: ({_FORWARD[i + 1]} if i + 1 < len(_FORWARD) else set())
    for i, s in enumerate(_FORWARD)
}
LEGAL_TRANSITIONS["critiqued"].add("declared")          # critique fails completeness lint
LEGAL_TRANSITIONS["in_progress"].add("accepted")        # material amendment approved
for s in ("accepted", "in_progress", "technically_confirmed", "provisionally_confirmed"):
    LEGAL_TRANSITIONS[s] |= {"disproven", "superseded", "abandoned"}

REQUIRED_FIELDS = [
    "schema_version", "intent_id", "title", "kind", "status", "risk_tier",
    "iteration", "review_by", "owner", "hypothesis", "confirmation_criteria",
    "disproof_criteria", "bindings", "history",
]
# review_by is required, not optional -- an intent may not float indefinitely
# unfalsified.

_INTENT_ID_RE = re.compile(r"^INT-\d{4}-\d{2}-\d{2}-\d{3}$")


def validate_intent(path: Path, repo_root: Path) -> list[str]:
    errors: list[str] = []

    def err(msg: str) -> None:
        errors.append(f"{path.relative_to(repo_root)}: {msg}")

    try:
        data = yaml.safe_load(path.read_text())
    except yaml.YAMLError as exc:
        return [f"{path.relative_to(repo_root)}: not valid YAML ({exc})"]
    if not isinstance(data, dict):
        return [f"{path.relative_to(repo_root)}: not a YAML mapping"]

    for field in REQUIRED_FIELDS:
        if field not in data:
            err(f"missing required field '{field}'")
    if errors:
        return errors  # field-level checks below assume the fields exist

    if data["intent_id"] != path.parent.name:
        err(f"intent_id {data['intent_id']!r} does not match its directory {path.parent.name!r}")
    if not _INTENT_ID_RE.match(str(data["intent_id"])):
        err(f"intent_id {data['intent_id']!r} does not match the INT-YYYY-MM-DD-NNN format")
    if not str(data["hypothesis"]).strip():
        err("hypothesis must be non-empty -- an intent without a claim is not an intent")
    conf = data["confirmation_criteria"]
    if not isinstance(conf, list) or not conf or not all(
        isinstance(c, str) and c.strip() for c in conf
    ):
        err("confirmation_criteria must be a non-empty list of non-empty strings")
    if data["status"] not in STATUSES:
        err(f"status {data['status']!r} not in the lab's vocabulary")
    if data["risk_tier"] not in RISK_TIERS:
        err(f"risk_tier {data['risk_tier']!r} not in T0-T3")
    if data["kind"] not in KINDS:
        err(f"kind {data['kind']!r} not in the tektograph-1.0 kind set")

    disproof = data["disproof_criteria"]
    if not isinstance(disproof, list) or not disproof or not all(
        isinstance(c, str) and c.strip() for c in disproof
    ):
        err("disproof_criteria must be a non-empty list of non-empty strings -- "
            "falsifiability is mandatory")

    owner = data["owner"]
    if not isinstance(owner, dict) or "accountable_human" not in owner:
        err("owner must name an accountable_human")

    history = data["history"]
    if not isinstance(history, list) or not history:
        err("history must be a non-empty append-only list")
    else:
        for i, entry in enumerate(history):
            if not isinstance(entry, dict) or not {"status", "date", "by", "evidence"} <= set(entry):
                err(f"history[{i}] must carry status/date/by/evidence")
                break
        else:
            if history[0]["status"] != "declared":
                err(f"history must begin at 'declared', not {history[0]['status']!r}")
            for prev, curr in zip(history, history[1:]):
                if curr["status"] not in LEGAL_TRANSITIONS.get(prev["status"], set()):
                    err(f"illegal transition {prev['status']!r} -> {curr['status']!r}")
            if history[-1]["status"] != data["status"]:
                err(f"status field {data['status']!r} disagrees with history tail "
                    f"{history[-1]['status']!r}")
            if data["status"] in TERMINAL:
                final = history[-1]
                if not str(final.get("evidence", "")).strip():
                    err(f"terminal status {data['status']!r} requires cited evidence "
                        "in the final history entry")

    bindings = data["bindings"]
    if not isinstance(bindings, dict):
        err("bindings must be a mapping")
    else:
        for manifest in bindings.get("mission_manifests", []) or []:
            if not (repo_root / manifest).exists():
                err(f"bindings.mission_manifests path does not exist: {manifest}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", default=".hekton/intents",
                        help="Registry directory (default: .hekton/intents)")
    parser.add_argument("--repo-root", default=".", help="Repository root")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    registry = repo_root / args.registry
    if not registry.is_dir():
        print(f"intent registry not found at {registry} -- nothing to validate")
        return 0

    intent_files = sorted(registry.glob("*/intent.yaml"))
    if not intent_files:
        print(f"intent registry at {registry} is empty -- nothing to validate")
        return 0

    all_errors: list[str] = []
    for path in intent_files:
        errs = validate_intent(path, repo_root)
        status = "FAIL" if errs else "ok"
        try:
            status_str = yaml.safe_load(path.read_text()).get("status", "?")
        except Exception:
            status_str = "?"
        print(f"[{status}] {path.parent.name} (status: {status_str})")
        all_errors.extend(errs)

    if all_errors:
        print(f"\n{len(all_errors)} violation(s):")
        for e in all_errors:
            print(f"  - {e}")
        return 1
    print(f"\n{len(intent_files)} intent(s) valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
