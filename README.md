# Veil Ecosystem

**Classification:** factory-output
**Lifecycle:** active
**Owner:** hekton
**Promotion target:** `none`

> Master architecture repo for the VeilGremlin product family: describes the trust boundaries, data flows, and integration seams across veil-proxy, veil-foundations, veil-custodian, veil-observatory, and veil-demo, and documents how to stand up each component today.

## Implementation Status

- Scaffolded 2026-08-24, architecture doc written same day. Documentation only — no code, no
  CI, nothing to deploy. See [docs/architecture.md](docs/architecture.md) for what's real across
  the family it describes.

## Documentation Contract

Agents working here must inspect `.hekton/project.yaml` before structural changes, keep `docs/session-log.md` current, record meaningful design decisions in `docs/decisions.md`, and update `docs/next-actions.md` when the work queue changes.

Vault mutation policy: see `vault_mutation_allowed` in `.hekton/project.yaml` (authoritative; defaults to false at scaffold time). The repo-local `mind-palace/` folder is only a mirror draft; do not write to the live vault unless `.hekton/project.yaml` says mutation is allowed and it is explicitly authorised in-session.

## The VeilGremlin family

| Component | Repo | Role |
|---|---|---|
| veil-proxy | [dermdunc/veilgremlin](https://github.com/dermdunc/veilgremlin) | Masking data plane (laptop) |
| veil-foundations | [dermdunc/veil-foundations](https://github.com/dermdunc/veil-foundations) | AWS Bedrock control plane (Terraform) |
| veil-custodian | [dermdunc/veil-custodian](https://github.com/dermdunc/veil-custodian) | Device-pseudonym-to-identity mapping custodian |
| veil-observatory | [dermdunc/veil-observatory](https://github.com/dermdunc/veil-observatory) | Correlation & assurance plane |
| veil-demo | [dermdunc/veil-demo](https://github.com/dermdunc/veil-demo) | Public interactive demo — [live](https://veil-demo.fly.dev/) |

See [docs/architecture.md](docs/architecture.md) for how they fit together, what's actually
wired today, and where the gaps are.

## Quick Start

```bash
# This repo is documentation, not a runnable service.
# For per-component setup, see docs/setup.md.
```

## Key Docs

- [Architecture](docs/architecture.md) — trust boundaries, integration status, seams, sequencing
- [Setup](docs/setup.md) — per-component run instructions, honestly scoped
- [Session Log](docs/session-log.md)
- [Decisions](docs/decisions.md)
- [Risks](docs/risks.md)
- [Project Walkthrough](docs/project-walkthrough.md)
- [Next Actions](docs/next-actions.md)
- [Operating Model](docs/operating-model.md)
- [Human Understanding Check](docs/human-understanding-check.md)
- [Depth Decision](docs/depth-decision.md)

