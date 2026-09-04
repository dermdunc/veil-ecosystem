#!/usr/bin/env python3
"""veil-ecosystem status collector -- Phase 0 of docs/interactive-plan.md.

Reads an explicit component allow-list (scripts/eco-components.json, or
$VEIL_ECO_COMPONENTS_FILE) and never scans a directory -- factory-output/
now holds several unrelated private repos alongside this family's own two
private siblings, and interactive-plan.md section 4 names that as a real
leak vector for anything that walks the directory instead of reading a
fixed list.

Collects only machine-verifiable facts, each wrapped with {value, source,
observed_at}: per-checkout git HEAD/branch/dirty/ahead/behind vs
origin/main; GitHub visibility and current repo name via `gh api`
(degrades to source="unavailable" rather than crashing when gh or the
network is unreachable -- confirmed necessary the hard way, when a Codex
critique run hit exactly that failure); .github/workflows/ci.yml vs
ci-proposed/ci.yml presence; privacy_boundary from each repo's own
.hekton/project.yaml.

veil-ecosystem-private/ and veil-foundations-private/ are never read --
not because of a name check (there is one, defensively) but because they
are never in the component list in the first place.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_CONFIG = SCRIPT_DIR / "eco-components.json"
SCHEMA_VERSION = "veil.ecostatus.v1"

# Belt-and-braces: even though the allow-list is the sole source of paths,
# refuse to touch anything whose basename isn't one of these -- a defence
# against a future config edit accidentally widening scope.
ALLOWED_BASENAMES = {
    "veilgremlin",
    "veil-foundations",
    "veil-custodian",
    "veil-enrol",
    "veil-observatory",
    "veil-demo",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_config(config_path: Path) -> dict:
    with config_path.open() as f:
        return json.load(f)


def resolve_component_path(component: dict, config_path: Path, config: dict) -> Path:
    if "path_env" in component:
        env_value = os.environ.get(component["path_env"])
        raw = env_value if env_value else component["path_env_default"]
        path = Path(os.path.expanduser(raw)).resolve()
    else:
        base_env = config.get("base_dir_env")
        base_override = os.environ.get(base_env) if base_env else None
        # base_dir_default is relative to this repo's root (config_path's
        # grandparent: scripts/eco-components.json -> scripts/ -> repo
        # root), not to scripts/ itself -- ".." from the repo root lands
        # in factory-output/, which is what every sibling path assumes.
        base = Path(base_override) if base_override else (config_path.parent.parent / config["base_dir_default"])
        path = (base / component["relative_path"]).resolve()

    if path.name not in ALLOWED_BASENAMES:
        raise ValueError(
            f"refusing to read {path} -- basename {path.name!r} is not in the "
            f"component allow-list; this should be impossible via the shipped config"
        )
    return path


def run(cmd: list[str], cwd: Path | None = None, timeout: float = 8.0) -> tuple[int, str, str]:
    try:
        proc = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return proc.returncode, proc.stdout.strip(), proc.stderr.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        return 1, "", str(exc)


def provenance(value, source: str, observed_at: str | None = None) -> dict:
    return {"value": value, "source": source, "observed_at": observed_at if observed_at is not None else now_iso()}


def unavailable() -> dict:
    return {"value": None, "source": "unavailable", "observed_at": None}


def collect_git_facts(path: Path) -> dict:
    facts: dict = {}
    if not path.is_dir():
        facts["local_head"] = unavailable()
        facts["local_branch"] = unavailable()
        facts["dirty"] = unavailable()
        facts["remote_head"] = unavailable()
        facts["ahead"] = unavailable()
        facts["behind"] = unavailable()
        return facts

    rc, head, _ = run(["git", "rev-parse", "HEAD"], cwd=path)
    facts["local_head"] = provenance(head, "probed") if rc == 0 else unavailable()

    rc, branch, _ = run(["git", "branch", "--show-current"], cwd=path)
    facts["local_branch"] = provenance(branch or None, "probed") if rc == 0 else unavailable()

    rc, status_out, _ = run(["git", "status", "--porcelain"], cwd=path)
    facts["dirty"] = provenance(bool(status_out), "probed") if rc == 0 else unavailable()

    # Best-effort fetch so ahead/behind reflect the real remote, not a
    # possibly-days-stale local remote-tracking ref. Never fatal if it
    # fails (no network, no remote, etc.) -- fall back to whatever
    # remote-tracking ref is already there, explicitly marked as such.
    fetch_rc, _, _ = run(["git", "fetch", "origin", "main"], cwd=path, timeout=15.0)
    fetch_source = "probed" if fetch_rc == 0 else "machine-derived"

    rc, remote_head, _ = run(["git", "rev-parse", "origin/main"], cwd=path)
    facts["remote_head"] = provenance(remote_head, fetch_source) if rc == 0 else unavailable()

    if rc == 0:
        rc_a, ahead_out, _ = run(["git", "rev-list", "--count", "origin/main..HEAD"], cwd=path)
        rc_b, behind_out, _ = run(["git", "rev-list", "--count", "HEAD..origin/main"], cwd=path)
        facts["ahead"] = provenance(int(ahead_out), fetch_source) if rc_a == 0 and ahead_out.isdigit() else unavailable()
        facts["behind"] = provenance(int(behind_out), fetch_source) if rc_b == 0 and behind_out.isdigit() else unavailable()
    else:
        facts["ahead"] = unavailable()
        facts["behind"] = unavailable()

    return facts


def collect_ci_facts(path: Path) -> dict:
    has_workflow = (path / ".github" / "workflows" / "ci.yml").is_file()
    has_proposed = (path / "ci-proposed" / "ci.yml").is_file()
    return {
        "has_ci_workflow": provenance(has_workflow, "probed"),
        "has_ci_proposed": provenance(has_proposed, "probed"),
    }


def read_privacy_boundary(path: Path) -> dict:
    project_yaml = path / ".hekton" / "project.yaml"
    if not project_yaml.is_file():
        return unavailable()
    try:
        text = project_yaml.read_text()
    except OSError:
        return unavailable()
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("privacy_boundary:"):
            value = stripped.split(":", 1)[1].strip().strip('"').strip("'")
            return provenance(value, "machine-derived")
    return unavailable()


def gh_available() -> bool:
    rc, _, _ = run(["gh", "--version"], timeout=3.0)
    return rc == 0


def collect_github_facts(github_repo: str | None, gh_ok: bool) -> dict:
    if not github_repo or not gh_ok:
        return {
            "github_visibility": unavailable(),
            "github_current_name": unavailable(),
        }
    rc, out, _ = run(
        ["gh", "api", f"repos/{github_repo}", "--jq", "{name,full_name,visibility}"],
        timeout=10.0,
    )
    if rc != 0 or not out:
        return {
            "github_visibility": unavailable(),
            "github_current_name": unavailable(),
        }
    try:
        data = json.loads(out)
    except json.JSONDecodeError:
        return {
            "github_visibility": unavailable(),
            "github_current_name": unavailable(),
        }
    return {
        "github_visibility": provenance(data.get("visibility"), "probed"),
        "github_current_name": provenance(data.get("full_name"), "probed"),
    }


def derive_tier(privacy_boundary: dict, github_visibility: dict) -> str:
    """The schema calls tier "enforced by code," so it must be computed
    from real facts, not a hand-set default -- a hardcoded "internal" for
    every repo (including the genuinely-public veil-proxy) would make that
    claim false. Fails closed: tier is only "public" when BOTH the
    declared privacy_boundary and the actual GitHub visibility agree it's
    public; any missing, unavailable, or disagreeing signal defaults to
    "internal", never "public" by default.
    """
    if privacy_boundary["source"] == "unavailable" or github_visibility["source"] == "unavailable":
        return "internal"
    if privacy_boundary["value"] == "public" and github_visibility["value"] == "public":
        return "public"
    return "internal"


def collect_repo(component: dict, path: Path, gh_ok: bool) -> dict:
    entry = {
        "name": component["name"],
        "kind": component["kind"],
        "local_path": str(path),
        "github_repo": component.get("github_repo"),
        "github_repo_aliases": component.get("github_repo_aliases", []),
    }
    entry["privacy_boundary"] = read_privacy_boundary(path)
    entry.update(collect_github_facts(component.get("github_repo"), gh_ok))
    entry["tier"] = derive_tier(entry["privacy_boundary"], entry["github_visibility"])
    entry.update(collect_git_facts(path))
    entry.update(collect_ci_facts(path))
    return entry


def collect(config_path: Path, now: str | None = None) -> dict:
    """`now`, when given, overrides generated_at -- the schema document
    describes this document-level timestamp as caller-injectable
    specifically so a re-run is reproducible and testable; per-field
    observed_at timestamps are NOT overridden by this, since those are
    supposed to reflect real observation time, not a fixed test fixture.
    """
    config = load_config(config_path)
    gh_ok = gh_available()
    repos = []
    for component in config["components"]:
        path = resolve_component_path(component, config_path, config)
        repos.append(collect_repo(component, path, gh_ok))

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": now if now is not None else now_iso(),
        "repos": repos,
        "integrations": [],  # populated by eco_checker.py from docs/architecture.md
        "runtime": [],  # reserved for Phase 1
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    env_config = os.environ.get("VEIL_ECO_COMPONENTS_FILE")
    parser.add_argument("--config", type=Path, default=Path(env_config) if env_config else DEFAULT_CONFIG)
    parser.add_argument("--out", type=Path, default=None, help="write JSON here instead of stdout")
    args = parser.parse_args()

    doc = collect(args.config)
    output = json.dumps(doc, indent=2)
    if args.out:
        args.out.write_text(output + "\n")
    else:
        print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
