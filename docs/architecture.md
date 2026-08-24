# Architecture: Veil Ecosystem

**Status:** living document. First written 2026-08-24, directly answering the gap an
[audit of the ecosystem](https://github.com/dermdunc/veil-ecosystem) named as its own final
recommendation: *"No document ties the five repos together... write the missing architecture
document."* This is that document. It will drift out of date the moment any component repo
changes — see [Keeping this current](#keeping-this-current).

## Overview

**VeilGremlin** is the umbrella name for a product family aimed at one problem: keep real PII
and sensitive enterprise identifiers out of an AI coding agent's cloud context, and give
regulated organisations a way to prove that's happening. No single repo is "VeilGremlin" — it's
five components, each with its own repo, maturity level, and privacy boundary:

| Component | Repo | Role | Privacy |
|---|---|---|---|
| **veil-proxy** | [`dermdunc/veilgremlin`](https://github.com/dermdunc/veilgremlin) | Masking data plane — runs on the developer's laptop | public |
| **veil-foundations** | [`dermdunc/veil-foundations`](https://github.com/dermdunc/veil-foundations) | Terraform control plane for Amazon Bedrock | public (+ private sibling) |
| **veil-custodian** | [`dermdunc/veil-custodian`](https://github.com/dermdunc/veil-custodian) | Device-pseudonym-to-identity mapping custodian | internal |
| **veil-observatory** | [`dermdunc/veil-observatory`](https://github.com/dermdunc/veil-observatory) | Correlation and assurance plane | private, local-first (standalone location, outside `~/Development/hekton`) |
| **veil-demo** | [`dermdunc/veil-demo`](https://github.com/dermdunc/veil-demo) | Public interactive demo of the masking engine | internal |

**veil-proxy's repo is still named `veilgremlin` on GitHub.** VeilGremlin was promoted from "the
name of this one repo" to "the name of the family" on 2026-07-26; the rename of the GitHub
remote itself was deliberately deferred (no second repo existed yet to disambiguate from) and
still hasn't happened. Runtime identity — the `.veilgremlin/` state directory, the
`com.veilgremlin.vault` keychain service, and the `vg` CLI binary — is intentionally unchanged
and should stay that way: those name the *product*, not the repo, so existing installs and
vaults keep working regardless of what any repo is called.

**veil-foundations was originally named `veil-walled-garden`.** Same deliverable, renamed once
per-team cost attribution and inference profiles came into scope, which "walled garden" didn't
suggest. If you see the old name in commit history or session logs of the older repos, this is
what it refers to.

## Components

### veil-proxy (repo: `veilgremlin`)

The only component that's fully built and running today: 270 tests across 10 crates, a real
`vg` CLI (`vg run`, `vg inspect`, `vg diff --masked`, `vg demask`, `vg audit`), detectors,
policy engine, and a SQLCipher vault. Runs entirely on the developer's laptop with no network
dependency in its hot path.

- **Owns:** parse → detect → mask → vault → policy → masked pack, plus local demask.
- **Explicitly does not:** decide fleet-wide policy, aggregate telemetry across machines,
  authenticate its own actor (`--actor`/`--role` are self-asserted, not authenticated), or gate
  *whether* a Bedrock call is allowed at all (that's veil-foundations — veil-proxy only
  minimises *what's in* a call it's already permitted to make).
- **Gaps:** no cryptographic signing anywhere in the pipeline — the audit log is
  tamper-evident, not tamper-proof, and the policy-pack "signature" field is a hardcoded
  placeholder that always verifies. There is no `TelemetryEvent` type in code yet, only a
  draft proposal, so nothing downstream has anything real to ingest.

### veil-foundations

Terraform for Amazon Bedrock as a governed invocation control plane: IAM model allowlists,
invocation logging, VPC endpoints, cost attribution. Composes with veil-proxy as **defence in
depth** — veil-proxy minimises *what* goes out, veil-foundations constrains *whether it can go
out at all, and to which model*. A leak requires both a masking failure and an
invocation-authority failure; deployed alone, each is weaker in a specific, nameable way (see
`veilgremlin/docs/architecture/product-family.md` §2 for the full argument).

- **Status:** one real module (`iam-model-allowlist`, a paired Allow/Deny IAM policy) passes
  `fmt`/`validate`/`test` against a mock provider. Nothing has run against a real AWS account.
- **Known defect, not an open design question:** the one built module currently makes a
  Bedrock Guardrail mandatory per invocation. That contradicts the family's actual, decided
  policy (ADR-0001 in veil-observatory, ADR-010 in veil-foundations, superseding ADR-004):
  **Bedrock Guardrails are excluded ecosystem-wide**, because an inline content filter adds
  latency that interactive, vibe-coding workflows can't absorb. Fix before this module is
  applied to a real account.

### veil-custodian

Holds the mapping between opaque device pseudonyms and real device/user identity, so
veil-observatory can key everything on a pseudonym and never touch identity itself.
Pseudonym resolution is a separate, explicit, authorised, audited act — the same
opaque-reference / access-controlled-store / explicit-resolution discipline veil-proxy already
applies to *content* (`MappingRef` → vault → `rehydrate`, gated by policy), applied here to
*identity* instead. Device attestation is decided as **mTLS device certificates**
(2026-07-26).

- **Status:** the resolution audit log is real and tested (hash-chained, append-only, 539
  lines, 15 tests). The `attestation/status` API contract is well-specified — it answers "is
  this pseudonym's cert valid," never "who is this," and veil-observatory's service identity is
  structurally denied any grant on the resolution API itself.
- **Gap:** the HTTP service — device schema, Postgres store, mTLS attestation handshake — is
  100% unbuilt. A well-designed contract with zero implementation and zero callers.

### veil-observatory

The correlation and assurance plane: ingests Bedrock/CloudTrail evidence, veil-proxy telemetry
receipts, and device-pseudonym attestation to surface residual PII exposure, missing controls,
and EU AI Act risk signals. Lives outside `~/Development/hekton` at
`~/Development/veil-observatory` — graduated to a standalone-external product location; see its
own `docs/decisions/ADR-0002-standalone-product-location.md`. Must run and be understood with
zero Hekton processes running (`ADR-0003-hekton-runtime-independence.md`) — Hekton is
build-time provenance/orchestration only, never a runtime dependency of the product itself.

- **Status:** the most complete component by test count — 491 tests, seven real detectors, a
  two-tier correlator, hash-chained local storage, a working evidence-pack CLI. Multiple
  adversarial review rounds have already found and fixed real defects (a re-identification join
  vulnerability, a severity/confidence inversion).
- **Gaps:** the receipt schema it ingests against is a draft guess worked from a research
  doc's example — never validated against veil-proxy's actual output, because veil-proxy
  doesn't emit one yet. Signature verification is a structural stub. Nothing calls
  veil-custodian anywhere; pseudonymisation today is done locally and independently instead.
  Everything has run against synthetic fixtures only — no real AWS deployment, no real evidence
  replay.

### veil-demo

Public interactive demo — paste text, watch PII get masked and demasked in real time against
the real `vg-core` engine (not a mock). The one component with a live, deployed URL.

- **Status:** live at [veil-demo.fly.dev](https://veil-demo.fly.dev/), two machines in `lhr`,
  scale-to-zero on idle. `/`, `/pitch`, and `/api/session` verified live. Terraform owns app
  existence, `fly deploy` owns releases.
- **Relationship to veil-proxy:** pulls `vg-core` in as a pinned git dependency — this is, as of
  2026-08-22, **the only one of the five designed cross-repo integrations that's actually
  wired and running.** See [Integration status](#integration-status) below.

## Data Flow and Trust Boundaries

The central design tension, and how it's resolved (full argument in
`veilgremlin/docs/architecture/product-family.md` §3): veil-proxy's existing claim is *"the
cloud model sees placeholders, not the values behind them"* — true, and about what the model
sees. But a fleet-wide observatory implies something leaves the laptop, which an older, stronger
claim ("PII never leaves the machine") doesn't survive. The resolution is to split what's
unconditional from what's opt-in:

**Never crosses the boundary, unconditionally — with or without veil-observatory deployed,
regardless of policy or role:**
- The SQLCipher vault itself: the database file, its encryption key, the OS-keychain wrap.
- Any raw detected value, in any form — plaintext, hashed-but-reversible, or otherwise.
- The full, unmasked request or response body, in whole or in part.

**Can cross the boundary, only if an organisation opts into veil-observatory:** masked
telemetry — entity-type counts, policy decisions and their version, opaque mapping references,
block reasons, demask request/decision records (actor id, destination, allow/deny — never the
resolved value), latency measurements, and a device pseudonym (never a hostname or username —
those are enterprise-sensitivity-class data under the project's own taxonomy, and shipping one
to an observatory would be a small version of the exact leak this product exists to prevent).

The intended enforcement mechanism is a purpose-built `TelemetryEvent` type in veil-proxy,
constructible only via a reviewed, exhaustive conversion from the existing local `AuditEvent` —
so the emitter's own type signature, not just test discipline, makes "sent something it was
never given a way to hold" the enforced invariant. **This type does not exist in code yet** —
it's the design target the next section's integration status measures against.

## Integration Status

Five cross-repo integrations are called for by the design. As of the 2026-08-22 ecosystem audit,
**one is real; four are designed-but-uncalled or entirely unbuilt.**

```mermaid
flowchart TB
    VP["veil-proxy<br/>laptop masking engine"]
    WG["veil-foundations<br/>AWS Bedrock control plane"]
    OBS["veil-observatory<br/>correlation & assurance"]
    CUST["veil-custodian<br/>pseudonym resolution"]
    DEMO["veil-demo<br/>public playground"]

    VP -. "signed receipt / telemetry: not emitted" .-> OBS
    WG -. "CloudTrail / Bedrock logs: not deployed" .-> OBS
    OBS -. "GET attestation/status: spec'd, zero callers" .-> CUST
    VP -. "POST /devices enrolment: designed, unbuilt" .-> CUST
    VP == "vg-core as pinned git dep: live" ==> DEMO
```

| Integration | Status |
|---|---|
| veil-proxy → veil-observatory (signed telemetry receipt) | **Missing.** No `TelemetryEvent` type exists; nothing is emitted. |
| veil-foundations → veil-observatory (CloudTrail / Bedrock logs) | **Missing.** No real AWS account has been touched. |
| veil-observatory → veil-custodian (`attestation/status` query) | **Designed, no caller.** Endpoint spec'd; nothing invokes it. |
| veil-proxy → veil-custodian (`POST /devices` enrolment) | **Designed, unbuilt.** |
| veil-proxy → veil-demo (`vg-core` as a pinned git dependency) | **Built and live.** The one real integration today. |

## Where the seams are

Ranked by how much downstream work is blocked on each one closing (from the 2026-08-22 audit):

1. **No wire format between veil-proxy and veil-observatory.** The producer emits nothing; the
   consumer's schema is an untested guess. This is the single blocker that makes every other
   integration moot.
2. **No cryptographic trust anywhere in the pipeline.** "Signed receipt" and "verified
   signature" are both stubs, on both ends. The assurance half of an assurance plane doesn't
   exist yet — today everything is trust-on-read.
3. **veil-custodian's API has zero callers.** The one place the ecosystem has a genuinely
   well-designed cross-repo contract, and nothing invokes it.
4. **veil-foundations produces none of the evidence veil-observatory assumes.** No sandbox AWS
   account has been touched; every finding so far is against synthetic fixtures.
5. **Demask authorisation is open ecosystem-wide.** Actor/role attribution is self-asserted,
   not authenticated, at the one point "invisible governance" could be silently bypassed.
6. **No document tied the five repos together — until this one.** Two plan docs elsewhere in
   the ecosystem were already named like ecosystem architecture ("aws-phase2," "entity-graph")
   and turned out to be about unrelated internals; that's an early symptom of the same gap.

## Sequencing to close them

A recommendation, open to redirect, carried over from the audit and consistent with the
dependency order in `veilgremlin/docs/architecture/product-family.md` §9:

1. ~~Ship veil-demo~~ — **done**, live at veil-demo.fly.dev.
2. **Freeze the receipt/telemetry contract.** Reconcile veil-proxy's draft `TelemetryEvent`
   proposal with veil-observatory's draft receipt schema into one schema both sides commit to.
   Everything else is downstream of this decision.
3. **Build the emitter, retire the fixtures.** Implement the frozen schema in veil-proxy;
   switch veil-observatory's ingestion off synthetic fixtures onto real receipts.
4. **Wire one real custodian call.** Even against a stub server, have veil-observatory call
   `attestation/status` for real — proves the "observatory never touches identity" boundary
   structurally, not just on paper.
5. **Stand up one sandbox AWS account.** Apply veil-foundations' one real module (after fixing
   the Guardrail defect above) against it, then extend to invocation logging.
6. **Decide signing last** — once the wire format is stable. Signing a schema that's still
   moving is wasted work.
7. ~~Write the missing architecture document~~ — **done: this document.** Keeping it current is
   now the open item; see below.

**Also unresolved and load-bearing for anything fleet-shaped:** real device/actor identity
(§6 of the product-family doc) is architected — opaque pseudonym minted at enrolment, held by
veil-custodian, mTLS-attested — but the cryptographic attestation mechanism's implementation,
MDM enrolment mechanics, and the still-open dashboard-repo-location question (does
`veil-dashboard` live inside veil-observatory, or get its own repo?) are all open. See
`veilgremlin/docs/architecture/product-family.md` §10 for the full list of open questions this
document doesn't re-litigate.

## Running the ecosystem today

See [setup.md](setup.md) for what's actually runnable per component, honestly scoped against
the integration status above — most components run standalone today; almost nothing runs
*together* yet, because the wiring between them (seam #1 above) doesn't exist.

## Keeping this current

This document is only as good as its next update. Whoever lands the changes in the sequencing
above should update the relevant sections here in the same PR — particularly
[Integration Status](#integration-status), which will go stale the moment any of the four
missing/designed-only integrations gets built. Record ecosystem-level decisions (not
single-repo ones — those belong in that repo's own `docs/decisions.md`) in
[decisions.md](decisions.md).
