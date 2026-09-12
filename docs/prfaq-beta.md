# PRFAQ: Veil Ecosystem Beta

**Status:** draft, 2026-09-12, reconciled 2026-09-12 against
`veil-ecosystem/docs/beta-implementation-plan.md` (the phased cross-repo plan to reach this
beta — Fable draft → adversarial critique → Opus consolidation). Written before that plan
existed, per the PR/FAQ discipline of writing the press release first and letting it
pressure-test the plan, not the other way round. The Reconciliation Note (end of this document)
records what changed once the plan landed: seven real beta-readiness gaps the plan found that
this document's original Q3 had missed, and one stale claim in the plan's own early draft that
this document's Cite-Check pass had already caught the other way. The press release's
`[DATE]`/`[Contact/signup mechanism]` placeholders remain placeholders deliberately — the plan
sizes beta in sessions (~22-35 with two parallel workers), not calendar time, and a real date
requires real operator-availability scheduling this document has no basis to assume.

**Author's note on voice:** this family's own established discipline (see any ADR in
`veilgremlin/docs/decisions.md`, or `concept-blueprint-gremlin.md`'s Story-agent rule) is: cite
a real mechanism or omit the claim. Every capability claim in the press release below is true
today, live-run proven, and cross-referenced to the ADR/XREPO item that proves it in the
Internal FAQ. Nothing here is aspirational marketing language describing what AI generally can
do — if it reads that way anywhere, that's a defect in this draft, not a style choice.

**Review provenance:** produced via `~/hekton/gremlins/concept-to-product/prfaq-gremlin.md`'s
Grounding → Draft → Cite-Check → Recorder pipeline. The first drafting pass's own Cite-Check
step ran inline in the same session that wrote the draft — a real gap against that Gremlin's
own design, named honestly rather than smoothed over. A genuinely independent Cite-Check pass
(fresh-context reviewer, no memory of the drafting session) then ran against this document for
real and found six concrete problems, all fixed in place with an inline correction note at
each fix rather than a silent edit: one outright factual reversal (the credential-generation
claim), one press-release claim missing a caveat the FAQ already had, one quote-marking gap,
one fabricated audit-trail field, one wrong risk citation, and one real, unmet quality gate
(detector recall/precision) that the original draft's own citation pointed at but didn't
surface as a gap. See the inline "Correction (2026-09-12, independent Cite-Check finding)"
notes throughout for exactly what changed and why.

---

## PRESS RELEASE

### Veil Ecosystem Beta: prove your AI coding agent never saw what it wasn't supposed to

**A masking proxy and cryptographically verifiable audit trail for AI coding assistants,
purpose-built for teams who can't just take a vendor's word for it.**

[CITY], [DATE] — Today marks the beta availability of Veil Ecosystem, a privacy-preserving
layer for AI coding assistants like Claude Code. Veil sits between a developer's laptop and
the cloud model: it detects and masks secrets, PII, and sensitive enterprise identifiers
before they ever leave the machine, restores them locally when the agent's response comes
back, and — new in this beta — produces a cryptographically signed, device-attributable
record of every masking decision an organization can independently verify, without trusting
Veil's own say-so.

Engineering teams have adopted AI coding assistants faster than their security and compliance
functions can answer a simple question: *what did the model actually see?* Pasting a
stack trace into a chat window can just as easily paste a customer's email address, an
internal hostname, or a database credential along with it. Existing approaches ask developers
to self-police, or block AI tools outright — neither holds up under a real audit. Veil
Ecosystem is built for the organizations in between: they want their engineers using AI
coding assistants, and they need to be able to prove, to an auditor or a regulator, exactly
what left the building and what didn't.

Veil's masking engine — the `vg` CLI, wrapping an agent invocation directly — already runs
standalone on a developer's laptop today, deterministically detecting and masking the
categories of data it's tuned for, with a policy engine that hard-denies specific
destinations regardless of who's asking. What's new in this beta is the identity layer: each
enrolled device now holds its own custodian-issued signing credential, installed and loaded
entirely from the operating system's own credential store — never a manually-copied secret,
never a raw key sitting in a config file. Every audit-relevant event is signed with that
credential and reaches a separate verification service that checks the signature
independently, ties it to a real (but pseudonymous, never directly identifying) enrolled
device, and — once a security team's own verification tool has refreshed its local record of
which keys are still trusted — will flag a revoked or compromised device that keeps signing
after that refresh. The result: a security team doesn't have to trust that masking happened —
they can verify it happened, and verify who it happened on, without ever seeing what was
actually masked.

"The gap in every other tool in this space is the same," said [PRODUCT LEAD — illustrative,
not a real quote, see Internal FAQ]. "They'll tell you they mask sensitive data. None of them
will show you cryptographic proof, tied to a real device, that a specific masking decision
actually happened the way they claim. That's the bar we built beta around — not a bigger list
of regexes, a verifiable one."

**Getting started.** A team enrolls each developer's machine once, through an operator-run
CLI that issues a device-specific signing credential from the organization's own custodian
service — the device itself generates that credential's private key, and it never leaves the
device: not transmitted anywhere, not written to a file, not printed to a terminal, held only
in the OS keychain. From there, `vg run -- claude "..."` wraps any Claude Code invocation
transparently:
masking happens automatically, policy gates block anything the organization has marked
hard-deny, and every relevant event is signed and reported without the developer doing
anything differently. A security team runs a separate verification tool against the
organization's own audit trail to confirm, independently, that signing is real and devices
are in good standing.

"We needed something we could actually put in front of our auditors, not a vendor claim,"
said [an illustrative beta customer, not a real quote — see Internal FAQ]. "Being able to
show them a signature that our own infrastructure verified, not Veil's, was the difference
between a six-month evaluation and a real pilot."

Veil Ecosystem's beta is available today to design-partner organizations running Claude Code
or compatible AI coding assistants who need an auditable masking layer before they can expand
usage past an early-adopter team. [Contact/signup mechanism — TBD, see Internal FAQ Q9.]

---

## FAQ

### External FAQ (customer-facing)

**Q1: What exactly does Veil mask?**
Deterministic detectors for secrets and structured PII categories (the detector suite's exact
recall/precision gates are tracked in `veilgremlin/docs/risks.md`, RISK-0003/RISK-0004) —
things like API keys, credentials, emails, phone numbers, and similar structured identifiers.
It is not a general-purpose redaction tool for arbitrary sensitive prose; if your risk is
someone typing a sensitive business narrative in plain English with no structured identifiers
in it, that's outside what pattern-based masking catches today, and beta does not change that.

**Q2: Does Veil ever see or store what it masks, unencrypted, anywhere Veil operates?**
The masking vault lives locally, wrapped by an OS-keychain-backed key (SQLCipher, AES-256).
Nothing masked leaves the developer's machine as part of the masking operation itself. The
*verification* layer (veil-observatory) never receives masked content — only a signed record
of a policy decision and a device identity, never the category or content of what was masked —
by design, not as a redaction step applied after the fact. See the Internal FAQ's "what does
the audit trail actually contain" question for the precise field list.

**Q3: What happens if I need something un-masked — say, to actually run the code the model
suggested?**
A local, policy-gated demask operation restores the real value to a local destination (never
back to the cloud model automatically). Certain destinations — sending a rehydrated value to
a remote model prompt — are hard-denied in the default policy regardless of who requests it;
that's enforced structurally, not by convention.

**Q4: How is this different from just telling developers not to paste secrets?**
It doesn't rely on developer discipline at all — masking is automatic and happens before the
data leaves the machine, and the audit trail exists specifically so a security team never has
to take a developer's (or Veil's) word for what happened.

**Q5: Do you ever learn our engineers' real identities from this?**
No. Devices are enrolled under an opaque, custodian-minted pseudonym, not a real-identity
binding. A legally-gated resolution process exists for the rare case an organization's own
authorized process needs to map a pseudonym back to a real device/user, and it is
independently audited and access-controlled — Veil's verification layer itself never performs
or needs that resolution to do its job.

**Q6: What AI coding assistants does this work with today?**
Claude Code, via a direct wrapping invocation (`vg run -- claude ...`). Other agent harnesses
are not proven in beta; see Internal FAQ Q7 for what "harness-agnostic" would actually require.

**Q7: What platforms are supported?**
The masking engine itself is cross-platform. The new device-credential writer this beta adds
is verified on macOS only at launch — Windows and Linux support is explicitly a fast-follow,
not a beta blocker for macOS-only design partners (tracked as `XREPO-011`).

**Q8: Does Veil protect against a malicious or compromised AI agent, not just an accidental
leak? (Added 2026-09-12, per the beta-planning pipeline's D-BETA-1 disclosure requirement)**
No — and we want to be direct about that rather than let it be discovered later. Veil is built
for, and proven against, the case where an AI coding assistant is behaving as intended and
would otherwise accidentally see sensitive data pasted into its context: masking happens
automatically before that data reaches the model, and the audit trail proves it happened. What
Veil does **not** yet defend against is an actively adversarial or compromised agent
deliberately trying to exfiltrate data it already has local access to — for example, by
invoking Veil's own unmasking command directly. Closing that gap requires attesting *which
process* is asking, not just what role it claims, and that requires OS-level mechanisms beyond
this beta's scope. Beta ships with mitigations that raise the bar (the masking hooks refuse to
run an unmask command from inside a wrapped agent session, credential and pack files carry
restrictive permissions, and the underlying vault key is verified to never enter a wrapped
session's environment) but this is disclosed as a real, current limitation, not a solved
problem.

---

### Internal FAQ (the hard questions)

**Q1: Is any of the press release above true today, or is beta the point at which it becomes
true?**
Everything about masking, policy gating, and the local vault is true today, live-run proven,
running standalone (`veilgremlin`'s own `docs/setup.md`/README). The device-signing-credential
identity layer — enrollment, credential install into the real OS keychain, signed telemetry
reaching a real verification service and landing `accepted` — is also true today as of
2026-09-12 (ADR-017, `XREPO-009`, live-run proven end to end in
`veil-demo/scripts/xrepo-009-device-credential-install-proof.sh`). What is **not** true today,
and is exactly what a beta-readiness plan needs to close, is listed in Q3 below — the press
release above describes the beta bar this document is arguing *for*, not the current state
without qualification. Every specific technical claim in the press release is grounded in a
real, named mechanism; see Q2 for the mapping.

**Q2: Mechanism citations for every press-release claim, so none of it is unverifiable
marketing language:**
- "masks secrets, PII... before they ever leave the machine" — `veilgremlin`'s detector suite
  + local vault, `vg diff --masked`/`vg run`.
- "restores them locally when the agent's response comes back" — `vg demask --to
  local-patch`, policy-gated.
- "hard-denies specific destinations regardless of who's asking" — the policy engine's
  hard-deny table, `remote_model_prompt` named explicitly as an example destination that is
  always denied.
- "each enrolled device now holds its own custodian-issued signing credential, installed and
  loaded entirely from the operating system's own credential store" — `vg enrol
  request-csr`/`install-cert` (ADR-017, `vg-vault::enrol`), never a manually-extracted raw
  scalar.
- "reaches a separate verification service that checks the signature independently" —
  `veil-observatory`'s `EcdsaP256Verifier` (ADR-0022, `XREPO-008`).
- "will flag a revoked or compromised device that keeps signing after that refresh" —
  `verify-signing-keys`' revoked-key finding (ADR-0018, `XREPO-001`), explicitly caveated in
  the press release itself (not just here) that this requires a refresh of the local cache
  first — the refresh is manual today, not yet automated (`XREPO-012`); see Q4.
- "the device itself generates that credential's private key, and it never leaves the
  device... held only in the OS keychain" — `vg-vault::csr`'s `request_device_signing_csr`
  generates the keypair in-process, on-device (`vg-vault/src/enrol.rs`'s own module doc);
  the live-run proof transcript confirms the key is never written to disk or printed at any
  step, only stored to/loaded from the OS keychain. **Correction (2026-09-12, independent
  Cite-Check finding):** an earlier draft of this press release claimed "no code on the
  device generates... a raw private key," which was the literal opposite of what this
  mechanism does — the key generation happening on-device, in-process, is the entire point
  of `XREPO-009`. Fixed to state what's actually true: on-device generation, never
  transmitted/written/printed.
- "opaque, custodian-minted pseudonym, not a real-identity binding" — `veil-custodian`'s
  `dev_<32hex>` pseudonym scheme (ADR-D/ADR-N).
- "a legally-gated resolution process" — `POST /v1/resolutions`, `Role::ResolutionAuthority`,
  fail-closed audit-before-disclosure (named in `veilgremlin/docs/next-actions.md`'s 2026-09-07
  entry).

**Q3: What has to be true that isn't true today, for the press release to stop being
aspirational?**
This is the actual beta-readiness gap — the 7 open XREPO items plus the operational gaps named
in this session's own "how usable end to end is the ecosystem now" assessment:
1. Enrollment and credential install are entirely human-CLI-operated today. The press
   release's "a team enrolls each developer's machine once, through an operator-run CLI"
   sentence is honest about that (it says operator-run, not self-service), but a beta with
   more than a handful of design-partner machines needs that operator flow to not be a
   bottleneck — not full MDM, but at minimum a scriptable/batchable enrollment path.
2. No CA trust-anchor distribution mechanism (`XREPO-010`) — an operator hand-carries the
   trust-anchor file today. Fine for a handful of design partners; not fine past that.
3. No renewal automation (`XREPO-012`) — 30-day credentials, 7-day warning, manual
   re-enrollment. A beta running longer than ~3 weeks per customer will hit this for real.
4. Telemetry transport is plain HTTP (`XREPO-015`) — now that a real, stable pseudonym rides
   along, this is a real gap for any design partner who'd ask about it, not a theoretical one.
5. `--actor`/`--role` authorization is self-asserted, not authenticated, ecosystem-wide —
   tracked as veil-ecosystem's `RISK-0004` (**write this as F4 or VE-RISK-0004**, never bare
   `RISK-0004`: veilgremlin has its own, unrelated `RISK-0004` covering detector
   false-positive rate, and both the original Cite-Check and the beta-planning pipeline each
   had to correct a conflation of the two). **Resolved as a named beta-gating decision,
   2026-09-12 (D-BETA-1, `docs/beta-implementation-plan.md` §3): partially beta-blocking.**
   The threat splits cleanly: an accidentally-cooperating agent is stopped (masking holds —
   this is the beta's actual value proposition); an actively adversarial or prompt-injected
   agent is not (full authentication needs OS-level caller attestation, out of reach for
   beta). Ships with three mechanical mitigations (hook refusal to spawn `vg demask` from a
   wrapped session, restrictive file permissions, a vault-key-absence test) plus a written,
   signed disclosure in the beta participation agreement — see External FAQ, a new Q8 below.
   This is not a gap left for a security team to discover; it is disclosed to them upfront.
6. No AWS sandbox account exists (`XREPO-002`) — blocks KMS Verify as an alternative signature
   backend and any cloud-evidence-ingestion story; does NOT block the beta bar above, which
   only needs the native P-256 path already built.
7. Windows/Linux device-credential writer support is unbuilt (`XREPO-011`) — acceptable to
   scope beta to macOS-only design partners explicitly, not silently.
8. **(Corrected 2026-09-12, beta-planning pipeline — this item was itself stale in the
   opposite direction from how it read the day it was written)** The detector suite's
   false-positive-rate fix (`veilgremlin/docs/risks.md`'s *own* RISK-0004, not to be confused
   with the ecosystem-level `RISK-0004`/F4 covering demask authorization — see item 5's own
   correction, and always write **VE-RISK-0004** for this one to avoid the collision) is
   **merged to `main`** as `6f4ea5d`, `vg bench` verdict GO, false-positive rate 0.0% —
   independently confirmed during beta-plan consolidation, contradicting this item's own
   earlier claim that the fix was "not yet merged... pending human review." What is still
   genuinely open, and is the actual half of this gate a beta customer should care about:
   **RISK-0003 (detector recall, ≥99% secret / ≥95% PII) has no recorded measurement at
   all.** A false-positive rate of 0% proves nothing about how much real, sensitive data the
   detectors are missing. Tracked as beta-plan item A7 (measure recall against RISK-0003's
   own gates before beta condition (1) can be honestly graded as met) — measurement only; a
   miss opens separately-sized remediation, not absorbed into A7 itself.
9. **(Added 2026-09-12, from the beta-implementation-plan's Finding A)** There is no
   shippable masking daemon. Real TLS to Claude Code/Anthropic (M5) and streaming (M6) are
   both unbuilt, and even setting those aside, no real production service binary exists —
   today's constructors take already-resolved config, not the real state-dir/keychain
   discovery a running service needs. This is the single largest concrete gap between "the
   mechanism is proven" and "a beta user can actually run this," and it sat entirely outside
   the XREPO registry because it's single-repo work.
10. **(Added 2026-09-12, from the same Finding)** There is no server-side deployment story
    for veil-custodian or veil-observatory at all: no working non-dev authenticator, no TLS
    termination anywhere despite one being named in an existing ADR, no container/IaC/secrets/
    backup artifacts. Every proof this family has ever produced, including `XREPO-009`'s, ran
    entirely on one laptop. This is the plan's identified critical path (9-15 of its ~22-35
    total sessions).
11. No component holds a real, authenticated revocation credential (`XREPO-016`, new) — every
    device revocation ever executed in this family's history used a dev-only stub credential.
12. No remote-enrollment workflow exists (`XREPO-017`, new) — every enrollment proof ran
    device and operator on the same machine; a real beta cohort needs a defined CSR handoff
    with out-of-band fingerprint confirmation instead.
13. No release engineering exists for `vg` (`XREPO-018`, new) — no signed/notarized binary, no
    real SBOM, no tested upgrade path against the binary-scoped keychain ACLs `XREPO-009`'s own
    closure documented.
14. No cross-repo version-compatibility policy exists (`XREPO-019`, new) — this family's own
    interface contract moved v1.4→v1.9 in about seven weeks across six independently-cadenced
    repos, with nothing naming how a deployed beta cohort's component versions stay compatible.

**Q4: What's the single scariest thing a beta customer's security team will find if they dig?**
Revocation lag: a device signing key revoked at the custodian continues to verify successfully
until the next `verify-signing-keys` run refreshes veil-observatory's local cache (ADR-0022's
own named limitation, restated honestly in `XREPO-008`'s closure). This is an accepted design
trade-off today, not a bug, but it needs a real answer — an automated refresh cadence, most
naturally folded into `XREPO-012`'s renewal-automation work — before a beta customer's security
team is told "revoked means revoked" without a caveat attached.

**Q5: What does the audit trail actually contain — the precise field list, for anyone who
wants to check the privacy claim themselves?**
`Envelope`/`Integrity` fields per `veil.edge_event.v2` (schema-versioned, ADR-016): a decision
kind (`demask_request`/`demask_decision`/`blocked_attempt`), a policy decision where
applicable (`allowed`/`policy_version`), a device_ref (the pseudonym, not a real identity),
and the ECDSA signature/algorithm/key_ref — never the masked value itself, never the raw
pre-mask text, and (**correction, 2026-09-12 independent Cite-Check finding**) also never a
per-category tally like "1 x EMAIL masked" — that's `vg diff --masked`'s own local console
output, which never reaches veil-observatory at all; an earlier draft of this answer
conflated the two. Independently verifiable against `veil-observatory`'s actual
`veil.edge_event.v2.schema.json` and in
`veil-demo/scripts/xrepo-009-device-credential-install-proof-transcript.txt`'s Step 13, which
shows exactly what a captured record contains (device_ref/schema_version/algorithm only, no
category breakdown).

**Q6: Why now — what changed that makes a beta conversation timely rather than premature?**
`XREPO-009` (this session) closed the last structural gap in the identity pipeline: until
today, every "organic" signed event still relied on a documented test-only env-var seam for
its signing credential, not a real device-installed one. That's the difference between "we
proved this works in a lab" and "this is a mechanism a real device could actually use" — the
qualitative line a beta conversation needs on the far side of, even though real beta hardening
(Q3) still sits between here and shipping to a design partner.

**Q7: What would "harness-agnostic" (multiple AI coding assistants, not just Claude Code)
actually require, and is it a beta blocker?**
Not scoped or estimated anywhere in this family's current backlog — worth naming as a real gap
in this PRFAQ rather than silently assumed. Not a beta blocker (design partners piloting
against Claude Code specifically don't need it), but the external FAQ's Q6 answer should stay
honestly scoped to "Claude Code today" until real design work exists for a second harness.

**Q8: What's explicitly NOT beta scope, on purpose?**
- Full MDM/fleet enrollment (any beta-scale operator-run flow is a bridge, not the end state).
- KMS Verify / any backend beyond native P-256 (blocked on `XREPO-002`, not needed for beta).
- Cross-platform (Windows/Linux) device-credential writer support (`XREPO-011`).
- A public, self-service veil-demo experience (its own deployment is currently down,
  `RISK-0006`, and isn't the beta's delivery mechanism regardless).
- Any second AI coding assistant beyond Claude Code (Q7).

**Q9: What is the actual beta signup/contact mechanism?**
Not decided — placeholder in the press release. This is a real open question for whoever owns
go-to-market for this product, not a technical one this document can answer; flagged here so
it isn't silently left as marketing copy nobody actually owns.

**Q10: Who is the illustrative customer quote and leader quote in the press release, and are
they real?**
No, neither is real — both explicitly marked inline as illustrative/not real quotes. Per this
family's own discipline (and the PRFAQ Gremlin's Completion Condition #4, "every quote and
named-leader statement... never left ambiguous"): a fabricated quote of either kind must
never ship as if real. **Correction (2026-09-12, independent Cite-Check finding):** an
earlier draft marked only the customer quote as illustrative — the leader quote had a
placeholder *name* in brackets but nothing marking its *content* as fabricated, which a
reader could easily misread as "this quote is real, only the name is pending." Both are now
marked the same way, inline, at the point of the quote. Replace either with a real one once
it exists, or cut the section — do not leave placeholder wording in any externally-facing
version of this document.

---

## Reconciliation Note (closed out 2026-09-12)

This PRFAQ was written ahead of, and independently from, the phased cross-repo implementation
plan (Fable draft → adversarial critique → Opus consolidation, `docs/beta-implementation-plan.md`).
That plan has now landed; the three open questions below are answered, not left standing.

**Does the plan's "beta-ready" definition match Q3's gap list, or scope beta differently?**
Mostly matches, with the plan being materially more complete — it caught real gaps this PRFAQ's
Q3 missed entirely (a shippable masking daemon doesn't exist yet; there is no server-side
deployment story anywhere for veil-custodian/veil-observatory; detector recall is unmeasured,
only false-positive rate is; no revocation-authority credential exists; no remote-enrollment
workflow exists; no release engineering exists; no cross-repo version-compatibility policy
exists). Where they disagreed, the plan's version is corrected and this PRFAQ's Q3/Q5/Q3-item-8
have been fixed to match, not left to silently diverge (see the inline "Corrected 2026-09-12"
notes throughout, both from the independent Cite-Check and from this reconciliation pass).

**Does the plan's sequencing suggest a realistic Availability date?**
Not a calendar date — the plan's own unit is sessions (~22-35 with two parallel workers, ~31-47
serial), not elapsed time, and converting that to a date requires knowing actual operator
availability this document has no basis to assume. The press release's `[DATE]` placeholder
stays a placeholder; replace it once real scheduling exists, not with an invented date. What
this document *can* now say concretely: beta follows the plan's five phases (Phase 0 decisions
→ two parallel tracks, data-plane and server-side → telemetry/revocation → enrollment/lifecycle
→ release engineering and acceptance proof), and the acceptance gate is a specific, named
artifact (the plan's item E2: a second-machine, signed-binary, remote-enrollment, streaming,
TLS-telemetry, real-revocation proof) — not a subjective "feels ready."

**Did the plan surface anything this PRFAQ's Q3 missed, or vice versa?**
Yes, in both directions, and both are now fixed rather than left as a known gap: the plan found
the seven items listed in the first answer above, none of which were in this PRFAQ's original
Q3. This PRFAQ's own Cite-Check pass, in turn, found that the plan's initial draft had a stale
claim in the opposite direction — treating merged masking work (M3/M4) as unbuilt — which the
consolidation stage corrected before this reconciliation ran. The corrected Q3 gap list (§ above)
now reflects the plan's findings; nothing from either document was left un-reconciled.
