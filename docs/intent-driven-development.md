# Intent-Driven Development in Veil Ecosystem — Operating Definition

**Status:** operative from 2026-09-13 (`INT-2026-09-12-001`, this practice's own founding
intent in this repo, accepted that date). Adopted `tektograph-1.0` on the
explicit instruction of the project owner (dermdunc — this repo's actual GitHub identity
across all seven Veil-family repos, confirmed directly rather than assumed from any
sibling repo's own git-config convention), given via an `AskUserQuestion` choice in the
same session that kicked off the beta-implementation-plan's Phase 0 work, after being told
plainly this was a project-governance decision unresolved elsewhere and that no repo in
the six-repo Veil family had ever declared an intent before.

**Veil Ecosystem is the second `factory-output` repo to adopt this practice**, after
`kriterion` (2026-09-05). Every other adopter (`hekton-assurance-lab`,
`hekton-cli-lab`, `regulated-architecture-lab`, `scriptorium-lab`) is a `lab`.
`hekton-loops-lab` and `egress-broker-lab` instead run the nested `1.0` schema. There is
still no factory-output-wide ruling on which schema is correct — this document follows
`kriterion`'s own precedent for a scoped, disclosed, non-binding choice, not a claim that
it settles anything beyond this repo.

## Why tektograph-1.0, and why this does not settle the org-wide question

The same unmerged, unadopted proposal `kriterion`'s own operating doc names
(`~/hekton/docs/proposals/intent-schema-consolidation.md`) still reserves this exact
schema choice for the project owner and still does not pick a winner among its four
options. **This document does not resolve that proposal.** It records a pragmatic,
scoped choice for Veil Ecosystem only, made with the fragmentation disclosed to the
owner before the choice was made.

Counted directly on this machine on 2026-09-12, before choosing:

| Registry | Schema | Live intent count |
|---|---|---|
| `kriterion` | `tektograph-1.0` | 2 |
| `hekton-assurance-lab` | `tektograph-1.0` | 3 |
| `hekton-cli-lab` | `tektograph-1.0` | 2 |
| `regulated-architecture-lab` | `tektograph-1.0` | 2 |
| `scriptorium-lab` | `tektograph-1.0` | 2 |
| `hekton-loops-lab` | `1.0` (nested) | 6 |
| `egress-broker-lab` | `1.0` (nested) | 1 |

(`kriterion--human-run-001` is a linked git worktree of `kriterion` sharing the same
`.git` — confirmed via `git worktree list` — not an independent registry; its
byte-identical intent content is not double-counted here.)

Both schemas are live, real practice. The basis for choosing `tektograph-1.0` here,
same as `kriterion`'s own reasoning: it has a working, ported validator
(`scripts/validate_intents.py`, copied byte-identical from `kriterion`, itself ported
verbatim through `hekton-assurance-lab` and `regulated-architecture-lab` from the
schema's origin) and an explicit `history` block giving an append-only audit trail,
which the nested `1.0` shape does not have. No Veil-specific reason favored either
schema — this is a "pick the one with working tooling" call, not a claim that
`tektograph-1.0` is this family's correct answer, still less the whole factory's.

## Why this is a real gate, not a new one

`.hekton/governance.yaml`'s `required_gates.intent_recorded: true` has been set since
this repo's 2026-08-24 scaffold — before this document, before any intent registry
existed here. Every decision this repo has made until now (the 19 `XREPO-*` items, all
D-BETA groundwork, every ADR-log row in `docs/decisions.md`) satisfied that gate through
`docs/decisions.md`'s own dated-entry discipline, not through a machine-checked
registry. This document does not retire that discipline — see "Binding to existing
machinery" below — it adds a second, machine-checked evidence trail for intents that go
through this registry from here forward. Nothing already recorded in `docs/decisions.md`
is retroactively required to gain an intent file.

## The registry

**Location:** `.hekton/intents/<intent-id>/intent.yaml`. One directory per intent;
amendments live beside the intent file, never overwrite it. The directory listing is the
index — no separate index file.

**Id format:** `INT-YYYY-MM-DD-NNN`, date = declaration date, NNN = same-day sequence.
Assigned at declaration, never pre-allocated.

**Format**, `tektograph-1.0`:

```yaml
schema_version: "tektograph-1.0"
intent_id: "INT-2026-09-12-NNN"
title: "..."
kind: feature | fix | refactor | experiment | ops | security | decision
status: declared                         # the full 10-status vocabulary
risk_tier: T0 | T1 | T2 | T3              # see tier boundary note below
iteration: 0                             # veil-ecosystem has no formal iteration concept yet
review_by: YYYY-MM-DD                    # an intent may not float indefinitely unfalsified
owner:
  accountable_human: dermdunc                # this repo's GitHub identity for
                                              # its sole accountable human --
                                              # checked directly against every
                                              # sibling intent's own convention
                                              # (majority is a "Derm"/"derm"
                                              # form, not "coderturtle") rather
                                              # than assumed, at this repo's
                                              # first intent (INT-2026-09-12-001)
  responsible_agent: "<agent/branch>"
hypothesis: >                            # one falsifiable claim, plain language
confirmation_criteria:
  - "..."
disproof_criteria:                       # mandatory, never empty, genuinely falsifiable
  - "..."
bindings:
  mission_manifests: []
  adrs: []                               # this repo has no ADR-id convention of its own;
                                          # decisions are recorded in docs/decisions.md by
                                          # date/row — cite those in confirmation evidence
  risks: []                              # RISK-nnnn ids from .hekton/risk-register.yaml
  prs: []                                # PR numbers once they exist
history:
  - {status: declared, date: ..., by: ..., evidence: "..."}
```

`disproof_criteria` is mandatory. An intent whose author cannot state what would disprove
it is not accepted.

**T2/T3 boundary.** No sibling repo defines this precisely (a real gap a Codex cross-model
critique of this repo's own founding intent named, 2026-09-12) — for this repo: a
`kind: decision` intent is **T3** if its substance triggers one or more of
`.hekton/governance.yaml`'s `human_required` `approval_policy` categories
(`destructive_changes`, `public_release`, `production_changes`,
`credential_or_secret_changes`, `financial_changes`, `personal_data_changes`,
`dependency_changes`); otherwise it matches sibling `kind:decision` precedent at **T2**. A
departure from sibling tier precedent must state which category triggered it, not just
assert a higher number.

## Lifecycle: states, transitions, and who moves them

Adopted verbatim from `kriterion` (itself from `hekton-assurance-lab`/`tektograph`):
`declared → critiqued → accepted → in_progress → technically_confirmed →
provisionally_confirmed → operationally_confirmed`, with side-exits to `disproven`,
`superseded`, `abandoned` at any point after `accepted`.

| Transition | Moved by | Evidence required |
|---|---|---|
| → `declared` | a session (agent drafts, human sees it) | the intent file itself, with non-empty disproof criteria |
| `declared → critiqued` | an adversarial pass: `doubt-driven-development`, an independent review, or the user's own pushback | the critique's findings recorded in `history` (or a note that critique found nothing — also evidence, only if it names what it tried to break) |
| `critiqued → accepted` | **the user, explicitly** — never an agent | user approval recorded in `history`; for T2/T3 this is a named per-intent approval, not bundled with any other sign-off |
| `accepted → in_progress` | the session that picks it up | the kickoff commit |
| `in_progress → technically_confirmed` | session closure | the closure summary + this project's own review with no blocking findings (reuse `.hekton/review-log.yaml`'s `REV-XXXX` mechanism — do not build a parallel gate) |
| `technically_confirmed → provisionally_confirmed` | PR merge (user-approved, per-event) | the merge itself; PR number added to `bindings.prs` |
| `provisionally_confirmed → operationally_confirmed` | a later, real observation | real dogfooding evidence or an end-session report reflecting the change, cited concretely |
| any (post-accepted) → `disproven` | whoever holds the disproving evidence — agent or human; an agent may propose, the record is made immediately, the user is told in the same session | the disproving evidence, cited concretely |
| any (post-accepted) → `superseded` / `abandoned` | the user (T2/T3) or the session with user visibility (T0/T1) | the successor intent id (superseded) or the recorded reason (abandoned) |

Amendments: clarifications and narrowing that change no risk tier, constraint, or
confirmation criterion are recorded directly in `history`; anything material gets an
amendment file beside the intent and, for T2/T3, explicit user approval before work
continues. The original hypothesis text is never edited — only appended to.

**This amendment protocol governs `accepted`-and-later intents only.** Pre-acceptance,
the `declared → critiqued` step's whole purpose is to fix real defects — including in
the hypothesis and criteria text itself — directly in the file.

## Binding to existing machinery

1. **Risk register.** `bindings.risks` cites `RISK-nnnn` ids from
   `.hekton/risk-register.yaml` when an intent addresses or is constrained by an open
   risk (e.g. RISK-0004/VE-RISK-0004). Check each registered risk's actual title/scope
   before citing it as "directly mapping" to a new question — `INT-2026-09-12-001`'s own
   critique caught RISK-0006 as registered (veil-demo's dead Fly.io deployment) being
   silently overloaded by a planning document to also mean a different, not-yet-built
   custodian/observatory hosting question; fix the registry's own scope rather than
   letting an intent's citation paper over the gap.
2. **Cross-repo dependency registry.** `.hekton/cross-repo-deps.yaml`'s `XREPO-*` ids are
   a separate, already-established stable-id mechanism for cross-repo work items — an
   intent that touches one cites it in its hypothesis/criteria text (this schema has no
   dedicated `bindings.xrepo` field); do not duplicate the registry's own narrative.
3. **Governance gate.** `.hekton/governance.yaml`'s `required_gates.intent_recorded: true`
   was already true before this doc existed; this practice is what makes that gate mean
   something concrete, from here forward, for intents that go through it.
4. **Decisions log.** `docs/decisions.md` remains the durable, human-readable record of
   *why*, for every decision including ones with no intent file. An intent's `history`
   additionally records *when it moved and on what evidence*, for intents declared
   through this registry. Both are kept; neither replaces the other.
5. **Validation.** `scripts/validate_intents.py` (ported verbatim, unmodified, from
   `kriterion`) checks registry mechanics: required fields present, `disproof_criteria`
   non-empty, legal `history` transitions, terminal-status intents cite evidence.
   Advisory posture, same precedent: reports and exits non-zero on registry-mechanics
   violations only; not wired into `scripts/verify-project.sh` or `eco_checker.py`,
   which must stay runnable with no new pip dependency forced on every invocation. Its
   own docstring still references `engine/schema.md` and `scripts/verify-lab.sh`, neither
   of which exists in this repo — a deliberate byte-identical port, not an oversight; a
   Codex cross-model critique of this repo's founding intent flagged it as stale
   lab-specific prose, which it is, but the family-wide convention is to keep ported
   validators byte-identical to their source rather than edit per-repo, so it stays as
   copied.

## Choreography

The `declared → critiqued → accepted` front half has a named, user-level skill,
`~/.claude/skills/intent-choreography`, which scaffolds the file, composes with
`doubt-driven-development` for the critique step, and drafts the acceptance prompt — it
stops at `accepted`; everything after still moves by real evidence, never by the skill.
Non-interactive contexts (CI, `/loop`, scheduled runs) must stop at `critiqued` and say
so, since acceptance requires a live human answer.
