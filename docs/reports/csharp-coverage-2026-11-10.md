# C# coverage correction — 10 November 2026

By Jason Stys. **The first hosted run verified the core fix; final acceptance is pending.**
Local parser, protocol and inert process tests do not by themselves establish
.NET/Coverlet behavior.

The [initial hosted current-source run](https://github.com/JasonStys/code-flow-studio/actions/runs/42881205975)
passed all 70 ordinary compiler/private API scenarios, including measured C# invoice
coverage. It also preserved the exact instrumented returns 0, 1, 2, 7, 255 and 2,
with collector exit zero and measured coverage. Unexpected returns/exceptions
remained partial. Its final fault-control assertion failed: the test incorrectly
assumed an invalid Coverlet option would cause a nonzero process exit.

The pinned Coverlet entry point invokes its argument parser but does not propagate
the parser's return code. The corrected control records actual outcomes before
assertion, verifies parser rejection independently, and requires blocked coverage
without a valid target observation even when the wrapper exits zero. A separate
post-target report-write failure checks nonzero collection after a valid successful
target observation. No worker change or weakened target oracle was needed for
this fault-test correction. Historical failed evidence remains retained.

## Defect and correction

The [0.4.2 validation](hosted-compilers-2026-11-10.md) found all six ordinary C#
invoice cases passed, but Coverlet 8.0.1 mapped an approved target exit 2 to its
own failure exit 1. Reporting partial was conservative; inferring the target's
exact status from wrapper code or text would be incorrect. The pinned
[Coverlet implementation](https://github.com/coverlet-coverage/coverlet/blob/v8.0.1/src/coverlet.console/Program.cs)
has no preserve-target-exit option.

The 0.4.3 worker now runs a trusted isolated Python bridge. It waits for the real
instrumented .NET child, exclusively records its exact exit with source/case/input
bindings, and independently requires successful collection and real coverage XML.
Expected nonzero returns can therefore be fully measured while unexpected returns,
collector failures, timeouts and invalid evidence remain failures/partial/blocked.
See the [implementation and report-field contract](../csharp-coverage.md).

## Acceptance plan

- Real hosted .NET/Coverlet: expected exits 0, 1, 2, 7 and 255 plus malformed-input
  rejection; each exact target return retained with collector exit zero and measured coverage.
- Real hosted unexpected return and exception: failed ordinary cases, never a false measured pass.
- Real hosted invalid collector option, post-target unwritable report and enforced
  collector timeout: healthy ordinary target still passes, actual collector and
  observation outcomes are recorded and coverage is blocked.
- Ordinary twelve-language suite, private C# execution, encrypted report replay,
  original worker/fuzz checks, browser, native package, training and CodeQL checks.
- Local protocol tests: actual inert Python child returns, exact Unicode/binary stdin,
  fresh records, atomic publication, schema/type/hash/identity/alias/race negatives.
- Local measurement integration: valid receipt and XML still cannot hide a bad
  collector, timeout/truncation, missing/tampered observation or missing/invalid report.

## Scope

Published 0.4.2 releases and evidence are immutable historical baselines. The fix
uses source/application/worker version 0.4.3; it does not relabel old partial results.
Docker, installed apps, existing accounts and data on the owner's PC are unchanged.
No new release has been published by this source change. Shared-UID file bindings
are consistency checks, not a hostile-program attestation mechanism.
