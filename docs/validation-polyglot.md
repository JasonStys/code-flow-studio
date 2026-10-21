# Polyglot evidence validation — 0.3.0

By Jason Stys. Validation in progress; this report will record the final exact source and measured CI evidence before release. Unit/mock results do not establish compiler/instrumentation success.

## Scope

- Existing Python location, static review and multi-file coverage regressions retained.
- Eleven independently authored non-Python fixtures require native unused-code candidates and actual unexecuted/executed original source lines, plus source hashes.
- Controller/private accounts, three browser engines, actual restricted workers, training smoke and three native OS-package launch checks remain mandatory.
- Docker Desktop on the development PC is intentionally unchanged. No submitted code is run on the host. Actual compiler/coverage acceptance runs on GitHub-hosted Linux under the existing restricted container policy.

## Local checks so far

142 Python tests passed; controller/training.dataset coverage 84.46% (80% gate). Ruff, generated source maps, TypeScript and Vite build passed. The build retains the existing editor chunk-size advisory, not a failed validation. Native tool integration and final browser/native-package counts are pending CI.

Actions artifacts were 61,385,326 bytes before triggering validation; quota percentage was unavailable. Caches were a separate 13,406,153,746 bytes. No runs/artifacts/caches were deleted and CI artifact uploads remain opt-in/off.

See [measurement contracts and limitations](polyglot-locations.md). No universal bug-finding, dead-code, branch-coverage, MC/DC or tool-tamper-resistance claim is made.
