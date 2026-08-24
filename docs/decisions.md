# Decisions: Veil Ecosystem

## ADR Log

| Date | Decision | Rationale |
|---|---|---|
| 2026-08-24 | Initial scaffold as factory-output, privacy `public` (+ private sibling `veil-ecosystem-private`) | Master architecture repo for the VeilGremlin product family, following the same public/private-sibling split as veil-foundations. Sourced directly from a full ecosystem audit run 2026-08-22, which named "no document ties the five repos together" as its final open seam. |
| 2026-08-24 | `docs/architecture.md` written in this session, not deferred to a separate Fable design pass | Unlike dark-lab's greenfield architecture (which needed net-new design), this repo's job is synthesising design decisions and status that already exist and are well-documented across the five component repos' own decision logs and the audit — a synthesis task, not a novel design one. |
| 2026-08-24 | `docs/setup.md` documents per-component run instructions "as-is," explicitly not an aspirational docker-compose for the integrated end-state | Only 1 of 5 designed cross-repo integrations (veil-proxy → veil-demo) is actually wired as of the 2026-08-22 audit; an orchestration script implying a working integrated system would misrepresent that. |
