# Account release test plan

Risk-based testing prioritizes confidentiality, data loss and untrusted execution over cosmetic coverage. Fictional aliases/keys/source are used; real personal directories are never test fixtures.

| Risk | Required evidence |
|---|---|
| Unauthorized source/provider access | Missing/expired sessions denied; separate owners empty; same-owner login-only session cannot join an unlocked key; ID guessing fails. |
| CSRF/rebinding/XSS/credential echo | Literal host and port, Origin/fetch checks, JSON custom mutation header, closed schemas, no-store/CSP, inert report escaping; errors and settings omit credentials. |
| History loss/tampered archives | Real save/lock/reopen/SQLite snapshots; authenticated tag damage rejected before extraction; path/device rejection; disk failure retains code/login recovery. |
| Unsafe execution | No host fallback; remote engine rejected before contact; fixed job-only mount/resource flags; real 12-adapter account execution and existing 24 isolated compiler/fuzz/adversarial scenarios in Linux CI. |
| AI leakage/false claims | Own-key isolation, no global-key fallback; destination revision consent invalidation; protocol parameter and credential-echo tests; proposals never marked verified. Mocks do not establish model quality. |
| UI regression | Original 9 browser checks plus 6 private checks in Chromium/Firefox/WebKit; registration, WebCrypto unlock, editor, genuine static review, encrypted download, reopening, empty second account and 390px help. |
| Installer/runtime gaps | Actual frozen service and sandboxed Electron tests on three OS runners; repeat against packaged app, then downloaded Windows executable; no separate user Python/Node needed. |
| Dependency/release problems | Python/npm audits, Ruff, checked source maps, build, retained >=80% coverage gate, license bundles, exact-source CI gate and checksummed Release assets. |

Known exclusions: physical mobile devices, notarization/signing, independent penetration testing, power-cut/fault campaigns, OS compromise, live paid AI quality/cost evaluation, exhaustive semantic equivalence and certified hostile-kernel isolation. Missing Docker locally is a blocked execution result, not a passing compiler test.
