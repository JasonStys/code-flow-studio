# Documentation refresh — 2026-11-09

By Jason Stys.

This documentation-only edition describes source `7d2158a57bb49e8f837fffbfe23b301902465412`. It does not change application behavior, accounts, private data, installers or published releases.

## Published editions and completed review

| File                                                 | Bytes | SHA-256                                                            | Reviewed scope                                                                                                  |
| ---------------------------------------------------- | ----: | ------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------- |
| [project-guide.docx](project-guide.docx)             | 46007 | `4d0a998f70fb0d798a6a76e3739af62f54c73c4d147bc9ddbdf1f5f3bac0d039` | 6 pages, each individually viewed at original resolution                                                        |
| [validation-review.docx](validation-review.docx)     | 47230 | `3e472c90824be2501e0acdc7aff2ea6750ca9f4f0109804d0ff97e74020ee973` | 6 pages, each individually viewed at original resolution                                                        |
| [validation-evidence.xlsx](validation-evidence.xlsx) |  7760 | `0a9b5f1e6239dcb400bf195887461fcc967eec545633d1ebf3280d3353356c71` | Both previews; two actual Tables/autoFilters, four formulas, 3/3/0/0 values and failure-toggle/restore verified |

Word review checked plain black titles, readable pagination, whole table rows, source references, practical limits and absence of clipping or overflow. Render receipts were matched to the current DOCX digest before approval. Workbook review inspected both tab previews and actual exported Table/autoFilter elements; recalculated success/failure summaries were compared independently with workflow metadata. Static previews do not draw Excel dropdown arrows; the exported workbook contains the actual filters.

## Evidence and change boundary

- Functional baseline: `7d2158a57bb49e8f837fffbfe23b301902465412`.
- Workflow observation: `2026-11-10T13:28:55.865054+00:00`; exact run URLs and source identities remain in [publications.json](publications.json).
- Local document-package validation verifies exact copied bytes, Office ZIP integrity, approved page/tab identities and internal documentation links. Repository-specific documentation and source-policy commands are run separately and recorded in the integration handoff.
- Source/index metadata is regenerated using the repository’s existing tools. Existing privacy, security, coverage and workflow gates are retained.
- PR and later main workflows must pass independently. This record does not claim future or unrun integration CI success.

## Interpretation

The Word files document the cited source; dated source reports retain their original execution scope. A passing workflow is distinct from completed analysis with zero findings, and neither establishes production suitability. The Excel source inventory is not a per-test execution report. Checksums identify exact bytes, not a signature or publisher attestation.

Use the [handbook](../handbook.md) to choose usage, design, security and test documentation. Keep editable Markdown and reviewed editions together; do not replace historical measurements with undated claims.

## Local integration checks and future CI

The runtime baseline above passed its full main workflows, actual full supported-language
CodeQL analysis and three-OS native acceptance. Final local documentation integration
passed 275 tests and 28 subtests in 48.49 seconds, measuring 1,539/1,808 controller/data
statements (85.12%, unchanged 80% floor). The ten publication cases include real
package tamper, closed filenames, macro/ActiveX/embedding rejection, missing Word
root, changed Excel filters/formulas and understated compressed XML sizes.

Actual XML inflation is bounded to an eight-MiB read plus one sentinel byte before
checking actual/declared length. The genuine zlib oracle rejects the former
unbounded reader before a large output request; later CRC rejection alone is not
a memory-bound proof. Development-only defusedxml 0.7.1 forbids DTDs, with no new
application runtime dependency, account schema or migration.

Ruff, 87 exact source maps, strict TypeScript/Vite production build, approved-byte/
ZIP/source/workflow/link validation and diff hygiene passed. The existing pytest
cache and large UI-chunk warnings remain visible. All twelve current Word pages
and both workbook previews were independently viewed at original resolution;
saved OOXML contains the two actual Tables/autoFilters, all 27 source-bound test
paths and four formulas with 3/3/0/0 cached results. The matching failure-change/
restore receipt was checked; native Excel recalculation is not claimed.

These are local integration observations. Fresh PR and final main workflows and
later draft/download/installer acceptance remain separate required gates. Existing
0.4.0 public assets, installed user apps and account stores are unchanged.
