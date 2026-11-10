# Hosted compiler and code-execution validation — 10 November 2026

By Jason Stys. This report extends the local Windows installation acceptance for
version 0.4.2 with hosted compiler execution. It never represents a GitHub runner
as Docker running on the owner's PC.

## Status and source identities

The realistic examples and evidence validators have been added. Hosted execution
results are pending the workflow run and will be recorded here after inspection.
Local evidence-validator tests are not compiler execution evidence.

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
