# C# coverage correction — 10 November 2026

By Jason Stys. **The 0.4.3 worker now reports measured coverage for approved nonzero C# exits, retaining the actual target exit separately from the collector.** The correction passed real .NET/Coverlet validation on GitHub-hosted Linux. Docker, installed applications and account data on the owner's PC were unchanged.

## Observed exact target results

| Approved case | Expected target | Actual instrumented target | Collector | Coverage |
|---|---|---|---|---|
| success-zero | 0 | 0 | 0 | measured |
| expected-one | 1 | 1 | 0 | measured |
| expected-two | 2 | 2 | 0 | measured |
| expected-seven | 7 | 7 | 0 | measured |
| expected-255 | 255 | 255 | 0 | measured |
| malformed-input | 2 | 2 | 0 | measured |

The ordinary realistic invoice also passed all six cases with measured coverage, both through the normal broker and a real authenticated private account. All twelve languages passed the ordinary 70-scenario matrix, including exact native unused/uncovered anchors. Twelve complete reports were sealed, logged out/in, reopened and compared with exported JSON.

## Genuine failures still fail

| Controlled fault | Actual collector | Independent target observation | Coverage result |
|---|---|---|---|
| invalid-option | 0 | none | blocked |
| unwritable-output | 101 | 0 | blocked |
| timeout | -9 / timeout | none | blocked |

The argument-error control proves that collector exit zero alone is insufficient: no instrumented target ran and no valid observation existed. The report-write control completed a real target returning zero before the collector failed writing to the unchanged read-only `/opt` directory. The timeout used the existing process-group deadline and produced no successful observation. No sandbox permissions were widened.

An actual target return 7 with approved expectation 2 remained a failed ordinary case with partial coverage; the collector itself returned 0. An authored unhandled exception remained a failed case/partial coverage. The fix does not force unsuccessful programs or broken collectors to appear measured.

## Validation and source identity

| Check | Observed result | Run |
|---|---|---|
| Compiler execution acceptance | 2 jobs passed | [42883764689](https://github.com/JasonStys/code-flow-studio/actions/runs/42883764689) |
| Validate | 3 jobs passed | [42883765065](https://github.com/JasonStys/code-flow-studio/actions/runs/42883765065) |
| Desktop packages | 3 jobs passed | [42883753311](https://github.com/JasonStys/code-flow-studio/actions/runs/42883753311) |
| CodeQL | 3 jobs passed | [42883764587](https://github.com/JasonStys/code-flow-studio/actions/runs/42883764587) |

- Hosted full suite: **410 tests and 28 subtests passed**; **85.01% controller/training coverage**, unchanged 80% floor. This percentage is not presented as worker-source coverage.
- Local focused suite: **238 passed**, with two explicit Windows platform skips for POSIX signal/symlink capabilities. The complete hosted Linux suite exercised both platform paths.
- Browser, original isolated worker/fuzz checks, real private-worker replay, training, three-OS compiled native package checks and CodeQL passed. The reviewed PR merge ref had zero open alerts.
- Native package acceptance checked that the new helper was present and its exact bytes matched the reviewed source.
- Reviewed head: [`4bf014904b7b032887cb720b169af2d72874ff45`](https://github.com/JasonStys/code-flow-studio/commit/4bf014904b7b032887cb720b169af2d72874ff45); actual current PR runtime/verifier checkout: `f6d313754c9b9db2f8fdb6a4452ffc48f2286c14`.
- Actual bridge SHA-256: `64e1d4e2dfca531b58e595945e937b41de1334eaba71b729e85794f8ff4fcc41`. Source identities, worker image IDs, compiler versions and raw evidence hashes are in the [machine-readable observation](csharp-coverage-2026-11-10.json).

These are dated observations for the listed sources/runs, not a certification of an unrun later revision. [Current main workflows](https://github.com/JasonStys/code-flow-studio/actions?query=branch%3Amain) are checked separately after merge.

## Defect and implementation

Coverlet 8.0.1 intentionally maps a positive target exit to its own failure code; it has no preserve-target-exit switch. The 0.4.2 application correctly kept the resulting mismatch partial. Inferring the actual program exit from wrapper 1 or log text would be wrong.

The 0.4.3 trusted worker bridge bounds/verifies exact stdin, launches only the fixed .NET executable and this job's assembly, waits for actual completion and exclusively publishes a fresh source/case/input-bound observation before returning success to Coverlet. The worker independently requires collector success, the valid observation and genuine source-bound XML before comparing actual target status with the approved oracle. Invalid/missing/truncated evidence remains blocked. See the [full field and trust-boundary contract](../csharp-coverage.md).

## First acceptance failure and corrected control

The [first current-source attempt](https://github.com/JasonStys/code-flow-studio/actions/runs/42881205975) is preserved as failed evidence. The product fix already passed its 70 ordinary scenarios and all six exact-exit cases. Its fault test incorrectly assumed that invalid Coverlet arguments must return nonzero and required a particular error-message word. The [pinned entry point](https://github.com/coverlet-coverage/coverlet/blob/v8.0.1/src/coverlet.console/Program.cs) invokes the argument parser without propagating its return code, so a parser rejection can exit 0 without invoking the target.

The corrected control records actual fault evidence before assertions, checks parser rejection/no observation independently, and requires blocked coverage even for wrapper 0. The additional actual post-target report-write failure proves that a valid successful target observation cannot hide a broken collector. No product or oracle relaxation was needed for this test correction.

## Version, installation and measurement limits

- The fixed source/application/worker identity is **0.4.3**, using `code-flow-worker:0.4.3`. The immutable 0.4.2 baseline, published binaries and old partial records remain unchanged. Its historical lane still reports partial C# coverage, independently of the strict current lane.
- This task changed source, tests and documentation. It did **not** publish a new release, install a 0.4.3 app, rebuild local images, repair Docker or modify existing accounts/data. An installed 0.4.2 app remains 0.4.2; using the fix locally requires a matching 0.4.3 application/worker build.
- Expected nonzero exits now have fully measured instrumentation; that does not mean every possible source branch has been tested or every line has 100% coverage. Unexpected exits and real tool failures retain partial/blocked states.
- Source, bridge and actual worker image identity are recorded. Mutable upstream base/APT tags mean a fresh source-bound image is not claimed identical to historical image bytes. Timing includes process startup and is not an empirical Big-O or cross-language ranking.
- The existing non-root/no-network/read-only/resource controls remain. Same-UID targets can interfere with job files; record bindings detect stale/inconsistent evidence, not malicious-target tamper-proof attestation.
- Only small synthetic JSON evidence has three-day per-artifact retention. No runs/artifacts/caches were deleted and no account retention policy changed.
