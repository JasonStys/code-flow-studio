# Testing strategy and capability claims

The original final capstone supported 12 direct families: smoke, unit/component, functional, integration, interface, regression, property-based, security/input validation, CLI, API, GUI and system/end-to-end, alongside aggregate coverage, mutation and AFL++/compatibility fuzzing. The successor preserves an isolated custom pytest-harness path for those families, explicit approved CLI oracles, property tooling and report/history exports. **It does not automatically infer complete test specifications, create every harness without a configured AI model, or ship built-in browser/API/GUI runners for arbitrary target applications.** Rich integrations remain explicit work.

The supplied 48-category document is represented one-to-one in the capability catalog. Category names are not run results. Human acceptance, exploratory work, peer review, walkthroughs, formal inspection and usability need people and evidence. Hardware-in-the-loop needs actual hardware. Chaos and penetration testing require authorized scope. Load/soak/scalability/recovery/browsers need dedicated environments and harnesses. Missing prerequisites must remain blocked/external/manual, never automatically passed.

## Risk-based layers

- Exact-location regressions: auxiliary-file/Unicode/syntax checks, conservative Python unused/unreachable candidates, toolchain reference parsing, unlocated failures, immutable source hashes, bounded per-file coverage lists, escaped UI/HTML/JSON/ZIP and legacy-report behavior. See [the detailed contract](located-diagnostics.md). Real worker acceptance is separate from mocked coverage-function and UI tests.

- Controller unit/API tests: filename traversal/device aliases, malformed and oversized requests, base64, duplicate names, zero/invalid preferences, token/origin/host checks, source side-effect avoidance, SQL transactions, history recovery, immutable baseline oracles and candidate gates.
- Provider contracts: all three protocol envelopes, explicit consent, private key headers, endpoint restrictions and unverified proposal schemas. These are mocks, not live paid-provider quality evidence.
- Browser tests: actual editor rendering, catalog, controls, consent, unavailable-provider error, history persistence, evidence downloads and narrow-screen overflow in Chromium/Firefox/WebKit.
- Native tests: bundled-service launch, offline editor rendering, absence of Node access in renderer and catalog interaction. Package-build success is not equivalent to a clean-machine installation test or app-store acceptance.
- Real worker tests: every compiler adapter, approved cases, wrong oracle, syntax error, custom generated harness, real Python coverage/mutation, deterministic raw-byte fuzz corpus, libFuzzer/AFL++/Atheris instrumentation, timeout/output limits, no worker key, read-only root and blocked outbound connection.
- Training smoke: an actual tiny new causal model, saved safe-tensors, project-disjoint held-out loss. This proves pipeline mechanics, not coding performance.

## Fuzz semantics

Generation, mutation (bit/byte insertion/deletion/arithmetic/splicing), dictionary, bounded extremes and CSV/SQL grammar are seeded and reproducible. Their black-box mode reports executions and concrete crashes/hangs; it is **not** coverage-guided and invents no edge counts. Ordinary nonzero exits may be correct rejection behavior and are not automatically called bugs. Differential testing needs a reference oracle; metamorphic testing needs a valid relation; stateful testing needs a state model. Supply these through a reviewed harness rather than treating random bytes as equivalent methods.

## Gates and measurements

An empty approved-case suite cannot establish correctness or candidate eligibility. Compile errors, blocked isolation, failed expectations, failed generated tests, selected blocked fuzz methods and concrete fuzz findings prevent CLI success/ranking. Surviving mutants are reported, not automatically asserted to be defects. Existing approved test code cannot be removed from candidates. Benchmark samples include process startup; peak RSS is the child peak over a batch, not precise function allocation. Differences may be noise. Readability and syntax complexity proxies do not establish safety or Big-O.

Coverage thresholds apply to explicitly named controller/data-validation modules, not all optional ML and worker code. Real integration runs supply additional evidence. Every report must state scope, counts, environment, seed and exclusions. Never claim “all tests passed” when live provider, hardware, production deployment or native device tests are absent.

Benchmark repetitions must also match the approved oracle; a mismatching repeat records a failure rather than an attractive timing sample. Mutation scores exclude invalid and inconclusive timed-out mutants; supplied pytest checks run against each evaluated mutant only after the original baseline passes.

