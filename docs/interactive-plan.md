# Making Veil Ecosystem Interactive — Plan

**Status:** design plan, not yet implemented. Produced 2026-08-24 via a three-stage review
chain (Fable design → Codex critique against live repo state → Opus reconciliation with
independent verification) at the user's request, after both this repo's architecture doc and
a fresh 5-repo audit were completed the same day.

**Read this before anything else in this document lands as code:** the plan below assumes
`docs/architecture.md` is the current, fact-checked source of truth it describes elsewhere in
this repo. **As of this document's own commit, that assumption is false on `main`.** The real,
three-times-corrected architecture document (28KB, corrected through 3 rounds of adversarial
review) exists only on the unmerged branch `agent/claude/architecture-doc`
([PR #1](https://github.com/dermdunc/veil-ecosystem/pull/1)). `main`'s `docs/architecture.md`
is still the original 11-line scaffold stub. See [Phase −1](#phase--1--prerequisites-mostly-not-code)
below — merging that PR is the first, blocking item, and this plan was deliberately written to
name that dependency rather than quietly assume it away.

---

## 0. The governing principle

`docs/architecture.md` exists because claims about this family go stale within days — it was
corrected three times in its first twelve hours. Any status surface built on top of it inherits
that failure mode unless staleness is first-class in the data model. So: **every field carries
`{value, source, observed_at, tier}`, and the UI renders provenance, not just value.** "Wired
✅" without "probed 14:32 today" vs "hand-asserted 2026-08-24" recreates the exact problem this
repo was created to fix.

A second principle, forced by verification during this plan's own review: **do not create a
second hand-maintained source of truth.** There is already a live instance of that failure
inside this repo — see [§2](#2-the-integration-statusyaml-question-is-already-settled--by-evidence-in-this-repo).

## 1. What was verified, and what it changed

Findings that altered the plan, all checked directly against the repos, GitHub's API, and the
live deployment during the review chain:

**The corrected architecture document is not on `main`.** See the callout above. This is the
single most important sequencing fact and it was invisible until the final review pass.

**That branch is already public.** It is pushed to a public repo. Everything in the document —
veil-custodian's full route inventory, its authz model, the self-asserted-demask gap,
veil-observatory's unkeyed hash chain, the private sibling's name — is readable by anyone right
now. The public-exposure question is therefore not "should we expose this" but "we already
have; do we accept it or trim it before merging to `main`?"

**Repo visibility contradicts the architecture doc's Privacy column.** Via `gh api`:

| Repo | GitHub visibility | Declared `privacy_boundary` |
|---|---|---|
| veil-ecosystem | public | public |
| veilgremlin | public | public |
| veil-foundations | **private** | **public** ← mismatch |
| veil-custodian | private | internal |
| veil-demo | private | internal |
| veil-observatory | private | local-first |
| veil-ecosystem-private | does not exist on GitHub | — |
| veil-foundations-private | does not exist on GitHub | — |
| veil-dashboard | does not exist | — |

`has_pages` is `false` on all of them. veil-ecosystem being public means Pages is available on
GitHub Free — but it is an unmade settings change, not a confirmed configuration. veil-foundations
is declared public in `.hekton/project.yaml` and described as "public (+ private sibling)" in
architecture.md, while its GitHub repo is private — a real inconsistency in the ecosystem's own
records, worth fixing independently of this plan.

**The demo pin in `veil-demo/Cargo.toml` is a truncated SHA.**
`rev = "324e85f2ec853e5e0b59e54479063819d54494a"` is 39 hex characters, one short of a full SHA;
the real commit is `...94ab`. Cargo resolves the prefix fine, but any currency check that
string-compares the pin against `git rev-parse HEAD` would return a wrong answer. Resolved
properly, the pin is dated 2026-08-02 and sits **25 commits** behind veilgremlin's `main`.

**CI adoption is not a Phase-0 freebie.** veilgremlin has CI installed. veil-custodian,
veil-foundations, and veil-observatory have staged `ci-proposed/ci.yml` — but veil-custodian's
own README states `.github/workflows/` is a protected path requiring `HEKTON_ALLOW_PROTECTED=1`
**set by a human, explicitly not by an agent**, and that setting the variable *is* the approval
record. veil-demo and veil-ecosystem have neither `ci-proposed/` nor `.github/workflows/` — CI
there has to be written from scratch. "Turn on staged CI" covers 3 of 6 repos, each a gated
human action, not a bulk Phase-0 item.

**veil-observatory's `ci-proposed/README.md` is stale.** It says this repo "has no GitHub
remote at all yet." It has one, private, pushed 2026-08-23. Its stated blocker is gone.

**Governance gates the public surface.** `.hekton/governance.yaml` sets
`approval_policy.public_release: human_required`. Standing up a public Pages site is a public
release. No agent flips that switch.

**Live-state checks:** `GET /` → 200, `/pitch` → 200, `POST /api/session` → 200.
`fly status`: two `lhr` machines, one started, one stopped — scale-to-zero working as intended.
veil-demo's own README is stale here (says "Not yet actually deployed"; also states "8
integration tests" in one place and "6" in another). `tower-http` features are `["fs", "trace"]`
— no `cors` feature. The demo's router has 7 routes including `/gateway` and `/playground`,
neither mentioned in `docs/architecture.md`.

## 2. The `integration-status.yaml` question is already settled — by evidence in this repo

The originally proposed mitigation for a hand-maintained YAML mirror of the Integration Status
table was "same-PR discipline plus a build-time check." Same-PR discipline is a stated norm
with no enforcement mechanism, and **it has already failed here, within one day.**
`docs/risks.md` opens with: *"Machine-readable risk state lives in
`.hekton/risk-register.yaml`. Keep this Markdown file as the human-readable explanation."* That
YAML contains exactly one risk, RISK-0001. The Markdown lists five. A hand-maintained YAML
mirroring a hand-maintained Markdown table drifted immediately, in the very repo whose reason
for existing is catching drift.

**So: no `integration-status.yaml`.** The five integration rows stay in `architecture.md` as
the sole source, and the collector *parses that Markdown table*. One source that people already
update in the same PR beats two sources plus a norm. The build-time contradiction check
(§4) survives, repurposed from "check the mirror matches" to "check the claims match reality."

This also surfaces a real, separate cleanup item: file the `risk-register.yaml` /
`risks.md` drift itself into `next-actions.md`.

## 3. The veil-demo `privacy_boundary` — resolved, not a contradiction

`veil-demo/.hekton/project.yaml` declares `privacy_boundary: internal`, carries in-repo
`local_repo_path`/`mind_palace_path`, has an in-repo `mind-palace/` and `runs/`, and declares no
`private_sibling` — the complete non-public-capable layout. The GitHub repo is private. This is
**internally consistent**: the repo is internal. `privacy_boundary` governs *repo contents* —
exactly why veil-custodian was reclassified public→internal on 2026-07-27 ("because this
component resolves device pseudonyms to real people," per its own file's comment). What is
public about veil-demo is the *deployed artifact*, not the source.

**Do not reclassify veil-demo.** Flipping it to `public` would strip the in-repo protections
that classification carries and imply someone decided to publish the source, which nobody did.
Instead:

1. Split `architecture.md`'s Privacy column into two: *Repo privacy* and *Public surface*.
   veil-demo reads `internal` / `veil-demo.fly.dev`. veil-foundations reads
   `public (declared) — repo currently private` / `none`.
2. Add a comment to `veil-demo/.hekton/project.yaml`, in the style veil-custodian already uses,
   recording that the repo is deliberately internal *and* ships a publicly reachable
   deployment, so nobody "corrects" it in the wrong direction later.
3. Treat this as a **schema requirement**: repo privacy and surface reachability are
   independent axes, and the status schema (§4) must carry both. Any model that collapses them
   will get veil-demo wrong forever.

Also file into `next-actions.md`: veil-demo's stale README ("Not yet actually deployed"; 6-vs-8
test count inconsistency).

## 4. The data layer: `veil.ecostatus.v1`

One JSON document. Three sections: `repos[]`, `integrations[]`, `runtime[]`.

**Export tier is a property of every field**, not of a document: `public` | `internal` |
`local`. A public export is produced by *filtering* the full document down, never by
hand-writing a separate public file. That decision makes the public/private boundary a schema
property enforced by code rather than a review discipline, and removes any need for auth on the
public tier, because nothing above `public` is ever in that artifact.

Every field also carries `source` (`probed` | `machine-derived` | `hand-asserted`),
`observed_at`, and — on integration rows — an optional `verification` that flips from
hand-asserted to probed as integrations land, without a schema change. Independent axes for
repo privacy and surface reachability, per §3.

The interactive doc page and the dashboard are both thin renderers over this document. The
orchestrator's `status --json` *is* this document with `runtime[]` populated.

**The collector's hard invariant, with a test:** it must never read `veil-ecosystem-private/`
or `veil-foundations-private/`. Neither exists on GitHub, so Pages build logs cannot leak them
by enumeration, and the public repo already names `private_sibling: veil-ecosystem-private` in
`.hekton/project.yaml` on public `main`, so existence is disclosed anyway. The real leak vector
is not Pages: it is a collector whose entire job is walking sibling directories, running on a
laptop where the private sibling is one relative path away. Deny-list it explicitly and test
the denial.

**The contradiction checker** fails the build when a hand-asserted claim conflicts with a
machine-verifiable fact:

- demo pin currency — resolved via `git rev-parse` inside a veilgremlin checkout, **not** string
  comparison (the pin is a truncated SHA — see §1)
- declared `privacy_boundary` vs. actual GitHub visibility (would have caught veil-foundations
  today)
- claimed CI state vs. presence of `.github/workflows/ci.yml`
- integration rows citing files or paths that no longer exist
- links in `README.md` and `architecture.md` resolving to files that actually exist in the repo
  — public `main`'s README currently links to three docs (`session-log.md`,
  `human-understanding-check.md`, `depth-decision.md`) that are gitignored in this public repo
  and will never exist there

It runs in `scripts/verify-project.sh`, and in CI once veil-ecosystem has CI. **Its own
last-run result is a rendered field in the dashboard** — the checker's health is part of the
status surface, not hidden behind it.

## 5. Phasing

Public Pages hosting was originally scoped for Phase 0. That is the highest-risk,
lowest-information ordering available: the good document is not on `main`, public release needs
human approval, the source document is hours old and already through three correction cycles,
and this family's defining characteristic is that its claims decay in days. Inverted below:
prove the machinery locally, publish second.

### Phase −1 — prerequisites, mostly not code

- **Merge `agent/claude/architecture-doc` into `main`.** Nothing else can be built on a
  document that is not there.
- Resolve the privacy taxonomy per §3: split the two columns, annotate veil-demo's
  `project.yaml`, correct veil-foundations' row.
- Fix the three broken README links on public `main`.
- File into `next-actions.md`: veil-observatory's `ci-proposed/README.md` stale no-remote
  claim; veil-demo's README staleness; the `risk-register.yaml`/`risks.md` drift.
- **Decide, before merging, whether the security-gap content stays.** The document publicly
  inventories, for a security product aimed at regulated enterprises: veil-custodian's complete
  route surface and authz grants, that the service has zero callers, that demask authorisation
  is self-asserted and unauthenticated ecosystem-wide, and that veil-observatory's hash chain is
  unkeyed such that anyone who can edit a finding can recompute the whole chain. The
  radical-honesty posture is genuinely on-brand for build/integration state. It is a different
  thing for an unmitigated-weakness inventory. **This is a human decision, and it belongs
  before the merge, not after.**

### Phase 0 — build, local-only, no public surface

- `veil.ecostatus.v1` with export tiers and provenance baked in from day one (§4).
- The collector, reading only machine-verifiable facts: per-checkout git HEAD/branch/dirty;
  GitHub visibility, default branch, and `has_pages` via `gh api`; the demo pin resolved (not
  string-compared) and its commit-distance from HEAD; `.github/workflows/ci.yml` vs.
  `ci-proposed/ci.yml` per repo; `privacy_boundary` from each `project.yaml`. Sibling discovery
  from config or env, never hardcoded — note that **veil-observatory lives outside
  `~/Development/hekton`**, so a "scan the factory-output directory" shortcut silently drops it.
- The integration table parsed out of `architecture.md`. No mirror file (§2).
- The contradiction checker, wired into `verify-project.sh`.
- **CI for veil-ecosystem itself** — written from scratch, since nothing is staged here —
  because that is where the checker needs to run.
- `scripts/eco.sh status`, rendering the full local tier to the terminal. That is the entire
  Phase-0 UI.

### Phase 1 — local orchestration and CI adoption

- `eco.sh up|down|smoke` with profiles:
  - **`demo`** — native `cargo run`, with the `.cargo/config.toml` patch to a local veilgremlin
    checkout.
  - **`custodian`** — delegate to `veil-custodian/scripts/dev-db.sh up`, which already exists
    and already matches `ci-proposed/ci.yml`'s container shape. Do not write a second one. Then
    `DATABASE_URL=… cargo test --no-fail-fast` (the default invocation never reaches
    `tests/db_grants`), plus a curl smoke test over enrol → `attestation/status` → CRL.
  - **`foundations`** — `terraform -chdir=modules/iam-model-allowlist init/fmt/validate/test`.
    Never `apply`.
  - **`observatory`** — deliberately absent until its `docs/setup.md` stops being scaffold
    boilerplate with two literal TODOs.
- CI adoption for veil-custodian, veil-foundations, and veil-observatory: scoped as human-run,
  protected-path actions, one at a time, with veil-observatory's stale README corrected first.
  veil-demo's CI written from scratch or deferred.

### Phase 2 — the public surface, gated on explicit human `public_release` approval

Only after Phase 0's exporter and checker have run clean over a real interval. Then enable
Pages on veil-ecosystem: push-triggered, plus `workflow_dispatch`, plus a modest cron. Restrict
`GITHUB_TOKEN` permissions; never add a PAT for private-repo reads — the public tier must be
buildable from public data alone, which the tier design already guarantees.

The public page renders the public tier only: the mermaid graph, the five integration rows with
status and provenance, an "as of" banner, and per-repo currency for the two genuinely public
repos. Components in private repos appear by name and role only — no HEADs, no CI state, no
test counts, no liveness. Links to private repos render as plain text with a "private
repository" marker rather than as 404-bound links.

**Security-gap redaction is a hard rule at this tier**, notwithstanding that the same content
is currently readable in the public branch. Publishing an unmitigated-weakness inventory as a
structured, navigable, machine-readable surface is a materially different act than having it in
prose inside a long document. If Phase −1's security-content decision trims the source, this
follows automatically.

**Demo liveness: no cron probe.** `min_machines_running = 0` is deliberate and working. Render
"last externally verified `<timestamp>`" from the local collector, plus an optional client-side
fetch on page load. Never render an unconfirmed demo as red; "may be asleep" is the honest state
and costs nothing.

**`/api/status` on veil-demo: defer past Phase 2.** It needs a `tower-http` `cors` feature
bump, which means touching `Cargo.toml`, which means rebuilding and redeploying an app pinned
25 commits behind veilgremlin — forcing the pin-bump question already open in
`next-actions.md`. Do not couple a status convenience to that decision. Client-side probing `/`
for a 200 gets most of the value with zero repo changes.

### Phase 3+ — gated on real integrations

As the veil-proxy network emitter, the first observatory→custodian call, and the sandbox AWS
account land, each unlocks a genuine orchestrator profile and flips its integration row's
`verification` from hand-asserted to probed — with no schema change, which is precisely why
`verification` goes in on day one. AWS evidence (account IDs, CloudTrail shapes) stays in the
local tier permanently.

## 6. Naming and location

**"Ecosystem Console" / `eco-console`.** `veil-dashboard` is reserved:
`veilgremlin/docs/architecture/product-family.md` defines it as two query surfaces (CSOC and
Legal/Privacy) over veil-observatory's store, with a still-open question of whether it gets its
own repo. Taking that name now would prejudge a live architectural decision.

Everything lives in `veil-ecosystem`, which already declares `enables: [all five]`. Nothing new
is a deployed service, so no reclassification or hosting decision is forced. Not a route on
veil-demo (mixing an investor demo with an engineering status board is a smell, and the demo is
framed as a throwaway one-month artifact) and not a hosted Claude Artifact (not versioned
in-repo next to the source it renders).

## 7. On credibility if Phase 0 is itself wrong

It will be wrong somewhere — this family's track record is unambiguous, and this plan's own
review chain found five fresh stale claims in an afternoon. The design should make being wrong
cheap and visible rather than attempting to be right. Three mechanisms carry that: every field
renders its source and age; the contradiction checker's own last-run result is a rendered
field, so a broken checker is visible rather than silently permissive; and the phasing means
the first public publication happens after the machinery has demonstrably worked locally, not
on day one. The one thing that would genuinely damage credibility is a public page asserting a
green integration state that a reader can disprove in thirty seconds — which is exactly what a
Pages workflow pointed at today's `main` would have produced, since `main`'s architecture doc is
an empty stub.

---

## Summary of what changed across the review chain

Killed the `integration-status.yaml` mirror outright (the same pattern has already drifted
inside this repo — parse the Markdown table instead); moved the public Pages site out of Phase
0 into an approval-gated Phase 2 and added a Phase −1 whose first item is merging the
architecture doc to `main` (currently an 11-line stub there); resolved veil-demo's
`privacy_boundary` as *not* a contradiction — the repo is genuinely internal, the deployment is
public, and the schema needs both axes; downgraded "adopt staged CI" from a Phase-0 freebie to
a gated, human-run, 3-of-6-repos Phase-1 item; and found that veil-foundations is declared
public while its GitHub repo is private, that veil-observatory's CI README's stated blocker is
stale, that the demo pin is a truncated SHA that would defeat naive currency checks, and that
the fact-checked document is already publicly readable on a pushed branch — which makes the
security-exposure question a decision to make before merging, not after publishing.
