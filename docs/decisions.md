# Decisions: Veil Ecosystem

## ADR Log

| Date | Decision | Rationale |
|---|---|---|
| 2026-08-24 | Initial scaffold as factory-output | Master architecture repo for the VeilGremlin product family: describes the trust boundaries, data flows, and integration seams across veil-proxy, veil-foundations, veil-custodian, veil-observatory, and veil-demo, and documents how to stand up each component today. |
| 2026-08-24 | Wrote `docs/interactive-plan.md`: public dashboard + local orchestration + interactive docs artifact, phased, public launch gated on explicit human `public_release` approval | Produced via a 3-stage review chain (Fable design → Codex critique against live repo state → Opus reconciliation with independent verification). The final pass found the plan's most important fact: `docs/architecture.md` on `main` is still the original 11-line stub — the real, corrected document only exists on the unmerged `agent/claude/architecture-doc` branch (PR #1). Phasing was restructured around that: nothing public-facing before that PR merges and a human decides whether the security-gap content it documents (veil-custodian's full route/authz surface, self-asserted demask auth, veil-observatory's unkeyed hash chain) should be public. Also killed a proposed `integration-status.yaml` mirror file after finding this repo's own `risk-register.yaml`/`risks.md` had already drifted (1 risk vs. 5) — same-PR discipline alone isn't sufficient; the collector should parse `architecture.md`'s table directly instead of maintaining a second source. |
