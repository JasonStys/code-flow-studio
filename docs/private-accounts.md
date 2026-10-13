# Private local website and app — 0.2

By Jason Stys. Contact: [GitHub](https://github.com/JasonStys), [LinkedIn](https://www.linkedin.com/in/jason-stys-31b30b351/).

## Installation and first use

Download the package matching your OS and architecture from Releases. Windows x64 has a per-user one-click NSIS installer and a portable ZIP; macOS ARM64 has a DMG and portable archive; Linux x64 has an AppImage and portable archive. Verify the adjacent SHA-256 checksum before use. Packages bundle Python, React, offline Monaco and Electron, but are unsigned/not notarized: do not blindly bypass OS warnings. No native mobile installer or public hosting is provided. AppImage may need your normal OS FUSE support; the portable Linux directory is an alternative. Keep the complete unpacked folder together.

Open the app. Create a non-identifying local alias (3–40 lower-case letters/digits/underscore/hyphen) and a unique 15–128 character login password. Save the once-shown login recovery code. Create a separate 20–256 character vault phrase, preferably six random words; save it privately. Account data is not synchronized to Jason, GitHub or a hosted backend.

For browser use choose **Code Flow → Open local website**. The address is literal loopback with an automatically assigned port, contains no secret, and only works while the installed app/service is running. Browser sessions sign in and prove their vault key independently. Only one account engine can be unlocked at a time. Sign out/lock before another owner opens it.

Import flat source/data files or start from the clearly synthetic CSV draft. Choose an adapter/entry and independent expected cases. **Save revision only** retains history without executing code. **Static review** inspects bounded syntax/metrics and is labeled not executed. Save revisions before locking; unsaved editor drafts are not archived. Actual checks require the fixed isolated Docker worker. Reports retain failed/blocked outcomes, not artificial passing scores.

## Private storage and recovery

Default roots:

| OS | Dedicated private root |
|---|---|
| Windows | `%LOCALAPPDATA%/CodeFlowStudioAccounts` |
| macOS | `~/Library/Application Support/CodeFlowStudioAccounts` |
| Linux | `$XDG_DATA_HOME/CodeFlowStudioAccounts` or `~/.local/share/CodeFlowStudioAccounts` |

The native launcher has a separate `CodeFlowStudioLauncher` directory for nonsecret startup logs. The new account root never opens or migrates older capstone/native/developer history. A trusted operator can explicitly override `CFS_ACCOUNT_DATA` to an empty dedicated directory; this is not a browser-selectable path. A held OS advisory lock prevents two services sharing it.

Passwords use salted scrypt N=2^17/r=8/p=1. Random session and recovery credentials are stored as digests. Cookies are HttpOnly/SameSite=Strict and expire after eight hours absolute or thirty minutes without requests; human-idle vault locking is independently ten minutes by default. Polling does not renew the human clock. Choose thirty minutes/two hours explicitly for a slow job. Authentication is rate limited.

The browser derives a 256-bit key using PBKDF2-SHA256/600,000 iterations and a random salt. The phrase itself is not sent; the derived key is sent to the trusted local service for active processing. Account-owned source/history/API keys are encrypted at lock using authenticated AES-256-GCM, fresh nonces and streamed SQLite online backups. Keys are not saved in browser storage/URLs. This is not zero-knowledge hosting or browser-only end-to-end encryption: active files, process memory and local Docker work are plaintext accessible to OS administrators/owners or malware. Use a private OS login and device encryption. A malicious modified app or engine remains outside this boundary.

**Save encrypted snapshot** requires terminal jobs. **Download encrypted archive** returns only your ciphertext. An archive alone does not restore your account/key configuration: quit, confirm no managed `active` directory remains, then cold-back up the **entire** dedicated root to protected storage. To restore, close the service and restore that complete root to its original protected location; do not merge another owner's active state. No cloud backup or automatic archive-import endpoint is implemented.

Lock/sign out cancels owned jobs, seals history and removes only its checked managed plaintext directory. Failed encryption preserves working recovery data and the previous complete ciphertext. After crashes, the matching account owner must unlock/lock to recover. An incomplete marker/directory pair fails closed: preserve the directory and ask for support, do not delete it. Native parent loss requests graceful sealing. Power loss, forced kill, filesystem failures and malware can leave plaintext; no secure disk-sector erasure is claimed.

Login recovery rotates the login password/recovery code and revokes sessions but cannot recover a forgotten vault phrase. There is no Jason/operator plaintext recovery API. Account deletion requires the current password and explicit confirmation, affects only its live data and does not erase exported files, backups or disk sectors. Protect plaintext source/report ZIPs separately.

## AI providers and execution

Use **Private AI settings** after unlocking. Enter your own full approved endpoint, protocol, model, key/token and task routes. OpenAI-compatible endpoints choose `max_tokens` or `max_completion_tokens`; blank temperature omits it. Anthropic/Ollama have their documented protocol adapters. Not every model/API is compatible; no model is downloaded or selected automatically.

Provider keys are input once to the local service, saved only in its encrypted account workspace and never returned by the settings API, copied into revision/report ZIPs, or mounted into workers. Global developer/environment credentials are ignored in account mode. A destination change cannot retain an old key. Config changes rotate a revision identifier and clear live suggestions/source consent; stale requests fail before contacting the provider.

Review destinations, then opt in to sending project text. Requirements/cases/harness/source/prompt may be sent; binary fixtures are not sent. Cloud providers may store that text or charge fees under their policies. No external calls happen without an explicitly configured provider and consent. Protocol tests use synthetic mocks, not live keys or model-quality claims. Proposals are unverified, must be reviewed, and cannot silently replace approved oracles or claim test evidence.

Compiler jobs require a local Unix/named-pipe engine and the reviewed `code-flow-worker:0.1.0` image. Remote Docker contexts are blocked in account mode; targets get no network, broad host mounts, account database, provider settings or Docker socket. No automatic Docker installation/repair and no direct-host execution fallback exist. Training remains a separate optional, rights-checked ML workflow, not bundled in the end-user runtime.

## Source operation and limits

Python 3.12+ and Node 24 are required only for source development:

```bash
python -m venv .venv
# Activate your platform's virtual environment.
python -m pip install -e '.[dev]'
npm ci
npm run build
python -m studio.private_cli
```

The printed URL is nonsecret. Ctrl+C requests sealing. Legacy `python -m studio.cli serve` intentionally remains a different bearer-token developer mode; do not expose either service to a network.

Limits: 20 flat files/1 MiB project; 192 KiB browser file import; 64 cases; 4 MiB HTTP request; 500 revisions/128 MiB history; 512 MiB/2,000 archived workspace files; eight providers; one unlocked engine; bounded worker output/deadlines/resources. Unexpected/unsupported formats fail explicitly. Run hostile unknown code in a dedicated disposable VM with independent review; containers are not a certified hostile multi-tenant boundary.

Help is available inside the app before and after login. Do not send credentials/private source with support requests. Only creator links selected by the user open externally; unsolicited popups/navigation/permissions and renderer external network requests are blocked. CSP is defense in depth, not a browser-extension ad blocker or absolute immunity to XSS.
