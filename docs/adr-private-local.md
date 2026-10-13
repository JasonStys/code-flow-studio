# ADR: private local accounts around the existing isolated controller

Status: accepted for version 0.2; local hosting chosen by the owner. Public source is approved; public backend hosting is not.

The existing Python controller, language worker, SQLite history and optional ML workflow remain. React/TypeScript owns account forms, offline editing and WebCrypto; Python owns auth, archive lifecycle and server-side model routing; SQL owns bounded durable history; Electron supplies OS-specific installation and a hardened renderer. Rewriting compiler/tooling in the UI would enlarge the attack surface without improving its boundary.

Alternatives: bearer-only legacy mode has no independent accounts; public SaaS adds HTTPS/identity/queue/remote hostile execution/operations requirements the owner did not authorize; browser-only encryption prevents the service from compiling code, reading history and using keys. Chosen: loopback local accounts plus locked-at-rest encryption, with clearly disclosed trusted active plaintext.

Every session authenticates and independently proves its vault key. A single mutable engine cannot accidentally switch while another account is unlocked. Request serialization protects lock/config/history transitions; only owned exact Docker containers and checked managed plaintext directories are cleaned. AES-GCM archives are authenticated before ZIP extraction; portable paths/link/count/byte limits prevent unsafe restoration. Disk-save failure retains recovery state.

Consequences: only one active account engine; no public host/mobile native package, operator source read API, cloud synchronization, universal compiler or universal AI compatibility. User/admin OS compromise defeats active confidentiality. Backups must include account/key configuration. The older 0.1 CLI remains explicit rather than a fallback on failed authentication. No legacy private data is auto-imported.
