# Practical workflow validation — 2026-11-09

Jason Stys · local Windows x64 · Python 3.14.6 · Node 24 · Electron 44.10.2. This report records local observations; GitHub-hosted checks are coordinated separately and are not claimed here.

## User-visible improvement

Located diagnostics, unused-code candidates and missed-coverage lines now lead to a verified, read-only source snapshot. File/category filters reduce triage noise. Nearby-line browsing validates bounds. Opening the editable draft requires the exact file/artifact and SHA-256 still to match, including a second check after asynchronous hashing. Generated tests/harnesses cannot masquerade as same-named source files. Stale, legacy, binary and missing-source references have explicit unavailable states. Account locking removes the inspector.

Actual typing exposed a pre-existing controlled-editor race: rapid model changes could be replaced by delayed React state. A narrowly scoped synchronous update in the Monaco callback now keeps the draft and model aligned. The regression types into the real editor and checks retained bytes, rather than calling the state helper directly.

## Observed checks

| Check | Observed result |
|---|---|
| Controller/privacy/provider/parser regressions | 148 passed; 1,446/1,712 measured lines covered (84.46%), above the existing 80% threshold. No target code executed on the host. |
| Three-engine web suite | 45 passed: 27 actual browser journeys and 18 repeated pure source-binding checks across Chromium, Firefox and WebKit. |
| Three-engine private accounts | 9 passed, including a real static-review source inspection and no external request, then account locking. |
| Final strict fingerprint/browser subset | 11 passed, including newline-tainted hash, exact bytes, generated distinction, stale draft and real static-review navigation. |
| Packaged Windows app | Actual frozen Python service and electron-builder unpacked application launched; 1 end-to-end native test passed. Registration/unlock, source inspection, catalog, lock, no renderer Node access and packaged worker-resource boundaries were asserted. Both launcher profile and accounts used disposable test directories. |
| Type/build/style/index | TypeScript and Vite build passed; Ruff passed; all 65 source maps current. |
| Dependencies | `pip check` passed; isolated Python audit found no known vulnerabilities; npm audit found 0. The editable project itself is not published on PyPI and is audited through its dependencies/source tests. |
| Packaging | PyInstaller and `electron-builder --dir --publish never` passed. Output stayed under ignored build/release directories; no installer installed or release published. |

Coverage UI fixtures intentionally simulate report contracts for mismatch/out-of-range/partial/native-metric display. They do **not** claim a new compiler/coverage collector run. The auxiliary Python static-review journey uses the real API. Source-binding unit oracles use independent Node SHA-256 and cover all twelve manifest languages; this does not establish compiler acceptance.

## Reproduction

Use the declared isolated development dependencies, then run:

```text
python -m ruff check studio training runner scripts examples tests
python scripts/code_index.py --check
python -m pytest --cov=studio --cov=training.dataset --cov-fail-under=80 --cov-report=xml:artifacts/coverage.xml --junitxml=artifacts/tests.xml
python -m pip check
python -m pip_audit --local --progress-spinner off
npm ci
npm audit --audit-level=moderate
npm run build
npm run test:browser
npm run test:private
```

Tests use owned, non-reused loopback services. `CFS_WEB_TEST_PORT` / `CFS_PRIVATE_TEST_PORT` permit a dedicated unused port instead of interfering with a user's open app. Test outputs are separated under `test-results/web`, `private` and `desktop` so independent suites cannot erase each other's traces. For the packaged native test, build the existing frozen-service/notices/package pipeline and set `STUDIO_INSTALLED_APP` to the produced executable before `npm run test:desktop`.

## Dependency corrections and remaining limits

Electron 44.10.2 replaces vulnerable 44.5.0. Compatible lockfile updates plus the narrow `minimatch@>=7 <11.0.1` override remove current npm advisories; full UI and actual native packaging validate that dependency combination. The local venv's pip was independently patched to 26.2 after its audit reported PYSEC-2026-3721. No advisory was suppressed. Primary records: [Electron advisory](https://github.com/advisories/GHSA-jr5w-w6x2-84p9), [minimatch advisory](https://github.com/advisories/GHSA-g3hv-75wg-m249), [pip advisory](https://github.com/advisories/GHSA-qwm4-qh6w-59xr).

The existing Monaco main bundle still produces Vite's large-chunk warning (about 4.31 MB minified, 1.12 MB gzip); it has not been hidden or represented as a passing performance budget. Installed Windows lifecycle, macOS/Linux packaging, isolated compiler/fuzz/coverage scenarios and CPU model training remain the existing coordinated CI gates. Docker was left unchanged. No paid/live AI provider, personal source, external dataset or real applicant data was used. Worker isolation, consent and account encryption were not weakened. Render bounds and unsupported evidence are documented in [source navigation](../source-navigation.md).
