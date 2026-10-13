# Version 0.2 validation

Observed October 12, 2026 (America/Los_Angeles). This document will record final source/run IDs after CI and native publication finish.

Local evidence: **82 Python tests pass**, with **82.89% statement coverage** across all `studio` and `training.dataset` (1,508 statements; 258 missed). The >=80% gate is retained. Python 3.14.6/pytest 9.0.3 on Windows; Linux CI uses Python 3.12. Production TypeScript/Vite build, Ruff and generated maps pass. Python/npm audits report zero known dependency vulnerabilities after reviewed transitive/tooling fixes. The local package itself is not on PyPI and is not an audited third-party package. Vite's large offline-Monaco bundle warning remains explicit.

Private browser journeys: four passing checks in Chromium/WebKit. Historical browser checks: six passing checks in these engines. Local Firefox process launch fails with `spawn UNKNOWN` before app interaction; no Windows security policy was changed. Three-engine tests remain required in Linux CI, not removed/skipped to hide the local limitation.

Bundled Windows service/native shell and actual unpacked packaged executable both pass: real account registration, WebCrypto unlock, editor, saved source revision, non-executing static evidence, 48-category catalog, renderer Node/process restrictions and encrypted lock. Downloaded-runtime and three-OS evidence are pending at this document's initial revision.

Gitleaks 8.30.1 (official checksum-verified binary) scans all seven historical commits, staged changes and authored source directories with zero findings. Ignored runtime/test/build/vendor files are not published. This is evidence from a scanner, not proof that secrets can never be committed.

Local Docker remains unchanged per owner direction. Compilation/testing is explicitly blocked without isolation; all real compiler/fuzz/training validations run in Actions. Provider contracts use mocks and synthetic credentials; no paid/live model call or useful model-quality assertion is made.

Actions artifacts are opt-in via `CODE_FLOW_UPLOAD_CI_ARTIFACTS=true`; default pipelines leave uploads off because account storage was reported full. Release files use Releases, not Actions artifacts. This does not delete existing storage or claim the billing meter is zero.

Initial CI source `084129a796316ba65eb9352714d28c3c6b45d2be`: [Validate 38346908169](https://github.com/JasonStys/code-flow-studio/actions/runs/38346908169) passed all three jobs: 81 Python tests, all 15 browser checks (including Firefox), 24 real worker scenarios, twelve genuine private-account compiler/oracle jobs with encrypted-history reopen, and actual tiny-model training/inference. Linux/macOS packaged apps passed. The Windows package test detected that slow Docker readiness held the serialized source request lock; the release was withheld. Background cached diagnostics plus a real pending-probe regression fix that issue while every execution still rechecks the pinned local engine. No Windows security policy or test assertions were weakened. Final release evidence follows after rerun.
