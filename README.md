# Code Flow Studio

An independently written successor to a group AI-in-SDLC capstone: a local-first development workbench for isolated polyglot checks, configurable AI proposals, and replayable revision evidence.

**Version 0.2: real private local accounts.** Create an account, unlock your encrypted source/history workspace, and use the same interface in the desktop app or your browser. No public backend, shared login, analytics, ads or cloud AI calls are enabled by default. By [Jason Stys](https://github.com/JasonStys); [contact via LinkedIn](https://www.linkedin.com/in/jason-stys-31b30b351/).

Download OS-specific installers/portable packages from [Releases](https://github.com/JasonStys/code-flow-studio/releases). Read [private-account operation](docs/private-accounts.md), [current validation](docs/validation-v0.2.md) and [security boundaries](docs/security.md). Packages are unsigned. This is a local development tool, not a public hostile-code SaaS sandbox or an autonomous correctness oracle.

## The development loop

1. Upload flat source/data files or edit code in the offline Monaco editor. Select a compiler adapter and entry point. Write requirements and approve independent stdin/stdout cases.
2. Optionally ask a configured model to generate code, tests, improvements or live suggestions. Source transmission is opt-in. Responses are schema-validated **unverified proposals**, not executed results.
3. Save an immutable revision and run it through the container broker. Compilation, approved cases, supplied pytest harnesses, Python coverage/mutation, bounded fuzzing and exploratory benchmarks produce separate evidence.
4. Review findings and add a candidate revision. Baseline expectations and existing tests cannot be removed. Compare results under the same environment and adjustable runtime/memory/readability/footprint preferences.
5. Download escaped HTML, machine-readable JSON and a source/test/harness/report ZIP. Reopen saved revisions and replay them.

## Features and limits

| Feature | Implemented contract |
|---|---|
| Private accounts | Real alias/password registration, hashed sessions and one-use login recovery. Independent browser-derived vault key, authenticated AES-256-GCM locked source/history/provider archives and per-session unlock proof. No developer plaintext read API. Trusted local service and OS can access active plaintext; not browser-only E2EE. |
| Desktop application | Electron shell and bundled Python service; one-click Windows installer plus OS-specific Linux/macOS builds. No IntelliJ or separately installed Python required for the UI. Unsigned development packages. |
| Web application | Same responsive editor/API served on loopback. Narrow-screen browser support; not a native Android/iOS installer or public hosted service. |
| Polyglot execution | Fixed CLI adapters for Python, JavaScript, TypeScript, C/C++, Java, C#, Rust, PHP, Bash, SQLite SQL and GNU x86-64 assembly. Actual toolchains live inside the worker image. |
| Testing | Approved CLI oracles and reviewed pytest harnesses, including subprocess harnesses for non-Python targets. 48-category applicability catalog; human, hardware, cloud/load and specialized tool checks need independent integrations. |
| Coverage/mutation | Python entry line/branch coverage; up to eight operator mutants. No fabricated condition/MC/DC, function, edge or universal mutation scores. |
| Fuzzing | Seeded black-box generation, mutation, dictionary, boundaries and CSV/SQL grammar; instrumented libFuzzer/AFL++ for reviewed C/C++ harnesses and Atheris for Python harnesses. Differential/metamorphic/stateful relations require custom oracles. |
| AI routing | Account-owned OpenAI-compatible, Anthropic and Ollama endpoints/keys, four task routes and destination-version-bound consent. Keys stay server-side after explicit settings submission, outside histories/exports/workers. Protocol tests use mocks, not a claim of live model quality. |
| Metrics/ranking | Repeated process wall times, peak child RSS, source bytes and transparent long-line proxy. Passing independent cases is mandatory. No syntax-based Big-O claims or automatic “best” model claims. |
| Training | Rights-checked, project-disjoint JSONL preparation, actual small causal-model creation or approved local-model fine-tuning, safe-tensor output and authenticated local inference API. Tiny synthetic smoke training is not a useful general coding model. |
| CI | SHA-pinned, read-only Actions validate controller/browser behavior, real worker scenarios, training smoke and native packages. Push analysis retains generated tests/candidate evidence when a provider is explicitly configured; never auto-commits model changes. |

Binary formats can be retained as fixtures. There is no promise to understand every document, image, encrypted archive or binary. Supply text requirements and explicit harnesses for formats without a parser; unsupported extraction must not silently succeed.

## Run and install

For end users, use the checksummed OS-specific packages in Releases. The UI runtime is bundled. Open the app's **Code Flow → Open local website** menu for browser use; no login token appears in the URL. Compiler jobs require an isolated local Unix/named-pipe Docker engine and the trusted worker image. Missing isolation is blocked, never passed; there is no host-execution fallback. Save/edit/static review/history/help remain usable without Docker.

Source-development instructions, provider setup, first-run diagnostics and packaging are in [setup](docs/setup.md). All documentation is indexed in [docs](docs/README.md). Original private capstone code, team files, API credentials and vendor trees are not distributed here.

## Source map

| Location | Responsibility |
|---|---|
| `studio/accounts.py`, `studio/permissions.py` | scrypt logins, session/recovery digests, bounded attempts and private per-OS data permissions. |
| `studio/private_api.py` | Account-only HTTP/CSRF boundary, own provider settings, per-session key proof, backup/recovery/deletion and scoped controller proxy. |
| `studio/private_workspace.py`, `studio/vault.py` | Single-instance ownership, account-specific engine lifecycle, authenticated streaming encryption, SQLite online snapshots and safe restoration. |
| `studio/private_cli.py` | Token-free loopback account service, dedicated data root and exact-parent graceful shutdown monitor. |
| `ui/Account.tsx` | Sign-in/unlock/recovery, contextual help, encrypted backup, private AI configuration and creator contact. |
| `studio/models.py` | Validated flat-file, project, case, preference and AI proposal schemas; size/path limits. |
| `studio/api.py` | Authenticated loopback API, bounded jobs, history, reports, comparisons and AI tasks. |
| `studio/store.py` | SQLite transactions, append-only revisions, immutable baseline oracles and interrupted-job recovery. |
| `studio/execution.py` | Fixed container flags, readiness checks, output/deadline bounds and exact owned-container cleanup. |
| `studio/analysis.py` | Non-executing source heuristics and correctness-gated weighted comparisons. |
| `studio/providers.py` | Private provider configuration, task routes, consent, bounded requests and proposal schema validation. |
| `studio/catalog.py` | All 48 supplied test categories with applicability/integration requirements. |
| `studio/reports.py` | Escaped, inert HTML/JSON/ZIP evidence exports. |
| `studio/cli.py` | Shared web launcher and manifest-to-report CI command. |
| `runner/Dockerfile`, `runner/worker.py` | Trusted compiler image and isolated compile/test/coverage/mutation/fuzz/benchmark execution. |
| `ui/App.tsx` | Workspace, cases, priorities, live suggestions, proposal approval, evidence and history views. |
| `ui/main.tsx`, `ui/api.ts` | Offline editor worker registry and authenticated same-origin client/downloads. |
| `ui/demo.ts`, `ui/types.ts` | Synthetic CSV example and renderer contracts. |
| `ui/index.html`, `ui/style.css` | Local HTML entry and responsive accessible layout. |
| `desktop/main.cjs` | Sandboxed Electron renderer and private bundled-service lifecycle. |
| `training/dataset.py`, `training/train.py`, `training/serve.py` | Provenance/split validation, parameterized real training, local model API. |
| `examples/projects.py`, `examples/web-demo.project.json` | Compiler-contract fixtures and the exact synthetic CSV source/manifest used by the UI, checked in CI. |
| `examples/training.json`, `examples/training.jsonl` | Tiny rights-owned training smoke parameters and data; no quality claims. |
| `scripts/frozen_entry.py` | Frozen-service entry point for installers. |
| `scripts/worker_checks.py` | Actual isolated compiler/fuzz/security-boundary integration scenarios. |
| `scripts/private_worker_checks.py` | Real twelve-adapter execution through authenticated account API and encrypted-history reopen. |
| `scripts/license_bundle.py`, `scripts/release_archive.py` | Generated third-party notices, portable app packages and SHA-256 checksums; never package user accounts. |
| `scripts/push_analysis.py` | Push generation/test/candidate workflow without automatic source promotion. |
| `tests/` | Controller/security/history/provider/metric tests, browser flows and native launch smoke. |
| `.github/workflows/` | Validation, real isolated workers, training and native OS-package workflows. |
| `pyproject.toml`, `package.json`, lockfile, TypeScript/Vite/Playwright configs | Dependency and reproducible build/test definitions. |

Every source header points to the checked symbol/variable line map. [Architecture](docs/architecture.md) explains trade-offs; [testing](docs/testing.md) separates test claims from evidence.

Historical 0.1 bearer-token CLI mode remains explicitly opt-in for existing automation; it is not account mode. No automatic import of legacy plaintext projects or global AI keys occurs.

