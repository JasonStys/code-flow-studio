# ADR: language-native evidence instead of a universal inferred coverage score

Status: accepted for 0.3.0. Author: Jason Stys.

## Context and decision

The existing flat CLI adapters compiled eleven non-Python languages but retained Python-only coverage and Python-aware unused candidates. Compiler exits alone cannot identify untested lines or prove unused code. A universal textual heuristic would produce misleading locations and denominators.

Use each language's real compiler/analyzer and instrumentation inside the existing restricted worker, with bounded parsers and original-snapshot hashes. Keep benchmarks on baseline binaries, before instrumentation. Retain per-tool branch IDs/counts instead of inventing source-to-source arcs. Separate static candidates from dynamic non-execution. Preserve unknown, partial, blocked and truncated states across JSON, HTML and UI. Extend fixed packaged worker resources and test their presence in actual native apps.

## Alternatives and consequences

- Host-side execution would be simpler to install but violates the existing isolation boundary and the user's instruction to leave Docker unchanged; rejected.
- One generic coverage scanner cannot infer executable lines, compiler source maps, SQL statement semantics or assembly debug data reliably; rejected.
- One huge generalized build framework could support more dependency ecosystems but adds unbounded package/network/configuration behavior; deferred. Keep documented flat-file contracts and fixed tool configuration.
- Native tools increase trusted image size/build cost and maintenance/licensing obligations. Official Rust plus matching LLVM/profile runtime is needed because Debian's compiler lacks profiling support. Pin tools/lockfiles/checksums, audit dependencies and require real independent location oracles for every adapter.
- Bash, SQL, assembly and optimized/generated code have narrower semantics, documented in [the measurement matrix](polyglot-locations.md). Missing debug data or unloaded files do not become full coverage. Same-UID worker interference remains possible; this is not a hostile-code SaaS or attested correctness system.

## Acceptance and rollback

Pure parser tests are separate from real isolated compiler tests. All adapters require known executed/missed lines and unused candidates at independently authored exact locations. Baseline stdin contracts, prior sandbox probes, Python regressions, private-account/browser flows and actual native package launches remain required. No database migration is introduced. Revert source/install the prior tested app and rebuild its corresponding trusted worker if exact-location, privacy or sandbox regressions occur; preserve encrypted backups and immutable historical evidence.
