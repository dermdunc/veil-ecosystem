# Veil Ecosystem (VeilGremlin) — Consolidated Phased Cross-Repo Plan to Beta

**Date:** 2026-09-12 · Planning artifact only.

**Provenance:** produced by a three-stage pipeline at the user's explicit request: a Fable-model
draft, an independent adversarial critique (Codex was rate-limited; a fresh-context Claude
reviewer was substituted, same standard), and an Opus consolidation pass that re-verified the
contested points directly against repo source before merging both documents. Not yet committed
to git or reconciled into `.hekton/cross-repo-deps.yaml` — this file is the output for human
review before any of that happens.

---

## 0. Verification done during consolidation

Four checks, because the two prior documents disagreed or were silent:

1. **M3/M4 are merged to `main`.** `f9f2bae` (M3, request masking) and `65d467f` (M4, response
   demask) both `git branch --contains` → `main`. The draft's Finding A (M3 "still open") is
   dead. `veilgremlin/docs/next-actions.md` lines 33-91.
2. **M3/M4's own named-gap lists contain a beta blocker neither prior document mentioned.**
   Both entries name "real production state-dir/keychain discovery for a `vg-proxy` daemon
   *binary* — this milestone's `Daemon` constructors take already-resolved config, matching
   what tests need, **not a real running service**." There is no shippable proxy daemon today.
   New Track 1 item A3.
3. **ADR-T's renew endpoint exists; the enumeration endpoint genuinely does not.**
   `veil-custodian/src/api/mod.rs` has issue, renew, and get-by-`key_ref` — no device-level
   list. The critique's correction to Fable's D3 claim is upheld exactly.
4. **The detector-quality gate is half-closed, in the opposite direction from what the PRFAQ
   claims.** `6f4ea5d` (FP-rate fix, `vg bench` verdict GO, FP 0.0%) **is on `main`** — so
   `docs/prfaq-beta.md` Q3 item 8's "not yet merged to main" is itself stale. But
   `veilgremlin/docs/risks.md` RISK-0003 (**recall**: secret ≥99% / PII ≥95%) has no recorded
   measurement at all. New Track 1 item A7 — this is what makes beta condition (1) gradable.

**Registry-hygiene landmine found:** `RISK-0004` means two different things in two repos. In
`veil-ecosystem/.hekton/risk-register.yaml` it is "demask authorisation is self-asserted, not
authenticated, ecosystem-wide." In `veilgremlin/docs/risks.md` it is the **false-positive-rate**
risk. Both the Fable draft and the critique wrote "F4/RISK-0004" as if it were one ID. This plan
calls the self-asserted-authorisation issue **F4** (its veilgremlin T11-scope ID) or
**VE-RISK-0004**, never bare `RISK-0004`.

Also confirmed real: veilgremlin RISK-0012 (placeholder IANA PEN `55555` in the ADR-S signing
EKU OID) and a live, dated `veil-ecosystem/docs/prfaq-beta.md` that explicitly asks to be
reconciled with this plan.

---

## 1. Beta bar (ratify in Phase 0)

A cohort of **3-10 real, non-author users on their own macOS machines** can be onboarded and use
the product for real work; an operator is involved at enrolment but not mid-session; security
gaps are enumerated and accepted **in writing**, not latent.

| # | Condition | Gradable when |
|---|---|---|
| 1 | **Masking data plane works for real traffic** — real Claude Code / Anthropic API, real TLS upstream, streaming included, running as a real daemon | M5, M6, A3 daemon bootstrap done; recall measured against RISK-0003's own gates (A7); F4 mitigations shipped and the residual disclosed in writing (A5) |
| 2 | **Install without a compiler** — signed, notarized, versioned `vg` binary, macOS only, tested upgrade path | E1 |
| 3 | **Enrolment at a distance** — device `request-csr`+`install-cert`, operator-side `veil-enrol` against a deployed, really-authenticated custodian | B1, B2, D2 |
| 4 | **Telemetry trustworthy without a human in the loop** — signed events over TLS, hosted observatory, real `device_ref` reaching `accepted`, `verify-signing-keys` on a schedule, revocation within a stated window | B5, C1, C2 |
| 5 | **Custodian fit to hold strangers' identity bindings** — real authn+TLS, identity columns encrypted at rest or signed acceptance of the interim, backups, known bugs fixed, legal/consent basis | B1-B4, Phase 0 legal item |

**macOS-only is justified, not assumed:** `vg-vault::enrol`'s `EnrolLock` is `#[cfg(unix)]`-gated
with a genuinely erroring (not silently no-op) stub, and CI runs `macos-latest` only for
build/test/clippy/fmt. XREPO-011 stays open and out of scope; beta scopes to macOS explicitly,
in the participation agreement.

---

## 2. The two reshaping findings, as corrected

**Finding A (revised): the data plane is the biggest unfiled beta blocker — on M5, M6, and
daemon bootstrap, not M3.** M3 and M4 shipped 2026-08-24. Genuinely unbuilt:
`vg-proxy/src/upstream.rs` is plain-HTTP-only, M5 (real Claude Code/API-key mode) and M6
(streaming) unbuilt, no production daemon binary, display-collision corruption open (1 in 3
round-trips), pack-purge TTL (F5) open, dead `artefacts.by_language [dotenv]` path, `document`
content-block handling unbuilt. T11's NO-GO stands. No XREPO item tracks any of it — single-repo
work the registry structurally can't see.

**Finding B: holds up line-for-line, with more supporting detail than first stated. Reuse
near-verbatim.** `DenyAllAuthenticator` is the default build; `stub-authn` is feature-gated
**and** refuses to start when `VEIL_ENV=production` (a real safety net worth crediting); ADR-O
explicitly puts the mTLS gateway out of scope and no nginx/caddy/envoy reference exists anywhere;
no Dockerfile/`.tf`/docker-compose anywhere; `ca/mod.rs::load_or_generate` performs zero
validation when files exist; the revocation cascade is three separate un-transacted store calls,
each independently failable; the `device_binding` UNIQUE collision falls through to a 500 not a
409 (migration 0002's partial unique index guarded by an `ON CONFLICT` on the wrong column);
`CaError::UnsupportedKeyAlgorithm → ApiError::Validation` leaks raw internal text via 422; no
component holds `Role::RevocationAuthority` in any gateway-verified sense and `veil-enrol` has no
`revoke` subcommand (ADR-VE-001 excludes it deliberately); the observatory receiver defaults to
`127.0.0.1`, admits no TLS/transport auth in its own docstring, and runs stdlib
`http.server.HTTPServer` **single-threaded**.

---

## 3. Named beta-gating decisions (Phase 0 — decide before building)

**D-BETA-1 — F4 / VE-RISK-0004: self-asserted demask authorisation. PARTIALLY BETA-BLOCKING.
Mitigate + disclose; do not attempt real authentication.** Threat model splits: accidental
disclosure by a cooperating agent (masking holds — this is the beta's actual value proposition)
vs. an actively adversarial/prompt-injected agent (masking does not hold today, and won't by
beta — full fix needs OS-level caller attestation, a separate research track). Ship three
mechanical mitigations (A5): hooks refuse to spawn `vg demask` from inside a wrapped session;
0600 perms on packs/state dir; a test asserting the vault key never enters the wrapped
environment. Plus a written, signed threat-model disclosure in the PRFAQ and the beta
participation agreement. Condition (1) is graded against the mitigated-and-disclosed state, not
"solved."

**D-BETA-2 — Legal/consent basis for holding real users' bindings and telemetry.
BETA-BLOCKING. Phase 0, human-owned, external latency.** ADR-H treats the binding as regulated
personal data. Required before the first non-author enrolment: a beta participation agreement
(macOS-only scope, F4 residual, revocation-lag window), a privacy notice, a data-processing
description. Start in Phase 0, run parallel. **May force B3's answer:** if review rejects the
unsealed interim, ADR-H sealing becomes mandatory and B3 goes from 0.5 to 2 sessions — the
single largest schedule risk in this plan.

**D-BETA-3 — ADR-H sealing.** Default: take the interim (managed-Postgres encryption at rest +
signed risk acceptance) for beta; keep real sealing post-beta. 0.5 session, contingent on
D-BETA-2.

**D-BETA-4 — XREPO-014.** Raw P-256 scalar exportability accepted for beta; env-var override
forbidden except as a documented support path.

**D-BETA-5 — XREPO-013 decision half.** Custodian formally pins production CA provisioning to
P-256/ECDSA-SHA256. Implementation half (larger than filed) lands in B4.

**D-BETA-6 — XREPO-002 route-around.** Native P-256 only for beta. KMS Verify, veil-foundations,
cloud-evidence ingestion all defer; XREPO-002 stays open. Hosting/billing for the beta's own
custodian/observatory deployment is a separate Phase 0 decision (RISK-0006: no funded target
today).

**D-BETA-7 — PEN registration ordering.** Not schedule-critical against a 9-15-session Track 2,
but the gate sits at *first non-dev certificate issuance* (ADR-S), i.e. Phase D/E, not Phase 0.
Start registration in Phase 0 for latency; enforce the gate at D2/E2.

---

## 4. Phase plan

### Phase 0 — Ratify, decide, unblock external latency
*Repos: veil-ecosystem, veil-custodian, veilgremlin · **2 sessions***

- Ratify §1's beta bar; record D-BETA-1..7 with names against them.
- Start day one: IANA PEN registration, legal/consent drafting and review.
- Decide the hosting/billing target for the custodian/observatory beta deployment.
- Registry hygiene: file XREPO-016/017/018/019 (§6); annotate XREPO-010/011/012/013/015 with
  corrected scopes (§7); disambiguate the two `RISK-0004` IDs; correct `prfaq-beta.md` Q3 item 8
  (the FP fix **is** merged; recall is the live half) and reconcile its Availability/cutline
  placeholders against this plan.

### Track 1 / Phase A — Data plane to real traffic
*Repo: veilgremlin · **9-12 sessions** · fully parallel with Track 2*

| Item | Work | Sessions |
|---|---|---|
| ~~A1~~ | ~~Finish M3~~ — **deleted, shipped `f9f2bae` 2026-08-24.** M4 also shipped (`65d467f`). | 0 |
| A2 | Real TLS client in `vg-proxy/src/upstream.rs`, Anthropic API-key mode, real Claude Code session. Confirm conservative default for unhandled `document` content blocks. | 2 |
| A3 | Production daemon bootstrap — real state-dir/keychain discovery; today's `Daemon` constructors take already-resolved config only. | 1-2 |
| A4 | M6 streaming — M4's per-complete-block demask design doesn't answer SSE chunk-boundary/partial-placeholder questions. | 2-3 |
| A5 | F4 mitigations + disclosure (D-BETA-1). | 1-2 |
| A6 | `vg diagnose` — redacted support bundle (versions, policy hash, config shape, counters; never raw text/masked values/vault/packs). | 1 |
| A7 | Measure detector recall against RISK-0003's ≥99%/≥95% gates. Measurement only; a miss opens separately-sized remediation. | 1 |
| A8 | Beta hygiene — display-collision fix, `vg pack purge` TTL (F5), dead dotenv config path. | 1 |

**Not in Track 1:** Receipt/Alert, GLiNER warm path, LiteLLM gateway, MCP server mode, F3
(ancestor state-dir trust — keep warning, defer refusal), M4's unbounded binding-store growth.

### Track 2 / Phase B — Stand up a server side (critical path)
*Repos: veil-custodian, veil-observatory, veil-enrol · **9-15 sessions***

| Item | Work | Sessions |
|---|---|---|
| B1 | One TLS edge for both services (Caddy/Envoy: mTLS vhost for custodian, TLS vhost for observatory). Replaces `DenyAllAuthenticator`. First real exercise of `veil-enrol`'s `mtls` profile. Shared-fate trade-off accepted at cohort scale; split post-beta. | 3-4 |
| B2 | Deploy/ops from zero — containerize, managed Postgres, secrets, backups + tested restore, CI deploy. No existing Dockerfile/IaC/sibling pattern anywhere. | 3-5 |
| B3 | ADR-H sealing — 0.5 (interim) or 2 (if legal review rejects it). | 0.5-2 |
| B4 | Transactional revocation cascade; fix the `ON CONFLICT` target so `device_binding` collision returns 409; stop `CaError` text leaking via 422; real validation in `load_or_generate` (key-matches-cert, algorithm, expiry). | 1-2 |
| B5 | Observatory hosted off-loopback behind B1; real schedules for `verify-signing-keys`/`verify-device-attestation`/`fetch-crl`; publish the resulting revocation window as a number; swap to `ThreadingHTTPServer` + document a cohort-scale concurrency limit. | 1-2 |

### Phase C — Telemetry over TLS + revocation authority
*Repos: veilgremlin, veil-observatory*

| Item | Work | Sessions | Depends on |
|---|---|---|---|
| C1a | XREPO-015 client half — starts in parallel, does not wait for B1. Interface-contract change (a pinned test currently rejects `https`) + rustls client + a second trust-anchor decision. Builds/unit-tests against a local mock TLS server. | 1-2 (parallel) | none |
| C1b | XREPO-015 integration against the real TLS edge. | 0.5-1 | B1 |
| C2 | XREPO-016 revocation-authority tooling (new) — real authenticated revocation path + operator command. Pair with D4. | 1-2 | B1 |

### Phase D — Enrolment, trust anchors, renewal, lifecycle
*Repos: veilgremlin, veil-enrol, veil-custodian · **5-9 sessions** · needs B1+B2*

| Item | Work | Sessions |
|---|---|---|
| D1 | XREPO-010 CA trust-anchor distribution — bundle pinned device-CA cert inside the signed `vg` release artifact. State whether it covers the telemetry TLS anchor too. | 1-2 |
| D2 | XREPO-017 remote enrolment workflow (new) — CSR handoff with out-of-band SPKI-fingerprint confirmation, scriptable/batchable operator path. PEN gate enforced here. | 1-2 |
| D3 | XREPO-012 renewal — **re-scoped down.** ADR-T already built the renew endpoint and settled the trust boundary. Remaining: one device-level list-keys endpoint + client-side scheduling. | 1-2 |
| D4 | Uninstall/offboarding (new) — `vg uninstall`: remove keychain items/state dir/packs, emit a final event, prompt operator to revoke via C2. | 1 |
| D5 | XREPO-019 cross-repo version compatibility (new) — `vg` sends contract version on enrolment/telemetry; custodian/observatory reject or warn on unknown major; a published compat matrix. Full negotiation deferred. | 1-2 |

### Phase E — Release engineering and beta acceptance
*Repos: veilgremlin, veil-demo · **4-6 sessions (+1 optional)** · needs Track 1 + Track 2 + C + D*

| Item | Work | Sessions |
|---|---|---|
| E1 | XREPO-018 `vg` release engineering — signed/notarized binary, real SBOM, versioned artifact. Test matrix: install v1 → enrol → install v2 (same signing identity) → confirm keychain ACL still grants; macOS minor-update rehearsal; documented recovery procedure. | 3-4 |
| E2 | Beta acceptance proof — fork XREPO-009's proof script into a full beta-path proof on a second machine: signed binary, remote enrolment, real streaming Claude Code session, TLS telemetry reaching `accepted`, real revocation within the stated window, `vg uninstall`. The go/no-go artifact. | 1-2 |
| E3 | Optional: restore veil-demo's public deployment (RISK-0006). | 0-1 |

---

## 5. Dependency graph and critical path

```
Phase 0 (2)
  external latency, day 1: IANA PEN → gate at D2/E2 · legal/consent → gates B3, gates all enrolment
  TRACK 1 · veilgremlin (9-12): A2→A3→A4; A5/A6/A7/A8 independent
  TRACK 2 · server side (9-15) [CRITICAL PATH]: B1(3-4)→B2(3-5)→B5(1-2); B3, B4 parallel within
      ├─ C1b(0.5-1), C2(1-2)   [needs B1]
      └─ Phase D (5-9)         [needs B1+B2]
  C1a (1-2) parallel from day 1
                                  ↓
                        Phase E (4-6) → BETA
Independent/optional: XREPO-011 (Windows/Linux) — not on the path
```

**Critical path (two workers):** 2 + (9-15) + (2-3) + (5-9) + (4-6) ≈ **22-35 sessions**.
**Single worker, fully serial:** ≈ **31-47 sessions**.

**Three schedule risks, in order:** (1) legal review rejecting the unsealed interim (B3 grows,
possibly more); (2) B2's from-zero deployment overrunning even 5 sessions; (3) A7 measuring
recall below RISK-0003's gate, opening unsized detector remediation on condition (1).

---

## 6. New XREPO filings (Phase 0, item 0.4)

| ID | Title | Phase |
|---|---|---|
| XREPO-016 | No component holds `Role::RevocationAuthority`; every revocation to date was a stub-authn curl, and `veil-enrol` has no `revoke` subcommand | C2 |
| XREPO-017 | No remote-enrolment workflow: CSR handoff and out-of-band SPKI-fingerprint confirmation for a user who is not the operator | D2 |
| XREPO-018 | No release engineering for `vg`: no signed/notarized binary, no SBOM, no tested upgrade path against binary-scoped keychain ACLs | E1 |
| XREPO-019 | No cross-repo version-compatibility policy or version handshake; contracts moved v1.4→v1.9 in ~7 weeks across six independently-cadenced repos | D5 |

**Non-XREPO items needing owners** (single-repo or governance — the registry structurally can't
see these): the data-plane M5/M6/daemon-bootstrap block; custodian/observatory deployment
posture; D-BETA-2 legal/consent; D-BETA-3 ADR-H sealing; veilgremlin RISK-0012 PEN registration;
RISK-0003 recall measurement.

---

## 7. Under- and over-scoped existing items

| Item | Correction |
|---|---|
| XREPO-010 | Should state whether it covers the device-cert CA only, or also the telemetry TLS trust anchor C1a introduces. |
| XREPO-011 | Not merely "untested" — `#[cfg(unix)]`-absent with an erroring stub, no compiling non-macOS CI job. |
| XREPO-012 | Over-scoped as the original draft framed it; ADR-T already built the renew endpoint and settled the trust boundary. Remaining: one list-keys endpoint + client scheduling. |
| XREPO-013 | Under-scoped: `load_or_generate` does zero validation when files exist, not just a missing algorithm pin. |
| XREPO-015 | Under-scoped: an interface-contract change + a rustls client + an observatory TLS listener that doesn't exist + a second trust-anchor decision. Not config. |

---

## 8. Explicitly out of scope for beta, with reasons

- **Real authentication for demask authorisation** — needs OS-level caller attestation; mitigated and disclosed instead (D-BETA-1).
- **Windows and Linux** (XREPO-011) — macOS-only, stated in the participation agreement.
- **AWS sandbox, KMS Verify, veil-foundations, cloud-evidence ingestion** (XREPO-002) — native P-256 covers beta; no funded account exists.
- **MDM/fleet enrolment** — D2's scriptable operator path is the beta answer.
- **Full renewal automation** — D3's scheduled-renew loop is the beta answer.
- **ADR-H real sealing** — interim per D-BETA-3, contingent on D-BETA-2.
- **Splitting the shared TLS edge** — accepted shared fate at cohort scale.
- **M4's unbounded binding-store growth** — documented session-length caveat instead.
- **F3 ancestor state-dir trust** — keeps warning; refusal defers.
- **GLiNER warm path, LiteLLM gateway, MCP server mode, CI/CD mode, Receipt/Alert + aggregator, dashboard/reporting UI, multi-tenancy, Secure-Enclave keys, synthetic-data/quasi-identifier scoring** — all post-beta.
- **veil-demo public deployment** (E3) — optional; RISK-0006 unresolved.

---

## 9. What changed during consolidation, and why

1. **A1 "finish M3" deleted** — M3/M4 both merged 2026-08-24, confirmed on `main`. Finding A's conclusion survives on M5/M6 alone.
2. **M4 added to the picture** — the draft never mentioned response demasking at all.
3. **A3 added (daemon bootstrap)** — surfaced by reading M3/M4's own named-gap lists, which neither prior document had done.
4. **A7 added (recall measurement), and the PRFAQ corrected the other way** — the FP fix is merged (contradicting the PRFAQ's own claim it wasn't); recall is the actually-unmeasured half.
5. **D3 re-scoped down** — ADR-T already answered the architecture question the draft called open.
6. **F4 resolved rather than deferred** — partially beta-blocking, not a one-line "accepted" bullet.
7. **B1 and the draft's B5-infra merged** into one TLS edge, trade-off stated explicitly.
8. **C1a un-bundled from B5** and moved to day one.
9. **Sizing corrected in three directions** — B2 grown (1-2→3-5), A4/M6 grown (streaming forces real design questions), Track 1 grown overall (4-6→9-12) despite deleting A1.
10. **PEN gate moved later, not dropped** — bound to first non-dev issuance (Phase D/E), not Phase 0.
11. **All five "missing entirely" items placed, none deferred silently** — legal/consent, support/diagnostics, uninstall/offboarding, version compatibility, OS-update fragility.
12. **Observatory single-threaded `HTTPServer`** added to B5's scope.
13. **Registry-hygiene fix** — the two colliding `RISK-0004` IDs, disambiguated throughout.
14. **Kept because it held up under direct source inspection:** Finding B in full, the four custodian bugs + validation gap, the two-track parallel shape, the XREPO-002 route-around, the XREPO-016/017/018 filings, the under-scoped-items list minus XREPO-012, the macOS-only justification, and the Phase 0 → Tracks → C → D → E structure.
15. **`prfaq-beta.md` reconciliation is Phase 0's job**, answering its own Reconciliation Note's three questions: Q3's gap list (§1, §4 here), Q4's revocation lag (B5 publishes a number), and its Availability/cutline placeholders (§5's estimate, §8's cutline).
