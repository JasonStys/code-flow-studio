# Located-diagnostics validation — 2026-10-21

By Jason Stys. This report supplements, rather than rewrites, [historical account validation](validation-v0.2.md). Scope and caveats are in [located diagnostics](located-diagnostics.md).

## Local measurements

- Final local Windows run: **120 Python tests passed**, **84.55% statement coverage** in `studio` and `training.dataset`; the existing >=80% gate is retained. JSON coverage and JUnit evidence are generated privately under ignored `artifacts/`.
- **Five Chromium browser tests and two private-account journeys passed**, including the real auxiliary-file static-review upload, UI-only coverage rendering/escaping, mobile layout, lock/reopen and account isolation. Firefox/WebKit acceptance remains a separate CI gate.
- Python and npm audits report **zero known dependency vulnerabilities** after pinning certifi 2026.10.19 and Vite 8.3.5; `pip check` passed. The local application is not on PyPI and is not a third-party audited package.
- Ruff and TypeScript/Vite production build passed. Vite retains its expected offline-Monaco large-chunk warning, not a failed build.
- Local source inspections and function-contract tests never execute uploaded target programs. The temporary-folder sandbox issue found during initial verification was resolved by using a dedicated ignored test-data root, not by changing application behavior or suppressing tests.
- Docker Desktop remains unchanged by owner instruction; real compiler/coverage acceptance is performed by GitHub-hosted isolated workers, not claimed from mocks.

## Publication gates

Native-package and GitHub Actions results are pending until the implementation is published and validated remotely. Do not interpret this section as a passing remote run. The final update will link exact source/run evidence. A 0.2.1 release is gated on successful validation and three-OS package checks for its exact source commit; older releases are not overwritten.

## Storage and data safety

Initial fresh read: **61,385,326 artifact bytes** across the account; separate caches **13,254,452,931 bytes**. Quota percentage unavailable. Artifact uploads remain governed by the existing opt-in repository variable; no retention, deletion or cleanup was authorized or performed. Account data, API keys and local test traces are not committed.

## Rollback and remaining limits

No database migration is required; old history remains readable with explicit legacy-location notices. Roll back the source/app version if account lock/reopen, source hashes, export escaping or exact-location regressions fail. Rebuild the corresponding trusted worker when changing compiler/coverage behavior. Do not rewrite past measurement reports to pretend they contain new location evidence. Unsigned packages, local-only accounts, Python-only built-in coverage/unused checks, dynamic-code ambiguity and same-worker interference limitations remain explicit.
