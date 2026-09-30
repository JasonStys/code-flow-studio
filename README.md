# Code Flow Studio

An independently written successor to a group AI-in-SDLC capstone: a local-first development workbench for isolated polyglot checks, configurable AI proposals, and replayable revision evidence.

**Development preview.** A recognized language or test category is not a claim of universal support. Read [validation evidence](docs/validation.md), [language contracts](docs/languages.md), and [security boundaries](docs/security.md) before executing code. This is not a production multi-tenant sandbox or an autonomous correctness oracle.

## The development loop

1. Upload flat source/data files or edit code in the offline Monaco editor. Select a compiler adapter and entry point. Write requirements and approve independent stdin/stdout cases.
2. Optionally ask a configured model to generate code, tests, improvements or live suggestions. Source transmission is opt-in. Responses are schema-validated **unverified proposals**, not executed results.
3. Save an immutable revision and run it through the container broker. Compilation, approved cases, supplied pytest harnesses, Python coverage/mutation, bounded fuzzing and exploratory benchmarks produce separate evidence.
4. Review findings and add a candidate revision. Baseline expectations and existing tests cannot be removed. Compare results under the same environment and adjustable runtime/memory/readability/footprint preferences.
5. Download escaped HTML, machine-readable JSON and a source/test/harness/report ZIP. Reopen saved revisions and replay them.

## Features and limits

| Feature | Implemented contract |
|---|---|
| Desktop application | Electron shell and bundled Python service; one-click Windows installer plus OS-specific Linux/macOS builds. No IntelliJ or separately installed Python required for the UI. Unsigned development packages. |
| Web application | Same responsive editor/API served on loopback. Narrow-screen browser support; not a native Android/iOS installer or public hosted service. |
| Polyglot execution | Fixed CLI adapters for Python, JavaScript, TypeScript, C/C++, Java, C#, Rust, PHP, Bash, SQLite SQL and GNU x86-64 assembly. Actual toolchains live inside the worker image. |
| Testing | Approved CLI oracles and reviewed pytest harnesses, including subprocess harnesses for non-Python targets. 48-category applicability catalog; human, hardware, cloud/load and specialized tool checks need independent integrations. |
| Coverage/mutation | Python entry line/branch coverage; up to eight operator mutants. No fabricated condition/MC/DC, function, edge or universal mutation scores. |
| Fuzzing | Seeded black-box generation, mutation, dictionary, boundaries and CSV/SQL grammar; instrumented libFuzzer/AFL++ for reviewed C/C++ harnesses and Atheris for Python harnesses. Differential/metamorphic/stateful relations require custom oracles. |
| AI routing | OpenAI-compatible, Anthropic and Ollama protocols; per-task administrator routing and consent; no credentials in renderer, history exports or execution containers. Protocol tests use mocks, not a claim of live model quality. |
| Metrics/ranking | Repeated process wall times, peak child RSS, source bytes and transparent long-line proxy. Passing independent cases is mandatory. No syntax-based Big-O claims or automatic “best” model claims. |
| Training | Rights-checked, project-disjoint JSONL preparation, actual small causal-model creation or approved local-model fine-tuning, safe-tensor output and authenticated local inference API. Tiny synthetic smoke training is not a useful general coding model. |
| CI | SHA-pinned, read-only Actions validate controller/browser behavior, real worker scenarios, training smoke and native packages. Push analysis retains generated tests/candidate evidence when a provider is explicitly configured; never auto-commits model changes. |

Binary formats can be retained as fixtures. There is no promise to understand every document, image, encrypted archive or binary. Supply text requirements and explicit harnesses for formats without a parser; unsupported extraction must not silently succeed.

## Run and install

For end users, use an OS-specific installer produced by the **Desktop packages** workflow. The UI runtime is bundled. Compiler jobs still require an isolated Docker engine and the trusted worker image; the app reports blocked execution if these are missing. No host-execution fallback exists.

Source-development instructions, provider setup, first-run diagnostics and packaging are in [setup](docs/setup.md). All documentation is indexed in [docs](docs/README.md). Original private capstone code, team files, API credentials and vendor trees are not distributed here.

## Source map

| Location | Responsibility |
|---|---|
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
| `scripts/push_analysis.py` | Push generation/test/candidate workflow without automatic source promotion. |
| `tests/` | Controller/security/history/provider/metric tests, browser flows and native launch smoke. |
| `.github/workflows/` | Validation, real isolated workers, training and native OS-package workflows. |
| `pyproject.toml`, `package.json`, lockfile, TypeScript/Vite/Playwright configs | Dependency and reproducible build/test definitions. |

Every source header points to the checked symbol/variable line map. [Architecture](docs/architecture.md) explains trade-offs; [testing](docs/testing.md) separates test claims from evidence.

