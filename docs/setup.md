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
cargo build --release -p vg-cli
export PATH="$PWD/target/release:$PATH"
vg run -- claude "..."                        # wrap an agent with masking hooks
vg inspect <file>                              # preview what WOULD be masked
vg diff --masked <file>                        # masked rendering + stats, stores a reversible pack
vg demask --from pack.json --to local-patch    # reverse a stored pack into a local destination
vg audit                                       # most recent audit event by default (refs/counts only)
```

**Correction (2026-08-24, 3rd review cycle):** the previous version of this block —
`cargo build --release` immediately followed by `vg run`, with no `-p vg-cli` and no `PATH`
export — genuinely fails with "command not found." The binary lands at `target/release/vg` and
nothing puts it on PATH; veilgremlin's own `docs/runbook-hooks.md` gets this right and the
commands above now match it. Also: `--masked` is a required flag on `vg diff`, not optional as
earlier phrasing implied, and `vg audit` takes its target as a positional argument defaulting to
`last`, not a `last` subcommand.

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
runnable service" — false as of 2026-08-23: `src/main.rs` runs a real axum HTTP server with 8
routes (device enrolment/revocation, pseudonym resolution, `attestation/status`, mTLS
certificate renewal, CRL, health) against a real Postgres store. **`cargo test` as shown above
will report 15 failures and then stop — it never reaches all of the Postgres-backed tests**
(corrected 2026-08-24, 3rd review cycle: the true count is **19 failures across 3 test files**,
not 15 across 2 — `src/store/postgres.rs` has 11, `src/audit_log/postgres.rs` has 4, and a
separate integration-test binary, `tests/db_grants.rs`, has 4 more that prove a Postgres-level
INSERT-only grant on the resolution audit log; run `cargo test --no-fail-fast` to see all 19, or
just `cargo test --test db_grants` for that target alone). All require a live database via
`DATABASE_URL`. See that repo's `.env.example` for the expected shape; 62 non-Postgres tests
pass with no setup at all. **Nothing in the ecosystem calls its API yet** — the service is real,
but has zero external callers today. **This repo's own `docs/setup.md` doesn't mention
`DATABASE_URL` either** — worth noting it's not a more authoritative source than this section:
verified 2026-08-24, it's the same generic Hekton scaffold boilerplate
(`check-prereqs.sh`/`bootstrap-project.sh`/`verify-project.sh` + two `TODO` lines) as
veil-observatory's, not a legitimate reference this doc is merely summarising.

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

Per [architecture.md](architecture.md#sequencing-to-close-them), in order: a real network
emitter in veil-proxy (the telemetry schema itself was already reconciled and ratified
2026-08-23 — corrected 2026-08-24, 3rd review cycle; that's no longer the blocker), at least one
real veil-observatory→veil-custodian call, and one applied veil-foundations sandbox account.
None of that exists today — this section will move from "what would require" to "how to" once
the first of those lands.
