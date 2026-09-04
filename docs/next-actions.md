# Next Actions: Veil Ecosystem

Carried over from the 2026-08-22 ecosystem audit's sequencing (full detail in
[architecture.md](architecture.md#sequencing-to-close-them)), in dependency order, and
corrected 2026-08-24 after a doubt-driven-development review found the audit-sourced draft had
gone stale within two days (see `docs/decisions.md`). Sequencing items 1 and 7 are done as of
this repo's creation.

## Immediate

- [x] ~~Freeze the receipt/telemetry contract~~ — already ratified 2026-08-23, before this
      repo's first draft was written. Caught during the 3rd doubt-driven-development review;
      see `docs/decisions.md`.
- [x] ~~Fix veil-foundations' Guardrail-mandatory defect~~ — already fixed via ADR-010 on
      2026-08-23, before this repo existed. Caught and corrected during a 2026-08-24
      doubt-driven-development review; see `docs/decisions.md`.
- [ ] Ask veil-observatory to write real project-specific commands into its own `docs/setup.md`
      — currently a boilerplate stub with two literal TODOs, so this repo can't honestly point
      to it for runnable instructions
- [ ] Ask veil-custodian to document the `DATABASE_URL` requirement (and point at
      `.env.example`) in its own `docs/setup.md` — `cargo test` fails 15/77 tests out of the box
      without it, and the default invocation doesn't even reach the 4 additional `db_grants`
      failures
- [ ] Ask veil-observatory to update `correlation/correlator.py` and `docs/decisions/ADR-0016` —
      both still assert a "structural stub" signature verifier that a real `HmacReceiptVerifier`
      already superseded. This repo's own doc inherited that stale self-description once; it
      could happen again from the same source.
- [x] ~~Build the `veil.edge_event.v1` signing/wire contract in veil-proxy~~ — done 2026-08-29,
      independently re-verified this session (not just self-reported): serialization, canonical
      JSON, and HMAC-SHA256 signing all land in `crates/vg-core/src/telemetry/`, 176 tests pass,
      golden vector matches a fresh hand-computed Python HMAC byte-for-byte. Unmerged, unpushed
      (branch `worktree-agent-a9869ec2363020f3e`, commit `1d14b13`). `Receipt`/`veil.receipt.v2`
      remains unbuilt — the aggregator it needs is still an explicit skeleton; this was a
      deliberate scope narrowing to `EdgeEvent`, not a claim about `Receipt`.
- [x] ~~Build `veil.edge_event.v1` ingestion in veil-observatory~~ — done 2026-08-29: schema,
      generalized `HmacReceiptVerifier`, and a loopback HTTP receiver (`veil-observatory serve`)
      all real. 547 passed, 1 skipped (up from 491), independently re-run this session, including
      tamper/replay/ECDSA-refusal/loopback-binding checks. Unmerged, unpushed (branch
      `agent/claude/edge-event-v1-ingestion`, commit `775a219`). Edge events do not yet reach
      `Correlator`/`FindingEngine` — no aggregator for a single event to attach to yet.
- [ ] Build the network *client* in veil-proxy that actually POSTs a signed `EdgeEvent` to
      veil-observatory's new receiver — the signer exists, nothing calls it over a socket yet.
- [ ] Wire `TelemetryCountingAuditSink::write` (`crates/vg-audit/src/telemetry_sink.rs`) to call
      the signer on a successful `EdgeEvent` conversion instead of discarding it — currently only
      counts the conversion, does nothing with the value.
- [x] ~~Build the network client and wire the audit-sink hook~~ — done 2026-08-29: fire-and-forget
      emitter on a dedicated thread, structurally opt-in on `VEIL_RECEIPT_KEY` +
      `VEIL_OBSERVATORY_ENDPOINT`, wired into `TelemetryCountingAuditSink::write`.
- [x] ~~Merge both branches~~ — fast-forward merged to local `main` in both repos, 2026-08-29.
      Not pushed to GitHub.
- [x] ~~Demonstrate one genuine live delivery~~ — done 2026-08-29: real cross-process run
      against a real `veil-observatory serve` instance, logged 202 Accepted, persisted with a
      genuine HMAC pseudonym. See `veilgremlin/crates/vg-audit/tests/live_edge_event_integration.rs`.
- [ ] Push both branches to GitHub, once a human reviews the diffs.
- [ ] Document the `VEIL_RECEIPT_KEY` hex-vs-UTF-8 encoding mismatch between the two repos
      somewhere an operator will actually see it before configuring a real deployment — right
      now it's only in `veilgremlin`'s build-log and this doc's architecture update.

## This Week

- Keep [architecture.md](architecture.md#integration-status) in sync as any of the four
  missing/designed-only integrations moves toward built
- Consider whether veil-demo's veilgremlin pin (currently ~3 weeks stale) should be bumped
  before it's used to demonstrate capabilities veil-proxy has since gained (e.g. telemetry)

## Later

- Switch veil-observatory's ingestion off synthetic fixtures onto real receipts, once the
  emitter above exists
- Wire one real veil-observatory → veil-custodian call (`attestation/status`,
  `/certificates/crl`, or `/signing-keys/{key_ref}` — all three are real, all three are
  `Role::Observatory`-gated, all three have zero callers today)
- Stand up one sandbox AWS account and apply veil-foundations' module against it
- Build the veil-proxy signer, once the wire format is stable (deliberately last) — the
  veil-observatory verifier side is already real
- [x] ~~Once veil-enrol's PR #2 merges: update `docs/architecture.md`'s Integration Status
      table and the veil-enrol component section from "built, locally proven, PR open" to
      "merged"~~ — done 2026-09-04, same day PR #2 merged.
- No component holds the `RevocationAuthority`, `ResolutionAuthority`, or `AuditRead`
  credentials yet (see `docs/architecture.md`'s 2026-09-04 role-audit note) — worth a
  decision on whether veil-enrol grows a `revoke` subcommand under a second credential, or
  a separate operator tool is the right home for revocation and resolution instead

## Session Update: 2026-08-30 — fresh 5-repo audit

- [ ] **Human, time-sensitive**: veil-demo's live deployment is down — Fly.io trial has ended,
      needs a credit card added (or a decision to let the demo stay offline). Independent of
      any code issue; confirmed via a failed TLS handshake and `fly status`'s own error.
- [ ] Bump veil-demo's `veilgremlin` pin (`0a4ec71...`, confirmed 8 commits behind `main` as of
      this audit) once a human decides whether the demo should showcase the new edge_event.v1
      telemetry capability or stay minimal.
- [x] ~~Fix veilgremlin's CI (`cargo-fmt-check` failing on every push since this session's
      telemetry work landed)~~ — done same day, confirmed green afterward.
- [x] ~~Record veil-foundations' redaction fix in its own decisions.md/next-actions.md~~ — done;
      it previously existed only as a commit message.
- [ ] Everything else from the 2026-08-24 sequencing (custodian caller, AWS sandbox, the
      aggregator/Receipt path) remains open and unchanged by this session's work, which was
      scoped to seam #1's `EdgeEvent` slice only.

## Session Update: 2026-09-04 — veil-enrol added, enrolment-side custodian caller now real

- [x] Add veil-enrol to `README.md`/`docs/architecture.md` component tables, plus a new
      `### veil-enrol` component section
- [x] Correct the `veil-proxy → veil-custodian` enrolment edge (architecturally impossible
      under ADR-D/ADR-N) to `veil-enrol → veil-custodian` in the diagram and Integration
      Status table
- [x] Verify and correct `Role::Observatory`'s actual grant count (three, not two — ADR-S's
      `signing-keys/{key_ref}` lookup) and `POST .../revoke`'s actual role
      (`RevocationAuthority`, distinct from the enrolment authority's grant), directly
      against `src/authz/mod.rs` and each handler
- [x] Record the veil-custodian `device_binding`/`ON CONFLICT` gap found running veil-enrol's
      end-to-end script, in this document's veil-custodian section
- [x] Once veil-enrol PR #2 merges: flip its status here and in `docs/architecture.md` from
      "built, locally proven" to "merged" — done 2026-09-04.
- [ ] Decide whether veil-enrol grows a `revoke` subcommand (a second, distinct credential)
      or a separate tool should hold `RevocationAuthority`/`ResolutionAuthority`/`AuditRead`

## Session Update: 2026-09-04 — interactive-plan Phase −1′ + Phase 0 implemented

Fable-model review + Codex adversarial critique of `docs/interactive-plan.md`, reconciled by
hand, then implemented. See `docs/interactive-plan.md`'s own "2026-09-04 reconciliation"
section for the full account of what each review pass got right/wrong.

- [x] Fix the three broken README links (`session-log.md`/`human-understanding-check.md`/
      `depth-decision.md`) — removed with an explanatory note rather than silently deleted
- [x] Split `docs/architecture.md`'s Privacy column into *Repo privacy* / *Public surface*
- [x] Correct the veilgremlin→veil-proxy GitHub rename claim in `docs/architecture.md`
- [x] Adopt the Status-cell enum convention in the Integration Status table
- [x] Record the retroactive security-exposure decision in `docs/decisions.md`
- [x] Reconcile `.hekton/risk-register.yaml` with `docs/risks.md` (was 1 risk vs. 6)
- [x] Build Phase 0: `schemas/veil.ecostatus.v1.schema.json`, `scripts/eco_collector.py`,
      `scripts/eco_checker.py`, `scripts/eco.sh`, `scripts/eco-components.json`, 17 unit
      tests, wired into `scripts/verify-project.sh`. Verified end-to-end against the real 6
      repos: 0 errors, 1 disclosed warning (the still-open veil-foundations mismatch).
- [x] Found and fixed incidentally: `scripts/verify-project.sh` has checked for
      `docs/local-assumptions.md` since this repo's original scaffold, but the file is
      gitignored (machine-local, same class as `docs/session-log.md`) and
      `scripts/bootstrap-project.sh` never generated it — pure boilerplate, a literal `TODO`
      where project-specific setup should be. `verify-project.sh` had apparently never
      actually passed on a real bootstrap flow before this fix. Fixed properly, not
      papered over: `bootstrap-project.sh` now generates the file if missing (verified by
      deleting it and re-running bootstrap from scratch), rather than just hand-creating one
      copy that would still be missing on the next fresh clone.
- [x] Single-model doubt-driven-development review of the collector/checker (Codex not
      invoked this round, disclosed — see `docs/decisions.md`), found and fixed 8 issues:
      `eco.sh status` not actually rendering repo facts (the biggest one), `tier` hardcoded
      instead of derived, a typo/offline ambiguity in the GitHub probes, `generated_at` not
      actually injectable despite the schema's own claim that it was, `check_demo_pin` only
      checking one of six crate pins, a malformed table row silently dropped instead of
      flagged, plus two dead/unimplemented pieces (`unavailable()`'s unused parameter,
      `$VEIL_ECO_COMPONENTS_FILE` documented but not read).

**Deliberately deferred as of the prior PR — status as of this update:**

- [x] ~~CI for veil-ecosystem itself~~ — done (PR #9, human-run protected-path commit, first
      real run confirmed green before merging).
- [x] ~~veil-demo's `.hekton/project.yaml` annotation~~ — done (veil-demo PR #13).
- [x] ~~veil-observatory's `ci-proposed/README.md` stale "no GitHub remote at all yet"
      claim~~ — done (veil-observatory PR #13).
- [x] ~~`veil-enrol/scripts/dev-e2e.sh` doesn't persist a last-run result~~ — done (veil-enrol
      PR #3: writes `.project-setup/last-runs/dev-e2e.json`, gitignored, identity-free).
      `eco_checker.py` now reads it and flips the veil-enrol → veil-custodian integration
      row's `verification` from hand-asserted to probed when the last run passed — the first
      integration row in the family for which that flip is possible. Confirmed end-to-end
      against a real run.
- [x] ~~JSON Schema validation isn't automated~~ — done, hand-written (not `jsonschema` —
      the schema is currently looser than what the collector emits, so a real `jsonschema`
      validation today would pass almost anything; `eco_checker.validate_document_shape`
      checks `schema_version`, the real 6-repo set, every provenance object's shape/enum/
      null-iff-unavailable invariant, and the `kind`/`tier`/`status_enum`/severity enums).
- [ ] veil-foundations' `privacy_boundary` vs. actual GitHub visibility mismatch — **still
      genuinely unresolved.** A Codex consult recommends flipping the GitHub repo to public
      (not the metadata) — its `.hekton/project.yaml` is internally consistent with
      public-capable source (no `local_repo_path`/`mind_palace_path` in-repo, those live in
      the private sibling), and `docs/session-log.md` there already records a human-decision
      point on this exact question. **Not acted on** — flipping a private repo to public is
      an irreversible-ish, security-relevant decision this agent should not make
      unilaterally; surfaced to the user directly instead of silently implementing.
- [ ] The role/credential coverage matrix — still deferred, Codex consult agrees: real risk
      of duplicating veil-custodian's own `src/bin/mutual-exclusivity-check.rs` and IAM
      separation-of-duties design. Cheap safe scope instead, done in this round: fixed the
      stale role-count comment at the source (veil-custodian PR #22) rather than building a
      second, ecosystem-side view of the same fact.
- [ ] `credentials_held[]` schema field — still deferred, Codex consult agrees: no sourcing
      decision has been made, and the wrong one invites probing keychains/credential files.

**Additional findings from the same Codex consult, fixed in this round (none were on the
original list):**

- [x] `README.md` said "Documentation only — no code, no CI" — stale since Phase 0 shipped
      real code and CI.
- [x] `docs/setup.md` cloned `dermdunc/veilgremlin` (renamed to `veil-proxy`) and claimed the
      demo was "already live" (down since 2026-08-30, RISK-0006). Also added the missing
      veil-enrol section and corrected a stale "nothing calls veil-custodian's API" claim.
- [x] `docs/architecture.md`'s Integration Status section claimed veil-enrol → veil-custodian
      was "described here alongside the original five, not folded silently into an existing
      row" — false; it replaced the row that used to read `veil-proxy → veil-custodian`. The
      table has five rows, not six, and never did.

## Session Update: 2026-09-04 — retired the out-of-band Claude artifact

- [x] The "Veil Ecosystem Audit" Claude artifact no longer carries its own status narrative —
      it now redirects to this repo's `docs/architecture.md`, with its three prior audit runs
      kept as a dated historical archive. See `docs/decisions.md` for why (it had become a
      second, unsynced source of the same facts this repo already tracks).
- [ ] **Genuinely unresolved, not closed by the above**: there is still no single document for
      the *cross-repo plan* (as opposed to per-repo backlogs). Today it's split across this
      repo's `docs/architecture.md` ("Sequencing to close them"), this file, and fragments of
      cross-repo intent still living in individual repos' own `next-actions.md`. Worth a
      deliberate decision later on whether that's fine as-is or needs consolidating — not
      decided today, just named so it doesn't get silently assumed as solved.
