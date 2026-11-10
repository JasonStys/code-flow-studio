# Code Flow Studio handbook

By Jason Stys.

Current source is 0.4.3, with the [exact C# target/collector exit correction](csharp-coverage.md)
and [its own validation report](reports/csharp-coverage-2026-11-10.md). This source
change does not replace published 0.4.2 packages or install anything on a user's PC.

Version [0.4.2 is published](https://github.com/JasonStys/code-flow-studio/releases/tag/v0.4.2).
Read its [release notes](releases/v0.4.2.md), the
[observed draft-verification CI correction](reports/draft-release-visibility-2026-11-10.md)
and the [realistic hosted compiler validation](compiler-execution.md).
The unchanged Word/Excel editions below
remain explicit historical snapshots of accepted runtime source
`7d2158a57bb49e8f837fffbfe23b301902465412`; they are not regenerated or relabeled as
0.4.2 acceptance. The 0.4.1 draft and its assets remain preserved and unpublished.

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

The reviewed source is [`7d2158a57bb49e8f837fffbfe23b301902465412`](https://github.com/JasonStys/code-flow-studio/tree/7d2158a57bb49e8f837fffbfe23b301902465412). The observed functional workflow baseline is `7d2158a57bb49e8f837fffbfe23b301902465412`; those observations are recorded at `2026-11-10T13:28:55.865054+00:00`. They do not certify an unrun later revision.

- [Detailed recorded validation](reports/native-http-drain-2026-11-10.md)
- [Current Actions](https://github.com/JasonStys/code-flow-studio/actions) records later integration checks separately.
- Preserve dated measurements and follow the existing testing guide to reproduce them; a test-source inventory alone does not establish execution.

## Practical boundaries

- Local account/vault plaintext is accessible to the trusted local service and device OS while unlocked; this is not browser-only end-to-end encryption or public SaaS authentication.
- Compiler tests require the fixed isolated local worker image. No host-code fallback, automatic Docker repair, universal coverage/bug detection or hostile-code security certification is provided.
- The five-second HTTP drain is not a universal exit-time guarantee: critical disk/container cleanup and vault sealing must finish safely; preserve recovery data on failure.
- Supported CodeQL categories, actual statement coverage, fixture browser journeys and tiny CPU training have distinct scopes. Passing checks do not establish model quality, vulnerability freedom or clean-machine installer acceptance.

## Maintaining these editions

Update the editable usage/design/test documents first. Rebuild and visually review every Word page and workbook tab before replacing an edition; verify the exact binary digests and evidence source in publications.json. Keep account data, logs with secrets, installed-app state and private test stores out of documentation. Source and release assets retain their existing security and licensing boundaries.
