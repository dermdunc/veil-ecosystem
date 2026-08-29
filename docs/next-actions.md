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
- [ ] Merge and push both branches above once the client/wiring items land, then update this
      doc's Integration Status table from "built and verified, unmerged" to "wired and running."

## This Week

- Keep [architecture.md](architecture.md#integration-status) in sync as any of the four
  missing/designed-only integrations moves toward built
- Consider whether veil-demo's veilgremlin pin (currently ~3 weeks stale) should be bumped
  before it's used to demonstrate capabilities veil-proxy has since gained (e.g. telemetry)

## Later

- Switch veil-observatory's ingestion off synthetic fixtures onto real receipts, once the
  emitter above exists
- Wire one real veil-observatory → veil-custodian call (`attestation/status` or `/certificates/crl`
  — both are real, both have zero callers today)
- Stand up one sandbox AWS account and apply veil-foundations' module against it
- Build the veil-proxy signer, once the wire format is stable (deliberately last) — the
  veil-observatory verifier side is already real
