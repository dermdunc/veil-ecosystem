#!/usr/bin/env python3
"""veil-ecosystem contradiction checker -- Phase 0 of docs/interactive-plan.md.

Runs the collector, parses docs/architecture.md's Integration Status table
(using the Status-cell enum convention added 2026-09-04), and flags
hand-asserted claims that conflict with a machine-verifiable fact:

  - declared privacy_boundary vs actual GitHub visibility
  - claimed GitHub repo name vs gh api's current name (would have caught
    architecture.md asserting veilgremlin "still hasn't" been renamed, the
    same day the rename had already happened)
  - risk-register.yaml vs risks.md RISK-ID set parity (the exact drift this
    document's own no-mirror decision was justified by)
  - links in README.md and docs/architecture.md resolving to files that
    actually exist in the repo
  - the veil-demo Cargo.toml pin resolving to a real commit in the
    veil-proxy checkout (not string-compared -- the pin has been a
    truncated SHA before)
  - Integration Status table cells conforming to the Status-cell enum

Exits non-zero if any error-severity contradiction is found. Warnings do
not fail the build but are always printed -- a silent warning is worse
than a noisy one for a tool whose whole job is catching drift.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import eco_collector  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent

STATUS_ENUM_PHRASES = {
    "Wired and demonstrated": "wired_and_demonstrated",
    "Built, no caller": "built_no_caller",
    "Callee built, no caller": "built_no_caller",  # pre-convention wording, still accepted
    "Built, locally proven": "built_locally_proven",
    "Built, not live": "built_not_live",
    "Missing": "missing",
}

VISIBILITY_TO_PRIVACY = {
    # A GitHub visibility value is "consistent" with a set of acceptable
    # declared privacy_boundary values. Anything outside this set is a
    # contradiction worth a human's attention, not necessarily a bug --
    # veil-foundations' own row is a known, disclosed, still-open case.
    "public": {"public"},
    "private": {"internal", "local-first"},
}


def add_contradiction(out: list[dict], rule: str, message: str, severity: str = "error") -> None:
    out.append({"rule": rule, "message": message, "severity": severity})


def check_github_probe_health(repos: list[dict], out: list[dict], gh_ok: bool) -> None:
    """A per-repo `gh api` failure looks identical to gh being globally
    unavailable (both become source: "unavailable") unless checked
    separately -- a typo'd github_repo slug in the config would otherwise
    degrade silently into the same "clean, offline" outcome as a healthy
    blank machine, which defeats the point of a contradiction checker.
    """
    if not gh_ok:
        return  # gh itself is unavailable -- every repo degrading is expected, not a finding.
    for repo in repos:
        if repo["github_visibility"]["source"] == "unavailable" or repo["github_current_name"]["source"] == "unavailable":
            add_contradiction(
                out,
                "github_probe_failed",
                f"{repo['name']}: `gh` is available and reachable, but the API call for "
                f"github_repo={repo.get('github_repo')!r} still failed -- likely a wrong or "
                f"renamed slug in eco-components.json, not an offline machine.",
                severity="warning",
            )


def check_privacy_vs_visibility(repos: list[dict], out: list[dict]) -> None:
    for repo in repos:
        privacy = repo["privacy_boundary"]
        visibility = repo["github_visibility"]
        if privacy["source"] == "unavailable" or visibility["source"] == "unavailable":
            continue
        acceptable = VISIBILITY_TO_PRIVACY.get(visibility["value"])
        if acceptable is not None and privacy["value"] not in acceptable:
            add_contradiction(
                out,
                "privacy_vs_visibility",
                f"{repo['name']}: declared privacy_boundary={privacy['value']!r} but GitHub "
                f"visibility is {visibility['value']!r} -- these disagree.",
                severity="warning",
            )


def check_repo_name_vs_github(repos: list[dict], out: list[dict]) -> None:
    for repo in repos:
        current = repo["github_current_name"]
        if current["source"] == "unavailable":
            continue
        claimed = repo.get("github_repo")
        aliases = set(repo.get("github_repo_aliases", []))
        if claimed and current["value"] != claimed and current["value"] not in aliases:
            add_contradiction(
                out,
                "repo_name_vs_github",
                f"{repo['name']}: configured github_repo={claimed!r} but `gh api` reports the "
                f"current name is {current['value']!r} -- update eco-components.json (and any "
                f"prose claiming the old name is still current).",
                severity="error",
            )


def check_risk_register_parity(out: list[dict]) -> None:
    yaml_path = REPO_ROOT / ".hekton" / "risk-register.yaml"
    md_path = REPO_ROOT / "docs" / "risks.md"
    yaml_ids = set(re.findall(r"id:\s*(RISK-\d+)", yaml_path.read_text())) if yaml_path.is_file() else set()
    md_ids = set(re.findall(r"\bRISK-\d+\b", md_path.read_text())) if md_path.is_file() else set()
    only_in_yaml = yaml_ids - md_ids
    only_in_md = md_ids - yaml_ids
    if only_in_yaml or only_in_md:
        add_contradiction(
            out,
            "risk_register_parity",
            f".hekton/risk-register.yaml and docs/risks.md disagree on which risks exist -- "
            f"only in YAML: {sorted(only_in_yaml) or 'none'}; only in Markdown: "
            f"{sorted(only_in_md) or 'none'}.",
            severity="error",
        )


XREPO_ID_PATTERN = re.compile(r"\bXREPO-\d+\b")


def _find_registry_ids() -> set[str]:
    registry_path = REPO_ROOT / ".hekton" / "cross-repo-deps.yaml"
    if not registry_path.is_file():
        return set()
    return set(re.findall(r"id:\s*(XREPO-\d+)", registry_path.read_text()))


def check_cross_repo_dep_ids(repos: list[dict], out: list[dict]) -> None:
    """Mirrors check_risk_register_parity's pattern for a different stable-ID
    registry: `.hekton/cross-repo-deps.yaml` (machine-readable) vs.
    `docs/cross-repo-deps.md` (human-readable) vs. every repo's own
    `next-actions.md`, which is expected to *reference* an ID rather than
    restate the dependency independently. Only the "dangling reference"
    direction is an error -- a referenced ID that doesn't exist anywhere is
    unambiguously a typo or a stale reference. The reverse (a registry entry
    nothing references yet) is a warning, not an error: this registry was
    seeded by a one-time grep, not fully backfilled everywhere on day one,
    and treating an unreferenced-but-real entry as a failure would make the
    first honest run of this check red for reasons that aren't bugs.
    """
    registry_ids = _find_registry_ids()
    md_path = REPO_ROOT / "docs" / "cross-repo-deps.md"
    md_ids = set(XREPO_ID_PATTERN.findall(md_path.read_text())) if md_path.is_file() else set()
    only_in_yaml = registry_ids - md_ids
    only_in_md = md_ids - registry_ids
    if only_in_yaml or only_in_md:
        add_contradiction(
            out,
            "cross_repo_dep_parity",
            f".hekton/cross-repo-deps.yaml and docs/cross-repo-deps.md disagree on which "
            f"dependencies exist -- only in YAML: {sorted(only_in_yaml) or 'none'}; only in "
            f"Markdown: {sorted(only_in_md) or 'none'}.",
            severity="error",
        )

    referenced_ids: set[str] = set()
    sources = [("veil-ecosystem", REPO_ROOT)] + [(r["name"], Path(r["local_path"])) for r in repos]
    for repo_name, repo_path in sources:
        na_path = repo_path / "docs" / "next-actions.md"
        if not na_path.is_file():
            continue
        for match in XREPO_ID_PATTERN.findall(na_path.read_text()):
            referenced_ids.add(match)
            if match not in registry_ids:
                add_contradiction(
                    out,
                    "cross_repo_dep_dangling_reference",
                    f"{repo_name}'s docs/next-actions.md references {match!r}, which does not "
                    "exist in .hekton/cross-repo-deps.yaml -- typo, or a stale reference to a "
                    "removed entry.",
                    severity="error",
                )

    unreferenced = registry_ids - referenced_ids
    if unreferenced:
        add_contradiction(
            out,
            "cross_repo_dep_unreferenced",
            f"{sorted(unreferenced)} exist in the registry but are not referenced from any "
            "repo's docs/next-actions.md yet -- not necessarily wrong (this registry was "
            "seeded by a one-time grep, backfilling is incremental), but worth checking.",
            severity="warning",
        )


def extract_markdown_links(text: str) -> list[str]:
    return re.findall(r"\[[^\]]*\]\(([^)]+)\)", text)


def check_links(out: list[dict]) -> None:
    for doc_name in ("README.md", "docs/architecture.md"):
        doc_path = REPO_ROOT / doc_name
        if not doc_path.is_file():
            continue
        for raw_link in extract_markdown_links(doc_path.read_text()):
            if raw_link.startswith("http://") or raw_link.startswith("https://") or raw_link.startswith("#"):
                continue
            # Strip a trailing `"title"` (markdown link title syntax) and
            # any #anchor before resolving to a filesystem path.
            link = raw_link.split(" ", 1)[0]
            link_path = link.split("#", 1)[0]
            if not link_path:
                continue
            # A leading "/" means repo-root-relative in this project's own
            # convention, not filesystem-root -- resolving it against
            # doc_path.parent would silently discard the leading slash
            # (pathlib treats an absolute operand as replacing the base),
            # which either false-positives a real link or false-negatives
            # a broken one depending on what happens to exist at "/".
            base = REPO_ROOT if link_path.startswith("/") else doc_path.parent
            target = (base / link_path.lstrip("/")).resolve()
            if not target.is_file():
                add_contradiction(
                    out,
                    "broken_link",
                    f"{doc_name} links to {raw_link!r}, which does not resolve to a file on disk.",
                    severity="error",
                )


def check_demo_pin(repos: list[dict], out: list[dict]) -> None:
    demo = next((r for r in repos if r["name"] == "veil-demo"), None)
    proxy = next((r for r in repos if r["name"] == "veil-proxy"), None)
    if demo is None or proxy is None:
        return
    cargo_toml = Path(demo["local_path"]) / "Cargo.toml"
    if not cargo_toml.is_file():
        return
    text = cargo_toml.read_text()
    # All six vg-* crates are pinned independently in veil-demo's
    # Cargo.toml (vg-core, vg-vault, vg-detectors, vg-parsers, vg-policy,
    # vg-audit) -- checking only vg-core's pin misses a partial bump that
    # leaves the others mismatched, which Cargo itself wouldn't catch
    # either (each `rev =` is resolved independently).
    pins = dict(re.findall(r'(vg-[a-z]+)\s*=\s*\{[^}]*rev\s*=\s*"([0-9a-f]+)"', text))
    if not pins:
        add_contradiction(
            out,
            "demo_pin",
            "veil-demo/Cargo.toml has no resolvable vg-* git rev pins -- expected `rev = "
            '"<sha>"` entries.',
            severity="warning",
        )
        return
    distinct_pins = set(pins.values())
    if len(distinct_pins) > 1:
        add_contradiction(
            out,
            "demo_pin",
            f"veil-demo/Cargo.toml's vg-* crates are pinned to different commits, a partial "
            f"bump: {pins!r}.",
            severity="error",
        )
    for crate, pin in pins.items():
        if len(pin) < 40:
            add_contradiction(
                out,
                "demo_pin",
                f"veil-demo/Cargo.toml pins {crate} to a {len(pin)}-character SHA ({pin!r}) -- "
                "shorter than a full 40-character SHA. Cargo resolves the prefix, but any "
                "currency check that string-compares against a full HEAD will silently "
                "misbehave.",
                severity="warning",
            )
        rc, _, _ = eco_collector.run(["git", "cat-file", "-e", f"{pin}^{{commit}}"], cwd=Path(proxy["local_path"]))
        if rc != 0:
            add_contradiction(
                out,
                "demo_pin",
                f"veil-demo's pin for {crate} ({pin!r}) does not resolve in the veil-proxy "
                f"checkout at {proxy['local_path']!r} -- the pin may be wrong, or the checkout "
                "needs a fetch.",
                severity="error",
            )


def parse_integration_table(out: list[dict]) -> list[dict]:
    arch_path = REPO_ROOT / "docs" / "architecture.md"
    integrations: list[dict] = []
    if not arch_path.is_file():
        return integrations
    text = arch_path.read_text()
    match = re.search(r"\| Integration \| Status \|\n\|[-|]+\|\n((?:\|.*\n)+)", text)
    if not match:
        add_contradiction(
            out,
            "integration_table_parse",
            "Could not locate the Integration Status table in docs/architecture.md -- its "
            "header row may have changed shape.",
            severity="error",
        )
        return integrations
    for line in match.group(1).splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|", 1)]
        if len(cells) != 2:
            # A row with no "|" separator at all after stripping the outer
            # pipes -- genuinely malformed, not just a status cell that
            # happens to contain its own "|" (split(..., 1) already
            # handles that correctly). Flagged, not silently dropped: a
            # row vanishing from the table with a clean 0-error run is
            # exactly the false-negative failure mode this checker exists
            # to prevent.
            add_contradiction(
                out,
                "integration_table_parse",
                f"Integration Status row {line!r} does not split into exactly two columns -- "
                "skipped, not included in the parsed integration list.",
                severity="error",
            )
            continue
        edge, status_cell = cells
        bold_match = re.match(r"^\*\*([^*]+?)\.?\*\*", status_cell)
        status_text = bold_match.group(1) if bold_match else None
        status_enum = STATUS_ENUM_PHRASES.get(status_text) if status_text else None
        if status_enum is None:
            add_contradiction(
                out,
                "status_cell_enum",
                f"Integration Status row {edge!r} does not open with a recognised bold status "
                f"phrase (got {status_text!r}) -- see docs/interactive-plan.md's Status-cell "
                "convention.",
                severity="error",
            )
            status_enum = "missing"
        from_to = edge.split("→", 1)
        integrations.append(
            {
                "from": from_to[0].strip() if len(from_to) == 2 else edge,
                "to": from_to[1].split("(", 1)[0].strip() if len(from_to) == 2 else "",
                "status_enum": status_enum,
                "detail": status_cell,
                "verification": {"value": "hand-asserted", "source": "hand-asserted", "observed_at": None},
                # Hardcoded, not yet derived, unlike repos[]'s tier (see
                # eco_collector.derive_tier). Deriving an integration's own
                # export tier needs its own design pass -- Phase 2 scope,
                # not guessed here. Fails closed to "internal" in the
                # meantime, same direction as the repo-level default.
                "tier": "internal",
            }
        )
    return integrations


DEV_E2E_RESULT_RELATIVE_PATH = Path(".project-setup") / "last-runs" / "dev-e2e.json"


def apply_dev_e2e_verification(repos: list[dict], integrations: list[dict], out: list[dict]) -> None:
    """veil-enrol/scripts/dev-e2e.sh persists a last-run result (added
    2026-09-04, see veil-enrol PR #3) specifically so this can flip the
    veil-enrol -> veil-custodian row from verification: hand-asserted to
    probed -- the first integration row in the family for which that flip
    is actually possible, per docs/interactive-plan.md section 4's design.
    """
    veil_enrol = next((r for r in repos if r["name"] == "veil-enrol"), None)
    row = next((i for i in integrations if i["from"] == "veil-enrol" and i["to"] == "veil-custodian"), None)
    if veil_enrol is None or row is None:
        return
    result_path = Path(veil_enrol["local_path"]) / DEV_E2E_RESULT_RELATIVE_PATH
    if not result_path.is_file():
        return
    try:
        result = json.loads(result_path.read_text())
    except (OSError, json.JSONDecodeError):
        add_contradiction(
            out,
            "dev_e2e_result",
            f"{result_path} exists but is not valid JSON -- could not use it to verify the "
            "veil-enrol -> veil-custodian integration row.",
            severity="warning",
        )
        return
    status = result.get("status")
    if status == "passed":
        row["verification"] = {
            "value": "probed",
            "source": "probed",
            "observed_at": result.get("finished_at"),
        }
    elif status == "failed":
        add_contradiction(
            out,
            "dev_e2e_result",
            f"veil-enrol's last dev-e2e.sh run FAILED (finished {result.get('finished_at')!r}, "
            f"exit_code={result.get('exit_code')!r}) -- the veil-enrol -> veil-custodian "
            "integration is not currently proven, despite architecture.md's own claim.",
            severity="warning",
        )
    else:
        add_contradiction(
            out,
            "dev_e2e_result",
            f"{result_path} has an unrecognised status {status!r} -- expected 'passed' or 'failed'.",
            severity="warning",
        )


PROVENANCE_SOURCE_ENUM = {"probed", "machine-derived", "hand-asserted", "unavailable"}
REPO_KIND_ENUM = {"service", "cli", "library", "terraform-module", "docs"}
TIER_ENUM = {"public", "internal", "local"}
REPO_PROVENANCE_FIELDS = (
    "privacy_boundary",
    "github_visibility",
    "github_current_name",
    "local_head",
    "local_branch",
    "dirty",
    "remote_head",
    "ahead",
    "behind",
    "has_ci_workflow",
    "has_ci_proposed",
)


def _validate_provenance_field(out: list[dict], where: str, field: dict) -> None:
    if not isinstance(field, dict) or {"value", "source", "observed_at"} - field.keys():
        add_contradiction(out, "schema_shape", f"{where}: not a well-formed provenance object: {field!r}")
        return
    if field["source"] not in PROVENANCE_SOURCE_ENUM:
        add_contradiction(out, "schema_shape", f"{where}: source={field['source']!r} is not in the provenance enum.")
    # By construction (eco_collector.unavailable() vs. provenance()), a field
    # is unavailable if and only if observed_at is None -- this is the one
    # invariant hand-written here specifically because the schema's own
    # comment claims it and nothing had ever checked it was actually true.
    is_unavailable = field["source"] == "unavailable"
    has_no_timestamp = field["observed_at"] is None
    if is_unavailable != has_no_timestamp:
        add_contradiction(
            out,
            "schema_shape",
            f"{where}: source={field['source']!r} but observed_at={field['observed_at']!r} -- "
            "unavailable must mean observed_at is null, and nothing else may leave it null.",
        )


def validate_document_shape(doc: dict, expected_repo_names: set[str], out: list[dict]) -> None:
    """Hand-written structural check against schemas/veil.ecostatus.v1.schema.json,
    since `jsonschema` isn't a stdlib module and the schema itself is currently
    looser than what the collector actually emits (only name/kind/tier are
    schema-required on a repo, but the collector always emits far more) --
    a real `jsonschema` validation today would pass almost anything. This
    checks the fields that actually matter: exact schema_version, the real
    six-repo set, every provenance object's shape/enum/null-iff-unavailable
    invariant, and the enums on kind/tier/status_enum/severity.
    """
    if doc.get("schema_version") != eco_collector.SCHEMA_VERSION:
        add_contradiction(out, "schema_shape", f"schema_version={doc.get('schema_version')!r}, expected {eco_collector.SCHEMA_VERSION!r}.")

    repo_names = {r.get("name") for r in doc.get("repos", [])}
    if repo_names != expected_repo_names:
        add_contradiction(
            out,
            "schema_shape",
            f"repos[] names {sorted(repo_names)} do not match the configured component set "
            f"{sorted(expected_repo_names)}.",
        )

    for repo in doc.get("repos", []):
        name = repo.get("name", "<unnamed>")
        if repo.get("kind") not in REPO_KIND_ENUM:
            add_contradiction(out, "schema_shape", f"{name}: kind={repo.get('kind')!r} is not in the kind enum.")
        if repo.get("tier") not in TIER_ENUM:
            add_contradiction(out, "schema_shape", f"{name}: tier={repo.get('tier')!r} is not in the tier enum.")
        for field_name in REPO_PROVENANCE_FIELDS:
            if field_name in repo:
                _validate_provenance_field(out, f"{name}.{field_name}", repo[field_name])

    for integration in doc.get("integrations", []):
        edge = f"{integration.get('from')} -> {integration.get('to')}"
        if integration.get("status_enum") not in STATUS_ENUM_PHRASES.values():
            add_contradiction(out, "schema_shape", f"{edge}: status_enum={integration.get('status_enum')!r} is not in the enum.")

    # Snapshot: at the real call site, `out` IS `doc["contradictions"]` (see
    # check() below) -- iterating the live list while appending to it would
    # also validate findings this function just added about itself.
    for contradiction in list(doc.get("contradictions", [])):
        if contradiction.get("severity") not in {"error", "warning"}:
            add_contradiction(out, "schema_shape", f"a contradiction has severity={contradiction.get('severity')!r}, not error/warning.")


def check(config_path: Path, now: str | None = None) -> dict:
    doc = eco_collector.collect(config_path, now=now)
    gh_ok = eco_collector.gh_available()
    contradictions: list[dict] = []
    check_github_probe_health(doc["repos"], contradictions, gh_ok)
    check_privacy_vs_visibility(doc["repos"], contradictions)
    check_repo_name_vs_github(doc["repos"], contradictions)
    check_risk_register_parity(contradictions)
    check_cross_repo_dep_ids(doc["repos"], contradictions)
    check_links(contradictions)
    check_demo_pin(doc["repos"], contradictions)
    doc["integrations"] = parse_integration_table(contradictions)
    apply_dev_e2e_verification(doc["repos"], doc["integrations"], contradictions)
    doc["contradictions"] = contradictions
    expected_names = {c["name"] for c in eco_collector.load_config(config_path)["components"]}
    validate_document_shape(doc, expected_names, contradictions)
    return doc


def _fmt(field: dict) -> str:
    if field["source"] == "unavailable":
        return "unavailable"
    return f"{field['value']} ({field['source']})"


def render_repos_table(repos: list[dict]) -> str:
    """The Phase-0 UI, per docs/interactive-plan.md: 'scripts/eco.sh status,
    rendering the full local tier to the terminal. That is the entire
    Phase-0 UI.' A contradiction-only summary is not that -- this renders
    the actual per-repo facts the collector gathered.
    """
    lines = []
    for repo in repos:
        lines.append(f"\n{repo['name']}  [{repo['kind']}, tier={repo['tier']}]")
        lines.append(f"  path:        {repo['local_path']}")
        lines.append(f"  github:      {repo.get('github_repo')} -> {_fmt(repo['github_current_name'])}")
        lines.append(f"  visibility:  {_fmt(repo['github_visibility'])}  privacy_boundary: {_fmt(repo['privacy_boundary'])}")
        lines.append(f"  local HEAD:  {_fmt(repo['local_head'])}  branch: {_fmt(repo['local_branch'])}  dirty: {_fmt(repo['dirty'])}")
        lines.append(f"  vs origin:   ahead={_fmt(repo['ahead'])}  behind={_fmt(repo['behind'])}")
        lines.append(f"  CI:          workflow={_fmt(repo['has_ci_workflow'])}  proposed={_fmt(repo['has_ci_proposed'])}")
    return "\n".join(lines)


def render_integrations_table(integrations: list[dict]) -> str:
    lines = []
    for i in integrations:
        lines.append(f"\n{i['from']} -> {i['to']}  [{i['status_enum']}]")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    default_config = eco_collector.DEFAULT_CONFIG
    parser.add_argument(
        "--config",
        type=Path,
        default=Path(os.environ["VEIL_ECO_COMPONENTS_FILE"]) if os.environ.get("VEIL_ECO_COMPONENTS_FILE") else default_config,
    )
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--json", action="store_true", help="print the full document, not just a summary")
    args = parser.parse_args()

    doc = check(args.config)

    if args.out:
        args.out.write_text(json.dumps(doc, indent=2) + "\n")

    if args.json:
        print(json.dumps(doc, indent=2))
    else:
        print(f"veil.ecostatus.v1 -- generated {doc['generated_at']}")
        print("=" * 60)
        print("REPOS")
        print(render_repos_table(doc["repos"]))
        print()
        print("INTEGRATIONS")
        print(render_integrations_table(doc["integrations"]))
        print()
        print("CONTRADICTIONS")
        errors = [c for c in doc["contradictions"] if c["severity"] == "error"]
        warnings = [c for c in doc["contradictions"] if c["severity"] == "warning"]
        if not doc["contradictions"]:
            print("  none")
        for c in doc["contradictions"]:
            marker = "ERROR" if c["severity"] == "error" else "WARN "
            print(f"[{marker}] ({c['rule']}) {c['message']}")
        print(f"\n{len(errors)} error(s), {len(warnings)} warning(s).")

    has_errors = any(c["severity"] == "error" for c in doc["contradictions"])
    return 1 if has_errors else 0


if __name__ == "__main__":
    sys.exit(main())
