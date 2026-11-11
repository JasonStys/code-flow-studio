# Desktop runtime maintenance — 10 November 2026

Author: Jason Stys. Scope: the 0.4.4 source candidate and a locally built unsigned
Windows application image. Published installer and hosted acceptance are separate
gates; this report does not label an uninstalled candidate as the installed app.

## Changes and reason

The existing 0.4.3 one-file service contains Python 3.12.10. That historical Windows
installer line no longer receives new official binary installers. The new desktop
build uses the official full Python 3.14.10 SDK and Electron 44.11.0, preserving
the same account/vault formats and application identity. The frozen entry refuses
another interpreter before private-service dispatch. `/health` reports the actual
interpreter, and native acceptance requires that value rather than trusting only
a package label. The compiler worker stays on its compatibility line with a
digest-pinned Python 3.12.16 Bookworm base and a matching 0.4.4 worker identity.

The 0.4.3 C# target-exit bridge and located-diagnostic contracts are retained.
The existing local `.runtime` directory is ignored; no contents are packaged,
deleted, inspected for account data or added to source control.

## Observed candidate validation

| Check | Observed result |
| --- | --- |
| Complete source suite on Python 3.14.10 | 422 passed, two Windows platform-specific skips and 28 subtests passed |
| Existing controller coverage scope | 85.13%; unchanged 80% floor, `studio` plus `training.dataset` |
| Frozen-runtime regressions | Unexpected interpreter versions refuse before account-service dispatch; reviewed frozen and supported source modes dispatch correctly |
| Ruff and exact source maps | Passed; 98 source maps checked |
| TypeScript and production UI build | Passed |
| Electron readiness/lifecycle regressions | Passed |
| Actual packaged Windows journey | Passed: authenticate, encrypted history, sandboxed offline editor, source inspector and test catalog; service drained and exited normally |
| Dependency advisories | npm: zero known findings; pip-audit: no known findings in auditable build dependencies; this unpublished local project is not a PyPI package |
| Docker on this PC | Unchanged; no local compiler container was started or built |

The native pilot used a dirty, explicitly labeled development candidate based on
`3825eecda6f991a8ddbd21873bbcfc7a6734a48b`. It is evidence about the actual built
candidate, not clean release provenance. Exact-source hosted packages and compiler
acceptance must pass again before release promotion. Independent download,
installer-upgrade, private-data preservation and existing-shortcut checks remain
required before replacing the installed 0.4.3 application.

## Test environment diagnosis

Initial source-test attempts stalled before application dispatch in Python's
internal asyncio loopback socket pair inside the restricted tool sandbox. A
30-second thread traceback identified `socket.accept` during event-loop setup.
The same six API tests passed in normal local context, followed by the full suite
above. The stalled owned test processes were stopped after that diagnosis; their
logs remain private. No product workaround or weakened test was introduced.

Runtime sources: [Python 3.14.10 release notice](https://www.python.org/downloads/release/python-31410/),
[official Windows distribution manifest](https://www.python.org/ftp/python/3.14.10/windows-3.14.10.json).
Dependency scans are dated advisory observations, not guarantees of future safety.
