# Hosted compiler and code-execution validation — 10 November 2026

By Jason Stys. This report extends the local Windows installation acceptance for
version 0.4.2 with hosted compiler execution. It never represents a GitHub runner
as Docker running on the owner's PC.

## Status and source identities

The first [hosted compiler run](https://github.com/JasonStys/code-flow-studio/actions/runs/42869521158)
executed all twelve realistic projects in both source lanes. Every language had
six approved cases passed and zero failed, both through the broker and the real
authenticated account API. Its overall acceptance failed because the new
validator made incorrect coverage assumptions; these failures remain visible.
The corrected full acceptance and published-binary probe are awaiting a fresh run.
Local evidence-validator tests are not compiler execution evidence.

The first run identified three validation-contract issues: Python's module
docstring trace event differs from executable-statement counts; PHP can report
the empty terminal EOF line; Coverlet wraps an approved C# exit 2 as collector
exit 1, which correctly leaves coverage partial. The correction preserves tool
semantics and the exact original source/oracles, and rejects unexplained partial
or truncated results. The [tool-specific limits](../compiler-execution.md#tool-specific-coverage-completion)
describe these explicitly. The frozen-service probe also had a report-schema
assumption corrected against the actual SQLite `Store.timeline` dictionary;
its tests now use the real store instead of a mirrored mock schema.

There are 59 passing focused local evidence/protocol regressions, including replay
of four actual first-run reports and negative controls for altered result/export
identity. No change to an installed runtime, worker implementation, language
example or approved oracle was needed for these validation corrections.

The immutable published baseline is
[`eb9b1cd0c3e3fd1e70e397edeffb059073464f74`](https://github.com/JasonStys/code-flow-studio/tree/eb9b1cd0c3e3fd1e70e397edeffb059073464f74).
Its [published 0.4.2 packages](https://github.com/JasonStys/code-flow-studio/releases/tag/v0.4.2)
identify the same source and bundled `node_checks.cjs` SHA-256
`750b665e545b7cf0806d4c493db86174f7f4e7ab2218aa239718e652ccdce158`.

The [test plan and project matrix](../compiler-execution.md) describes 72 literal
realistic cases, deliberately failing controls, native location anchors, real
private-account execution and saved-report replay. The workflow retains separate
runtime and validation source identities and a newly built worker image ID.

## Environment and limits

- Hosted Linux compiler execution is separate from Windows installer/UI testing.
- Docker on the owner's PC, existing containers/images and app account data are unchanged.
- No external AI API, real account/source, network-enabled target or paid model is used.
- Fresh builds from mutable upstream image/APT tags do not identify historical image bytes.
- Timings include startup and shared-runner noise; they are not Big-O measurements or cross-language rankings.
- SQLite statement starts, Bash command-entry and assembly debug-backed instructions retain their documented coverage meaning.
- Unsupported frameworks, language/ISA adapters and every possible bug remain outside these examples.
- Only small synthetic result reports are uploaded, with three-day per-artifact retention. No storage cleanup is performed.
