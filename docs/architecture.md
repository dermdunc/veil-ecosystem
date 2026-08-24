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

The only component that's fully built and running today: 381 tests across 10 crates (verified
2026-08-24 — an earlier draft of this doc said 270, carried over from a stale audit; see
[Keeping this current](#keeping-this-current)), a real `vg` CLI (`vg run`, `vg inspect`,
`vg diff --masked`, `vg demask`, `vg audit`), detectors, policy engine, and a SQLCipher vault.
Runs entirely on the developer's laptop with no network dependency in its hot path.

- **Owns:** parse → detect → mask → vault → policy → masked pack, plus local demask.
- **Explicitly does not:** decide fleet-wide policy, aggregate telemetry across machines,
  authenticate its own actor (`--actor`/`--role` are self-asserted, not authenticated), or gate
  *whether* a Bedrock call is allowed at all (that's veil-foundations — veil-proxy only
  minimises *what's in* a call it's already permitted to make).
- **Gaps:** no cryptographic signing anywhere in the pipeline — the audit log is
  tamper-evident, not tamper-proof, and the policy-pack "signature" field is a hardcoded
  placeholder that always verifies. **Correction (2026-08-24):** a real `TelemetryEvent` type
  now exists — `crates/vg-core/src/telemetry/mod.rs`, a tested, `#[non_exhaustive]` enum with
  `Receipt`/`Alert`/`EdgeEvent` variants, landed 2026-08-23/24. What's still genuinely missing
  is the network emitter: the module's own doc comment states it provides "the payload types
  themselves — not a working emitter, which is separate, larger... work." So nothing is sent
  to veil-observatory yet, but the reason is "no sender," not "no type."

### veil-foundations

Terraform for Amazon Bedrock as a governed invocation control plane: IAM model allowlists,
invocation logging, VPC endpoints, cost attribution. Composes with veil-proxy as **defence in
depth** — veil-proxy minimises *what* goes out, veil-foundations constrains *whether it can go
out at all, and to which model*. A leak requires both a masking failure and an
invocation-authority failure; deployed alone, each is weaker in a specific, nameable way (see
`veilgremlin/docs/architecture/product-family.md` §2 for the full argument).

- **Status:** one real module (`iam-model-allowlist`, an Allow-only IAM policy) passes
  `fmt`/`validate`/`test` against a mock provider. Nothing has run against a real AWS account.
- **Correction (2026-08-24):** an earlier draft of this doc claimed the module makes a Bedrock
  Guardrail mandatory per invocation, contradicting the family's decided no-Guardrails policy
  (ADR-0001 in veil-observatory, ADR-010 in veil-foundations, superseding ADR-004). That was
  true of an *older* version of this module — **ADR-010 already fixed it, on 2026-08-23**,
  before this doc's own "as of 2026-08-24" claim, which is exactly the kind of drift this doc
  exists to catch and instead briefly reproduced. `main.tf` now reads, verbatim: *"Allow only,
  scoped to the entry's authorized resources, no guardrail condition of any kind."* There is no
  outstanding defect here. The no-Guardrails policy itself is real and correctly described.

### veil-custodian

Holds the mapping between opaque device pseudonyms and real device/user identity, so
veil-observatory can key everything on a pseudonym and never touch identity itself.
Pseudonym resolution is a separate, explicit, authorised, audited act — the same
opaque-reference / access-controlled-store / explicit-resolution discipline veil-proxy already
applies to *content* (`MappingRef` → vault → `rehydrate`, gated by policy), applied here to
*identity* instead. Device attestation is decided as **mTLS device certificates**
(2026-07-26).

- **Status (corrected 2026-08-24):** an earlier draft of this doc said the HTTP service was
  "100% unbuilt." That was true of the 2026-08-22 audit this doc was sourced from and stopped
  being true the next day: **a real service landed 2026-08-23** — `src/main.rs` binds a TCP
  listener and runs `axum::serve` against a real Postgres pool; `src/api/mod.rs` wires 8 routes
  to real handlers: `POST /v1/devices` (enrolment), `POST /v1/devices/{pseudonym}/revoke`,
  **`POST`+`GET /v1/resolutions`** (the actual pseudonym-resolution operation — see below),
  `GET /v1/attestation/status`, certificate renewal, CRL, and two health endpoints. (An earlier
  draft of this correction said "7 routes... cert issuance/renewal" — undercounted by one and
  wrong about renewal being a pair; certificate *issuance* happens as a byproduct of enrolment,
  not a separate route, and `/v1/resolutions` was dropped entirely despite being the component's
  headline operation.) `src/ca/mod.rs` implements mTLS CSR issuance (426 lines). The resolution
  audit log (`src/audit_log/mod.rs`, 745 lines, hash-chained, append-only, plus a Postgres-backed
  variant in `src/audit_log/postgres.rs`) is real and tested — `attestation/status` answers "is
  this pseudonym's cert valid," never "who is this," and veil-observatory's service identity is
  structurally denied any grant on the resolution API itself.
- **Gap:** the service exists but has **zero callers** — nothing in veil-proxy or
  veil-observatory invokes it yet, including `/v1/resolutions` itself (see
  [Integration Status](#integration-status), which now lists it explicitly). Its Postgres-backed
  tests (15 of them, in `src/store/postgres.rs` and `src/audit_log/postgres.rs`) require a live
  database via `DATABASE_URL`, not documented in this repo's own `docs/setup.md` — see
  [setup.md](setup.md) here for the caveat.

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
  2026-08-24, **the only one of the five designed cross-repo integrations that's actually
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

The enforcement mechanism is a purpose-built `TelemetryEvent` type in veil-proxy — it exists
today (`crates/vg-core/src/telemetry/mod.rs`, landed 2026-08-23/24). **Correction (2026-08-24,
2nd review cycle):** an earlier draft of this section overstated the construction guarantee as
"constructible only via a reviewed, exhaustive conversion from `AuditEvent`" — the type's own
doc comment is more careful than that: it also exposes `pub(crate)` direct constructors
(`new_receipt`/`new_alert`/`new_edge_event`) for code that already holds a valid `Envelope` +
payload pair, bypassing the `AuditEvent` conversion. The module's comment calls the
conversion-based path the "sole intended construction path **in practice**," not one Rust's
type system actually forecloses — a real, acknowledged limit, not a design flaw introduced by
this doc's earlier overclaim. **What doesn't exist yet is the emitter itself** — the code that
takes a `TelemetryEvent` and actually sends it over the network to veil-observatory. Nothing is
transmitted yet, regardless of construction path.

## Integration Status

Five cross-repo integrations are called for by the design (per the 2026-08-22 audit's own named
list). As of 2026-08-24 (re-verified against the actual repos — see
[Keeping this current](#keeping-this-current)), **one is real; four are still designed-but-
uncalled or missing** — but two of the "unbuilt" callees have grown real implementations since
the audit, so "no caller yet" is now the more accurate frame than "unbuilt" for those two.

**Not on the original list, but worth naming:** veil-custodian's real API surface is broader
than the two calls above — it also exposes `/v1/resolutions` (the actual pseudonym-resolution
operation) and device revocation, neither of which any other repo calls either. A second review
cycle on 2026-08-24 found the first correction's route description had silently dropped
`/v1/resolutions`, the component's own headline operation — corrected in the component section
above.

```mermaid
flowchart TB
    VP["veil-proxy<br/>laptop masking engine"]
    WG["veil-foundations<br/>AWS Bedrock control plane"]
    OBS["veil-observatory<br/>correlation & assurance"]
    CUST["veil-custodian<br/>pseudonym resolution"]
    DEMO["veil-demo<br/>public playground"]

    VP -. "signed receipt / telemetry: type exists, no emitter" .-> OBS
    WG -. "CloudTrail / Bedrock logs: not deployed" .-> OBS
    OBS -. "GET attestation/status: built, zero callers" .-> CUST
    VP -. "POST /devices enrolment: built, zero callers" .-> CUST
    VP == "vg-core as pinned git dep: live" ==> DEMO
```

| Integration | Status |
|---|---|
| veil-proxy → veil-observatory (signed telemetry receipt) | **Missing.** `TelemetryEvent` type exists and is tested; no network emitter exists, so nothing is sent. |
| veil-foundations → veil-observatory (CloudTrail / Bedrock logs) | **Missing.** No real AWS account has been touched. |
| veil-observatory → veil-custodian (`attestation/status` query) | **Callee built, no caller.** The endpoint is live in veil-custodian (real axum route, real handler); nothing in veil-observatory invokes it yet. |
| veil-proxy → veil-custodian (`POST /devices` enrolment) | **Callee built, no caller.** The endpoint is live in veil-custodian; nothing in veil-proxy invokes it yet. |
| veil-proxy → veil-demo (`vg-core` as a pinned git dependency) | **Built and live.** The one real integration today. |

## Where the seams are

Ranked by how much downstream work is blocked on each one closing (from the 2026-08-22 audit,
reconciled against live repo state 2026-08-24):

1. **No wire format between veil-proxy and veil-observatory.** The producer has a real,
   type-safe payload (`TelemetryEvent`) but no emitter to send it; the consumer's schema is
   still an untested guess. This is the single blocker that makes every other integration moot.
2. **No cryptographic trust anywhere in the pipeline.** "Signed receipt" and "verified
   signature" are both stubs, on both ends. The assurance half of an assurance plane doesn't
   exist yet — today everything is trust-on-read.
3. **veil-custodian's API has zero callers, despite the API itself now being real.** As of
   2026-08-23 this is no longer "a contract with no implementation" — it's a running service
   nobody calls. That's a smaller gap than it was, but still a gap: neither veil-proxy's device
   enrolment nor veil-observatory's attestation check actually happens.
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
2. **Freeze the receipt/telemetry contract.** veil-proxy's `TelemetryEvent` type is now real
   (2026-08-23/24); reconcile it with veil-observatory's still-draft receipt schema into one
   schema both sides commit to. Everything else is downstream of this decision.
3. **Build the emitter, retire the fixtures.** The type exists — build the network sender in
   veil-proxy that actually transmits a `TelemetryEvent`; switch veil-observatory's ingestion
   off synthetic fixtures onto real receipts.
4. **Wire one real custodian call.** veil-custodian's `attestation/status` endpoint is a real,
   running service as of 2026-08-23 — have veil-observatory call it for real. This proves the
   "observatory never touches identity" boundary structurally, not just on paper.
5. **Stand up one sandbox AWS account.** Apply veil-foundations' one real module against it,
   then extend to invocation logging. (The Guardrail-mandatory defect an earlier draft of this
   doc flagged here was already fixed via ADR-010 on 2026-08-23 — nothing left to fix before
   this step.)
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

**This document was itself stale on the day it was written, and that's the lesson to carry
forward, not just a footnote.** The first draft (2026-08-24) was synthesised from a 2026-08-22
audit and never independently re-checked against the component repos before publishing. A
doubt-driven-development review cycle the same day caught three load-bearing errors this
caused — a defect claimed against veil-foundations that ADR-010 had already fixed the day
before, a veil-custodian service claimed unbuilt that had already shipped, and a veil-proxy
`TelemetryEvent` type claimed nonexistent that already existed — all from real commits that
landed in the two days between the audit and this doc. See `docs/decisions.md` for the full
record of what was wrong and how it was corrected.

The takeaway: **synthesising from a point-in-time audit is not the same as verifying against
current repo state, even a few days later, in a fast-moving family of repos.** Whoever lands
changes in the sequencing above should update the relevant sections here in the same PR — and
should verify against the actual repo, not against this document's own prior claims — starting
with [Integration Status](#integration-status), the section most likely to go stale next.
