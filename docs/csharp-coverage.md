# Exact C# coverage exits — 0.4.3

By Jason Stys. See the [dated validation report](reports/csharp-coverage-2026-11-10.md)
for observed hosted results, rather than treating this design as test evidence.

## Correct behavior

An approved C# CLI rejection such as exit 2 is not a failed coverage collector.
Version 0.4.2 passed the program's real output/exit cases, but Coverlet 8.0.1
collapsed nonzero target exits to its wrapper failure code. The application
conservatively reported partial coverage. Version 0.4.3 removes that ambiguity
with a trusted worker bridge; it does not guess the exit from collector text or
convert every collector failure into success.

| Evidence | Meaning |
|---|---|
| `coverage.cases[].exit_code` | Compatibility field containing the actual instrumented .NET process return |
| `target_exit_code` | The same independently observed target return, explicitly named |
| `expected_exit_code` | Developer-approved oracle; never rewritten by collection |
| `collector_exit_code` | Coverlet's own process result; must be zero for a completed collection |
| `bridge` | Fresh case/source/input/helper binding and the actual child-process return |

All approved instrumented returns must equal their oracles before coverage is
`measured`. A valid target returning 7 when 2 was expected stays a failed test
with partial coverage. Collector errors/timeouts, missing or mismatched records
and missing/invalid XML remain blocked. A genuine unexpected exception is never
relabeled as a successful approved run.

## Collection flow

1. Build the debug C# assembly and portable PDB normally, offline.
2. Create a fresh, bounded request in the existing job-private analysis directory.
   Bind a nonce, case index, SHA-256 of all supplied files and exact stdin bytes.
3. Coverlet instruments that assembly and invokes fixed isolated Python under
   `/opt`. The bridge can launch only the fixed .NET executable and this job's
   fixed assembly, using argv without a shell.
4. The bridge bounds and verifies stdin, forwards the exact bytes, waits for the
   actual .NET child and exclusively publishes its observed exit. It returns zero
   to Coverlet only after that observation is committed. It does not detach from
   the process group or introduce another execution timeout policy.
5. The worker independently requires collector success, complete output, a fresh
   strict record matching this request and valid actual source-bound coverage XML.
   It then compares the observed target exit against the approved expectation.

The request/record has a closed schema with exact types; booleans are not integer
exit codes. Size budgets, duplicate/nonfinite JSON rejection, same-descriptor
regular-file checks, no-follow/nonblocking opens and one-link files reject stale,
aliased or malformed protocol data. Publication uses a flushed temporary file
and exclusive atomic hardlink, without overwriting a prior record. Input is
bounded at 32,768 bytes, preserving the API's 8,192-character UTF-8 allowance.

The worker retains its existing no-network, read-only-root, non-root UID,
capability, resource and process-group controls. The outer worker timeout kills
the owned collector/bridge/target group; an incomplete observation cannot authorize
measured coverage. No provider credentials or Docker socket are passed to target code.

Target code and instrumentation share a container UID and can interfere with
job-local files, just as with existing coverage outputs. The bindings detect stale
or inconsistent observations; they are not hostile-target tamper-proof attestation.
Use a dedicated disposable environment for untrusted hostile code.

## Versions and installation scope

The corrected source, worker image and native build identity are 0.4.3; the worker
is `code-flow-worker:0.4.3`. Published 0.4.2 tags/assets, historical snapshots and
the baseline workflow lane remain unchanged. Only a verifier explicitly bound to
the immutable old release source may accept that historical partial collector
behavior; current acceptance requires the new bridge and measured completion.

This change does not install an application, rebuild local worker images or repair
Docker on a user's PC. A 0.4.3 application/worker build is required to use the fix;
an existing installed 0.4.2 application and its data are not silently upgraded.
Published download availability is determined by [Releases](https://github.com/JasonStys/code-flow-studio/releases),
not by a source-version label or successful CI package build.

## Tests and files

| File | Responsibility |
|---|---|
| `runner/csharp_coverage_bridge.py` | Fixed child-process launch, bounded case binding and exclusive observation publication |
| `runner/language_checks.py` | Separate actual target/collector exits, strict record and real XML integration |
| `scripts/csharp_coverage_checks.py` | Hosted real .NET exits 0/1/2/7/255, malformed input, wrong expected exit, exception and real collector error/timeout controls |
| `tests/test_csharp_coverage_bridge.py` | Real inert child-process and protocol/filesystem regressions; no local .NET or Docker |
| `tests/test_csharp_measurement.py` | Actual adapter/request/record/XML integration with inert compiler/collector doubles |
| `scripts/compiler_acceptance.py` | Strict current evidence; separately pinned historical 0.4.2 policy |
| `tests/desktop.spec.ts` | Actual packaged bridge presence and exact source-digest comparison |

The [compiler workflow](../.github/workflows/compiler-execution.yml) builds each
lane's own versioned image. The current lane runs the six explicit exit oracles
and fault injection through the unchanged restricted worker path. The ordinary
realistic C# invoice is also tested through the real private account API and
encrypted report replay. No local Docker execution is needed for validation.
