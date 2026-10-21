# Polyglot evidence validation — 0.3.0

By Jason Stys. Unit/mock results are separated from genuine compiler/instrumentation results. Native release builds remain gated until all required jobs pass.

## Scope

- Existing Python location, static review and multi-file coverage regressions retained.
- Eleven independently authored non-Python fixtures require native unused-code candidates and actual unexecuted/executed original source lines, plus source hashes.
- Controller/private accounts, three browser engines, actual restricted workers, training smoke and three native OS-package launch checks remain mandatory.
- Docker Desktop on the development PC is intentionally unchanged. No submitted code is run on the host. Actual compiler/coverage acceptance runs on GitHub-hosted Linux under the existing restricted container policy.

## Local checks so far

**144 Python tests passed**, controller/training.dataset coverage **84.46%** (80% gate). Ruff, generated source maps, TypeScript and Vite build passed. Six local Chromium UI checks passed with normal Windows process permissions; the restricted process could not launch Chromium, and no browser sandbox was disabled. Python/native compiler fixtures are never executed directly on the host. Python/npm analyzer and app dependency audits found no known vulnerabilities at check time (the local editable project is not a PyPI package). The build retains the existing editor chunk-size advisory, not a failed validation.

## Verified GitHub results

[Validate 39675935177](https://github.com/JasonStys/code-flow-studio/actions/runs/39675935177), exact source `74c689ccc9943ca059851967cf2f2ba7bff5bc5f`, **passed**: 144 Linux unit tests, **84.28%** controller/training.dataset coverage; 18 browser checks across Chromium/Firefox/WebKit; six private-account browser journeys; lint/maps/build/audits; genuine training/inference smoke; all 38 isolated-worker scenarios and all twelve account-mode adapters/history checks. No artifact uploads were enabled.

Every one of the eleven non-Python location fixtures passed actual unused-rule and executed/missing-line assertions. Their independently authored missing/unused anchors and tool reports are retained in [machine evidence](evidence/polyglot-locations.json), copied from post-assertion `NATIVE_ACCEPTANCE` log records, not generated mock results. Negative SQL cases intentionally expect exit 1: source statement 2 fails at its statement-start anchor, and statement 3 is not reached.

Integration failures were diagnosed and corrected, not suppressed: JS package-export resolution; missing Debian Rust profiling runtime (official Rust 1.99.1 plus its matching LLVM/profile runtime); PHPMD 3 command syntax and explicit trusted ruleset; C# selected-assembly instrumentation and Cobertura source-root resolution. Missing/mismatched sources remain unknown rather than guessed from a path suffix. Earlier failed runs remain part of the audit trail.

Windows/Linux package checks for this source passed; the macOS job was still queued when this report was prepared. Final packaging/release evidence and the two additional JS/TS multi-file module checks are recorded after the final gates complete. No pending job is represented as passed.

Actions artifacts were 61,385,326 bytes before triggering validation; quota percentage was unavailable. Caches were a separate 13,406,153,746 bytes. No runs/artifacts/caches were deleted and CI artifact uploads remain opt-in/off.

See [measurement contracts and limitations](polyglot-locations.md). No universal bug-finding, dead-code, branch-coverage, MC/DC or tool-tamper-resistance claim is made.
