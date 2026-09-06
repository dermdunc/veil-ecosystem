# Retire / Promote Review: Veil Ecosystem

**Last updated:** 2026-09-06 (first real review since scaffold).

## Retire / Promote Review

### Current state
Active, factory-output classification per `.hekton/project.yaml` (`component_type: factory-output`,
`promotion_target: none`, `promotion_candidate: false`). It is the master architecture/coordination
repo for the six-repo VeilGremlin family (veil-proxy/veilgremlin, veil-foundations, veil-custodian,
veil-enrol, veil-observatory, veil-demo) and, as of 2026-09-04, is no longer documentation-only — it
ships and tests real automation (`scripts/eco_collector.py`, `eco_checker.py`, `eco.sh`) that other
repos' `next-actions.md` files reference by stable ID (`XREPO-00N`).

### Evidence gathered
- **Commit cadence:** 30 commits visible in `git log`, spanning 2026-08-24 to 2026-09-06 (today),
  all on `main` via merged PRs (#1–#17). Working tree is clean, `origin/main` up to date — verified
  with two `git status` calls 4 seconds apart before touching anything.
- **Tests are real and pass:** `python3 -m unittest discover -s tests -v` → **28 tests, all OK**
  (2026-09-06 run). README currently under-states this as "17-test," a live drift between prose and
  code the checker itself is designed to catch elsewhere but hasn't caught here.
- **CI is real and green:** `gh run list` shows the last 8 `CI` runs on `main`/PR branches all
  `completed success` (2026-09-05 through 2026-09-06), running `unittest discover`, a bootstrap
  script, and `scripts/verify-project.sh` — not just a lint stub.
- **Cross-repo mechanism is actually used, not aspirational:** `docs/cross-repo-deps.md` /
  `.hekton/cross-repo-deps.yaml` show 3 of 6 `XREPO-*` items closed in the last 24–48 hours
  (XREPO-001, -003, -005, closed 2026-09-05/06) with specific evidence per closure (PR numbers,
  live-run proofs, test counts in the *other* repos). This is the concrete "used in a real workflow"
  signal the Lab→Platform checklist asks for, even though this repo's own classification is
  factory-output, not lab.
- **Documentation discipline is unusually strong but self-critical:** `docs/risks.md` and
  `docs/decisions.md` document the project catching its own errors multiple times (RISK-0002:
  a 10-day-old architecturally-impossible edge in the integration diagram; RISK-0005: a stale
  "structural stub" claim about veil-observatory's verifier copied faithfully from a stale source).
  This is evidence of a real doubt-driven-development review habit, not just claimed rigor.
- **Known unresolved gaps, disclosed, not hidden:** RISK-0002's mitigation (contradiction checker)
  is not yet wired into CI (deferred — protected-path commit needed); RISK-0006 records veil-demo's
  production deployment is down (Fly.io trial lapsed) and unresolved as of 2026-08-30, still open.
- **Metadata drift:** `.hekton/project.yaml` still shows `maturity_level: 1` / `maturity_label:
  experimental`, `maturity_basis: asserted`, `maturity_date: 2026-08-24` — unchanged since scaffold
  despite the substantial automation/testing/CI work landed since. `version: ""` is also unset,
  despite the factory-output versioning table's "beta" bar (first real use, feedback in progress)
  arguably already being met by the XREPO closures.
- **Private sibling confirmed related, not duplicative:** `veil-ecosystem-private` exists at the
  sibling path and holds `CLAUDE.md`/`AGENTS.md`/`CODEX.md`, `mind-palace/`, and `runs/` —
  consistent with this repo's own `project.yaml` comment that session machinery and the
  `agent-run-log.yaml`/`change-log.yaml` live there because this repo is public-capable. Not
  reviewed further here (out of scope; not to be edited).
- **Cluster overlap noted, not duplicated:** This repo's `related_projects`/`enables` list names
  veilgremlin, veil-foundations, veil-custodian, veil-enrol, veil-observatory, veil-demo — all
  reportedly under parallel review by other agents this session. No attempt made here to assess
  those repos directly; only this repo's own claims about them were checked (test run, CI run
  list, its own docs).

### Value score
- **Reuse:** High — the cross-repo-deps registry and `veil.ecostatus.v1` schema are actively
  consumed (by ID) from at least 3 sibling repos' own `next-actions.md` files this week.
- **Clarity:** High — architecture.md, decisions.md, risks.md, next-actions.md all carry explicit
  dates and are cross-linked; the README openly corrects its own past inaccuracies rather than
  quietly editing them away.
- **Automation:** Medium — real collector/checker/CI exist and pass (28 tests), but the
  contradiction-checker is not yet enforced in CI (self-disclosed gap), and CI still trails README
  prose (28 vs. claimed "17" tests).
- **Decision quality:** High — repeated, dated doubt-driven-development reviews have caught and
  corrected real, material errors (architecturally-impossible edges, stale verifier claims) rather
  than merely asserting rigor.
- **Strategic leverage:** High — this is the only place the 6-repo family's cross-cutting state
  (trust boundaries, XREPO dependencies, integration status) is tracked at all; its absence would
  leave those dependencies implicit and repo-siloed.

### Cognitive load score
**Medium.** Core docs total ~1,700 lines (`architecture.md` 692 lines/55KB alone), plus
`decisions.md`/`risks.md`/`next-actions.md`/`interactive-plan.md`. The structure is consistent
(dated entries, "correct in place, don't delete" convention) and cross-linked, which keeps it
navigable, but a new reader needs several of these files simultaneously to get oriented, and the
project's own risk register admits documentation staleness is an ongoing, only-partially-mitigated
hazard (RISK-0002, RISK-0005).

### Recommendation
**Keep.**

### Rationale
Against the vault's Lab→Platform checklist: this repo isn't a lab and isn't seeking platform
promotion (`promotion_candidate: false`, `promotion_target: none` — both self-declared and
consistent with its role as a cross-cutting coordination/architecture document rather than a
reusable component). Judged instead as an active factory output against the Project→Archive
criteria, it fails every archival trigger: development is active (commits as recently as today,
2026-09-06), it has documented near-term work (`docs/next-actions.md`), and no dependency has been
orphaned. It is not a stale scaffold — the 2026-09-04 shift from "documentation-only" to a tested,
CI-gated automation layer (28 passing tests, `eco_checker`/`eco_collector`/`eco.sh`) is real,
verified evidence of ongoing investment, not a claim taken on faith. The strongest single piece of
evidence is the cross-repo dependency registry (`docs/cross-repo-deps.md`) showing three `XREPO-*`
items independently closed by sibling repos in the last 48 hours, citing this repo's own stable IDs
— that is reuse-in-the-wild, not aspirational documentation.

The two things holding this back from a cleaner "Promote"-equivalent (factory-output has no higher
tier to promote to, but the versioning table implies a `v0`→`beta` bump) are self-inflicted and
easy to close: the `.hekton/project.yaml` maturity/version metadata has not been touched since
scaffold (2026-08-24) despite the project having since met its own "beta" bar, and README's test
count (17) already lags the actual suite (28) — the exact kind of prose/code drift this project's
own tooling exists to catch, just not yet turned on itself.

### Next action
1. Human: bump `.hekton/project.yaml`'s `version` field from `""` to `beta` and refresh
   `maturity_date`/`maturity_basis` to reflect the 2026-09-04+ automation work (or explicitly
   decide not to and record why).
2. Update the README's "17-test unit suite" line to the current count (28) — cheap, and closes a
   drift the project's own checker philosophy says should never survive unnoticed.
3. Carry RISK-0002's remaining mitigation (wiring the contradiction checker into CI) and RISK-0006
   (veil-demo deployment down) forward as open items — do not close this review's loop by treating
   them as resolved.
