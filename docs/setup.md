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

**Correction (2026-08-24):** this repo's own `docs/setup.md` is not actually a source of real
commands — verified directly, it's the generic Hekton scaffold boilerplate
(`check-prereqs.sh`/`bootstrap-project.sh`/`verify-project.sh`) plus two literal `TODO` lines
under "Project-Specific Steps." An earlier draft of this doc pointed there as if it had
concrete instructions; it doesn't. Has a real CLI and evidence-pack generator exercised by 491
tests (confirmed), but the actual invocation commands weren't independently re-derived for this
doc — check that repo's source/tests directly, or ask there for a `docs/setup.md` fix. **What
it cannot do yet:** ingest a real veil-proxy telemetry receipt (none is emitted) or a real
veil-foundations CloudTrail/Bedrock log (none is deployed) — every finding it produces today is
against synthetic fixtures.

### veil-custodian — real service, but its own setup.md omits a required step

```bash
git clone git@github.com:dermdunc/veil-custodian.git
cd veil-custodian
cargo test
```

**Correction (2026-08-24):** an earlier draft of this doc called this "library only, no
runnable service" — false as of 2026-08-23: `src/main.rs` runs a real axum HTTP server with 7
routes (device enrolment, `attestation/status`, mTLS certificate issuance/renewal, CRL, health)
against a real Postgres store. `cargo test` as shown above **will report 15 failures** —
confirmed by actually running it — because the Postgres-backed tests in `src/store/postgres.rs`
and `src/audit_log/postgres.rs` require a live database via `DATABASE_URL`, which this repo's
own setup docs don't mention either. See that repo's `.env.example` for the expected shape; 62
non-Postgres tests pass with no setup at all. **Nothing in the ecosystem calls its API yet** —
the service is real, but has zero external callers today.

### veil-foundations — one Terraform module, validated against a mock provider only

```bash
git clone git@github.com:dermdunc/veil-foundations.git
cd veil-foundations
terraform -chdir=modules/iam-model-allowlist init
terraform -chdir=modules/iam-model-allowlist fmt -check
terraform -chdir=modules/iam-model-allowlist validate
terraform -chdir=modules/iam-model-allowlist test
```

**Correction (2026-08-24):** an earlier draft of this doc omitted the `init` step above and
claimed the module makes a Bedrock Guardrail mandatory per invocation. Neither is currently
true: `.terraform/` is gitignored, so a fresh clone needs `init` before `validate` will find its
provider (confirmed by checking `.gitignore` and simulating a fresh clone); and the
Guardrail-mandatory design was removed via ADR-010 on 2026-08-23 — `main.tf` now explicitly
states "no guardrail condition of any kind." Terraform apply against a real AWS account is
still untested, but there is no known defect blocking it.

## What "running the ecosystem together" would require

Per [architecture.md](architecture.md#sequencing-to-close-them), in order: a frozen
veil-proxy↔veil-observatory telemetry schema, a real emitter in veil-proxy, at least one real
veil-observatory→veil-custodian call, and one applied veil-foundations sandbox account. None of
that exists today — this section will move from "what would require" to "how to" once the first
of those lands.
