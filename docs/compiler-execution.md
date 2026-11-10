# Realistic compiler and execution validation

By Jason Stys. The [dated results](reports/hosted-compilers-2026-11-10.md)
distinguish actual hosted observations from local unit tests or planned checks.

## Realistic projects

Twelve standard-library CLI projects each have six independently authored
input/output/exit-code oracles. No AI provider, private source or real account is used.

| Adapter | Practical example | Important boundaries |
|---|---|---|
| Python | Telemetry count, sum, minimum and maximum | Empty, negative, malformed and out-of-range samples |
| JavaScript | Integer-cent invoice and basis-point discount | Zero quantity, rounding and discount limits |
| TypeScript | Typed temperature/vibration severity policy | Thresholds and malformed readings |
| C++ | Integer sensor calibration | Offset/scale changes and bounded inputs |
| C | Bounded byte XOR checksum | Empty/multiple inputs and rejected tokens |
| Java | Available-capacity allocation | Zero capacity, exhaustion and malformed fields |
| C# | Decimal invoice and tax | Decimal rounding, zero and rejected amounts |
| Rust | Inventory stock adjustments | Negative adjustments, insufficient stock and lexical errors |
| PHP | Bulk price quotation | Threshold discounts, zero and rejected quantities |
| Bash | Log severity summary | Empty/mixed input and invalid records |
| SQLite SQL | Product/order revenue reports | Joins, ordering, missing products, constraints and malformed queries |
| GNU x86-64 assembly | Alarm-bit decoder with real input and branches | Independent bits, all/zero bits and rejected input |

Approved rejection cases pass only when their exact expected output and exit
status match. A job reporting `completed` means it ran; that alone is not a test pass.

## Independent checks

1. Compile/run every realistic program through the ordinary restricted broker.
   Require every case's name, stdout, exit status and complete outcome; immutable
   oracle hash; real timing/RSS samples; native tool completion; exact source
   hashes and consistent coverage line partitions/counts.
2. Give a successful program an intentionally incorrect expected output. Its
   actual answer must still match the independently known correct result and it
   must exit normally, while the comparison is reported as failed.
3. Give all eleven adapters with a separate compile/syntax phase malformed source.
   Require nonzero compilation, no executed cases, blocked coverage/unused tools,
   and the exact independently authored filename/line/source hash. SQLite parses
   its schema/query during execution and is not described as compiled.
4. Run valid programs with authored runtime faults or explicit exit 7. Require
   the specific expected failure exit and, for exceptions, its synthetic marker;
   an unrelated loader error is insufficient.
5. Retain eleven independent fixtures with exact unused and uncovered anchors.
   SQL statement starts, Bash command entry and assembly debug-backed instructions
   retain their different measurement meanings.
6. Save/run realistic programs through a real authenticated private account API.
   Export JSON/HTML; seal; log out; prove anonymous history is denied; log back in;
   unlock; compare complete saved results and exported JSON after reopening.
7. In the release lane, verify/download the published Linux portable package,
   start its actual frozen service and repeat realistic API execution plus a full
   service restart with encrypted history. This tests the released backend binary.

## Hosted execution and evidence

The [workflow](../.github/workflows/compiler-execution.yml) runs a fixed release
lane (`eb9b1cd0c3e3fd1e70e397edeffb059073464f74`, version 0.4.2) and a current-source
lane. It identifies validation and runtime source separately, rejects dirty
tracked runtime code or controller imports from the wrong checkout, and records
the worker image identity. The real-execution entry points refuse non-hosted
Linux execution. Docker on Jason's PC is unchanged.

The worker retains no network, a read-only root, UID/GID 65534, dropped
capabilities, no privilege escalation, bounded memory/CPU/processes and one
read-only job input. No account store or provider key is mounted into the target.
These are development controls, not certification for public hostile multi-tenant use.

The image is freshly built from the identified source. Mutable upstream Docker
tags and APT packages mean it is not asserted identical to a historical image.
Recorded tool versions/image identities/raw results apply to the observed run.
Hosted Linux success does not imply that Windows Docker was installed/repaired,
or that arbitrary frameworks, packages, formats and ISAs are supported.

Only small synthetic JSON/table evidence is uploaded with three-day retention;
the run also has a result summary. Binaries and account directories are excluded.
This per-upload setting neither changes account retention nor deletes existing
artifacts/caches. See [GitHub artifact documentation](https://docs.github.com/en/actions/tutorials/store-and-share-data).

## Files and reproduction

| File | Responsibility |
|---|---|
| `examples/practical_projects.py` | Twelve programs, 72 literal oracles and failure controls |
| `scripts/compiler_acceptance.py` | Hosted source/broker/private-API checks and incremental evidence |
| `scripts/released_service_probe.py` | Published Linux package verification, frozen execution and restart |
| `tests/test_compiler_acceptance.py` | Evidence mutation regressions and local-execution refusal |
| `tests/test_released_service_probe.py` | Safe package/lifecycle regressions without local Docker |
| `.github/workflows/compiler-execution.yml` | Fixed source lanes, hosted worker build and small reports |

Use **Actions → Compiler execution acceptance → Run workflow** on `main`, or
`gh workflow run compiler-execution.yml --repo JasonStys/code-flow-studio --ref main`.
Local unit tests can use `python -m pytest tests/test_compiler_acceptance.py
tests/test_released_service_probe.py`; they do not execute the target source.

These are flat-project demonstrations, not production domain algorithms or an
empirical Big-O measurement. Timings include process startup; small changes and
cross-language rankings are not reliable performance comparisons.

### Historical 0.4.2 coverage completion

The historical 0.4.2 C# malformed-input case correctly returns exit 2 in ordinary execution.
Coverlet 8.0.1 wraps that expected nonzero target exit as collector exit 1. The
application conservatively retains `coverage.status: partial`, despite a valid
source-bound report. Acceptance requires all six ordinary case outputs/exits,
all instrumented case identities, successful zero-exit instrumentation, the exact
known nonzero wrapper behavior and a generated coverage report. It never relabels
that report as fully measured. An unrelated collector failure is rejected.
The [pinned Coverlet console implementation](https://github.com/coverlet-coverage/coverlet/blob/v8.0.1/src/coverlet.console/Program.cs)
maps positive target exits to its test-failed wrapper status. The exact nonzero
target exit is independently checked in ordinary execution, not inferred from
the instrumented wrapper's exit 1.

coverage.py may retain the module-docstring trace event while excluding it from
its executable-statement count. The validator permits only that source-proven
one-line difference. PHP Xdebug can report an implicit return at an empty terminal
source line; location bounds use the same newline convention as the app/editor.
The [observed report snapshots](../tests/fixtures/compiler-reports-042.json) retain
these actual first-run results, including their original failed-acceptance labels;
replay unit tests are not a new compiler run.

Current 0.4.3 workers use a [separate exact target-exit bridge](csharp-coverage.md)
and must report measured completion for approved nonzero exits. The old partial
allowance is available only to the independently pinned 0.4.2 baseline verifier;
it cannot make a current worker pass acceptance.
