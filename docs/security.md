# Security and trust boundaries

**0.3 native tools:** [polyglot measurement boundaries](polyglot-locations.md) extend the same sandbox; no network/capability/host-access increase. Fixed tool configurations, source-map restrictions, bounded report reads and source-hash-bound locations reduce accidental misattribution, not malicious-target attestation. Language-native unused candidates never trigger automatic deletion.

**0.2 account mode:** see [private accounts](private-accounts.md) and [ADR](adr-private-local.md). Password/session authorization and independent vault proof replace renderer bearer tokens in installed/account mode. Account-owned keys/history are encrypted at lock outside Git; active data is plaintext in the trusted local service. Legacy developer CLI token/environment behavior below remains opt-in, not a private-mode fallback. No operator source-read endpoint or public hosting is provided.

References used for this boundary: [OWASP password storage](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html), [Electron security](https://www.electronjs.org/docs/latest/tutorial/security), [Docker engine security](https://docs.docker.com/engine/security/), [cryptography authenticated encryption](https://cryptography.io/en/stable/hazmat/primitives/symmetric-encryption/), and [OpenAI Chat Completions protocol](https://developers.openai.com/api/reference/resources/chat/subresources/completions/methods/create). Parameter availability varies by model. Audits/tests do not certify freedom from vulnerabilities.

Threats include malicious source/harnesses, compiler exploits, traversal, resource exhaustion, report XSS, DNS rebinding/cross-origin submissions, leaked API keys, prompt injection, supply-chain changes and model/data licensing mistakes.

Account jobs resolve the effective local engine respecting DOCKER_CONTEXT precedence, then pin that verified Unix/named-pipe endpoint for info/image/run/cleanup. A generated empty Docker CLI config prevents automatic host proxy credentials from entering targets. This follows [Docker CLI environment/config precedence](https://docs.docker.com/reference/cli/docker/); it neither changes the user's Docker config nor repairs the engine.

The controller accepts bounded flat file names, retains binary fixtures without interpreting them, validates schemas, checks loopback hosts/origins and requires a strong per-process token. Reports escape all untrusted content. SQLite uses bound parameters and transactions. The renderer has no Node integration or privileged preload, context isolation and process sandboxing enabled, denied permissions/window opening and no remote navigation. Monaco assets are bundled locally.

Workers use no network, read-only root, an app-owned read-only job mount, private bounded tmpfs, non-root user, dropped Linux capabilities, no-new-privileges, memory/CPU/PID constraints and an external controller deadline/output bound. Uploaded values cannot add Docker mounts, sockets, flags, images or environment secrets. Only a broker-owned exact container name is force-removed on completion/cancellation. Never reset/delete unrelated Docker state.

The worker creates its own mode-0700 `XDG_RUNTIME_DIR` on that fresh private tmpfs before starting tools. Patched .NET runtimes need a UID-owned writable location for named mutexes; this avoids an unavailable passwd home without granting root access, a shared runtime directory or a new host mount.

The private tmpfs explicitly allows executable compiler output while remaining `nosuid,nodev`; Docker otherwise defaults tmpfs mounts to `noexec`, which prevents genuine C/C++/Rust/assembly and instrumented harness execution. This exception applies only inside the restricted disposable worker, not the host or any shared directory.

**Limitations:** containers share the host/VM kernel. Compiler and runtime vulnerabilities remain possible. Arbitrary target programs can interfere with same-user instrumentation inside their job; self-reported worker measurements are not cryptographic proof against actively malicious targets. Runtime/RSS and syntax warnings are evidence for reviewed development code, not security certification. Run hostile internet workloads in dedicated disposable VMs with stronger isolation, independent supervisors and security review.

This API intentionally binds loopback and is not a production public SaaS server. Public hosting requires HTTPS, real identity/tenant authorization, quotas, audit retention, queue separation, encrypted storage, hardened remote workers and independent security testing. Do not expose the local token interface directly to the internet or a mobile network.

AI providers receive only consented text, not binary fixtures, execution secrets or host tools. Keys remain private server environment values. Administrator endpoint configuration is trusted and can transmit source; review it. Model responses are untrusted schema-validated suggestions. Do not rely on prompt wording to contain a compromised model. Provider error output is not exposed with raw headers or keys.

Original private capstone code, project files and credentials were inspected only for understanding. None should be copied into this independent repository. Training data requires rights/provenance review, secret/PII scanning and project-disjoint evaluation. No automatic uploads, remote model-code execution or training on private source occurs.

