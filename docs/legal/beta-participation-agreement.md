# Veil Ecosystem Beta — Participation Agreement

**Status: DRAFT — NOT LEGALLY REVIEWED. Do not send to any design-partner organization or
participant until qualified legal counsel has reviewed and approved this document.**

**Drafted:** 2026-09-13, per `docs/beta-implementation-plan.md` D-BETA-2 (legal/consent basis
for holding real users' bindings and telemetry), as mission work under intent
`INT-2026-09-12-001`. Cross-referenced against `docs/prfaq-beta.md`'s External FAQ (especially
Q5, Q8) and `docs/beta-implementation-plan.md` §§1–3.

**NOT READY FOR ENROLMENT.** This draft describes the beta as *designed*, not as it stands
today. As of this draft's date, Phase A (data plane: real TLS/streaming, a production daemon)
and Phase B (server side: a real TLS-terminating gateway replacing the default
`DenyAllAuthenticator`, deployment of the custodian/observatory services themselves) are both
**not started** (`docs/beta-implementation-plan.md`'s Progress tracker). Do not enroll any real,
non-author participant, and re-review every claim in this document against actual system state,
before that work lands. Sections below distinguish between (i) *accepted, disclosed residual
risk the beta ships with on purpose* (§5(a)/(b)/(d) below) and (ii) *prerequisite work that must
exist before beta starts at all* (§5(c), §5(e)) — do not treat the second category as a
tolerable trade-off; it is unbuilt, not accepted.

**Open items this draft cannot resolve, flagged rather than guessed at:**
- [ ] Legal entity name, registered address, and signing authority (organization operating this
      beta) — placeholders throughout §1.
- [ ] Governing law / jurisdiction — placeholder `[JURISDICTION]`.
- [ ] The revocation-lag window (§5(b) below) has no fixed number yet — `docs/prfaq-beta.md` Q4
      names this as the single scariest thing a customer's security team will find if they
      dig, and ties a real answer to Phase B item B5's scheduled `verify-signing-keys` cadence,
      which does not exist yet.
- [ ] Contact/support channel — placeholder `[CONTACT]`, per `docs/prfaq-beta.md` Q9 (signup
      mechanism not yet decided).

**Resolved since this draft was first sketched:** hosting/billing *target* for the custodian and
observatory services is Fly.io, with a new credit card to be added (D-BETA-6 part 2,
`docs/decisions.md`, 2026-09-13). **This is a target, not a deployment** — no instance is
actually running there as of this draft; §3 below says so explicitly.

---

## 1. What this beta is

`[ENTITY NAME]`, a `[JURISDICTION]`-organized entity with its registered address at
`[REGISTERED ADDRESS]`, acting through `[SIGNING AUTHORITY / TITLE]` ("we", "us"), operates
Veil Ecosystem, a masking proxy and cryptographically signed audit trail for AI coding
assistants. This agreement governs your organization's ("Participant", "you") use of the Veil
Ecosystem beta.

## 2. Scope of the beta

- **Platform: macOS only for the new device-credential writer.** The masking engine itself is
  cross-platform; specifically the device-side signing-credential writer (`vg enrol`) is
  verified and supported on macOS only for this beta (tracked as `XREPO-011`) — this is not a
  claim that no part of Veil runs elsewhere.
- **Coding assistant: Claude Code only**, via `vg run -- claude ...`. No other AI coding
  assistant is proven or supported in this beta.
- **Enrolment is operator-run.** A designated operator at your organization enrolls each
  participating device individually; this is not a self-service or automatic process.
- This is a **beta**: features, APIs, and behavior may change, and the service may be
  interrupted, without the notice a generally-available product would carry.

## 3. What Veil does with your data

- Veil's masking engine detects and masks secrets, structured PII, and similar identifiers
  **before they leave your device**, using a local vault protected by an OS-keychain-backed
  key (SQLCipher, AES-256). The *original, unmasked* values are never transmitted as part of
  the masking operation itself — note that the *masked* (placeholder-bearing) version of your
  prompt is of course still sent onward to the model; that is the product's normal function,
  distinct from the original sensitive values it replaces.
- Each enrolled device holds its own custodian-issued signing credential. The device generates
  that credential's private key itself, on-device, and under normal operation loads it only
  from the OS keychain — not manually copied, typed, or read from a file. **A separate,
  narrow environment-variable override path exists for controlled support/debug use only
  (D-BETA-4, `docs/decisions.md`); it is not part of normal participant operation, and the raw
  key material is, by explicit beta-scoped policy, accepted as exportable via that path rather
  than claimed impossible to export.**
- Every audit-relevant event (a demask request, a demask decision, a blocked policy attempt) is
  signed with that credential and sent to a separate verification service (the "observatory").
  **The observatory's hosting target is Fly.io (region not yet selected) — as of this draft, no
  instance is actually deployed there; this describes the plan, not current infrastructure.**
  The observatory's design never receives the masked content itself, or which category of data
  was masked — only a signed record of a policy decision and a device identity (an opaque
  pseudonym, never your real identity). See the Privacy Notice §2 for the precise field list.

## 4. What Veil does NOT do

- Veil does not send unmasked/rehydrated values back to a remote model automatically; certain
  destinations (a remote model prompt) are hard-denied in the default policy regardless of
  who's asking.
- Veil does not learn your engineers' real identities from routine operation. A resolution
  process is designed for the rare case your organization's own authorized process needs to map
  a pseudonym back to a real device — access-controlled and logged, gated on a distinct role,
  and not something Veil's verification layer performs on its own initiative. `["Independently
  audited" is not yet an accurate claim — no third-party audit of this process has occurred as
  of this draft; removed pending one actually happening, or pending counsel's guidance on
  whether internal access-control logging alone supports weaker language here.]`

## 5. Known limitations and prerequisites, disclosed in writing

We disclose the following rather than let them be discovered later. **(a), (b), and (d) are
accepted residual risk the beta ships with on purpose. (c) and (e) are prerequisite gaps that
must close before real enrolment, not risks beta accepts.**

**(a) Demask authorisation is not cryptographically authenticated (D-BETA-1).** Veil's masking
holds against an AI agent behaving as intended — the case where an agent would otherwise
accidentally see sensitive data pasted into its context. It does **not** yet defend against an
actively adversarial or compromised agent that deliberately tries to invoke Veil's own unmask
command directly. Beta is designed to ship with three mechanical mitigations that raise the bar
(masking hooks refuse to spawn `vg demask` from inside a wrapped agent session; restrictive
file permissions on packs/state directories; a test asserting the vault key never enters a
wrapped session's environment) — **as of this draft these mitigations are not yet implemented**
(`docs/beta-implementation-plan.md` item A5, not started). Closing the underlying gap fully
requires OS-level caller attestation, out of scope for this beta regardless. Do not represent
these mitigations as shipped until A5 lands and is verified.

**(b) Revocation lag has no committed number yet.** A device's signing key, once revoked at the
custodian, continues to verify successfully until the observatory's next key-refresh run. As of
this draft there is no schedule for that refresh at all — it happens only when an operator runs
it by hand — so there is no committed maximum revocation-lag window to state here.
`[REVOCATION LAG WINDOW — TBD, blocks final sign-off of this agreement until Phase B item B5
lands a real schedule]`.

**(c) No component holds a real, gateway-authenticated capability to trigger a revocation
(`XREPO-016`) — a prerequisite gap, not accepted risk.** Every device revocation this family has
ever executed used a development-only trust shortcut, not a real authenticated credential; the
CLI operators would use for enrolment has no revoke command at all today. This is distinct from
(b)'s lag: (b) assumes a real revocation was triggered and asks how long a stale key stays valid
afterward; this is whether a real, gateway-authenticated party can trigger a revocation at all
(a development stub can, today, which is itself the problem — the beta needs a real credential
for this, not none). Separately: even a correctly authenticated trigger writes through three
independent, non-transactional database calls (`docs/beta-implementation-plan.md` §2, Finding
B) — any one of which can fail independently, potentially leaving a device only partially
revoked. Do not enroll real participants until `XREPO-016` lands a real revocation-authority
credential, an operator command, and the cascade is made transactional.

**(d) Telemetry transport is not yet encrypted in transit.** Telemetry from your device to the
observatory travels over plain HTTP as of this draft (tracked as `XREPO-015`).
`[TO BE UPDATED once C1a/C1b land a TLS-protected transport, before this agreement is finalized]`.

**(e) No real authentication is deployed for the custodian/observatory APIs at all — a
prerequisite gap, not accepted risk.** `docs/beta-implementation-plan.md` §2 (Finding B)
documents that `DenyAllAuthenticator` is this family's actual production default today (a real
safety net, but one that denies everything, not one that authenticates real callers), no mTLS
or other real gateway exists anywhere, and several further server-side defects remain open (a
device-registration collision that returns a raw server error instead of a clean conflict
response; internal error text that can leak through an API response; a certificate-authority
loader that performs no validation of files it's given). Phase B is this plan's own
critical-path work to fix this. Nothing in this beta's design implies any API role beyond the
revocation authority named in (c) is currently protected by real, deployed authentication —
disclosing only (c) would wrongly imply the others already are.

## 6. Your obligations

- You will enroll only devices under your organization's control, through your designated
  operator.
- You will not attempt to circumvent the masking or policy-gating mechanisms described here.
- You acknowledge the limitations and prerequisites in §5 and accept them as a condition of
  participating in this beta, in their current, unresolved state — understanding that §5(c) and
  §5(e) specifically must close before your organization is actually enrolled, per this
  document's own "NOT READY FOR ENROLMENT" notice above.

## 7. Term and exit

Either party may end participation at any time. `docs/beta-implementation-plan.md` item D4
(`vg uninstall` — remove keychain items/state dir/packs, emit a final event, prompt the operator
to revoke) is the designed offboarding path, but **is not yet built as of this draft**. Until it
exists, exit/offboarding is a manual process; `[EXIT/DATA-DELETION TIMELINE — TBD, and this
section needs updating once D4 actually ships]`.

## 8. Contact

`[CONTACT — TBD, see docs/prfaq-beta.md Q9]`
