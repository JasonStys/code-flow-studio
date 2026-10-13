# Code Flow Studio 0.2 validation

Observed October 12, 2026 (America/Los_Angeles). Released runtime source: `b18265c24dd76ff3b80742883075ac97ef51687c`. Published [version 0.2.0](https://github.com/JasonStys/code-flow-studio/releases/tag/v0.2.0) retains that exact runtime. Main additionally includes four regression cases and a packaging-only correction for GitHub's space-to-dot download filenames; released binary bytes are unchanged.

| Layer | Measured results |
|---|---|
| Windows Python 3.14.6 / pytest 9.0.3 | **87 tests passed** (83 controller/account/crypto/engine/provider/data cases plus four checksum metadata cases). **83.01% statement coverage**: 1,513 statements, 257 missed, across all `studio` and `training.dataset`; the >=80% gate is retained. CLI launchers are covered by process/native integration, not this unit denominator. |
| Release-source Linux Python 3.12 | **83 tests passed**, **82.75% coverage**, [Validate 38348198782](https://github.com/JasonStys/code-flow-studio/actions/runs/38348198782). OS-specific branches change coverage slightly; optional training runtime and worker code are outside this denominator. |
| Browser tests in Linux CI | **15 passed**: nine legacy checks and six private-account journeys in Chromium, Firefox and WebKit. Actual registration, WebCrypto key proof, separate empty accounts, encrypted downloads, lock/reopen/history, static review, consent, catalog and 390px layout/help. Not physical-device testing. |
| Real isolated workers | **24 positive/expected-negative compiler, fuzz, instrumentation and isolation scenarios**; additionally **12 actual private-account compiler/oracle jobs**, one per adapter, followed by encrypted-history lock/reopen. No host fallback. |
| Training/inference | Genuine small causal-model training and authenticated local API smoke passed in CI. Synthetic rights-owned tiny data proves mechanics, not useful coding ability or live provider quality. |
| Three-OS packaging | [Desktop packages 38348198793](https://github.com/JasonStys/code-flow-studio/actions/runs/38348198793): Windows x64, Linux x64 and macOS ARM64 all passed real bundled-service and actual packaged-executable journeys. |
| Native publication | [Release 38348634760](https://github.com/JasonStys/code-flow-studio/actions/runs/38348634760): prepare, all three build/test jobs and publish passed. Installers, portable archives, license notices and six SHA-256 records are published in Releases, not Actions artifacts. |
| Actual downloaded Windows package | Public ZIP SHA-256 `9e865286e261064defe49a4e112e24c1228ff85e26b50714f3614ffba5010eff` verified. Extracted into a new dedicated installation folder, preserving existing apps. That exact downloaded executable passed its real native account/editor/save/static/catalog/sandbox/lock journey using disposable credentials, then was launched with the normal private data root. |
| Installed local website | Visually verified the installed backend's real account-creation/help/creator page in the browser. No seeded/shared login or actual user credentials were created. [Screenshot](evidence/account-screen.png). Runtime listener is automatic; the local address can change after restart. |
| Static/supply-chain | Ruff, checked source maps, TypeScript/Vite builds and Python/npm audits passed with zero known third-party dependency vulnerabilities. The local package is not on PyPI and is not a third-party audited distribution. Vite's large offline-Monaco chunk warning remains explicit. |
| Source secret scanning | Checksum-verified Gitleaks 8.30.1 scanned all ten commits through release source, staged changes and authored source directories with zero findings. Ignored generated runtime/test/vendor data was not published. Scanning is not proof that secrets can never be committed. |

## Fixes and traceability

The initial [Windows package run](https://github.com/JasonStys/code-flow-studio/actions/runs/38346908179) failed because slow Docker diagnostics held the serialized history request lock. The release was withheld. Background readiness and a genuine pending-probe regression fixed it; every execution still rechecks and pins the local engine. [The full rerun](https://github.com/JasonStys/code-flow-studio/actions/runs/38347461662) passed all three platforms before the capacity safeguard was added and revalidated. No test assertions or Windows security policy were weakened.

History's 128 MiB soft write stop now also blocks repeat run queues, while a 160 MiB read recovery reserve permits existing history/exports after a final result crosses the threshold. The regression verifies lock/reopen with writes blocked. No automatic data deletion occurs.

GitHub canonicalized spaces in installer asset filenames. Their hashes were already correct; the three checksum filename fields were corrected without changing binaries. All six re-downloaded checksum records now match actual asset names and GitHub-computed SHA-256 digests. Four packaging regression cases prevent recurrence.

## Limits and storage

Docker Desktop remains unchanged per owner direction. Actual local compiler execution is blocked without isolation, while Actions supplies genuine worker evidence. No paid/live AI request, useful model-quality assertion, public account host, physical mobile installer, signing/notarization, independent penetration test or OS-compromise protection is claimed. Active local plaintext remains accessible to the trusted OS/admin; locked encryption is not zero-knowledge hosting.

Actions billing was freshly read at **0.5 GB / 0.5 GB included (100%)**, with $0 billable after discounts. This repository retained exactly **six old artifacts / 498,564,580 bytes** throughout validation/publication; no new Actions artifacts were uploaded or old runs deleted. Artifacts remain opt-in via `CODE_FLOW_UPLOAD_CI_ARTIFACTS=true`. Repository cache usage and billed storage are separate measurements; public visibility does not instantly reset the billing meter.
