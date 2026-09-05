# Cross-Repo Dependencies

Machine-readable state lives in `.hekton/cross-repo-deps.yaml`. Keep this Markdown
file as the human-readable explanation of the same IDs — `eco_checker.py`'s
`check_cross_repo_dep_ids` fails the build if a repo's `next-actions.md`
references an ID that doesn't exist in the YAML, the same discipline this repo
already applies to `.hekton/risk-register.yaml` vs. `docs/risks.md`.

**What this is, and what it isn't.** This is an index of dependencies that cross a
repo boundary — one repo is blocked on, or waiting for, another. It is not a
second copy of `docs/architecture.md`'s "Sequencing to close them" section,
which still owns the fuller reasoning and priority order. A repo's own
`next-actions.md` should reference an ID here (`XREPO-00N`) rather than
restating the dependency's own description independently — that restatement is
exactly the drift that produced this registry (see `docs/decisions.md`,
2026-09-04).

| ID | Repos | Status | Summary |
|---|---|---|---|
| XREPO-001 | veil-observatory, veil-custodian | Open | veil-observatory has never called any of veil-custodian's three `Role::Observatory`-gated endpoints. |
| XREPO-002 | veil-foundations, veil-observatory | Open | No sandbox AWS account exists — blocks veil-foundations' real-world validation and veil-observatory's real evidence ingestion. |
| XREPO-003 | veil-custodian, veil-enrol | Open | veil-custodian has no signing-key renewal endpoint; veil-enrol has no subcommand to call one that doesn't exist. Both repos independently named the other half of this gap, unlinked, until today. |
| XREPO-004 | veilgremlin, veil-custodian, veil-observatory | Closed 2026-09-05 | veilgremlin's raw `r\|\|s` (not DER) signature-encoding decision. veil-demo's 2026-09-05 ECDSA signing proof confirmed the encoding is sound and independently verifiable; human sign-off given on that evidence. Real ECDSA verification in veil-observatory is separate, still-unbuilt work this closure doesn't schedule. |
| XREPO-005 | veil-observatory, veilgremlin | Open | Whether ADR-0014's correlation/determinism suite should join the existing cross-repo CI veto ADR-0012's test already has — named in veil-observatory's own backlog as needing a joint decision, not yet made. |

## How an entry gets here

Found by grepping all six repos' `next-actions.md`/`decisions.md` files for
cross-repo language during a 2026-09-04 consolidation pass (prompted by a Codex
critique of an earlier, simpler design that tried to anchor into
`architecture.md`'s numbered sequencing list directly — rejected once actually
checked: numbered-list items don't get real anchors, and the section gets
reordered/struck-through too often for position-based references to survive).
This is a first population, not an exhaustive audit — there are almost
certainly more real cross-repo dependencies stated independently somewhere in
six repos' worth of backlog than the five caught in this pass. Add to this file
as more are found; each new entry should cite where it was found (which repo's
`next-actions.md`, roughly which date) the way the entries above do.

## How to close one

Flip `status: open` to `status: closed` in the YAML, add a `closed_date`, and
leave the entry in place (matching this project's "correct in place with a
date, don't delete history" convention for `docs/decisions.md`) rather than
removing the row — a closed dependency is itself informative history about
what used to block what.
