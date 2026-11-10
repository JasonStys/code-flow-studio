# Code Flow Studio handbook

By Jason Stys.

Filter diagnostics, unused-code candidates and missed coverage; inspect hash-verified source and navigate safely to unchanged drafts. Fixed rapid typing, worker compatibility and native launch preparation.

Turns report findings into a reproducible developer triage workflow while preserving source identity and isolated execution.

## Read the documentation

| Edition                                                      | Audience and contents                                                                                              |
| ------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------ |
| [project-guide.docx](reports/project-guide.docx)             | User and developer guide: purpose, current usage, design, boundaries and source references.                        |
| [validation-review.docx](reports/validation-review.docx)     | Reviewer edition: exact tested baseline, observed workflows, dated local results and remaining limits.             |
| [validation-evidence.xlsx](reports/validation-evidence.xlsx) | Two filterable Excel Tables for observed workflows and test-source inventory, with recalculating outcome formulas. |

The editable Markdown remains the maintenance source. The Word files are readable editions, and the workbook is an evidence index rather than a test runner. See [publication identities and review](reports/publications.json) and the [documentation refresh record](reports/documentation-refresh-2026-11-09.md).

## Current usage and help

[README quick start](../README.md) is the entry point. Use the project-specific guides below before changing inputs, operating modes or deployment assumptions.

### Usage and operations

- [release checklist v0.2](release-checklist-v0.2.md)
- [releases/v0.2.0](releases/v0.2.0.md)
- [releases/v0.2.1](releases/v0.2.1.md)
- [releases/v0.3.0](releases/v0.3.0.md)
- [releases/v0.4.0](releases/v0.4.0.md)
- [releases/v0.4.1](releases/v0.4.1.md)

### Design and contracts

- [adr polyglot evidence](adr-polyglot-evidence.md)
- [adr private local](adr-private-local.md)
- [architecture](architecture.md)
- [private api](private-api.md)
- [research](research.md)

### Security and validation

- [security](security.md)
- [test plan v0.2](test-plan-v0.2.md)
- [testing](testing.md)
- [validation locations](validation-locations.md)
- [validation polyglot](validation-polyglot.md)
- [validation v0.2](validation-v0.2.md)
- [validation](validation.md)

## Historical results and reproduction

The reviewed source is [`eeac1df6275437f401a8c060b7770c138dbaf132`](https://github.com/JasonStys/code-flow-studio/tree/eeac1df6275437f401a8c060b7770c138dbaf132). The observed functional workflow baseline is `eeac1df6275437f401a8c060b7770c138dbaf132`; those observations are recorded at `2026-11-10T09:40:54.286353+00:00`. They do not certify an unrun later revision.

- [Detailed recorded validation](reports/native-registration-completion-2026-11-10.md)
- [Current Actions](https://github.com/JasonStys/code-flow-studio/actions) records later integration checks separately.
- Preserve dated measurements and follow the existing testing guide to reproduce them; a test-source inventory alone does not establish execution.

## Practical boundaries

- Twelve bounded flat CLI adapters do not cover every framework, dependency or architecture; coverage and unused-code candidates are not correctness or dead-code proof.
- Execution needs a separately built local Docker worker with no host fallback. Shared worker identity and containers are not a certified public hostile-code sandbox.
- Hashes bind retained bytes and locations, not trusted attestation by a malicious target. UI-only report fixtures are separate from native collector evidence.
- Local accounts trust the OS and unlocked service. Downloads are unsigned development builds; no native mobile installer or clean-machine installer lifecycle certification is claimed.

## Maintaining these editions

Update the editable usage/design/test documents first. Rebuild and visually review every Word page and workbook tab before replacing an edition; verify the exact binary digests and evidence source in publications.json. Keep account data, logs with secrets, installed-app state and private test stores out of documentation. Source and release assets retain their existing security and licensing boundaries.
