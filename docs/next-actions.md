# Next Actions: Veil Ecosystem

Carried over from the 2026-08-22 ecosystem audit's sequencing (full detail in
[architecture.md](architecture.md#sequencing-to-close-them)), in dependency order, and
corrected 2026-08-24 after a doubt-driven-development review found the audit-sourced draft had
gone stale within two days (see `docs/decisions.md`). Sequencing items 1 and 7 are done as of
this repo's creation.

## Immediate

- [ ] Freeze the receipt/telemetry contract between veil-proxy and veil-observatory (reconcile
      veil-proxy's real `TelemetryEvent` type with veil-observatory's draft receipt schema) —
      everything else is downstream of this
- [x] ~~Fix veil-foundations' Guardrail-mandatory defect~~ — already fixed via ADR-010 on
      2026-08-23, before this repo existed. Caught and corrected during a 2026-08-24
      doubt-driven-development review; see `docs/decisions.md`.
- [ ] Ask veil-observatory to write real project-specific commands into its own `docs/setup.md`
      — currently a boilerplate stub with two literal TODOs, so this repo can't honestly point
      to it for runnable instructions
- [ ] Ask veil-custodian to document the `DATABASE_URL` requirement (and point at
      `.env.example`) in its own `docs/setup.md` — `cargo test` fails 15/77 tests out of the box
      without it

## This Week

- Keep [architecture.md](architecture.md#integration-status) in sync as any of the four
  missing/designed-only integrations moves toward built

## Later

- Build the veil-proxy telemetry emitter once the schema is frozen; switch veil-observatory off
  synthetic fixtures
- Wire one real veil-observatory → veil-custodian `attestation/status` call
- Stand up one sandbox AWS account and apply veil-foundations' module against it
- Decide on cryptographic signing, once the wire format is stable (deliberately last)
