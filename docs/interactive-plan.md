# Making Veil Ecosystem Interactive — Plan

**Status:** Phase −1 and Phase 0 implemented 2026-09-04 (this PR). Originally produced
2026-08-24 via a three-stage review chain (Fable design → Codex critique against live repo
state → Opus reconciliation with independent verification), then re-reviewed and revised
2026-09-04 via a second Fable-model pass plus a Codex adversarial critique, both reconciled
against live repo state by hand before any of this landed as code. See
[2026-09-04 reconciliation](#2026-09-04-reconciliation-fable-review--codex-critique) at the
end of this document for exactly what changed and why — read it before trusting any specific
factual claim elsewhere in this document, several of which were corrected there.

**The original blocking dependency named here is long since resolved.** The plan below was
first written when `docs/architecture.md` on `main` was still an 11-line scaffold stub and the
real, corrected document only existed on an unmerged branch. That merged (PR #1) on
2026-08-24, the same day this plan was drafted, and `docs/architecture.md` has since grown
into a 600+ line living document, corrected through PRs #1–#7 and current as of 2026-09-04
(veil-enrol's addition as the family's sixth component). This banner is left in place, corrected
rather than deleted, as a record of what the plan's own first blocking item was — the same
"don't silently rewrite a stale claim, correct it in place with a date" convention
`docs/architecture.md` itself uses.

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

**Note (2026-09-04):** the finding above ("corrected architecture document is not on `main`")
is long resolved — see the banner at the top of this document. The rest of §1's table and
findings are left as-written, a snapshot of 2026-08-24 state, not silently updated — several
have since changed (the demo pin distance shrank from 25 to single digits and keeps changing
by the hour; the architecture doc's Privacy column split proposed below is still not built;
veil-foundations' visibility mismatch is still unresolved 11 days later). See
[2026-09-04 reconciliation](#2026-09-04-reconciliation-fable-review--codex-critique) for the
current state of each claim, verified fresh rather than assumed from this section.

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
the denial. **Sharpened 2026-09-04 (implemented, see reconciliation below):** `factory-output/`
now holds far more than the family plus two private siblings — half a dozen unrelated private
repos live alongside it. A deny-list of two names is not enough; the collector reads an
**explicit allow-list of exactly six configured component paths** and refuses to walk the
directory itself at all. Same invariant, stronger mechanism.

**Schema extensions, added 2026-09-04 while folding veil-enrol in** (see reconciliation below
for why each is needed):

- `kind: service | cli | library | terraform-module | docs` per component. The original
  schema implicitly assumed every component is a long-running service with `runtime[]`
  liveness; veil-enrol is a single-shot CLI with none, and veil-foundations/veil-ecosystem
  never fit the service shape either.
- `github_repo` and `github_repo_aliases[]` per component, not just a single fixed name.
  veilgremlin's GitHub repo was renamed to `veil-proxy` while this plan was in flight, and
  the local checkout directory is still called `veilgremlin` — identity here is three-valued
  (component name, local path, current GitHub name) and time-varying, not a single constant.
- `local_head` / `remote_head` / `ahead` / `behind` per repo, resolved via `git rev-list
  --count`, never asserted from a checklist. A collector reading only `gh api` would have
  reported the family's second real integration (`edge_event.v1`) as not-yet-pushed for the
  eleven days it sat that way — and would keep reporting it that way today even though it
  was actually pushed on 2026-08-30, because nothing re-checked the git refs directly.
- **Explicitly NOT added, after a Codex critique flagged both as risky:** a `credentials_held[]`
  field and a role/credential coverage matrix (which roles exist in veil-custodian's
  `src/authz/mod.rs`, who holds them, which are orphaned). Both are real, useful ideas — but
  `credentials_held[]` was under-specified (derived from what: source code, config, keychain
  presence? a naive collector could probe exactly the sensitive stores it should avoid), and
  a role matrix risks duplicating veil-custodian's own `src/bin/mutual-exclusivity-check.rs`
  and its IAM separation-of-duties design (`docs/iam-separation-of-duties.md`) rather than
  reading it. Deferred to `next-actions.md`, to be built later as an explicitly read-only view
  over veil-custodian's own source — never a second source of truth for role assignments.

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
- **added 2026-09-04:** the `risk-register.yaml`-vs-`risks.md` ID-set match — the exact drift
  this document's §2 already used as its evidence for the no-mirror decision, and which had
  *widened*, not narrowed, by the time this was implemented (1 risk in the YAML vs. 6 in the
  Markdown, was 1-vs-5 on 2026-08-24)
- **added 2026-09-04:** claimed GitHub repo name vs. `gh api`'s actual current name — would
  have caught `docs/architecture.md` asserting in bold that veilgremlin's repo "still hasn't"
  been renamed, the same day the rename had already happened

**Status-cell convention, added 2026-09-04:** `docs/architecture.md`'s Integration Status
table cells have grown from short phrases into full paragraphs with cross-references
("**Merged, demonstrated locally, not yet a production integration.** veil-enrol (PR #2...)
..."). Parsing free prose is not parsing, it's guessing. The convention: every Status cell
must open with a bold canonical phrase drawn from a small enum (`Wired and demonstrated` /
`Built, no caller` / `Built, locally proven` / `Built, not live` / `Missing`), followed by
whatever prose detail the author wants. `Built, not live` was added while actually applying
this convention to the real table — the fifth real row (veil-proxy → veil-demo) didn't fit
any of the first four, and forcing it into the wrong one would have been worse than growing
the enum by one. The checker enforces the enum; nothing else about the table changes.

It runs in `scripts/verify-project.sh`, and in CI once veil-ecosystem has CI (still not
built — see [Phase 0](#phase-0--collector--checker--cli-local-only-implemented-2026-09-04)
below for what "CI" is deferred on). **Its own last-run result is a rendered field in the
dashboard** — the checker's health is part of the status surface, not hidden behind it.

## 5. Phasing

Public Pages hosting was originally scoped for Phase 0. That is the highest-risk,
lowest-information ordering available: the good document is not on `main`, public release needs
human approval, the source document is hours old and already through three correction cycles,
and this family's defining characteristic is that its claims decay in days. Inverted below:
prove the machinery locally, publish second.

### Phase −1 — prerequisites, mostly not code

- [x] ~~Merge `agent/claude/architecture-doc` into `main`~~ — done 2026-08-24, see banner.
- [ ] Resolve the privacy taxonomy per §3: split the two columns, annotate veil-demo's
  `project.yaml`, correct veil-foundations' row. **Partially done 2026-09-04, this PR**: the
  two-axis split landed in `docs/architecture.md`'s component table. veil-foundations' row
  is corrected in the same table (still shows the mismatch — `public` declared, private on
  GitHub — as a live, disclosed contradiction, since fixing which one is wrong is a human
  call, not this PR's to make). veil-demo's `.hekton/project.yaml` annotation is **not**
  done — it's a comment addition in a different repo, deliberately left as a next-action
  rather than bundled into this PR's cross-repo diff.
- [x] ~~Fix the three broken README links on public `main`~~ — done 2026-09-04, this PR.
- [x] ~~File into `next-actions.md`: veil-observatory's `ci-proposed/README.md` stale
  no-remote claim; veil-demo's README staleness; the `risk-register.yaml`/`risks.md`
  drift~~ — the risk-register drift is fixed directly (not just filed) in this PR; the other
  two are cross-repo and filed as next-actions, not fixed here.
- [ ] **Decide, before any public release, whether the security-gap content stays.** Still
  undecided as a formal human call — but overtaken by events: the document has been public on
  `main`, with the weakness inventory, since 2026-08-24 (see the 2026-09-04 reconciliation
  section's note on this). Not blocking Phase 0 (which is local-only); blocking Phase 2.

### Phase 0 — collector + checker + CLI, local-only — implemented 2026-09-04

- [x] `veil.ecostatus.v1` schema, with export tiers, provenance, and the 2026-09-04 schema
  extensions (§4) baked in from the start.
- [x] The collector (`scripts/eco_collector.py`), reading only machine-verifiable facts from
  an **explicit six-path allow-list** (config or env, never a directory scan — sharpened from
  the original deny-list design after finding `factory-output/` now holds several unrelated
  private repos): per-checkout git HEAD/branch/dirty/ahead/behind against `origin/main`;
  GitHub visibility and current repo name via `gh api`, with an explicit degraded mode when
  offline or unauthenticated rather than a crash or a silent stale value; the demo pin
  resolved via `git rev-list --count`, never string-compared; `.github/workflows/ci.yml` vs.
  `ci-proposed/ci.yml` per repo; `privacy_boundary` from each `project.yaml`.
- [x] The integration table parsed out of `architecture.md`, using the Status-cell convention
  above. No mirror file (§2).
- [x] The contradiction checker (`scripts/eco_checker.py`), wired into `verify-project.sh`.
- [ ] **CI for veil-ecosystem itself — deliberately deferred, not built in this PR.**
  `.github/workflows/` is a protected path under this machine's git-guardrail hook (same
  class of protection as `Cargo.toml` in the Rust repos this session touched) — creating it
  requires a human-run commit, and mid-loop coordination for that felt like the wrong
  trade-off against just documenting it as the next concrete step. The workflow file content
  is drafted in `next-actions.md`; a human runs the commit when ready, same precedent as
  veil-enrol's `Cargo.toml`.
- [x] `scripts/eco.sh status`, rendering the full local tier to the terminal. That is the
  entire Phase-0 UI, as designed.

### Phase 1 — local orchestration and CI adoption

- `eco.sh up|down|smoke` with profiles:
  - **`demo`** — native `cargo run`, with the `.cargo/config.toml` patch to a local veilgremlin
    checkout.
  - **`custodian`** — delegate to `veil-custodian/scripts/dev-db.sh up`, which already exists
    and already matches `ci-proposed/ci.yml`'s container shape. Do not write a second one.
    **Updated 2026-09-04**: the enrolment-side smoke test is superseded by something better
    than a hand-rolled curl script — `veil-enrol/scripts/dev-e2e.sh` already drives a real
    openssl-CSR → enrol → issue-signing-key → renew-cert → expiring loop against a real local
    custodian, with certificate-profile verification. Delegate to it rather than
    re-implementing curl calls. One caveat, a real bug found running it: the custodian's
    `device_binding` UNIQUE constraint isn't covered by its `ON CONFLICT` clause, so reruns
    need a fresh `device_binding` (the script already does this) until that's fixed upstream.
  - **`enrol`** — new 2026-09-04: `cargo test` + the structural tests in veil-enrol, plus the
    `custodian` profile's `dev-e2e.sh` delegation above as its own integration check.
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

The public page renders the public tier only: the mermaid graph, **whatever integration rows
`architecture.md` currently declares** (six as of 2026-09-04, not the five this plan was
originally scoped against — the count must always come from parsing the table, never be
hardcoded in the renderer or in prose like this sentence almost was) with status and
provenance, an "as of" banner, and per-repo currency for the two genuinely public repos.
Components in private repos appear by name and role only — no HEADs, no CI state, no test
counts, no liveness. Links to private repos render as plain text with a "private repository"
marker rather than as 404-bound links.

**Security-gap redaction is a hard rule at this tier**, notwithstanding that the same content
is currently readable in the public branch. Publishing an unmitigated-weakness inventory as a
structured, navigable, machine-readable surface is a materially different act than having it in
prose inside a long document. If Phase −1's security-content decision trims the source, this
follows automatically.

**Demo liveness: no cron probe, but not a binary state either — updated 2026-09-04.**
`min_machines_running = 0` is deliberate and working, and *that* ambiguity ("may be asleep,
scale-to-zero") should still never render as red. But as of the 2026-08-30 audit the demo's
deployment is not ambiguous — it is **confirmed down**: TLS handshake fails, Fly's own trial
expired (RISK-0006). That is a different, more certain state than "may be asleep," and hiding
it behind the same "never red" rule would be dishonest in the other direction. Three states,
not two: `up (probed)` / `down (probed, with reason)` / `unverified (scale-to-zero, may be
asleep)` — plus a human-asserted `fund | retire | undecided` field for the billing question,
which is a decision, not a probe result.

**`/api/status` on veil-demo: defer past Phase 2.** It needs a `tower-http` `cors` feature
bump, which means touching `Cargo.toml`, which means rebuilding and redeploying an app pinned
some number of commits behind veilgremlin/veil-proxy — **that number is not a stable fact to
cite in prose** (it was 25 on 2026-08-24, single digits by 2026-09-04, and changed three times
in ten minutes while this document was being reconciled that day — always resolve it live via
`git rev-list --count`, never read it off this page) — forcing the pin-bump question already
open in `next-actions.md`. Do not couple a status convenience to that decision. Client-side
probing `/` for a 200 gets most of the value with zero repo changes.

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

Everything lives in `veil-ecosystem`, which already declares `enables: [all six, since
2026-09-04 — a Codex critique caught this field still listing five hours after `README.md`
and `docs/architecture.md` had already been updated to six, itself a small live example of
the drift this document exists to catch]`. Nothing new
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

---

## 2026-09-04 reconciliation: Fable review + Codex critique

Eleven days after the original three-stage chain, this plan was re-reviewed via the same
family of technique — a Fable-model pass auditing this document against live repo state,
then a Codex adversarial critique of that pass, both reconciled by hand against the real
repos (not taken on either model's word) before anything below was implemented. This section
records what each pass got right and wrong, matching this repo's own established convention
(`docs/architecture.md`'s "Keeping this current" section) of disclosing correction history
rather than silently rewriting it.

**What the Fable pass got right:** confirmed that literally none of this plan's Phase 0
deliverable had been built (`scripts/` held only the three bootstrap/prereq/verify scripts;
no `.github/` at all); confirmed `docs/architecture.md`'s merge blocker was long resolved;
found that veilgremlin's GitHub repo was renamed to `veil-proxy` (confirmed independently via
`gh api` — this document's own line about "still hasn't happened" was itself stale, a genuine,
separate finding folded into `docs/architecture.md`'s 2026-09-04 correction); confirmed
veil-foundations' declared-public/actually-private mismatch was still unresolved; identified
that veil-enrol (added the same day) doesn't fit the schema's implicit "every component is a
service" assumption; identified the local-vs-remote git divergence gap in the original schema
— a real, valid design gap, even though the *specific example* used to justify it (see below)
turned out to be wrong.

**What the Fable pass got wrong, confirmed by direct re-verification, not by trusting
Codex either:**

- **Custodian role count.** Claimed "at least six roles," named one `AuditRead`. Directly
  reading `veil-custodian/src/authz/mod.rs:51-64` : there are **five** roles
  (`EnrolmentAuthority`, `ResolutionAuthority`, `RevocationAuthority`, `AuditReader`,
  `Observatory`), and the name is `AuditReader` — `AuditReadAuthorised` is a capability type,
  not a role. `docs/architecture.md` had also carried this exact error (from the same
  underlying miscount) and was fixed in the same session, same day.
- **"Edge-event work is unpushed."** False, confirmed directly with git: PR #58
  (`edge-event-v1-mvp`) merged to `origin/main` on both veilgremlin/veil-proxy and
  veil-observatory on **2026-08-30** — `main == origin/main` exactly on both, confirmed via
  `git rev-parse` after a fresh `fetch`. The Fable pass had cited `docs/next-actions.md:54` —
  a stale checklist item — as live evidence, exactly the failure mode ("verify against the
  repo, not the docs") its own stated methodology claims to avoid.
- **`dev-e2e.sh`'s "last-run result" claim.** Overstated. The script uses `mktemp -d` and a
  `trap cleanup EXIT` that deletes the scratch directory on completion — nothing persists. A
  collector cannot read a machine-verifiable "last run" that doesn't exist; this needs a
  wrapper that writes a result file first (tracked in `next-actions.md`, not built here).
- **Overstated novelty.** Framed the two-axis privacy split, the provenance schema, and
  config-driven (not hardcoded-scan) sibling discovery as gaps the original plan "missed."
  All three are already explicit in this document's §3/§4 — real hardening in the 2026-09-04
  revision (the sibling discovery became an *explicit allow-list*, stronger than the original
  deny-list-flavored language), not newly discovered gaps.
- **Internal inconsistency.** Opened with "zero lines of the plan have been implemented,"
  then credited the architecture-doc merge — itself part of Phase −1 — as already done a few
  paragraphs later. The narrower, accurate claim ("none of the Phase 0 code/dashboard
  artifacts exist") is what actually held.
- Trivia: cited `docs/architecture.md` as 618 lines; it was 617.

**What Codex could not verify, that turned out to be true anyway** — the sandboxed critique
run had no network access (`gh api`/`curl`/`fly status` all failed), so it correctly flagged
the GitHub-visibility and rename claims as unverifiable in its own environment rather than
asserting they were wrong. Checked directly afterward, with real network access: the
veilgremlin→veil-proxy rename is real (`gh api repos/dermdunc/veilgremlin` redirects to
`veil-proxy`, public, confirmed), and veil-foundations genuinely is private on GitHub while
declaring `public` in its own `project.yaml`. Both of Fable's claims held up; Codex's
"unverifiable" flag was itself the correct call given what it could see — a good example of
why a collector must degrade gracefully rather than guess when GitHub is unreachable, which
is now an explicit design requirement (§4/Phase 0 above).

**What Codex found that Fable missed entirely:**

- `.hekton/project.yaml`'s `related_projects`, `architecture.enables`, and `notes` fields
  still listed five components, not six — a real drift introduced earlier the same session
  (README and `architecture.md` were updated to add veil-enrol; this file wasn't). Fixed
  directly, opened as its own small PR (#7) rather than folded silently into this one.
- A role/credential coverage matrix — genuinely useful, and something Fable's own "what's
  missing" section proposed — risks duplicating veil-custodian's own
  `src/bin/mutual-exclusivity-check.rs` and its documented IAM separation-of-duties design
  (`veil-custodian/docs/iam-separation-of-duties.md`), both confirmed to exist. Deferred; see
  §4 above.
- The demo pin's "commits behind" figure is not a stable number to cite anywhere in prose —
  demonstrated by getting three different answers (5, 4, 6) checking it three times in under
  ten minutes while writing this section, as new commits landed on veil-proxy's `main` in
  real time. Folded into the design as "always resolve live," not "here is the current
  count," in the sections above.

**Reconciliation method, stated for anyone auditing this later:** every claim above that
mattered to what got built was re-checked directly — reading `src/authz/mod.rs`, running
`git merge-base --is-ancestor` and `git rev-parse` against real checkouts, calling `gh api`
directly, checking `scripts/dev-e2e.sh`'s actual `trap` behavior, and confirming
`mutual-exclusivity-check.rs` exists on disk — rather than picking a side between the two
models' claims. Two of Codex's findings (the role count, the unpushed-work claim) were
confirmed as outright errors in Fable's draft; two of Fable's findings (the rename, the
foundations mismatch) were confirmed correct despite Codex being unable to verify them; one
finding (the project.yaml drift) came from neither review pass directly but from checking the
file while investigating a related Codex point. This is the third time this repo's own
process has caught a model's confident claim being wrong by insisting on independent
verification rather than trusting the review chain's own output — see `docs/decisions.md`
for the first two (the 2026-08-24 three-cycle review, and the 2026-08-24 3rd-cycle paired
verification).
