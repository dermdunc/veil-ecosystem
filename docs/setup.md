# Setup

This repo is documentation, not a runnable service — there is nothing to `bootstrap-project.sh`
here beyond the standard Hekton scaffold checks. What follows is an honest, per-component guide
to what's actually runnable today across the VeilGremlin family, as of 2026-08-24. See
[architecture.md](architecture.md#integration-status) for why "run them together" mostly isn't
possible yet: only one of the five designed cross-repo integrations is actually wired.

```text
documented -> scripted -> idempotent-ish -> logged -> reproducible on a blank machine
```

```bash
./scripts/check-prereqs.sh
./scripts/bootstrap-project.sh --dry-run
./scripts/bootstrap-project.sh
./scripts/verify-project.sh
```

## Per-component status

### veil-proxy — runnable standalone today

```bash
git clone git@github.com:dermdunc/veilgremlin.git
cd veilgremlin
cargo build --release
vg run -- claude "..."                        # wrap an agent with masking hooks
vg inspect <file>                              # preview what WOULD be masked
vg diff --masked <file>                        # masked rendering + stats, stores a reversible pack
vg demask --from pack.json --to local-patch    # reverse a stored pack into a local destination
vg audit last                                  # most recent audit event (refs/counts only)
```

Fully functional, no network dependency in the hot path, no other component required.

### veil-demo — runnable standalone today, live deployment exists

```bash
git clone git@github.com:dermdunc/veil-demo.git
cd veil-demo
cargo run
# open http://127.0.0.1:7878
cargo test    # integration tests, hit the real vg-core engine end-to-end
```

Or just visit [veil-demo.fly.dev](https://veil-demo.fly.dev/) — already live. Co-developing
against a local veil-proxy checkout: copy `.cargo/config.toml.example` to `.cargo/config.toml`
(gitignored) in veil-demo to patch the git dependency back to your local `veilgremlin` path —
see that repo's `docs/decisions.md`.

### veil-observatory — runnable standalone, but with nothing real to ingest yet

```bash
git clone git@github.com:dermdunc/veil-observatory.git
cd veil-observatory
```

Has a real CLI and evidence-pack generator exercised by 491 tests — see that repo's own
`docs/setup.md` for exact commands, not duplicated here since they weren't independently
re-verified while writing this doc. **What it cannot do yet:** ingest a real veil-proxy
telemetry receipt (none is emitted) or a real veil-foundations CloudTrail/Bedrock log (none is
deployed) — every finding it produces today is against synthetic fixtures.

### veil-custodian — library only, no runnable service

```bash
git clone git@github.com:dermdunc/veil-custodian.git
cd veil-custodian
cargo test    # 15 tests against the hash-chained resolution audit log
```

The `attestation/status` HTTP API is specified but not implemented — there is no server to
start yet. Nothing in the ecosystem calls it today.

### veil-foundations — one Terraform module, validated against a mock provider only

```bash
git clone git@github.com:dermdunc/veil-foundations.git
cd veil-foundations
terraform -chdir=modules/iam-model-allowlist fmt -check
terraform -chdir=modules/iam-model-allowlist validate
terraform -chdir=modules/iam-model-allowlist test
```

**Do not `terraform apply` against a real AWS account yet** — the module as written makes a
Bedrock Guardrail mandatory per invocation, which contradicts the ecosystem's decided
no-Guardrails policy (ADR-0001 / ADR-010). Fix that first.

## What "running the ecosystem together" would require

Per [architecture.md](architecture.md#sequencing-to-close-them), in order: a frozen
veil-proxy↔veil-observatory telemetry schema, a real emitter in veil-proxy, at least one real
veil-observatory→veil-custodian call, and one applied veil-foundations sandbox account. None of
that exists today — this section will move from "what would require" to "how to" once the first
of those lands.
