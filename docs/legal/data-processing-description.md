# Veil Ecosystem Beta — Data Processing Description

**Status: DRAFT — NOT LEGALLY REVIEWED. Internal/legal-review document, not participant-facing
in its current form. Do not treat as a finalized Article 30-style record or DPA schedule until
qualified legal counsel has reviewed it.**

**Drafted:** 2026-09-13, per `docs/beta-implementation-plan.md` D-BETA-2, as mission work under
intent `INT-2026-09-12-001`. Companion to `privacy-notice.md` (participant-facing) and
`beta-participation-agreement.md` — this document is the more technical internal record of
what's actually processed, where, and why, meant to give legal counsel enough to assess the
other two rather than duplicate their prose.

**NOT READY FOR REAL ENROLMENT.** Describes the beta as *designed*. Phase A (data plane) and
Phase B (server-side infrastructure, including replacing the default `DenyAllAuthenticator`
with real authentication) are both **not started** as of this draft
(`docs/beta-implementation-plan.md`'s Progress tracker; §2, Finding B). §6 below distinguishes
accepted residual risk from unbuilt prerequisites.

---

## 1. Processing activities

| Activity | Data involved | Purpose | Automated? |
|---|---|---|---|
| Device enrolment | CSR (public key material only), operator-supplied enrolment metadata | Issue a device-specific signing credential | No — operator-run CLI, manual today (`XREPO-017` covers remote enrolment; not built for beta) |
| Masking (local) | Raw text seen by the AI coding assistant, masked/unmasked values | Detect and mask secrets/PII before they reach the model | Yes, entirely local — never transmitted to us |
| Signed telemetry | Device pseudonym, schema version, decision kind, policy decision (`allowed`/`policy_version`), signature/algorithm/key_ref | Prove a masking/policy decision happened, without seeing its content | Yes — automatic on every audit-relevant event |
| Key verification | Device pseudonym, public signing-key material, attestation/revocation status | Verify signatures, flag revoked/compromised devices | No — an operator runs `verify-signing-keys` by hand; there is no schedule yet (see `XREPO-012`) |
| Pseudonym resolution (rare) | Device pseudonym → real device/user mapping, retained by the custodian service specifically to make this resolution possible | Only on the organization's own authorized request | Partially — the mapping is retained continuously; the *lookup* is manual, `Role::ResolutionAuthority`-gated. "Audited" describes intended design; no third-party audit has occurred as of this draft. |

## 2. Data NOT processed

The *original, unmasked* content, raw pre-mask text, and per-category masking tallies never
leave the participant's device as part of normal operation — a structural property of the
design (the observatory's schema has no field for any of it), not a policy choice enforced by
discretion. (The *masked*, placeholder-bearing version of a prompt is of course still sent
onward to the model — that's the product's normal function, distinct from what this section
describes.) See `veil.edge_event.v2.schema.json` and `docs/prfaq-beta.md` Internal FAQ Q5 for
independent verification.

## 3. Where processing happens

- **On-device (participant's machine):** masking, local vault (SQLCipher/AES-256), signing
  private key generation and storage. Under normal operation the private key is loaded only
  from the OS keychain (see §6 for the narrow support/debug exception). Entirely under the
  participant organization's own control.
- **Custodian and observatory services:** hosting *target* is Fly.io (D-BETA-6 part 2,
  `docs/decisions.md`, 2026-09-13 — provider and billing decided; specific region/data-residency
  not yet chosen). **No instance is actually deployed there as of this draft** — Phase B (which
  includes standing up this deployment) has not started.
- **No sub-processors** are currently contemplated beyond the eventual hosting provider
  (Fly.io) — provisional, since nothing is deployed yet and Phase B's deployment work
  (containerization, managed Postgres, backups) may introduce others.

## 4. International transfers

`[TBD — depends on (a) the region ultimately chosen within Fly.io, and (b) where beta
participants and their devices are located. Cannot be assessed until both are known; flagged
here rather than assumed benign.]`

## 5. Retention and deletion

`[TBD, pending an operational decision not yet made.]` On offboarding, `docs/beta-implementation-
plan.md` item D4 (`vg uninstall`) is designed to remove a device's local vault, keychain items,
and packs client-side and prompt the operator to revoke — **D4 is not yet built as of this
draft.** Server-side retention of a device's historical signed-event records and pseudonym
mapping is not yet decided either.

## 6. Security measures (technical and organizational)

**(a)–(c) are accepted, disclosed residual risk. (d)–(f) are prerequisite gaps that must close
before real enrolment — unbuilt, not accepted.**

- **(a) Accepted risk:** on-device key generation loads only from the OS keychain under normal
  operation; a separate, narrow environment-variable override exists for controlled
  support/debug use (D-BETA-4), and beta-scoped policy accepts the underlying raw scalar as
  exportable via that path rather than claiming it cannot be exported.
- **(b) Accepted risk, in transit:** telemetry is plain HTTP as of this draft (`XREPO-015`);
  TLS work (`C1a`/`C1b`) is scoped but not built for this beta.
- **(c) Accepted risk, at rest (server-side):** D-BETA-3's interim posture is managed-Postgres
  encryption at rest plus a signed risk acceptance, not full field-level sealing — contingent
  on this document's own legal review outcome.
- **(d) Prerequisite gap, not closed:** no component holds a real, gateway-authenticated
  `Role::RevocationAuthority` in any deployment (`XREPO-016`) — every revocation this family has
  ever executed used a development-only trust shortcut. Even a correctly authenticated trigger
  today writes through three independent, non-transactional database calls, any one of which can
  fail separately, per `docs/beta-implementation-plan.md` §2 (Finding B).
- **(e) Prerequisite gap, not closed:** no real authentication is deployed for *any*
  custodian/observatory API role today. `DenyAllAuthenticator` (deny everything) is the actual
  production default; no mTLS or other real gateway exists. Naming only (d) above would wrongly
  imply the other roles (`Role::Observatory`, `Role::EnrolmentAuthority`,
  `Role::ResolutionAuthority`) are already protected by real, deployed authentication — they are
  not, as of this draft. Phase B is this plan's critical-path work to fix this, alongside
  further named defects (a device-registration collision returning a raw server error instead
  of a clean conflict; internal error text that can leak through an API response; a
  certificate-authority loader that performs no validation of files it's given).
- **(f) Known, disclosed limitation (accepted for beta, not a prerequisite gap):**
  demask-authorization is self-asserted, not authenticated (F4/VE-RISK-0004, D-BETA-1) — see
  the Participation Agreement §5(a). The three mechanical mitigations this ships with are **not
  yet implemented** as of this draft (plan item A5, not started); do not describe them as
  shipped until they are.

## 7. Open items for legal review

- [ ] Legal basis for processing (§1) — likely legitimate interest or contract performance,
      not yet confirmed by counsel.
- [ ] International transfer assessment (§4) — blocked on region/participant-location facts.
- [ ] Retention schedule (§5).
- [ ] Whether the interim (unsealed) at-rest posture (§6(c)) is acceptable, or forces
      D-BETA-3's "sealing becomes mandatory" branch — the single largest schedule risk named in
      `docs/beta-implementation-plan.md` §3 (D-BETA-2's own rationale).
- [ ] **Operational, not legal, but blocking regardless:** §6(d)/(e)'s prerequisite gaps
      (Phase B) must close before this document describes a system safe to enroll real
      participants against — legal sign-off on the *policy* does not substitute for that
      infrastructure actually existing.
