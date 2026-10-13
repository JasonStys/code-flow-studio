# Validation evidence — development preview

Historical 0.1 evidence, not current account-mode certification. See [0.2 results](validation-v0.2.md) for this release.

Observed on 2026-09-29 (America/Los_Angeles). Tested source commit: `9829a50278e5fef42565553174fae41858df7a23`. Documentation-only evidence updates do not imply additional functional capabilities.

## Results

| Layer | Observed evidence | Scope |
|---|---|---|
| Windows controller/API/data tests | **52 passed**, zero failures; **82.64% statement coverage** (495/599 statements) | `studio` plus `training.dataset`; optional ML training runtime and isolated worker are excluded from this denominator. One upstream Starlette/httpx TestClient deprecation warning. |
| Static/build checks | Ruff and exact code-map checks passed; TypeScript and production renderer build passed; npm audit: zero known vulnerabilities | Dependency audits and source heuristics are not security certification. Vite warns about large bundled editor chunks. |
| Actual browser flows | **9 passed**: three flows in Chromium, Firefox and WebKit; repeated locally and passed in Actions | Offline editor, 48-category catalog, priorities, consent/no-provider failure, saved run/download evidence, 390×844 responsive viewport. Not physical mobile-device testing. |
| Windows installed app | Per-user NSIS installation exited **0**; the installed executable passed its native smoke test, then was launched for the owner | Bundled service, actual offline editor, catalog and renderer Node-access restrictions. Existing Windows PC, not a clean-machine or signed-release test. |
| Real isolated workers | **24 integration scenarios passed their assertions** in Actions | Twelve compiler adapters, reviewed cases, pytest, coverage/mutation, raw-byte black-box fuzzing, genuine libFuzzer/AFL++/Atheris, expected-negative and isolation checks. Target failures in negative fixtures are intentional. |
| Exact web/native CSV example | **3/3 approved cases**, **3 pytest/property tests**, **24 fuzz executions**, no concrete crash/hang findings | Entry statement coverage **19/19**, branch coverage **5/6**; combined coverage **96%**. Three evaluated operator mutants were killed; this is not exhaustive mutation coverage. |
| Model training/API | Actual **33,248-parameter** CPU model trained for two steps; safe-tensor output and authenticated inference response verified | Four owned training records and one held-out record, project-disjoint. Held-out loss about **6.2533**. Tiny-model output is not useful or verified code. |
| Native CI packages | Windows installer, Linux AppImage and macOS DMG builds and native startup smoke tests passed | OS-specific hosted runners. Not notarization, signing, app-store approval or installation on every OS/device. |

The UI example's source hash in the worker report matches the source actually opened and saved through the web interface. Local web execution retained a **blocked** result because Docker was unavailable; the same source was then genuinely executed by the isolated CI worker, not on the host.

## Reproducible reports

- [Validation workflow](https://github.com/JasonStys/code-flow-studio/actions/runs/36659044896) and [desktop package workflow](https://github.com/JasonStys/code-flow-studio/actions/runs/36659044938): all jobs completed successfully for the tested source commit.
- [Full isolated-worker evidence](evidence/worker-evidence.json): positive/negative contracts, actual tool outputs, environment, seed, timing and exclusions.
- [Training report](evidence/training-report.json) and [local-model API smoke](evidence/training-api-smoke.json): actual weights-training mechanics, evaluation split and unverified completion.
- Local `artifacts/tests.xml`, `artifacts/coverage.xml` and browser/native screenshots are generated outputs; Actions retains its own artifacts. Do not confuse a local report with remote worker results.

Performance samples include process startup; the CSV example's observed median was about 63.9 ms with peak child RSS 47,740 KiB for that batch. These are exploratory measurements in one runner environment, not intrinsic algorithm latency, isolated function allocation, a speedup claim or a Big-O result.

## Explicitly blocked or unverified

Docker Desktop crashed in inference-socket initialization. The owner explicitly requested leaving it unchanged and using GitHub Actions. No Docker repair/reset, container/image deletion or permissive host-execution fallback was performed. The installed UI works, but local compiler/test jobs remain blocked until an approved isolated worker is available.

No useful live AI provider/model is configured. Provider protocol tests use mocks; the tiny-model training/API smoke does not validate live code generation, improvements or real-time coding assistance. No private capstone keys were reused and no paid API calls were made. Main-branch push AI generation is wired but opt-in and was not enabled in these runs.

All 48 categories are cataloged, **not all automated or executed**. Universal languages/formats/models, native mobile apps, arbitrary application-framework runners, physical hardware/human tests, production multi-tenant hosting and independently supervised hostile-target measurements are not delivered by this preview. See [remaining scope and acceptance milestones](remaining-scope.md).

The repository remains private pending the owner's visibility choice. Earlier failed CI attempts are retained and were followed by validated fixes; this report references observed successful runs, not an assertion that historical failures never occurred.

