# Documentation refresh — 2026-11-09

By Jason Stys.

This documentation-only edition describes source `eeac1df6275437f401a8c060b7770c138dbaf132`. It does not change application behavior, accounts, private data, installers or published releases.

## Published editions and completed review

| File                                                 | Bytes | SHA-256                                                            | Reviewed scope                                                                                                                      |
| ---------------------------------------------------- | ----: | ------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------- |
| [project-guide.docx](project-guide.docx)             | 45782 | `50920e113b79dd071f6f1e927d656bfc63d46e1bf98239374de634be2176bfd9` | 6 pages, each viewed individually                                                                                                   |
| [validation-review.docx](validation-review.docx)     | 48485 | `c94e4fc9b6a56c25baabd7160a5f0414015459107e14ea8c905cdf4c5b9a00ce` | 7 pages, each viewed individually                                                                                                   |
| [validation-evidence.xlsx](validation-evidence.xlsx) |  7695 | `12ed9f288f77f4a930115126fdc1b9140b8680da2c0c67d46ff1fc184ee83f8c` | Both tab previews; two actual Excel Tables/autoFilters; four formulas; failure-change/restore recalculation and zero formula errors |

Word review checked plain black titles, readable pagination, whole table rows, source references, practical limits and absence of clipping or overflow. Render receipts were matched to the current DOCX digest before approval. Workbook review inspected both tab previews and actual exported Table/autoFilter elements; recalculated success/failure summaries were compared independently with workflow metadata. Static previews do not draw Excel dropdown arrows; the exported workbook contains the actual filters.

## Evidence and change boundary

- Functional baseline: `eeac1df6275437f401a8c060b7770c138dbaf132`.
- Workflow observation: `2026-11-10T09:40:54.286353+00:00`; exact run URLs and source identities remain in [publications.json](publications.json).
- Local document-package validation verifies exact copied bytes, Office ZIP integrity, approved page/tab identities and internal documentation links. Repository-specific documentation and source-policy commands are run separately and recorded in the integration handoff.
- Source/index metadata is regenerated using the repository’s existing tools. Existing privacy, security, coverage and workflow gates are retained.
- PR and later main workflows must pass independently. This record does not claim future or unrun integration CI success.

## Interpretation

The Word files document the cited source; dated source reports retain their original execution scope. A passing workflow is distinct from completed analysis with zero findings, and neither establishes production suitability. The Excel source inventory is not a per-test execution report. Checksums identify exact bytes, not a signature or publisher attestation.

Use the [handbook](../handbook.md) to choose usage, design, security and test documentation. Keep editable Markdown and reviewed editions together; do not replace historical measurements with undated claims.

## Local integration checks and future CI

The complete original controller/training gate passed 261 tests and 28 subtests,
covering 1,462/1,734 measured statements (84.31%, unchanged 80% floor). This adds
nine actual publication cases: exact source-bound reviewed packages, binary tamper,
closed filenames, real macro/ActiveX/embedding ZIP members, missing Word root,
removed Excel autoFilter and changed real formula. Tampered structural fixtures
recompute their archive digest so the structural rejection is exercised independently.
The checks do not execute Office or substitute metadata for the independent visual review.

XML parsing uses explicitly pinned development-only
[defusedxml 0.7.1](https://pypi.org/project/defusedxml/0.7.1/) with DTDs forbidden;
the [upstream facade](https://github.com/tiran/defusedxml/blob/main/defusedxml/ElementTree.py)
provides entity/external-reference protection. That exact version was already present
in this isolated test environment. No application runtime dependency or account/schema
migration is introduced. ZIP member/expansion budgets, active-member rejection and
actual Table/formula/cache inspection remain independent checks.

Ruff, 82 exact source maps, strict TypeScript/Vite production build, approved-byte/ZIP/
source/workflow/link validation and diff hygiene passed. The existing pytest-cache
and large UI-chunk warnings remain visible. These local checks are separate from
the cited eeac full-main observation. The meaningful test-file change triggers the
existing Desktop packages workflow alongside Validate and CodeQL; fresh PR and final
main results must pass before any new draft/download promotion. No runtime, store,
installed application, existing release asset or user account was changed here.
