# Hosted compiler and code-execution validation — 10 November 2026

By Jason Stys. **The released 0.4.2 service and both source lanes passed hosted compiler acceptance.** Docker on the owner's PC and existing local accounts/data were unchanged.

## Observed results

| Check | Result | Observed run |
|---|---|---|
| Compiler execution acceptance | 2 jobs passed | [42871745673](https://github.com/JasonStys/code-flow-studio/actions/runs/42871745673) |
| Validate | 3 jobs passed | [42871745652](https://github.com/JasonStys/code-flow-studio/actions/runs/42871745652) |
| Desktop packages | 3 jobs passed | [42871731707](https://github.com/JasonStys/code-flow-studio/actions/runs/42871731707) |
| CodeQL | 3 jobs passed | [42871745412](https://github.com/JasonStys/code-flow-studio/actions/runs/42871745412) |

- **12 supported adapters, 72 distinct realistic input/output/exit oracles.** Each source lane passed 70 scenarios: 12 realistic programs, 12 wrong-oracle controls, 11 syntax failures, 12 runtime faults, 11 exact native-location fixtures and 12 authenticated private-API executions.
- Both source lanes sealed, logged out, logged in and reopened all 12 complete saved execution reports; anonymous history access was denied and managed plaintext was removed.
- The actual published Linux frozen service independently passed all 72 realistic cases. It sealed/exited, restarted, logged back in/unlocked, verified all 12 complete results and JSON exports, then sealed/exited again.
- The full hosted suite passed **345 tests and 28 subtests**, with **85.01% measured coverage** against the unchanged 80% floor. Browser, original worker/fuzz/location, private-worker, training and three-OS native package acceptance also passed.
- CodeQL completed Python, JavaScript/TypeScript and Actions analysis; the reviewed PR merge ref had zero open alerts. **59 focused local validator/protocol regressions passed.**

These are observations for the linked runs, not a claim that every later commit is already tested. The [current main checks](https://github.com/JasonStys/code-flow-studio/actions?query=branch%3Amain) and [machine-readable dated evidence](hosted-compilers-2026-11-10.json) preserve that distinction.

## Exact source and binary identity

- Published release/source: [`eb9b1cd0c3e3fd1e70e397edeffb059073464f74`](https://github.com/JasonStys/code-flow-studio/tree/eb9b1cd0c3e3fd1e70e397edeffb059073464f74), [version 0.4.2](https://github.com/JasonStys/code-flow-studio/releases/tag/v0.4.2), release ID 440504623.
- Reviewed validation head: [`9b5180489cb663a30e120c08ff37a469429db85f`](https://github.com/JasonStys/code-flow-studio/commit/9b5180489cb663a30e120c08ff37a469429db85f); PR current-runtime merge checkout: `c8288ea0bdc229c7bd7ec1a5eff93a4c314f4318`.
- Accepted published Linux payload: asset 731850461, 188,603,375 bytes, SHA-256 `1e75085bae4ab2611ead61a513b60f444941495608840cf33875d940cf963ebe`. Live provider digest, exact sidecar, tag, bounded archive and embedded provenance were independently checked.
- Bundled worker `node_checks.cjs` SHA-256: `750b665e545b7cf0806d4c493db86174f7f4e7ab2218aa239718e652ccdce158`. Worker image IDs and raw evidence hashes are recorded in the JSON edition.

## Actual observed toolchains

| Adapter | Version reported inside restricted worker |
|---|---|
| python | Python 3.12.12 |
| javascript | v24.22.2 |
| typescript | Version 5.9.3 |
| cpp | g++ (Debian 12.2.0-14+deb12u1) 12.2.0 |
| c | gcc (Debian 12.2.0-14+deb12u1) 12.2.0 |
| java | javac 17.0.21 |
| csharp | 8.0.427 |
| rust | rustc 1.99.1 (58cf8f9c3 2026-10-13) |
| php | PHP 8.2.35 (cli) (built: Oct 21 2026 06:29:51) (NTS) |
| bash | GNU bash, version 5.2.15(1)-release (x86_64-pc-linux-gnu) |
| sql | 3.40.1 2022-12-28 14:03:47 df5c253c0b3dd24916e4ec7cf77d3db5294cc9fd45ae7b9c5e82ad8197f3alt1 |
| assembly | GNU assembler (GNU Binutils for Debian) 2.40 |

## Initial failures and corrections

The [initial acceptance run](https://github.com/JasonStys/code-flow-studio/actions/runs/42869521158) is retained as failed evidence. All twelve languages already passed 6/6 ordinary cases in both source lanes and private execution. The new validator incorrectly assumed that every tool used the same line/count and collector-exit conventions. It was corrected without changing target sources, approved oracles, installed runtime or worker implementation.

1. coverage.py can retain a module-docstring trace event that it excludes from executable-statement counts. Only the exact AST-proven one-line difference is allowed.
2. PHP Xdebug can report an implicit return at an empty terminal source line. Bounds now match the app/editor's original newline convention.
3. Coverlet 8.0.1 maps a nonzero target exit to collector exit 1. The C# malformed-price case correctly exits 2 in ordinary execution; instrumentation is honestly retained as **partial coverage**. Exact instrumented nonzero target exit is not independently recoverable. All successful collector exits, identities and generated reports are checked; unrelated collector errors and false fully-measured labels are rejected.
4. The frozen-service probe initially expected a list for `iteration_history`; the actual API returns the SQLite `Store.timeline` dictionary. The checker was fixed and its tests now exercise real temporary SQLite persistence and export identity instead of a mirrored mock schema.
5. The separate version probe now calls the actual trusted worker runtime-directory initializer before invoking tools; isolation permissions were not widened.

Four original report snapshots remain unchanged in [observed regression fixtures](../../tests/fixtures/compiler-reports-042.json). Full source/result/export digests, explicit wrong-answer controls, authored failure exits and exact unused/uncovered anchors prevent a completed process or fabricated summary from counting as a pass. See the [test plan and measurement semantics](../compiler-execution.md).

## Environment and remaining limits

- No PC Docker changes, local compiler execution, real account/data upload, external AI API or paid provider call occurred in this validation.
- C# retains the stated partial collector coverage for approved nonzero rejection. Other eleven realistic positive adapters reported measured coverage. SQL statement starts, Bash command-entry and assembly debug-backed instructions retain their documented meanings.
- Images were freshly built from identified source; mutable upstream base tags/APT packages mean these are not historical image-byte claims. Timing includes startup/shared-runner noise and is not empirical Big-O or a cross-language ranking.
- The redundant broad local Windows unit attempt was stopped after ten minutes without a result and is not claimed as passed. The complete hosted Linux suite and separate genuine native package checks passed.
- Unsupported frameworks, dependencies, ISAs, every possible bug, production hostile multi-tenant safety and live AI quality are not established by these examples.
- Small synthetic Actions evidence has three-day per-upload retention; the dated summary is committed here. No old run/artifact/cache was deleted and no account retention policy changed.
