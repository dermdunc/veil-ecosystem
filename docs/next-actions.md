# Next Actions: Veil Ecosystem

Carried over from the 2026-08-22 ecosystem audit's sequencing (full detail in
[architecture.md](architecture.md#sequencing-to-close-them)), in dependency order. Items 1 and 7
are done as of this repo's creation.

## Immediate

- [ ] Freeze the receipt/telemetry contract between veil-proxy and veil-observatory (reconcile
      veil-proxy's draft `TelemetryEvent` proposal with veil-observatory's draft receipt schema)
      — everything else is downstream of this
- [ ] Fix veil-foundations' `iam-model-allowlist` module: it currently makes a Bedrock Guardrail
      mandatory per invocation, contradicting the ecosystem's decided no-Guardrails policy
      (ADR-0001 / ADR-010)

## This Week

- Keep [architecture.md](architecture.md#integration-status) in sync as any of the four
  missing/designed-only integrations moves toward built

## Later

- Build the veil-proxy telemetry emitter once the schema is frozen; switch veil-observatory off
  synthetic fixtures
- Wire one real veil-observatory → veil-custodian `attestation/status` call
- Stand up one sandbox AWS account and apply veil-foundations' fixed module against it
- Decide on cryptographic signing, once the wire format is stable (deliberately last)
