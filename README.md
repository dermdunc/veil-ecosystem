# Veil Ecosystem

**Classification:** factory-output
**Lifecycle:** active
**Owner:** hekton
**Promotion target:** `none`

> Master architecture repo for the VeilGremlin product family: describes the trust boundaries, data flows, and integration seams across veil-proxy, veil-foundations, veil-custodian, veil-observatory, and veil-demo, and documents how to stand up each component today.

## Implementation Status

- Scaffolded 2026-08-24 — initial setup in progress.

## Documentation Contract

Agents working here must inspect `.hekton/project.yaml` before structural changes, keep `docs/session-log.md` current, record meaningful design decisions in `docs/decisions.md`, and update `docs/next-actions.md` when the work queue changes.

Vault mutation policy: see `vault_mutation_allowed` in `.hekton/project.yaml` (authoritative; defaults to false at scaffold time). The repo-local `mind-palace/` folder is only a mirror draft; do not write to the live vault unless `.hekton/project.yaml` says mutation is allowed and it is explicitly authorised in-session.

## Quick Start

```bash
# Add project-specific commands here
```

## Key Docs

- [Interactive Ecosystem Plan](docs/interactive-plan.md)
- [Session Log](docs/session-log.md)
- [Decisions](docs/decisions.md)
- [Risks](docs/risks.md)
- [Project Walkthrough](docs/project-walkthrough.md)
- [Next Actions](docs/next-actions.md)
- [Operating Model](docs/operating-model.md)
- [Human Understanding Check](docs/human-understanding-check.md)
- [Depth Decision](docs/depth-decision.md)

