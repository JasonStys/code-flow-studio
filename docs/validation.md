# Validation evidence — development preview

As of 2026-09-29 (local date), the initial Windows controller/API suite passed **50 tests**. Statement coverage was **83%** across `studio` plus `training.dataset`; optional training runtime and container worker are not included in that denominator. One upstream Starlette/httpx TestClient deprecation warning was emitted.

TypeScript compilation and the production renderer build passed after correcting Monaco's current package export paths. npm reported zero known dependency vulnerabilities at installation. These results do not prove live AI quality, sandbox isolation or all supported compilers work.

Pending evidence at this checkpoint: final expanded suite, three-engine UI runs, bundled native startup, actual installer installation, real isolated compiler/fuzz checks, model-training smoke, local inference API and GitHub Actions results. This file will be updated only from observed results.

Local Docker execution is blocked. Docker Desktop crashed in inference-socket initialization; the owner explicitly requested leaving Docker unchanged and validating worker jobs through GitHub Actions. No factory reset, container/image deletion or host-execution fallback was performed.

No real AI provider/model is configured yet. Protocol tests use mocks. No private capstone API keys were reused, no paid API calls made, and no live-generated improved code is claimed validated. The repository remains a private development preview pending the visibility choice.

All 48 categories are cataloged, not all automated. Human/hardware/external test categories and production multi-tenant deployment remain outside built-in support. Compiler fixtures only prove their stated narrow contracts.

