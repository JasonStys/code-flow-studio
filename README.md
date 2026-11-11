# Code Flow Studio

An independently written successor to a group AI-in-SDLC capstone: a local-first development workbench for isolated polyglot checks, configurable AI proposals, and replayable revision evidence.

**Source version 0.4.4: reviewed desktop runtimes and exact instrumented C# exits.** The desktop service uses Python 3.14.10 and Electron 44.11.0; its frozen entry refuses an unreviewed interpreter before opening accounts. The separately isolated worker uses a digest-pinned Python 3.12.16 base. The 0.4.3 C# fix is retained: the worker separates the program's real exit status from the coverage collector, so approved nonzero returns can have fully measured coverage. Read the [release notes](docs/releases/v0.4.4.md) and [C# fix and validation](docs/csharp-coverage.md). Create an account, unlock your encrypted source/history workspace, and use the same interface in the desktop app or your browser. Filter diagnostics by file or unused-code category, select an exact line, inspect its read-only evidence snapshot, and open the editable draft only when its SHA-256 still matches. No public backend, shared login, analytics, ads or cloud AI calls are enabled by default. By [Jason Stys](https://github.com/JasonStys); [contact via LinkedIn](https://www.linkedin.com/in/jason-stys-31b30b351/).

Download OS-specific installers/portable packages from [Releases](https://github.com/JasonStys/code-flow-studio/releases). Read [private-account operation](docs/private-accounts.md), [current validation](docs/validation-polyglot.md), [historical Python-location validation](docs/validation-locations.md) and [security boundaries](docs/security.md). Packages are unsigned. This is a local development tool, not a public hostile-code SaaS sandbox or an autonomous correctness oracle.

## The development loop

1. Upload flat source/data files or edit code in the offline Monaco editor. Select a compiler adapter and entry point. Write requirements and approve independent stdin/stdout cases.
2. Optionally ask a configured model to generate code, tests, improvements or live suggestions. Source transmission is opt-in. Responses are schema-validated **unverified proposals**, not executed results.
3. Save an immutable revision and run it through the container broker. Compilation, approved cases, supplied pytest harnesses, native unused checks/coverage, Python mutation, bounded fuzzing and exploratory benchmarks produce separate evidence.
4. Review findings and add a candidate revision. In **Evidence**, filter by file/category and select a diagnostic or missing-coverage line. The inspector verifies the retained source fingerprint before displaying it. Browse nearby lines or open a matching current draft; changed drafts are never overwritten. Baseline expectations and existing tests cannot be removed. Compare results under the same environment and adjustable runtime/memory/readability/footprint preferences.
5. Download escaped HTML, machine-readable JSON and a source/test/harness/report ZIP. Reopen saved revisions and replay them.

## Hosted compiler acceptance

The [realistic compiler suite](docs/compiler-execution.md) covers all twelve executable adapters with 72 independently authored input/output cases, deliberate compiler/runtime/wrong-answer controls, exact unused/uncovered anchors, and encrypted private-report replay. Its historical lane preserves the published 0.4.2 baseline, including its C# limitation; the current 0.4.4 lane retains the corrected target/collector protocol and fully measured approved C# cases. Read the [0.4.2 observations](docs/reports/hosted-compilers-2026-11-10.md) and [0.4.3 C# validation](docs/reports/csharp-coverage-2026-11-10.md). Those are dated observations; a new release must pass its own exact-source compiler and native gates. Published historical packages are unchanged. Building or installing this desktop application does not install, start or repair Docker on an end user's PC.

## Features and limits

**Located diagnostics:** static review and execution evidence list original filenames and local line locations, with snapshot hashes. Python checks include auxiliary-file syntax, possibly unused imports/locals/functions and directly unreachable statements. Every other supported execution language now has native unused-code candidates and actual language-specific coverage. UI/HTML show missed source lines, genuine branch arcs or native branch IDs/counts, and explicit partial/unknown states. SQL measures completed statement starts, Bash command-entry lines and assembly instruction-backed debug lines—not universal statement/branch coverage. Unsupported locations and wrong-answer failures without source references stay unlocated. See the [language-by-language tools and limits](docs/polyglot-locations.md), [file/line contract](docs/located-diagnostics.md) and [validation](docs/validation-polyglot.md). No tool guarantees discovery or root-cause localization of every bug.

| Feature             | Implemented contract                                                                                                                                                                                                                                                                                                                                                                                             |
| ------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Private accounts    | Real alias/password registration, hashed sessions and one-use login recovery. Independent browser-derived vault key, authenticated AES-256-GCM locked source/history/provider archives and per-session unlock proof. No developer plaintext read API. Trusted local service and OS can access active plaintext; not browser-only E2EE.                                                                           |
| Desktop application | Electron shell and bundled Python service; one-click Windows installer plus OS-specific Linux/macOS builds. No IntelliJ or separately installed Python required for the UI. Unsigned development packages.                                                                                                                                                                                                       |
| Web application     | Same responsive editor/API served on loopback. Narrow-screen browser support; not a native Android/iOS installer or public hosted service.                                                                                                                                                                                                                                                                       |
| Polyglot execution  | Fixed CLI adapters for Python, JavaScript, TypeScript, C/C++, Java, C#, Rust, PHP, Bash, SQLite SQL and GNU x86-64 assembly. Actual toolchains live inside the worker image.                                                                                                                                                                                                                                     |
| Testing             | Approved CLI oracles and reviewed pytest harnesses, including subprocess harnesses for non-Python targets. 48-category applicability catalog; human, hardware, cloud/load and specialized tool checks need independent integrations.                                                                                                                                                                             |
| Coverage/mutation   | Exact original source locations from native collectors for all twelve adapters; per-file hashes, missed/executed lines, language-specific metric labels and honest unknown/partial states. Separate from baseline timing/RSS. Python additionally supports up to eight operator mutants. Approved CLI coverage excludes generated pytest; no fabricated MC/DC, universal dead-code or universal mutation scores. |
| Fuzzing             | Seeded black-box generation, mutation, dictionary, boundaries and CSV/SQL grammar; instrumented libFuzzer/AFL++ for reviewed C/C++ harnesses and Atheris for Python harnesses. Differential/metamorphic/stateful relations require custom oracles.                                                                                                                                                               |
| AI routing          | Account-owned OpenAI-compatible, Anthropic and Ollama endpoints/keys, four task routes and destination-version-bound consent. Keys stay server-side after explicit settings submission, outside histories/exports/workers. Protocol tests use mocks, not a claim of live model quality.                                                                                                                          |
| Metrics/ranking     | Repeated process wall times, peak child RSS, source bytes and transparent long-line proxy. Passing independent cases is mandatory. No syntax-based Big-O claims or automatic “best” model claims.                                                                                                                                                                                                                |
| Training            | Rights-checked, project-disjoint JSONL preparation, actual small causal-model creation or approved local-model fine-tuning, safe-tensor output and authenticated local inference API. Tiny synthetic smoke training is not a useful general coding model.                                                                                                                                                        |
| CI                  | SHA-pinned, read-only Actions validate controller/browser behavior, real worker scenarios, training smoke and native packages. Push analysis retains generated tests/candidate evidence when a provider is explicitly configured; never auto-commits model changes.                                                                                                                                              |

Binary formats can be retained as fixtures. There is no promise to understand every document, image, encrypted archive or binary. Supply text requirements and explicit harnesses for formats without a parser; unsupported extraction must not silently succeed.

The [source inspection workflow](docs/source-navigation.md) explains stale/legacy references, generated artifacts, bounds and review steps. [Observed local validation](docs/reports/practical-workflows-2026-11-09.md) separates actual browser/native journeys from UI report-contract fixtures and compiler checks that require isolated CI workers.

## Run and install

Version 0.4.4 retains bounded worker-report reads, verified source review and safe
local shutdown, and corrects the final draft-verification job's required metadata
visibility. The [current runtime validation](docs/reports/desktop-runtimes-2026-11-10.md),
[historical 0.4.2 release notes](docs/releases/v0.4.2.md)
and [full-main finding/validation report](docs/reports/codeql-main-fixes-2026-11-09.md)
describe the bounded worker reader and the fresh native/download checks required
before release promotion. The 0.4.1 draft passed native builds but its final
metadata check lacked GitHub's required draft visibility; that draft and all its
assets are preserved. See the [observed CI fault and narrow correction](docs/reports/draft-release-visibility-2026-11-10.md).
Check Releases for the currently published downloads; a source version alone does not replace one.

For end users, use the checksummed OS-specific packages in Releases. The UI runtime is bundled. Open the app's **Code Flow → Open local website** menu for browser use; no login token appears in the URL. Compiler jobs require an isolated local Unix/named-pipe Docker engine and the trusted worker image. Missing isolation is blocked, never passed; there is no host-execution fallback. Save/edit/static review/history/help remain usable without Docker.

Source-development instructions, provider setup, first-run diagnostics and packaging are in [setup](docs/setup.md). All documentation is indexed in [docs](docs/README.md). Original private capstone code, team files, API credentials and vendor trees are not distributed here.

## Source map

| Location                                                                                                | Responsibility                                                                                                                                                                          |
| ------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `studio/accounts.py`, `studio/permissions.py`                                                           | scrypt logins, session/recovery digests, bounded attempts and private per-OS data permissions.                                                                                          |
| `studio/private_api.py`                                                                                 | Account-only HTTP/CSRF boundary, own provider settings, per-session key proof, backup/recovery/deletion and scoped controller proxy.                                                    |
| `studio/private_workspace.py`, `studio/vault.py`                                                        | Single-instance ownership, account-specific engine lifecycle, authenticated streaming encryption, SQLite online snapshots and safe restoration.                                         |
| `studio/private_cli.py`                                                                                 | Token-free loopback account service, dedicated data root and exact-parent graceful shutdown monitor.                                                                                    |
| `ui/Account.tsx`                                                                                        | Sign-in/unlock/recovery, contextual help, encrypted backup, private AI configuration and creator contact.                                                                               |
| `studio/models.py`                                                                                      | Validated flat-file, project, case, preference and AI proposal schemas; size/path limits.                                                                                               |
| `studio/api.py`                                                                                         | Authenticated loopback API, bounded jobs, history, reports, comparisons and AI tasks.                                                                                                   |
| `studio/store.py`                                                                                       | SQLite transactions, append-only revisions, immutable baseline oracles and interrupted-job recovery.                                                                                    |
| `studio/execution.py`                                                                                   | Fixed container flags, readiness checks, output/deadline bounds and exact owned-container cleanup.                                                                                      |
| `studio/analysis.py`                                                                                    | Non-executing source heuristics and correctness-gated weighted comparisons.                                                                                                             |
| `studio/source_checks.py`, `studio/locations.py`, `ui/Locations.tsx`                                    | Python syntax/unused/unreachable candidates, bounded tool-output source references, file/category filters and clickable exact-location/coverage evidence views.                         |
| `ui/source-navigation.ts`, `ui/SourceInspector.tsx`                                                     | Exact UTF-8 SHA-256 verification, bounded immutable source inspection, nearby-line browsing and guarded navigation to an unchanged current draft.                                       |
| `studio/providers.py`                                                                                   | Private provider configuration, task routes, consent, bounded requests and proposal schema validation.                                                                                  |
| `studio/catalog.py`                                                                                     | All 48 supplied test categories with applicability/integration requirements.                                                                                                            |
| `studio/reports.py`                                                                                     | Escaped, inert HTML/JSON/ZIP evidence exports.                                                                                                                                          |
| `studio/cli.py`                                                                                         | Shared web launcher and manifest-to-report CI command.                                                                                                                                  |
| `runner/Dockerfile`, `runner/worker.py`                                                                 | Trusted compiler image and isolated compile/test/coverage/mutation/fuzz/benchmark execution.                                                                                            |
| `runner/language_checks.py`, `runner/node_checks.cjs`                                                   | Bounded native tool adapters, source binding, fixed ESLint configuration and V8 source-map conversion.                                                                                  |
| `runner/sql_runtime.py`, `runner/php_coverage.php`, `runner/bash_coverage.sh`, `runner/java-unused.xml` | SQLite statement anchors, pre-compilation Xdebug hook, transient Bash trace collector and fixed PMD unused rules.                                                                       |
| `runner/tools/package.json`, `runner/tools/package-lock.json`                                           | Pinned/audited worker-only JS analyzer dependencies; not desktop runtime dependencies.                                                                                                  |
| `ui/App.tsx`                                                                                            | Workspace, cases, priorities, live suggestions, proposal approval, evidence and history views.                                                                                          |
| `ui/main.tsx`, `ui/api.ts`                                                                              | Offline editor worker registry and authenticated same-origin client/downloads.                                                                                                          |
| `ui/demo.ts`, `ui/types.ts`                                                                             | Synthetic CSV example and renderer contracts.                                                                                                                                           |
| `ui/index.html`, `ui/style.css`                                                                         | Local HTML entry and responsive accessible layout.                                                                                                                                      |
| `desktop/main.cjs`                                                                                      | Sandboxed Electron renderer and private bundled-service lifecycle.                                                                                                                      |
| `studio/native_server.py`, `studio/completed_offload.py`                                                | Finite HTTP drain, completed cancellation cleanup and coherent account/vault transitions before normal sealing.                                                                         |
| `training/dataset.py`, `training/train.py`, `training/serve.py`                                         | Provenance/split validation, parameterized real training, local model API.                                                                                                              |
| `examples/projects.py`, `examples/web-demo.project.json`                                                | Compiler-contract fixtures and the exact synthetic CSV source/manifest used by the UI, checked in CI.                                                                                   |
| `examples/language_locations.py`, `tests/test_native_locations.py`                                      | Independent polyglot unused/missed-line oracles and pure native-report parser/security regressions.                                                                                     |
| `examples/training.json`, `examples/training.jsonl`                                                     | Tiny rights-owned training smoke parameters and data; no quality claims.                                                                                                                |
| `scripts/frozen_entry.py`                                                                               | Frozen-service entry point for installers.                                                                                                                                              |
| `scripts/verify_electron.cjs`                                                                           | Fail-fast pinned Electron path/embedded-version verification; official SDK installation happens before timed native tests.                                                              |
| `scripts/worker_checks.py`                                                                              | Actual isolated compiler/fuzz/security-boundary integration scenarios.                                                                                                                  |
| `runner/sanitizer_probe.py`, `scripts/worker_analyzer_checks.cjs`                                       | Trusted same-container sanitizer-startup/fault controls and independent exact-line JS/TS checks against the separately audited worker dependency graph.                                 |
| `scripts/private_worker_checks.py`                                                                      | Real twelve-adapter execution through authenticated account API and encrypted-history reopen.                                                                                           |
| `scripts/license_bundle.py`, `scripts/release_archive.py`                                               | Generated third-party notices, portable app packages and SHA-256 checksums; never package user accounts.                                                                                |
| `scripts/release_gate.py`, `scripts/draft_lookup.py`                                                    | Current-main source/CodeQL prerequisites, strict authenticated numeric draft identity, embedded source/worker provenance, bounded fixed-host uploads and draft-only final verification. |
| `tests/test_release_gate.py`, `tests/test_draft_lookup.py`, `tests/node-report.test.cjs`                | Independent GitHub response/policy mutation fixtures, real archive/transport negative oracles and actual descriptor-bound worker JSON read regressions.                                 |
| `scripts/push_analysis.py`                                                                              | Push generation/test/candidate workflow without automatic source promotion.                                                                                                             |
| `tests/`                                                                                                | Controller/security/history/provider/metric tests, browser flows and native launch smoke.                                                                                               |
| `.github/workflows/`                                                                                    | Validation, real isolated workers, training and native OS-package workflows.                                                                                                            |
| `pyproject.toml`, `package.json`, lockfile, TypeScript/Vite/Playwright configs                          | Dependency and reproducible build/test definitions.                                                                                                                                     |

Indexed Python/TypeScript/JavaScript headers point to the checked symbol/variable line map; the small Bash/PHP hooks describe their local variables inline. [Architecture](docs/architecture.md) and the [polyglot decision](docs/adr-polyglot-evidence.md) explain trade-offs; [testing](docs/testing.md) separates test claims from evidence.

[Worker compatibility](docs/worker-toolchain.md) explains the explicit libFuzzer runtime, bounded
startup comparison, deliberate ASan fault control and separate worker npm audit. Compiler/runner
problems remain visible as failures until the actual isolated acceptance checks pass.

Historical 0.1 bearer-token CLI mode remains explicitly opt-in for existing automation; it is not account mode. No automatic import of legacy plaintext projects or global AI keys occurs.

Native shutdown uses a five-second HTTP-drain budget and completes owned disk and
vault transitions before normal sealing. Critical I/O is never abandoned to meet
a fabricated fixed exit time. The [dated native-drain report](docs/reports/native-http-drain-2026-11-10.md)
separates the actual observed defect, real cancellation/recovery controls and
local packaged evidence from later hosted/release acceptance.

## CodeQL source security review

The [CodeQL guide](docs/codeql.md) defines genuine Python, JavaScript/TypeScript and
GitHub Actions `security-extended` analysis, review steps and unsupported scope.
The [dated scan report](docs/reports/codeql-2026-11-09.md) distinguishes actual results
from pending/missing evidence. Static scanning supplements the existing runtime,
dependency, privacy and isolation checks; it does not certify every input or platform.

## Documentation editions

The current [Windows application guide](docs/reports/windows-application-guide.docx)
contains actual installed 0.4.3 screenshots, a worked source-inspection journey,
important source excerpts and explicit test limits. See the
[fresh desktop acceptance](docs/reports/windows-application-2026-11-10.md) and
[guide identities](docs/reports/windows-application-guide.json).

Start with the [organized handbook](docs/handbook.md) for current usage, design, security and test guidance. Reviewed downloadable editions: [project-guide.docx](docs/reports/project-guide.docx) · [validation-review.docx](docs/reports/validation-review.docx) · [validation-evidence.xlsx](docs/reports/validation-evidence.xlsx).

[Publication identities and source scope](docs/reports/publications.json) · [Documentation validation record](docs/reports/documentation-refresh-2026-11-09.md). Historical results retain their own tested revision and date.

## Current Windows application guide

The [version 0.4.4 illustrated guide](docs/reports/windows-application-guide-0.4.4.docx) explains the actual
installed application with two real screenshots, a worked user workflow, important
source excerpts and observed validation. Read the [dated delivery report](docs/reports/installed-windows-2026-11-10.md)
and [byte and page review](docs/reports/windows-application-guide-0.4.4.json) for exact scope. Historical Office
editions remain available with their original baselines.

New documentation files:

- [docs/reports/windows-application-guide-0.4.4.docx](docs/reports/windows-application-guide-0.4.4.docx): Individually reviewed four-page installed application guide with actual screenshots, worked workflow, immutable source excerpts and limits.
- [docs/reports/windows-application-guide-0.4.4.json](docs/reports/windows-application-guide-0.4.4.json): Exact Word, actual screenshot and reviewed page digests plus observed source-specific validation results.
- [docs/screenshots/installed-0.4.4/desktop-workspace.png](docs/screenshots/installed-0.4.4/desktop-workspace.png): Actual installed application synthetic-profile screenshot: Installed developer workspace.
- [docs/screenshots/installed-0.4.4/desktop-source-inspector.png](docs/screenshots/installed-0.4.4/desktop-source-inspector.png): Actual installed application synthetic-profile screenshot: Verified source inspection.
