# File/line diagnostics and coverage

By Jason Stys. The workbench reports **where a tool observed a problem**, not a promise to find every bug or infer every root cause. Findings refer to the analyzed/saved source snapshot, never silently to a changed editor draft. No submitted program is imported or executed by static review.

Version 0.3 extends the original Python contract with [native coverage and unused checks for all other execution adapters](polyglot-locations.md). See that matrix for language-specific semantics and [current validation](validation-polyglot.md); the older validation report records the earlier release only.

## Use it

1. Upload the flat source files or edit them in Workspace. Select **Static review · no execution**. The Evidence view lists original filename, one-based line/column, check code and explanation. This works without Docker or a configured AI provider.
2. Approve independent stdin/stdout cases, save the revision and run checks with the updated isolated worker. Evidence adds compiler/runtime references, native unused candidates and **Uncovered source locations** with a language-specific metric. Rebuild the worker after updating source: `docker build -t code-flow-worker:0.2.0 runner`. This command is for an already working, authorized Docker engine; the application never repairs Docker or falls back to executing targets on the host.
3. Download JSON, HTML or ZIP. HTML now includes a readable location table and per-file missing-line lists before raw evidence. JSON and ZIP retain the same structured fields and source/test snapshots. Check a file's `source_sha256` against that snapshot before applying a finding to another version.

## What is checked

| Evidence | Implementation and boundaries |
|---|---|
| Python syntax | Parse and compile **all supplied `.py` files and the Python entry** in memory, without running the returned code object. Structural errors such as a module-level `return` are included. Normal syntax errors have a filename, line and character column. Parser/resource errors with no valid line are explicit file-level `static.files` limitations, not fabricated locations. Binary attachments and non-Python data are not parsed as Python. |
| Python risks | AST checks for dynamic `eval`/`exec`, literal `shell=True`, direct `pickle.load/loads`, and obvious embedded secret assignments. Comments and string examples do not count as calls. Secret values are omitted from warning messages. Aliases/dynamic calls and comprehensive taint/security analysis are outside this lightweight scanner. |
| Unused imports/locals/functions | Compiler symbol tables plus AST binding locations. `_`-prefixed intentional names, parameters, class APIs, closure captures, explicit `__all__` exports, decorated callbacks and direct supplied-file references are preserved. Imports can have side effects; public functions can be called externally. Findings are **possibly unused**, require human review and never trigger deletion. Dynamic reflection/exports and unprovided callers are not decidable here. Cross-project name matching is intentionally conservative and can miss unused names. This check is Python-specific; other adapters may separately emit their own compiler warnings. |
| Unreachable code | Python statements directly following unconditional `return`, `raise`, `break` or `continue` in the same suite. This is not whole-program reachability, branch-condition proof or a claim about every dead path. |
| Other text | Existing bounded risk-pattern hints retain **per-file**, not concatenated-project, offsets. These are not language-aware unused-code or complete syntax checks and can match examples/comments. |
| Compiler/runtime locations | Recognize source references from Python/pytest, GCC/Clang/assembler, Node, TypeScript, Java stack traces, C#, Rust, PHP and Bash. TypeScript emits source maps and Node uses them so mapped runtime frames refer to original `.ts` lines. Generated test/fuzz-harness references are labeled `artifact: generated`, not confused with target source. Only recognized, in-range filenames from this revision are accepted. Unsupported/optimized/stripped frames and SQLite errors without source lines stay explicitly unlocated; raw logs are preserved. |
| Wrong answers/hangs | Test-case failures and timeouts remain failures. Unless a tool supplies a genuine source reference, `unlocated_failures` names the stage and states that no root-cause line was inferred. A failed output oracle is not sufficient evidence to blame a particular statement. |
| Coverage | Real coverage.py line/branch measurement over approved CLI cases, retained for every supplied Python file represented in the tool's report, including unimported files when coverage.py discovers them. Other adapters use [native collectors](polyglot-locations.md), with exact source lines and explicitly different metrics. Generated pytest cases are **not** part of these coverage measurements. Absent records are `not-measured`, not zero/full coverage. |

“Uncovered” means an executable line was not exercised by these measured inputs. “Unused” is a static candidate with no recognized reference. “Unreachable” here means a direct control-transfer observation. None implies the others. Blank lines/comments are not uncovered executable statements. Missing branch arcs are `[from_line, to_line]`; a negative destination is coverage.py's function-exit sentinel, not an invalid source line.

## Machine contract and limits

`static.findings[]` includes `file`, `line`, `column`, `code`, `severity`, `origin`, `message`, `source_sha256`. Python AST byte offsets are converted to one-based Unicode character columns; compiler columns retain their own tool-reported convention. A source hash binds the reference to analyzed content; it is not an attestation that a malicious target cannot forge its own logs.

`diagnostics[]` adds tool-reported locations and their `stage`/`artifact`. `unlocated_failures[]` explains failures with no recognized source reference. Tool output is bounded, untrusted text, escaped in HTML/React; forged references are not proof of a defect. Raw logs retain the original surrounding exception/compiler context.

`coverage.entry` preserves the old entry-summary contract. `coverage.files[filename]` adds `status`, `summary`, `source_sha256`, `missing_lines`, `missing_branches`, `executed_lines`, `excluded_lines` and `truncated`. Source hashes refer to the submitted snapshot; same-user target interference remains a [worker trust limitation](security.md). Coverage configuration is fixed (`--rcfile=/dev/null`), not selected by an uploaded config.

Static findings and tool references are each capped at 1,000; the UI/HTML tables show the first 200 with an explicit limit notice and raw exports retain all collected items. Coverage shares a 20,000-entry budget across files, prioritizing all missing locations before executed/excluded lists. Truncation flags and original tool summaries stay visible; empty truncated lists never establish full coverage. Older saved reports are not rewritten: rerun the saved revision to obtain new fields. Legacy UI/HTML explicitly says when filenames or missing-line lists are unavailable. No schema migration or user-history deletion is required.

## Verification and references

`tests/test_locations.py` covers filename/line regressions, auxiliary syntax, Unicode columns, inert source, unused-code boundaries, toolchain log formats, unknown/malicious paths, output bounds, API/download escaping and coverage-field preservation. Coverage-function unit tests mock the compiler CLI; they do not claim new real compiler execution.

`scripts/worker_checks.py` separately asserts genuine isolated multi-file coverage (including an unimported module), missing branch `[2, 3]`, runtime failure `main.py:2`, compiler failure `main.cpp:1`, original TypeScript runtime locations, and unlocated wrong-answer behavior. Browser tests cover the real static-review API and a clearly labeled UI-only coverage fixture across Chromium, Firefox and WebKit. See [the validation report](validation-locations.md) for measured results.

Primary references: [Python AST location conventions](https://docs.python.org/3/library/ast.html#ast.AST), [compiler symbol tables](https://docs.python.org/3/library/symtable.html), [coverage.py branch arcs](https://coverage.readthedocs.io/en/7.11.0/branch.html), [coverage.py JSON output](https://coverage.readthedocs.io/en/7.11.0/commands/cmd_json.html), and [Node source-map support](https://nodejs.org/api/cli.html#--enable-source-maps).
