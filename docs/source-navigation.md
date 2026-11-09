# Inspect exact evidence without losing a draft

Code Flow Studio binds a finding or uncovered line to a file **and its measured content**. A filename/line alone can point at unrelated code after editing. The source inspector verifies SHA-256 over the original UTF-8 bytes and checks the physical line bounds before showing a read-only snapshot. It neither executes target code nor opens a filesystem path or external URL.

## Developer workflow

1. Upload or edit a project. Run **Static review** for non-executing source checks, or save/run with the isolated worker for execution and coverage evidence.
2. Open **Evidence**. Select an **Evidence file**, then optionally **Unused-code candidates**. Findings retain stage, tool, code, location and source fingerprint. A reference is not proof that the selected line caused the failure; review its context and the tool's limitations.
3. Select a linked source line or missed-coverage line. The inspector verifies the captured revision, shows the file, artifact kind and exact line, and highlights that whole line. Expand **Verified SHA-256** when comparing evidence. Tool columns keep their declared units; no byte/code-point/UTF-16 conversion is guessed.
4. Use **Browse snapshot line** to examine surrounding code. Zero, fractional, negative or out-of-range lines show an error. Browsing does not label additional lines as bugs or uncovered code.
5. **Edit matching draft at line …** is enabled only when the current source bytes still match. Navigation rehashes the draft again, selects the exact file and focuses the line. Further edits clear the old evidence highlight. Evidence retains its original snapshot.

A current draft that differs remains editable in Workspace, but its old evidence cannot direct edits into changed line numbers. Rerun static review or save/run a new revision to measure the new content. Switching projects/history, locking an account or starting a new measurement clears the previous inspector context. No source text is added to browser storage or a provider request by inspecting it.

## Honest unavailable states

| Situation | Behavior |
|---|---|
| Legacy report without a valid 64-hex SHA-256 | Plain line text; rerun to obtain navigable evidence. |
| Hash mismatch, unknown artifact or missing revision | Explicit blocked explanation; no alternate filename/path is opened. |
| Binary/base64 fixture | No source-line navigation. Retain the fixture and use an appropriate harness. |
| Reported line outside verified content | Blocked rather than clamped to an unrelated line. |
| Generated test/harness | Inspect only the separately captured `test_generated.py`, `fuzz_harness.py` or `fuzz_harness.cpp` artifact. It cannot overwrite a same-named supplied source file. |
| Wrong answer with no located reference, missing collector or partial coverage | Existing unlocated/partial state remains. Navigation invents no location or coverage. |
| Browser lacks secure-context WebCrypto | Hash verification is unavailable; use the loopback app or HTTPS. |

Physical lines use CRLF, CR or LF boundaries, preserving their original bytes for the hash. Unicode line-separator characters remain literal source content. Invalid lone surrogates are rejected because UTF-8 replacement would destroy exact identity.

## Bounds and trust

Navigation hashes at most 1 MiB per source. The view renders at most 200 finding rows, 32 coverage files and 200 missed-line links per file, with truncation notices; complete retained records remain available in reports. File filters reflect at most 64 names. These are rendering bounds, not assertions that an unshown issue was resolved. The manifest/backend input limits and existing collector bounds still apply.

Snapshots remain in component memory and the existing encrypted revision flow. Worker isolation, immutable approved oracles, provider consent and account authorization are unchanged. There is no host compiler/execution fallback. Static review and source browsing work when Docker is unavailable; running submitted code still requires the trusted isolated worker.

The editor integrates Monaco's native model event with one narrowly scoped synchronous React draft update. This prevents rapid keystrokes being lost when controlled state trails the external editor model. The [React integration guidance](https://react.dev/reference/react-dom/flushSync) describes the trade-off; this is confined to source-model changes and is regression-tested through actual typing, rather than applied to polling or the rest of the interface.

Created by Jason Stys. See the [code index](code-index.md) for exact source symbols and the [validation report](reports/practical-workflows-2026-11-09.md) for observed evidence and remaining platform checks.
