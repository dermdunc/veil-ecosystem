# Risks: Veil Ecosystem

## Risk Register

Machine-readable risk state lives in `.hekton/risk-register.yaml`. Keep this
Markdown file as the human-readable explanation of material risks and mitigations.

| ID | Date | Risk | Impact | Likelihood | Mitigation | Status |
|---|---|---|---|---|---|---|
| RISK-0001 | 2026-08-24 | Initial governance baseline needs first human/agent review | Medium | Medium | Run governance preflight and end-session review during the first material session | Open |
| RISK-0002 | 2026-08-24 | This document goes stale silently — no CI or process ties it to the 5 component repos' actual state | High | High | Treat `docs/architecture.md`'s Integration Status table as a required update whenever a cross-repo integration lands in any component repo; no automated check enforces this yet. **Materialised same-day:** a doubt-driven-development review found the first draft was already wrong in 3 load-bearing places, sourced from a 2-day-old audit never re-checked against live repo state — see `docs/decisions.md`. Corrected once; the underlying no-CI gap remains open. | Open |
| RISK-0003 | 2026-08-24 | No cryptographic *signing* exists in veil-proxy's pipeline, so veil-observatory's real verifier has nothing genuine to check yet | High | High (until closed) | Deliberately sequenced last, after the wire format stabilises — see architecture.md sequencing. **Corrected 2026-08-24 (3rd review cycle):** originally described as stubs on both ends; veil-observatory's verifier is real (`HmacReceiptVerifier`), only veil-proxy's signer is missing. | Open, tracked upstream in veil-proxy |
| RISK-0004 | 2026-08-24 | Demask authorisation (`--actor`/`--role`) is self-asserted, not authenticated, ecosystem-wide | High | Medium | Blocked on real device/actor identity work (product-family.md §6); not started | Open, tracked upstream in veil-proxy |
| RISK-0005 | 2026-08-24 | A component repo's own documentation can itself be stale relative to its code, and this document has no way to detect that except a fresh doubt-driven review | Medium | Medium | Materialised in the 3rd review cycle: veil-observatory's `correlation/correlator.py` and `ADR-0016` both still assert a "structural stub" signature verifier a real implementation had already superseded — this document copied that claim faithfully from a stale source, not a stale audit this time. Mitigation is procedural, not automatable yet: verify against code, not against any repo's prose about itself, including this one's. | Open |
