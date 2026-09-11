# Cross-Repo Dependencies

Machine-readable state lives in `.hekton/cross-repo-deps.yaml`. Keep this Markdown
file as the human-readable explanation of the same IDs — `eco_checker.py`'s
`check_cross_repo_dep_ids` fails the build if a repo's `next-actions.md`
references an ID that doesn't exist in the YAML, the same discipline this repo
already applies to `.hekton/risk-register.yaml` vs. `docs/risks.md`.

**What this is, and what it isn't.** This is an index of dependencies that cross a
repo boundary — one repo is blocked on, or waiting for, another. It is not a
second copy of `docs/architecture.md`'s "Sequencing to close them" section,
which still owns the fuller reasoning and priority order. A repo's own
`next-actions.md` should reference an ID here (`XREPO-00N`) rather than
restating the dependency's own description independently — that restatement is
exactly the drift that produced this registry (see `docs/decisions.md`,
2026-09-04).

| ID | Repos | Status | Summary |
|---|---|---|---|
| XREPO-001 | veil-observatory, veil-custodian | Closed 2026-09-06 | veil-observatory now has a real, live-proven caller for one of veil-custodian's three `Role::Observatory`-gated endpoints (`GET /v1/signing-keys/{key_ref}`, PR #17 + a live-run revoke round-trip in veil-demo's `ecdsa-signing-proof.sh`). `attestation/status` and `/certificates/crl` remain uncalled — tracked separately as `XREPO-006`, since they have no consumer anywhere yet (design-from-scratch work, not a fixture swap), and `architecture.md`'s sequencing step 4 only asked for one real call. |
| XREPO-002 | veil-foundations, veil-observatory | Open | No sandbox AWS account exists — blocks veil-foundations' real-world validation and veil-observatory's real evidence ingestion. |
| XREPO-003 | veil-custodian, veil-enrol | Closed 2026-09-06 | ADR first (veil-custodian's ADR-T), then built on both sides (renewal endpoint with lineage-not-validity supersession; `renew-signing-key` subcommand), independently verified (145 + 100 tests), then proven live against each other in `dev-e2e.sh`. Surfaced and corrected a real factual error in veil-enrol's ADR-VE-004 along the way. |
| XREPO-004 | veilgremlin, veil-custodian, veil-observatory | Closed 2026-09-05 | veilgremlin's raw `r\|\|s` (not DER) signature-encoding decision. veil-demo's 2026-09-05 ECDSA signing proof confirmed the encoding is sound and independently verifiable; human sign-off given on that evidence. Real ECDSA verification in veil-observatory is separate, still-unbuilt work this closure doesn't schedule. |
| XREPO-005 | veil-observatory, veilgremlin | Closed 2026-09-06 | Ratified on both sides: not `test_pipeline.py`'s full suite, a narrow `test_correlation_contract_gate.py` instead (veil-observatory ADR-0019), asserting against the production `Correlator`. veilgremlin had reached this conclusion 2026-08-23 but called it "deferred, not ratified" — the ratification, not the reasoning, was missing. 8 facts covered (not 7 — a more security-critical account/region-mismatch case was found while building). Cross-repo CI wiring remains deferred, unmet schema-artifact precondition on both sides. |
| XREPO-006 | veil-observatory, veil-custodian | Closed 2026-09-06 | ADR first (veil-observatory's ADR-0020), then built on both sides (attestation finding firing on revoked-or-expired plus an accepted signing-key sighting; CRL honestly scoped to fetch+cache only, no findings), independently verified (648 + 150 tests), then proven live in `dev-e2e`-style fashion via `ecdsa-signing-proof.sh`. Surfaced `XREPO-007` along the way. |
| XREPO-007 | veilgremlin, veil-observatory | Closed 2026-09-11 | ADR first on both sides (veilgremlin's ADR-016, veil-observatory's ADR-0021, each through three adversarial review rounds), then built (`SigningCredential::device_ref()`, `dev_<32hex>` wire form, `schema_version` bumped to `veil.edge_event.v2`, a shared dispatch resolver on the observatory side), independently verified, then live-run proven against real `veil-custodian`/`veil-enrol`/`veil-observatory` (`veil-demo/scripts/xrepo-007-device-ref-proof.sh`) — a real ECDSA credential produced a real `v2` record carrying the exact enrolled pseudonym, independently signature-verified, correctly landing as `unverifiable_algorithm` (no real ECDSA verifier exists yet). Four limitations closed with, not omitted: no device-side credential installer; no real ECDSA verification (→ `XREPO-008`); certificate loader doesn't check CA signature/validity; historical nulls not backfilled. |
| XREPO-008 | veil-observatory, veilgremlin, veil-custodian | Closed 2026-09-11 | ADR first (veil-observatory's ADR-0022, human-confirmed before code — native P-256 library over KMS since no AWS account exists, a local pre-fetched key-material cache over a live custodian call since `custodian.py` stays reachable only from `cli.py`), then built (`EcdsaReceiptVerifier`, the cache populated by `verify-signing-keys` with no second network call, an opt-in `AlgorithmDispatchVerifier` so a non-opted-in deployment sees zero behaviour change). Two full doubt-driven-development cycles against the shipped implementation (the second cross-model-corroborated by Codex) found and fixed 10 real issues, most severely a signing key never bound to a record's own claimed `device_ref` — fixed. Live-run proof (`veil-demo/scripts/xrepo-008-ecdsa-verification-proof.sh`, run twice) against real running services: the same real ECDSA-signed edge event lands `unverifiable_algorithm` before the cache is populated, `accepted` after — the first time this codebase has ever reached that disposition from organic ECDSA traffic. |
| XREPO-009 | veilgremlin, veil-enrol, veil-custodian | Open | No device-side writer exists for a telemetry signing credential — the OS-keychain loader is load-only, only ever populated via a test-only env-var seam. Filed on `XREPO-007`'s closure as its own Phase 3 item, the largest piece: `vg enrol request-csr`/`install-cert` (CSR-only issuance already ratified elsewhere, not re-litigated here), certificate-authenticity/trust-anchor distribution, atomic install/crash recovery, renewal lifecycle, mTLS-vs-signing profile separation, keychain platform scope, and plain-HTTP transport becoming materially more sensitive once a stable pseudonym rides along. |

## How an entry gets here

Found by grepping all six repos' `next-actions.md`/`decisions.md` files for
cross-repo language during a 2026-09-04 consolidation pass (prompted by a Codex
critique of an earlier, simpler design that tried to anchor into
`architecture.md`'s numbered sequencing list directly — rejected once actually
checked: numbered-list items don't get real anchors, and the section gets
reordered/struck-through too often for position-based references to survive).
This is a first population, not an exhaustive audit — there are almost
certainly more real cross-repo dependencies stated independently somewhere in
six repos' worth of backlog than the five caught in this pass. Add to this file
as more are found; each new entry should cite where it was found (which repo's
`next-actions.md`, roughly which date) the way the entries above do.

## How to close one

Flip `status: open` to `status: closed` in the YAML, add a `closed_date`, and
leave the entry in place (matching this project's "correct in place with a
date, don't delete history" convention for `docs/decisions.md`) rather than
removing the row — a closed dependency is itself informative history about
what used to block what.
