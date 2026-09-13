# Veil Ecosystem Beta — Privacy Notice

**Status: DRAFT — NOT LEGALLY REVIEWED. Do not publish or distribute until qualified legal
counsel has reviewed and approved this document, and confirmed it satisfies applicable law in
every jurisdiction where beta participants are located.**

**Drafted:** 2026-09-13, per `docs/beta-implementation-plan.md` D-BETA-2, as mission work under
intent `INT-2026-09-12-001`. Cross-referenced against `docs/prfaq-beta.md` External FAQ Q2/Q5
and Internal FAQ Q5 (audit-trail field list), and `docs/beta-implementation-plan.md` §2
(Finding B).

**NOT READY TO PUBLISH OR RELY ON.** This describes the beta as *designed*; Phase A and Phase B
server-side/data-plane work are both **not started** as of this draft
(`docs/beta-implementation-plan.md`'s Progress tracker) — see §5 for exactly which security
measures below are accepted, disclosed residual risk versus unbuilt prerequisites.

**Open items:** `[ENTITY NAME]` (data controller), `[JURISDICTION]`, `[LEGAL BASIS — TBD,
pending counsel: likely legitimate interest or contract performance, not yet confirmed]`,
`[DATA RETENTION PERIOD — TBD]`, `[CONTACT / DATA PROTECTION CONTACT — TBD]`.

**Resolved since this draft was first sketched:** hosting *target* is Fly.io (D-BETA-6 part 2,
`docs/decisions.md`, 2026-09-13) — no instance is actually deployed there yet, and the specific
region/data-residency jurisdiction within Fly.io is not yet chosen either; §6 states the
provider, not a live deployment or a precise location.

---

## 1. Who this notice covers

This notice describes how `[ENTITY NAME]` processes personal data in connection with the Veil
Ecosystem beta, for: (a) developers whose devices are enrolled by a participating
organization, and (b) the operator who performs that enrolment.

## 2. What personal data we process

**We do not process the content you mask.** The original, unmasked values, and the raw
pre-mask text an AI coding assistant would otherwise have seen, are never transmitted to us as
part of normal operation — they stay on your device, protected by a local, OS-keychain-backed
vault key. (The *masked*, placeholder-bearing version of your prompt is of course still sent to
the model — that's the product's normal function; it is not what this section is about.)

What we do process:

- **An opaque device pseudonym**, per enrolled device (`dev_<32 hex characters>`), minted by the
  custodian service at enrolment. This is not derived from, and does not contain, your name,
  username, email, or any other directly identifying value on its own.
- **A pseudonym-to-real-device mapping, held separately and only accessible through the
  resolution process in §4.** The pseudonym alone does not identify you to us, but a mapping
  allowing resolution is retained by the custodian service — this is what makes §4's resolution
  process possible at all, and is itself personal data while it exists.
- **A signing credential's public certificate** (not the private key, which is generated
  on-device and, under normal operation, loaded only from the OS keychain — see §5 for the
  narrow exception) and its associated metadata (issuance date, expiry, algorithm).
- **Signed audit events**, each containing: a schema version, a decision kind (e.g. a demask
  request, a demask decision, a blocked policy attempt), a policy decision where applicable
  (an `allowed` flag and `policy_version`, specifically — not a free-text description), the
  device pseudonym above, and a cryptographic signature with its algorithm and key reference.
  These events **never** contain the masked value itself, the raw pre-mask text, or even a
  per-category tally of what was masked (e.g. "1 email masked") — that information exists only
  in your own local console output and is never transmitted to us. Independently checkable
  against the schema at `veil.edge_event.v2.schema.json` and
  `docs/prfaq-beta.md` Internal FAQ Q5.
- **Operator-provided enrolment information** (whatever your organization's operator supplies
  during the CSR/certificate-issuance handshake — this is currently a manual, human-run
  process; no automated collection beyond the CSR itself).

## 3. Why we process it

To operate the beta: to verify that masking decisions were genuinely made and signed by an
enrolled device (without our needing to see what was masked), to detect and flag revoked or
compromised devices, and to support your organization's own audit/compliance needs.
`[LEGAL BASIS — TBD, pending counsel]`.

## 4. Re-identification (pseudonym resolution)

The device pseudonym is not, by itself, reversible to a real identity by anyone without access
to the mapping named in §2. A separate resolution process is designed for the rare case your
organization's own authorized process needs to map a pseudonym back to a real device
(`POST /v1/resolutions`, gated on a distinct `Role::ResolutionAuthority`, fail-closed). We do
not perform or need this resolution to operate the verification service day to day. `["Fail-
closed and audited" describes the intended design; no third-party audit of this process has
occurred as of this draft — pending counsel's guidance on appropriate language here.]`

## 5. Security measures

**(a) and (b) below are accepted, disclosed residual risk the beta ships with on purpose. (c),
(d), and (e) are prerequisite gaps that must close before real enrolment — not risk beta
accepts, work that isn't done yet.**

**(a) Demask authorization is not cryptographically authenticated.** Masking holds against an
AI agent behaving as intended; it does not yet defend against an actively adversarial or
compromised agent invoking Veil's own unmask command directly. Beta is designed to ship with
three mechanical mitigations (hook refusal inside a wrapped session, restrictive file
permissions, a vault-key-absence test) — **not yet implemented as of this draft**
(`docs/beta-implementation-plan.md` item A5). See the Participation Agreement §5(a) for the
full disclosure.

- Your device's signing private key is generated on-device and, under normal operation, is
  loaded only from the OS keychain — not manually copied, typed, or read from a file. A
  separate, narrow environment-variable override exists for controlled support/debug use only
  (D-BETA-4); beta-scoped policy accepts the underlying key material as exportable via that
  path, rather than claiming it cannot be exported.
- The masking vault is protected by SQLCipher with AES-256 encryption, keyed by an
  OS-keychain-backed key.
- **(b) Disclosed, accepted risk:** telemetry transport is not yet encrypted in transit (plain
  HTTP as of this draft; tracked as `XREPO-015`).
- **(b) Disclosed, accepted risk:** a revoked device's signing key continues to verify
  successfully until our next key-refresh run — there is currently no schedule for that refresh
  at all (it happens only when an operator runs it by hand), so there is no committed maximum
  lag. See the Participation Agreement §5(b).
- **(c) Prerequisite gap, not yet closed:** no component holds a real, gateway-authenticated
  capability to trigger a device revocation (`XREPO-016`) — every revocation this family has
  ever executed used a development-only trust shortcut. Even a correctly authenticated trigger
  today writes through three independent, non-transactional database calls, any one of which
  can fail separately. See the Participation Agreement §5(c).
- **(d) Prerequisite gap, not yet closed:** no real authentication is deployed for the
  custodian/observatory APIs at all. `DenyAllAuthenticator` (deny everything) is this family's
  actual production default; no mTLS or other real gateway exists yet. Disclosing only (c) above
  would wrongly imply other API roles are already protected by real, deployed authentication —
  they are not, as of this draft. See the Participation Agreement §5(e).
- **(e) Prerequisite/interim posture:** identity bindings and telemetry at rest use the interim
  posture named in D-BETA-3 (managed-Postgres encryption at rest plus a signed risk acceptance),
  not field-level sealing — contingent on this same legal review.

## 6. Where your data is processed and stored

Custodian and observatory services' hosting *target* is Fly.io — **no instance is actually
deployed there as of this draft.** `[Specific region/data-residency jurisdiction — also not yet
chosen (D-BETA-6, 2026-09-13, decided only the provider and billing arrangement).]` No
sub-processors beyond the eventual hosting provider are currently contemplated, but this is
provisional — nothing is deployed yet, and Phase B's deployment work (containerization,
managed Postgres, backups) may introduce others.

## 7. Retention

`[RETENTION PERIOD — TBD, pending counsel and an operational decision not yet made.]`

## 8. Your rights

Depending on your jurisdiction, you may have rights to access, correct, or delete personal data
we hold about you. Because the device pseudonym is not directly identifying to us without the
mapping in §2, exercising these rights may require your organization's operator to initiate the
resolution process in §4. `[Full rights language — TBD, pending counsel and jurisdiction.]`

## 9. Contact

`[CONTACT / DATA PROTECTION CONTACT — TBD]`
