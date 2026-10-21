# Polyglot locations, coverage and unused-code candidates

By Jason Stys. Version 0.3 adds native evidence to every existing execution adapter. This is a flat-file CLI workbench, not universal framework/build-system support. HTML/CSS syntax highlighting is not a separate executable adapter. Checks run only in the restricted, network-disabled Linux worker; static Python review remains available without it.

## Use and interpret the results

Rebuild the reviewed worker on an **already working, authorized** local Docker engine:

```sh
docker build -t code-flow-worker:0.2.0 runner
```

The new image tag prevents silently reusing the old Python-only coverage worker. No Docker repair, privileged container, host execution fallback, additional network or host filesystem access is introduced. Installed UI packages include the worker sources and locked tool manifest, not an installed Docker engine or container image.

Choose a supported language/entry, upload the flat source files, approve independent CLI cases, save and run. Evidence → **Exact source locations** shows compiler/runtime references and normalized native unused candidates. **Uncovered source locations** shows original filenames, missing lines and language-specific measurement labels. Download HTML/JSON/ZIP to retain all bounded records and the analyzed source snapshot. Findings refer to that immutable revision, not a subsequently edited file.

| Language | Actual coverage collector | Unused-code candidates and limitations |
|---|---|---|
| Python | coverage.py 7.11 line/branch arcs | Existing non-executing AST/symbol-table checks for imports, locals, functions and directly unreachable statements. |
| JavaScript | Node 24 V8 ranges, v8-to-Istanbul 9.3 source mapping | ESLint 10.13 `no-unused-vars`, fixed configuration. Dynamic usage and external consumers require review. |
| TypeScript | tsc 5.9.3 source maps + Node/V8, mapped to original `.ts` | typescript-eslint 8.72 `no-unused-vars`, not type-aware whole-program analysis. Compiler errors/runtime frames retain original locations. |
| C / C++ | Separate `-O0 -g --coverage` build; GCC/gcov JSON executable lines and branch IDs | GCC `-Wall -Wextra -Wunused` structured diagnostics for the entry translation unit and included headers. Unincluded translation units are not independently built. Public APIs may be intentionally unreferenced. |
| Rust | Separate rustc 1.99.1 instrument-coverage build; matching bundled LLVM profile merge/export | rustc `unused`/`dead_code` structured primary spans; standalone edition-2021 crate only. Official Rust supplies the profiling runtime missing from Debian's rustc package. |
| Java | Separate debug build + JaCoCo 0.8.15 instruction-backed lines and branch counts | PMD 7.28 fixed unused local/parameter/private-field/private-method rules. Unprovided callers, reflection and public APIs are outside this contract. |
| C# | Separate .NET 8 debug build + Coverlet 8.0.1 portable-PDB sequence points | Compiler CS0168/CS0169/CS0219/CS0414 unused locals/private fields. **Not** a general unused-method/class analyzer. |
| PHP | Xdebug opcode-backed source-line coverage, enabled before compiling the target | PHPMD 3.0 `unusedcode` rules; dynamic calls/reflection need review. |
| Bash | shfmt 3.6 typed AST command-entry lines + real Bash xtrace entry records | ShellCheck unused-variable/unreachable/unused-function rule selection; rule availability depends on installed ShellCheck. Not expression, branch, command-success or arbitrary subshell proof. A script can disable tracing; shared-worker interference is a limitation. |
| SQLite SQL | SQLite `complete_statement` parser and in-memory execution of original statement chunks; **completed top-level statement-start lines** | SQLFluff 4.4 SQLite ST03 unused CTE and AL05 unused table alias. Not general dead-query/column/schema analysis, row coverage, trigger-body coverage, expression coverage or portability proof. |
| GNU x86-64 assembly | DWARF executable instruction-line universe + Valgrind Callgrind instruction hits | Review-only unreferenced **named local-label** candidates. Exported, referenced and numeric labels excluded. Fall-through and dynamic linkage can be intentional. Not a universal unused-instruction proof. Missing debug records remain unknown. |

These are different denominators, not interchangeable scores. V8 block-derived lines can include non-statement lines; SQL lines can contain several statements and count as completed when any mapped statement completes. A SQLite error is anchored to the **start of its statement**, not a claim about the exact failing token inside it. Instrumentation can change behavior. Negative cases may legitimately expect a nonzero exit code; incomplete/time-limited reruns are partial, not complete measurements.

## Schema and safety

`unused` contains `status`, `tool`, review-only `findings`, truncation and scope. Native candidates have `file`, one-based `line`/tool column, rule `code`, `message`, `source_sha256`. The controller rebinds these to supplied source paths/ranges/hashes before putting them in `diagnostics` with `stage: unused-code`. No candidate triggers deletion. Tool parse/launch failures remain blocked; an empty list is not a clean-code certification. Compiler/runtime locations still use the [bounded log parser](located-diagnostics.md); wrong answers without genuine references stay explicitly unlocated.

`coverage` retains `entry` for compatibility and adds `tool`, `metric`, approved rerun `cases`, `requested_cases` and per-file records. Each measured record has a source hash, summary, missing/executed lines, truncation, and optional native `branch_points`. Native branch records retain source line plus tool ID/count/ratio: **not** invented source-to-source arcs. Python alone retains its genuine `missing_branches` arcs. Unloaded JS/TS/PHP files and absent debug/source records remain `not-measured`, never silently full/zero coverage.

Timing/RSS samples come from baseline binaries **before** extra instrumentation. Coverage is approved CLI reruns, not supplied/generated pytest execution, AI test quality, fuzz coverage or whole-program correctness. Compilers can omit optimized/uninstantiated/generated code. Frameworks, dependencies not installed in the image, other architectures and arbitrary binary/doc formats require reviewed integrations.

Existing 150-second worker budget, 180-second broker timeout, 1 GiB memory, two CPUs, 128 PIDs, private 256 MiB tmpfs, read-only root, dropped capabilities, UID 65534 and no network remain unchanged. Reports are bounded to 8 MiB before parsing; exported location lists share 20,000 entries; diagnostics cap at 1,000 and readable tables at 200. Missing/truncated lists do not establish full coverage. Bash expansion traces are transient private worker files; only source anchors enter coverage, not their expanded command text. JaCoCo's known external DTD declaration is removed without fetching; arbitrary DTD/entity declarations are rejected. Uploaded JS source-map directives are not followed; TypeScript maps come from this worker's fixed compiler build. Native tools never load uploaded linter plugins/configuration or import target modules in the controller.

Targets and tools share an unprivileged UID and writable job tmpfs. Malicious targets can forge logs/reports, stop instrumentation or interfere with tooling. Hashes bind a snapshot, **not** a trusted attestation. Do not deploy this as a public hostile-code service. Credentials, account data and provider APIs remain outside workers. Existing encrypted histories require no migration and are not rewritten; rerun old revisions for new evidence.

## Maintenance and complexity

`runner/language_checks.py` normalizes bounded native reports; `node_checks.cjs` uses fixed ESLint/V8 libraries; `sql_runtime.py` preserves source anchors in the SQLite driver; `php_coverage.php` starts Xdebug; `bash_coverage.sh` records command entries; `java-unused.xml` fixes the PMD rules. `runner/tools/package-lock.json` pins JS analyzer dependencies. Image downloads of JaCoCo, PMD and PHPMD are versioned and SHA-256 verified; Coverlet is pinned to a .NET-8-compatible version. Debian supplies matching native compilers/LLVM and package security updates. No additional native tooling is bundled into the desktop host runtime; tool licenses stay in the built image/distribution and apply to those components.

Normalization is linear in bounded report records plus sorting retained line lists (`O(L log L)`); original line limits/hashes are precomputed once per source. C# condition ratios retain a case index rather than falsely merging ratios into a joint branch result. Native compilation, analysis and profiling have tool-dependent costs and are bounded by time/memory, not assigned a fabricated source-level Big-O grade. Model suggestions and measurements remain distinct.

## Tests and primary references

`tests/test_native_locations.py` uses inert reports to test source binding, malformed/oversized XML/JSON, coverage union/truncation, native branch IDs, assembly exports, SQLite trigger/comment/string boundaries, unavailable tools and escaped downloads. `examples/language_locations.py` contains independently authored unused/missed-line oracles for **all eleven non-Python adapters**; `scripts/worker_checks.py` runs them under the actual sandbox and requires exact locations/hashes plus genuinely measured executed/missing lines. Browser contract fixtures separately verify presentation and unavailable/partial states; mocks do not count as native collector validation. Results are recorded in [polyglot validation](validation-polyglot.md).

Additional regressions cover imported JS/TS helper locations and unloaded modules; Unicode separators inside assembly data must not shift physical line numbers; invalid non-SQL Unicode whitespace is retained for SQLite to reject. The Bash AST walker uses an iterative traversal, and report-decoder nesting failures remain explicitly blocked rather than crashing the worker.

Primary tool contracts: [Node V8 coverage](https://nodejs.org/api/cli.html#node_v8_coveragedir), [v8-to-Istanbul](https://github.com/istanbuljs/v8-to-istanbul), [ESLint unused variables](https://eslint.org/docs/latest/rules/no-unused-vars), [typescript-eslint unused variables](https://typescript-eslint.io/rules/no-unused-vars/), [GCC gcov JSON](https://gcc.gnu.org/onlinedocs/gcc/Invoking-Gcov.html), [Rust instrumentation](https://doc.rust-lang.org/rustc/instrument-coverage.html), [LLVM coverage export](https://llvm.org/docs/CommandGuide/llvm-cov.html), [JaCoCo counters](https://www.jacoco.org/jacoco/trunk/doc/counters.html), [PMD Java rules](https://pmd.github.io/pmd/pmd_rules_java_bestpractices.html), [Coverlet CLI](https://github.com/coverlet-coverage/coverlet/blob/master/Documentation/GlobalTool.md), [Xdebug coverage](https://xdebug.org/docs/code_coverage), [PHPMD unused rules](https://phpmd.org/rules/unusedcode.html), [shfmt](https://github.com/mvdan/sh), [ShellCheck](https://www.shellcheck.net/wiki/SC2034), [SQLite completeness parser](https://docs.python.org/3/library/sqlite3.html#sqlite3.complete_statement), [SQLFluff unused CTE](https://docs.sqlfluff.com/en/stable/reference/rules/structure.html), [Callgrind format](https://valgrind.org/docs/manual/cl-format.html).
