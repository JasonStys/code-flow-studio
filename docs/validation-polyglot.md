# Polyglot evidence validation — 0.3.0

By Jason Stys. Unit/mock results are separated from genuine compiler/instrumentation results. Native release builds remain gated until all required jobs pass.

## Scope

- Existing Python location, static review and multi-file coverage regressions retained.
- Eleven independently authored non-Python fixtures require native unused-code candidates and actual unexecuted/executed original source lines, plus source hashes.
- Controller/private accounts, three browser engines, actual restricted workers, training smoke and three native OS-package launch checks remain mandatory.
- Docker Desktop on the development PC is intentionally unchanged. No submitted code is run on the host. Actual compiler/coverage acceptance runs on GitHub-hosted Linux under the existing restricted container policy.

## Local checks

**148 Python tests passed**, controller/training.dataset coverage **84.46%** (80% gate). Ruff, 61 generated source maps, diff whitespace checks, TypeScript and Vite build passed. Six local Chromium UI checks passed with normal Windows process permissions; the restricted process lacked the normal browser cache, and no browser sandbox was disabled. The test-only server was subsequently stopped without touching user apps or Docker. Python/native compiler fixtures are never executed directly on the host. Python/npm analyzer and app dependency audits found no known vulnerabilities at check time (the local editable project is not a PyPI package). The build retains the existing editor chunk-size advisory, not a failed validation.

## Verified GitHub results

[Validate 39678356525](https://github.com/JasonStys/code-flow-studio/actions/runs/39678356525), exact release source `c09877827991fd20fe13d98dd5ee4c91d54e819f`, **passed**: 148 Linux unit tests, **84.28%** controller/training.dataset coverage; 18 browser checks across Chromium/Firefox/WebKit; six private-account browser journeys; lint/maps/build/audits; genuine training/inference smoke; all **40 isolated-worker scenarios** and all twelve account-mode adapters/history checks. No artifact uploads were enabled. Worker and native-OS launch checks are integration tests outside that controller coverage denominator.

Every one of the eleven non-Python location fixtures passed actual unused-rule and executed/missing-line assertions. Additional JS/TS module scenarios verify the imported helper's unused definition at line 1, missed body at line 2, and explicit `not-measured` status for an unloaded source. Their independently authored anchors and tool reports are retained in [machine evidence](evidence/polyglot-locations.json), copied from post-assertion `NATIVE_ACCEPTANCE`/`MODULE_ACCEPTANCE` log records, not generated mock results. Negative SQL cases intentionally expect exit 1: source statement 2 fails at its statement-start anchor, and statement 3 is not reached.

Integration failures were diagnosed and corrected, not suppressed: JS package-export resolution; missing Debian Rust profiling runtime (official Rust 1.99.1 plus its matching LLVM/profile runtime); PHPMD 3 command syntax and explicit trusted ruleset; C# selected-assembly instrumentation and Cobertura source-root resolution. Missing/mismatched sources remain unknown rather than guessed from a path suffix. Earlier failed runs remain part of the audit trail.

[Desktop packages 39678356491](https://github.com/JasonStys/code-flow-studio/actions/runs/39678356491) **passed all three OS jobs** for that exact source: actual Windows/macOS/Linux packaged Electron app and bundled service launch, private registration/unlock/editor/history/lock journeys, renderer isolation, native worker-resource presence, Linux-compatible Bash line endings and exclusion of analyzer `node_modules` from the desktop bundle. Packages do not install/repair Docker or execute targets on the host.

[Release workflow 39679198552](https://github.com/JasonStys/code-flow-studio/actions/runs/39679198552) gates on those successful exact-source runs, independently rebuilds/tests each OS package, creates SHA-256 records and publishes [v0.3.0](https://github.com/JasonStys/code-flow-studio/releases/tag/v0.3.0) only after all three builds pass. Release assets, not optional Actions artifact uploads, carry the downloads. This describes the release gate; the linked run is the authoritative publication audit trail. Applications remain unsigned development builds. No account/history migration is required.

The code review checked fixed argv/configuration, source-path/range/hash binding, native report bounds, DTD/source-map restrictions, explicit partial/blocked states, baseline/instrumented measurement separation and unchanged container/privacy restrictions. Regressions additionally cover deep parser data and Unicode physical-source/SQL lexical boundaries. Rollback and worker-rebuild instructions are in the [release notes](releases/v0.3.0.md); restore only independently verified encrypted backups and do not rewrite historical evidence.

Actions artifacts were **61,385,326 bytes** before validation and again at the 2026-10-21 21:29 UTC release check; quota percentage was unavailable. Caches changed from a separate 13,406,153,746 to **13,547,949,690 bytes** during builds and are not the artifact billing meter. No runs/artifacts/caches were deleted; CI artifact uploads remain opt-in/off. Fresh cleanup approval would be required before deleting anything.

See [measurement contracts and limitations](polyglot-locations.md). No universal bug-finding, dead-code, branch-coverage, MC/DC or tool-tamper-resistance claim is made.
