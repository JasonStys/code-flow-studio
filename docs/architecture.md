# Architecture and decisions

Current 0.2 account wrapper and its active-plaintext/local trust decision are documented in [the ADR](adr-private-local.md); the controller/worker decisions below remain applicable. No public backend is hosted.

Status: development preview. This implementation is independently written, not a redistribution of the private group capstone.

```text
Monaco / TypeScript editor ── same-origin authenticated HTTP ── Python controller
Electron native shell       ── bundled loopback service           │
                                                                  ├─ SQLite revisions / run evidence
                                                                  ├─ consented provider router ─ AI API/local model
                                                                  └─ bounded broker ─ no-network compiler container
                                                                                       ├─ compile + approved oracles
                                                                                       ├─ reviewed pytest harness
                                                                                       └─ coverage/mutation/fuzz/metrics
```

## ADR 001: shared web/native UI

TypeScript and Monaco provide typed application code, an established multi-language editor and local worker assets. Electron supplies a distributable desktop shell and bundles a frozen Python service. The same renderer can run in a browser. This costs package size and memory compared with Tauri; it avoids requiring a separate Python setup and keeps one UI implementation. OS-specific installers are necessary; there is no single binary that installs on every OS. Mobile support is browser-based only.

## ADR 002: Python orchestration, not unrestricted host execution

Python fits the existing testing/coverage/property/ML ecosystem. It coordinates async jobs, bounds queues and stores metadata; it does not directly run uploaded source. Native compilers and fixed commands run inside a no-network worker. SQLite is appropriate for a single local workspace with short transactional operations and indexed history. This is not an internet-facing multi-user backend.

## ADR 003: preserve evidence and independent oracles

Inputs and candidate revisions are immutable. Existing approved tests and stdin/stdout expectations cannot be removed for candidate ranking. A completed workflow can still contain target findings. Compilation failure, blocked infrastructure, timeout, source warnings, failed expectations, coverage and mutation survivors are distinct. Generated test code is tested inside the same isolated environment but is not an independent specification; developers must review its assertions.

## ADR 004: extensible support rather than universal claims

Compiler adapters initially implement explicit single-entry CLI contracts. Reviewed Python harnesses can invoke any preinstalled compiler/process in the worker, enabling richer test styles without exposing shell execution on the host. New toolchains require a trusted image change, adapter code, fixture, negative test and CI evidence. Recognizing an extension, displaying syntax highlighting or listing a test family does not establish execution support.

## ADR 005: AI is advisory and routed by task

Task routes separate generation, test creation, improvement and suggestions, allowing different models per role. Administrator configuration and private environment keys select endpoints. Uploaded code is untrusted prompt data. Models never receive host-execution credentials, secretly promote code, change approved oracles, or report fabricated benchmarks. Endpoint/model choices should be evaluated on held-out tasks, correctness, latency and cost; the application cannot know the universally best provider.

## Performance reasoning

Queue size and concurrency are bounded. Database operations are indexed and parameterized. Projects/files and child output have explicit limits. Candidate metrics use real process measurements; runtime includes startup, RSS is a batch child peak, long lines are only a readability proxy. Algorithmic Big-O requires a human argument or controlled input-size study, not a guessed scalar score. Security and passing reviewed correctness tests come before soft optimization preferences.

